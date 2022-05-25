import os
import re
from typing import Any, Union
import jsonschema
import json
import jsonpath_ng, jsonpath_ng.ext
import networkx as nx
from ..utils.expand_all_lists import expand_lists_from_excel


def validate_ontology(input_file_or_json: Union[str, dict[Any, Any], 'os.PathLike[Any]']) -> bool:
    """
    Validates an ontology against the knora schema

    Args:
        input_file_or_json: the ontology to be validated, can either be a file or a json string (dict)

    Returns:
        True if ontology passed validation, False otherwise
    """

    data_model: dict[Any, Any] = {}
    if isinstance(input_file_or_json, dict):
        data_model = input_file_or_json
    elif os.path.isfile(input_file_or_json):
        with open(input_file_or_json) as f:
            onto_json_str = f.read()
        data_model = json.loads(onto_json_str)
    else:
        print('Input is not valid.')
        exit(1)

    # expand all lists referenced in the list section of the data model
    new_lists = expand_lists_from_excel(data_model)

    # add the newly created lists from Excel to the ontology
    data_model['project']['lists'] = new_lists

    # validate the data model against the schema
    current_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(current_dir, '../schemas/ontology.json')) as s:
        schema = json.load(s)
    try:
        jsonschema.validate(instance=data_model, schema=schema)
    except jsonschema.exceptions.ValidationError as err:
        print(f'Data model did not pass validation. The error message is: {err.message}\n'
              f'The error occurred at {err.json_path}')
        return False

    # cardinalities check for circular references
    if check_cardinalities_of_circular_references(data_model):
        print('Data model is syntactically correct and passed validation.')
        return True
    else:
        return False


def check_cardinalities_of_circular_references(data_model: dict[Any, Any]) -> bool:
    """
    Check a data model if it contains properties derived from hasLinkTo that form a circular reference. If so, these
    properties must have the cardinality 0-1 or 0-n, because during the xmlupload process, these values
    are temporarily removed.

    Args:
        data_model: dictionary with a DSP project (as defined in a JSON ontology file)

    Returns:
        True if no circle was detected, or if all elements of all circles are of cardinality "0-1" or "0-n".
        False if there is a circle with at least one element that has a cardinality of "1" or "1-n".
    """

    link_properties = collect_link_properties(data_model)
    errors = identify_problematic_cardinalities(data_model, link_properties)

    if len(errors) == 0:
        return True
    else:
        print('ERROR: Your ontology contains properties derived from "hasLinkTo" that allow circular references '
              'between resources. This is not a problem in itself, but if you try to upload data that actually '
              'contains circular references, these "hasLinkTo" properties will be temporarily removed from the '
              'affected resources. Therefore, it is necessary that all involved "hasLinkTo" properties have a '
              'cardinality of 0-1 or 0-n. \n'
              'Please make sure that the following properties have a cardinality of 0-1 or 0-n:')
        for error in errors:
            print(f'\t- {error}')
        return False


def collect_link_properties(data_model: dict[Any, Any]) -> dict[str, list[str]]:
    """
    map the properties derived from hasLinkTo to the resource classes they point to, for example:
    link_properties = {'rosetta:hasImage2D': ['rosetta:Image2D'], ...}
    """
    ontos = data_model['project']['ontologies']
    hasLinkTo_props = {'hasLinkTo', 'isPartOf', 'isRegionOf', 'isAnnotationOf'}
    link_properties: dict[str, list[str]] = dict()
    for index, onto in enumerate(ontos):
        hasLinkTo_matches = list()
        # look for child-properties down to 5 inheritance levels that are derived from hasLinkTo-properties
        for i in range(5):
            for hasLinkTo_prop in hasLinkTo_props:
                hasLinkTo_matches.extend(jsonpath_ng.ext.parse(
                    f'$.project.ontologies[{index}].properties[?super[*] == {hasLinkTo_prop}]'
                ).find(data_model))
            # make the children from this round to the parents of the next round
            hasLinkTo_props = {x.value['name'] for x in hasLinkTo_matches}
        prop_obj_pair: dict[str, list[str]] = dict()
        for match in hasLinkTo_matches:
            prop = onto['name'] + ':' + match.value['name']
            target = match.value['object']
            if target != 'Resource':
                # make the target a fully qualified name (with the ontology's name prefixed)
                target = re.sub(r'^:([^:]+)$', f'{onto["name"]}:\\1', target)
            prop_obj_pair[prop] = [target]
        link_properties.update(prop_obj_pair)

    # in case the object of a property is "Resource", the link can point to any resource class
    all_res_names: list[str] = list()
    for index, onto in enumerate(ontos):
        matches = jsonpath_ng.ext.parse(f'$.resources[*].name').find(onto)
        tmp = [f'{onto["name"]}:{match.value}' for match in matches]
        all_res_names.extend(tmp)
    for prop, targ in link_properties.items():
        if 'Resource' in targ:
            link_properties[prop] = all_res_names

    return link_properties


def identify_problematic_cardinalities(data_model: dict[Any, Any], link_properties: dict[str, list[str]]) -> set[str]:
    """
    make an error list with all cardinalities that are part of a circle but have "1" or "1-n"
    """
    # make 2 dicts of the following form:
    # dependencies = {'rosetta:Text': {'rosetta:hasImage2D': ['rosetta:Image2D'], ...}}
    # cardinalities = {'rosetta:Text': {'rosetta:hasImage2D': '0-1', ...}}
    dependencies: dict[str, dict[str, list[str]]] = dict()
    cardinalities: dict[str, dict[str, str]] = dict()
    for onto in data_model['project']['ontologies']:
        for resource in onto['resources']:
            resname: str = onto['name'] + ':' + resource['name']
            for card in resource['cardinalities']:
                # make the cardinality a fully qualified name (with the ontology's name prefixed)
                cardname = re.sub(r'^(:?)([^:]+)$', f'{onto["name"]}:\\2', card['propname'])
                if cardname in link_properties:
                    # Look out: if `targets` is created with `targets = link_properties[cardname]`, the ex-
                    # pression `dependencies[resname][cardname] = targets` causes `dependencies[resname][cardname]`
                    # to point to `link_properties[cardname]`. Due to that, the expression
                    # `dependencies[resname][cardname].extend(targets)` will modify 'link_properties'!
                    # For this reason, `targets` must be created with `targets = list(link_properties[cardname])`
                    targets = list(link_properties[cardname])
                    if resname not in dependencies:
                        dependencies[resname] = dict()
                        dependencies[resname][cardname] = targets
                        cardinalities[resname] = dict()
                        cardinalities[resname][cardname] = card['cardinality']
                    elif cardname not in dependencies[resname]:
                        dependencies[resname][cardname] = targets
                        cardinalities[resname][cardname] = card['cardinality']
                    else:
                        dependencies[resname][cardname].extend(targets)

    # transform the dependencies into a graph structure
    graph = nx.MultiDiGraph()
    for start, cards in dependencies.items():
        for edge, targets in cards.items():
            for target in targets:
                graph.add_edge(start, target, edge)

    # find elements of circles that have a cardinality of "1" or "1-n"
    errors: set[str] = set()
    circles = list(nx.simple_cycles(graph))
    for circle in circles:
        for index, resource in enumerate(circle):
            target = circle[(index+1) % len(circle)]
            for property, targets in dependencies[resource].items():
                if target in targets:
                    prop = property
            if cardinalities[resource][prop] not in ['0-1', '0-n']:
                errors.add(f'Resource "{resource}", property "{prop}"')

    return errors
