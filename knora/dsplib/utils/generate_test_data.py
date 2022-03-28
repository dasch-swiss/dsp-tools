import json
from typing import Any, Union, cast, Optional
from lxml import etree
from enum import Enum
import csv2xml_helper_functions as csv2xml


allowed_resources = [
    'Resource'
    'StillImageRepresentation'
    'TextRepresentation'
    'AudioRepresentation'
    'DDDRepresentation'
    'DocumentRepresentation'
    'MovingImageRepresentation'
    'ArchiveRepresentation'
    'LinkObj'
]

available_file_sizes = {
    '5KB': 5000,
    '10KB': 10000,
    '50KB': 50000,
    '100KB': 100000,
    '500KB': 500000,
    '1MB': 1000000,
    '5MB': 5000000,
    '10MB': 10000000,
    '50MB': 50000000,
    '100MB': 100000000,
}


class Defaults(Enum):
    numOfValuesPerProp = 1
    fileSize = 5000
    cardinality = '0-n'
    permission_sys_default = {'res-default': ['V', 'V', 'CR', 'CR']}
    permission_proj_default = None


def create_lists(number_of_lists: int, num_of_depth_levels: int, nodes_per_depth_level: int) -> list[dict[Any, Any]]:
    pass


def create_ontologies() -> list[dict[Any, Any]]:
    pass


def parse_permissions(value: Optional[dict[str, list[str]]]) -> dict[str, list[str]]:
    if value is None:
        return cast(dict[str, list[str]], Defaults.permission_sys_default)
    # TODO: if there are multiple permissions in the dict, find a way to define one as permission_proj_default


def parse_cardinalities(value: Optional[Union[int, dict[str, Any]]], permissions: dict[str, list[str]]) -> dict[str, Any]:
    if value is None:
        pass
        #TODO
    elif isinstance(value, int):
        res = {
            'numOfProps': value,
            'numOfValuesPerProp': [Defaults.numOfValuesPerProp] * value,
            'cardinality': [Defaults.cardinality] * value,
            'permissions': [Defaults.permission] * value
        }
    else:
        print('ERROR')

def validate_file_size_list(value: Optional[Union[str, list[str]]], length: int) -> list[int]:
    if value is None:
        new_value = [Defaults.fileSize] * length
    elif isinstance(value, str) and value in available_file_sizes:
        new_value = [available_file_sizes[value]] * length
    elif all([
        isinstance(value, list)
        and len(value) == length
        and all([elem in available_file_sizes for elem in value])
    ]):
        new_value = [available_file_sizes[elem] for elem in value]
    else:
        print('ERROR')
    return new_value


def validate_int_list(value: Optional[Union[int, list[int]]], maximum: int, default: int, length: int) -> list[int]:
    if value is None:
        new_value = [default] * length
    elif isinstance(value, int) and 1 <= value <= maximum:
        new_value = [value] * length
    elif all([
        isinstance(value, list)
        and len(value) == length
        and all([isinstance(elem, int) for elem in value])
        and all([1 <= elem <= 10 for elem in value])
    ]):
        new_value = cast(list[int], value)
    else:
        print('ERROR')
    return new_value


def create_configurable_test_data(config: dict[Any, Any]) -> None:
    # TODO: validate the config file

    # parse the config file
    #######################
    permissions = parse_permissions(config.get('permissions'))
    num_of_ontos: int = config.get("identicalOntologies", 1)
    parsed_resources: dict[Any, Any] = dict()
    for resname, resdef in config.get("resources").items():
        if resname not in allowed_resources:
            print('ERROR')
        inh_depth: int = resdef.get("inheritanceDepth", 1)
        classes_per_level = validate_int_list(
            value=resdef.get("classesPerInheritanceLevel"),
            maximum=10,
            default=1,
            length=inh_depth
        )
        res_per_class = validate_int_list(
            value=resdef.get("resourcesPerClass"),
            maximum=10000,
            default=10,
            length=inh_depth
        )
        ann_per_res = validate_int_list(
            value=resdef.get("AnnotationsPerResource"),
            maximum=100,
            default=0,
            length=inh_depth
        )
        regions_per_res = validate_int_list(
            value=resdef.get("RegionsPerResource"),
            maximum=100,
            default=0,
            length=inh_depth
        )
        file_size = validate_file_size_list(resdef.get('fileSize'), length=inh_depth)
        cardinalities = parse_cardinalities(resdef.get('cardinalities'), permissions)
        # TODO: isCompoundedOf
        parsed_resources[resname] = {
            'inheritanceDepth': inh_depth,
            'classesPerInheritanceLevel': classes_per_level,
            'resourcesPerClass': res_per_class,
            'AnnotationsPerResource': ann_per_res,
            'RegionsPerResource': regions_per_res,
            'fileSize': file_size,
            'cardinalities': cardinalities
        }

    properties = config.get('properties')


    # prepare the structure of a data model
    #######################################
    data_model = {
        "$schema": "https://raw.githubusercontent.com/dasch-swiss/dsp-tools/main/knora/dsplib/schemas/ontology.json",
        "project": {
            "shortcode": "0820",
            "shortname": "generatedproject",
            "longname": "A generated project",
            "groups": [
                {
                    "name": "testproject-editors",
                    "selfjoin": False,
                    "status": True
                }
            ],
            "users": [
                {
                    "username": "testprojectedit",
                    "email": "testprojectedit@test.org",
                    "givenName": "testproject-given",
                    "familyName": "testproject-family",
                    "password": "testproject1234",
                    "lang": "de",
                    "groups": [
                        ":testproject-editors"
                    ],
                    "projects": [
                        ":admin"
                    ]
                }
            ],
        }
    }

    data_model['project']['lists'] = create_lists(
        number_of_lists=number_of_lists,
        num_of_depth_levels=num_of_depth_levels,
        nodes_per_depth_level=nodes_per_depth_level
    )
    data_model['project']['ontologies'] = create_ontologies(parameters)





    root = make_root(shortcode=shortcode, default_ontology=default_ontology)
    root = append_permissions(root)



    ############
    # write files
    ############
    with open('testproject.json', 'w', encoding='utf8') as outfile:
        json.dump(data_model, outfile, indent=4, ensure_ascii=False)
    
