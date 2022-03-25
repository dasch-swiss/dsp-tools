import json
from typing import Any, Union, cast
from lxml import etree
import csv2xml_helper_functions as csv2xml


def create_lists(number_of_lists: int, num_of_depth_levels: int, nodes_per_depth_level: int) -> list[dict[Any, Any]]:
    pass


def create_ontologies() -> list[dict[Any, Any]]:
    pass


def validate_int_lists(value: Union[int, list[int]], max: int, default: int, length: int) -> list[int]:
    if value is None:
        new_value = [default] * length
    elif isinstance(value, int) and 1 <= value <= max:
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
    num_of_ontos: int = config.get("identicalOntologies", 1)
    parsed_resources: dict[Any, Any] = dict()
    for resname, resdef in config.get("resources").items():
        inh_depth: int = resdef.get("inheritanceDepth", 1)
        classes_per_level = validate_int_lists(
            value=resdef.get("classesPerInheritanceLevel"),
            max=10,
            default=1,
            length=inh_depth
        )
        res_per_class = validate_int_lists(
            value=resdef.get("resourcesPerClass"),
            max=10000,
            default=10,
            length=inh_depth
        )
        ann_per_res = validate_int_lists(
            value=resdef.get("AnnotationsPerResource"),
            max=100,
            default=0,
            length=inh_depth
        )


        # TODO: cardinalities


    # prepare the structure of a data model
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
    
