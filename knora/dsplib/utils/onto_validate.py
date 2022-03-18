import json
import os
import re
from typing import Any, Union, List, Set
import jsonschema
import jsonpath_ng, jsonpath_ng.ext
from ..utils.expand_all_lists import expand_lists_from_excel


def validate_ontology(input_file_or_json: Union[str, dict[Any, Any], os.PathLike]) -> bool:
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

    # Check if there are properties derived from hasLinkTo that form a circular reference. If so, these
    # properties must have the cardinality 0-1 or 0-n, because during the xmlupload process, these values
    # are temporarily removed.
    ontos = data_model['project']['ontologies']
    link_properties: dict[str, List[str]] = dict()
    for index, onto in enumerate(ontos):
        hasLinkTo_matches = jsonpath_ng.ext.parse(
            f'$.project.ontologies[{index}].properties[?@.super[*] == hasLinkTo]'
        ).find(data_model)
        new = dict()
        for match in hasLinkTo_matches:
            prop = onto['name'] + ':' + match.value['name']
            target = match.value['object']
            if target != 'Resource':
                target = re.sub(r'^(:?)([^:]+)$', f'{onto["name"]}:\\2', target)
            new[prop] = [target]
        link_properties.update(new)

    all_res_names: List[str] = list()
    for index, onto in enumerate(ontos):
        matches = jsonpath_ng.ext.parse(f'$.resources[*].name').find(onto)
        tmp = [f'{onto["name"]}:{match.value}' for match in matches]
        all_res_names.extend(tmp)
    for prop, targ in link_properties.items():
        if 'Resource' in targ:
            link_properties[prop] = all_res_names

    dependencies: dict[str, List[str]] = dict()
    for onto in ontos:
        for resource in onto['resources']:
            resname: str = onto['name'] + ':' + resource['name']
            for card in resource['cardinalities']:
                cardname = re.sub(r'^(:?)([^:]+)$', f'{onto["name"]}:\\2', card['propname'])
                if cardname in link_properties:
                    # Look out: if 'targets' points to 'link_properties', the expression
                    # `dependencies[resname].extend(targets)` will modify 'link_properties'!
                    # For this reason, a new list must be created with `list(link_properties[cardname])`
                    targets = list(link_properties[cardname])
                    if resname not in dependencies:
                        dependencies[resname] = targets
                    else:
                        dependencies[resname].extend(targets)

    # iteratively purge dependencies from non-circular references
    for i in range(30):
        # remove targets that point to a resource that is not in dependencies
        dependencies = {res: list({trg for trg in targets if trg in dependencies}) for res, targets in dependencies.items()}
        # remove resources that have no targets
        dependencies = {res: targets for res, targets in dependencies.items() if len(targets) > 0}
        # remove resources that are not pointed to by any target
        all_targets: Set[str] = set()
        for targets in dependencies.values():
            all_targets = all_targets.union(targets)
        dependencies = {res: targets for res, targets in dependencies.items() if res in all_targets}

    okay_cardinalities = ['0-1', '0-n']
    notok_dependencies: dict[str, List[str]] = dict()
    for res, deps in dependencies.items():
        ontoname, resname = res.split(':')
        for dep in deps:
            dep_without_colon = dep.split(':')[1]
            dep_with_colon = ':' + dep_without_colon
            card = jsonpath_ng.ext.parse(
                f'$[?@.name == {ontoname}].resources[?@.name == {resname}].cardinalities where ($[?@.propname == "{dep}"] | $[?@.propname == "{dep_with_colon}"] | $[?@.propname == "{dep_without_colon}"])'
            ).find(ontos)[0].value
            # problem: 'dependencies' stores the target resources, but I must search for the link prop. I need another dict
            # that stores the resources, link props and target resources all together...
            if card not in okay_cardinalities:
                if res not in notok_dependencies:
                    notok_dependencies[res] = [dep]
                else:
                    notok_dependencies[res].append(dep)



    print('Data model is syntactically correct and passed validation.')

    return True
