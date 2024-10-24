from typing import Any

import pytest


@pytest.fixture
def response_all_list_one_project() -> dict[str, Any]:
    return {
        "lists": [
            {
                "id": "http://rdfh.ch/lists/9999/list1",
                "projectIri": "http://rdfh.ch/projects/projectIRI",
                "name": "firstList",
                "labels": [{"value": "List 1", "language": "en"}],
                "comments": [{"value": "This is the first list", "language": "en"}],
                "isRootNode": True,
            },
            {
                "id": "http://rdfh.ch/lists/9999/list2",
                "projectIri": "http://rdfh.ch/projects/projectIRI",
                "name": "secondList",
                "labels": [{"value": "List", "language": "en"}],
                "comments": [{"value": "This is the second list", "language": "en"}],
                "isRootNode": True,
            },
        ]
    }


@pytest.fixture
def response_all_list_one_project_no_lists() -> dict[str, Any]:
    return {"lists": []}


@pytest.fixture
def response_one_list() -> dict[str, Any]:
    return {
        "type": "ListGetResponseADM",
        "list": {
            "listinfo": {
                "id": "http://rdfh.ch/lists/9999/list1",
                "projectIri": "http://rdfh.ch/projects/projectIRI",
                "name": "firstList",
                "labels": [{"value": "List 1", "language": "en"}],
                "comments": [{"value": "This is the first list", "language": "en"}],
                "isRootNode": True,
            },
            "children": [
                {
                    "id": "http://rdfh.ch/lists/9999/n1",
                    "name": "n1",
                    "labels": [{"value": "Node 1", "language": "en"}],
                    "comments": [],
                    "position": 0,
                    "hasRootNode": "http://rdfh.ch/lists/9999/list1",
                    "children": [
                        {
                            "id": "http://rdfh.ch/lists/9999/n11",
                            "name": "n1.1",
                            "labels": [{"value": "Node 1.1", "language": "en"}],
                            "comments": [],
                            "position": 0,
                            "hasRootNode": "http://rdfh.ch/lists/9999/list1",
                            "children": [
                                {
                                    "id": "http://rdfh.ch/lists/9999/n111",
                                    "name": "n1.1.1",
                                    "labels": [{"value": "Node 1.1.1", "language": "en"}],
                                    "comments": [],
                                    "position": 0,
                                    "hasRootNode": "http://rdfh.ch/lists/9999/list1",
                                    "children": [],
                                },
                                {
                                    "id": "http://rdfh.ch/lists/9999/n112",
                                    "name": "n1.1.2",
                                    "labels": [{"value": "Node 1.1.2", "language": "en"}],
                                    "comments": [],
                                    "position": 1,
                                    "hasRootNode": "http://rdfh.ch/lists/9999/list1",
                                    "children": [],
                                },
                            ],
                        }
                    ],
                }
            ],
        },
    }
