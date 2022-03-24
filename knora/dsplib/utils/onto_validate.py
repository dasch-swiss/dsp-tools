import json
import os
import re
from typing import Any, Union, List, Set
import jsonschema
import jsonpath_ng, jsonpath_ng.ext
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
    Check if there are properties derived from hasLinkTo that form a circular reference. If so, these
    properties must have the cardinality 0-1 or 0-n, because during the xmlupload process, these values
    are temporarily removed.
    """

    # search the ontology for all properties that are derived from hasLinkTo, store them in a dict, and map
    # them to their objects (i.e. the resource classes they point to)
    # example: if the property 'rosetta:hasTextMedium' points to 'rosetta:Image2D':
    # link_properties = {'rosetta:hasTextMedium': ['rosetta:Image2D'], ...}
    ontos = data_model['project']['ontologies']
    link_properties: dict[str, List[str]] = dict()
    for index, onto in enumerate(ontos):
        hasLinkTo_matches = jsonpath_ng.ext.parse(
            f'$.project.ontologies[{index}].properties[?@.super[*] == hasLinkTo]'
        ).find(data_model)
        prop_obj_pair: dict[str, List[str]] = dict()
        for match in hasLinkTo_matches:
            prop = onto['name'] + ':' + match.value['name']
            target = match.value['object']
            if target != 'Resource':
                # make the target a fully qualified name (with the ontology's name prefixed)
                target = re.sub(r'^(:?)([^:]+)$', f'{onto["name"]}:\\2', target)
            prop_obj_pair[prop] = [target]
        link_properties.update(prop_obj_pair)

    # in case the object of a property is "Resource", the link can point to any resource class
    all_res_names: List[str] = list()
    for index, onto in enumerate(ontos):
        matches = jsonpath_ng.ext.parse(f'$.resources[*].name').find(onto)
        tmp = [f'{onto["name"]}:{match.value}' for match in matches]
        all_res_names.extend(tmp)
    for prop, targ in link_properties.items():
        if 'Resource' in targ:
            link_properties[prop] = all_res_names

    # make a dict that maps resource classes to their hasLinkTo-properties, and to the classes they point to
    # example: if 'rosetta:Text' has the property 'rosetta:hasTextMedium' that points to 'rosetta:Image2D':
    # dependencies = {'rosetta:Text': {'rosetta:hasTextMedium': ['rosetta:Image2D'], ...}}
    dependencies: dict[str, dict[str, List[str]]] = dict()
    for onto in ontos:
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
                    elif cardname not in dependencies[resname]:
                        dependencies[resname][cardname] = targets
                    else:
                        dependencies[resname][cardname].extend(targets)

    # iteratively purge dependencies from non-circular references
    for _ in range(30):
        # remove targets that point to a resource that is not in dependencies,
        # remove cardinalities that have no targets
        for res, cards in dependencies.copy().items():
            for card, targets in cards.copy().items():
                dependencies[res][card] = [target for target in targets if target in dependencies]
                if len(dependencies[res][card]) == 0:
                    del dependencies[res][card]
        # remove resources that have no cardinalities
        dependencies = {res: cards for res, cards in dependencies.items() if len(cards) > 0}
        # remove resources that are not pointed to by any target
        all_targets: Set[str] = set()
        for cards in dependencies.values():
            for trgt in cards.values():
                all_targets = all_targets | set(trgt)
        dependencies = {res: targets for res, targets in dependencies.items() if res in all_targets}

    # check the remaining dependencies (which are only the circular ones) if they have all 0-1 or 0-n
    ok_cardinalities = ['0-1', '0-n']
    notok_dependencies: dict[str, List[str]] = dict()
    for res, cards in dependencies.items():
        ontoname, resname = res.split(':')
        for card in cards:
            # the name of the cardinality could be with prepended onto, only with colon, or without anything
            card_without_colon = card.split(':')[1]
            card_with_colon = ':' + card_without_colon
            card_variations = [card, card_with_colon, card_without_colon]
            for card_variation in card_variations:
                match = jsonpath_ng.ext.parse(
                    f'$[?@.name == {ontoname}].resources[?@.name == {resname}].cardinalities[?@.propname == "{card_variation}"]'
                ).find(ontos)
                if len(match) > 0:
                    break
            card_numbers = match[0].value['cardinality']
            if card_numbers not in ok_cardinalities:
                if res not in notok_dependencies:
                    notok_dependencies[res] = [card]
                else:
                    notok_dependencies[res].append(card)

    if len(notok_dependencies) == 0:
        return True
    else:
        print('ERROR: Your ontology contains properties derived from "hasLinkTo" that allow circular references '
              'between resources. This is not a problem in itself, but if you try to upload data that actually '
              'contains circular references, these "hasLinkTo" cardinalities will be temporarily removed from the '
              'affected resources. Therefore, it is necessary that the involved "hasLinkTo" cardinalities have a '
              'cardinality of 0-1 or 0-n. \n'
              'Please make sure that the following cardinalities have a cardinality of 0-1 or 0-n:')
        for _res, _cards in notok_dependencies.items():
            print(_res)
            for card in _cards:
                print(f'\t{card}')
        return False

