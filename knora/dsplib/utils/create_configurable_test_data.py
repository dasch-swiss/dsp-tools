import json
from typing import Any
from lxml import etree
from csv2xml_helper_functions import *

def create_lists(parameters) -> list[dict[Any, Any]]:
    pass


def create_ontologies(parameters) -> list[dict[Any, Any]]:
    pass


def create_configurable_test_data(parameters) -> None:
    #############
    # create JSON
    #############

    # prepare the structure of a data model
    data_model = {
        "$schema": "https://raw.githubusercontent.com/dasch-swiss/dsp-tools/main/knora/dsplib/schemas/ontology.json",
        "project": {
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
    
    shortcode_range = [0800, ]
    shortname_range = [f'shortname-{i}' for i in range(100)]
    longname_range = [f'longname-{i}' for i in range(100)]
    
    data_model['project']['shortcode'] = next(shortcode_range)
    data_model['project']['shortname'] = next(shortname_range)
    data_model['project']['longname'] = next(longname_range)
    data_model['project']['lists'] = create_lists(parameters)
    data_model['project']['ontologies'] = create_ontologies(parameters)



    ############
    # create XML
    ############
    root = make_root(shortcode=shortcode, default_ontology=default_ontology)
    root = append_permissions(root)



    ############
    # write files
    ############
    with open('testproject.json', 'w', encoding='utf8') as outfile:
        json.dump(data_model, outfile, indent=4, ensure_ascii=False)
    
