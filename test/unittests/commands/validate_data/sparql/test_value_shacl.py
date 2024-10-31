import pytest


from dsp_tools.commands.validate_data.sparql.value_shacl import _construct_one_list_node_shape
from dsp_tools.commands.validate_data.models.api_responses import OneList

class TestConstructListNode:
    def test_node_space(self) -> None:
        test_list = OneList(list_iri="<https//:>", list_name="", nodes=[])

    def test_node_backslash(self) -> None:
        test_list = OneList(list_iri="", list_name="", nodes=[])


    def test_node_apostrophe(self) -> None:
        test_list = OneList(list_iri="", list_name="", nodes=[])

    def test_list_special(self):
        test_list = OneList(list_iri="", list_name="", nodes=["a"])





l = {
  "type": "ListGetResponseADM",
  "list": {
    "listinfo": {
      "id": "http://rdfh.ch/lists/9999/gsUgVoeiSk2wTQOZNHLPZA",
      "projectIri": "http://rdfh.ch/projects/meXOSM_fSBqwbum-qaqqOg",
      "name": "secondList \\ ' space",
      "labels": [
        {
          "value": "List",
          "language": "en"
        }
      ],
      "comments": [
        {
          "value": "This is the second list and contains characters that need to be escaped in turtle.",
          "language": "en"
        }
      ],
      "isRootNode": True
    },
    "children": [
      {
        "id": "http://rdfh.ch/lists/9999/UPnCJdK9Rc6i7tTdFwEAtQ",
        "name": "l2n1 \\ or",
        "labels": [
          {
            "value": "List 2, Node 1",
            "language": "en"
          }
        ],
        "comments": [],
        "position": 0,
        "hasRootNode": "http://rdfh.ch/lists/9999/gsUgVoeiSk2wTQOZNHLPZA",
        "children": []
      },
      {
        "id": "http://rdfh.ch/lists/9999/kTNIti9UQ3qYzQKgW1_hxA",
        "name": "l2n2 \"",
        "labels": [
          {
            "value": "List 2, Node 2",
            "language": "en"
          }
        ],
        "comments": [],
        "position": 1,
        "hasRootNode": "http://rdfh.ch/lists/9999/gsUgVoeiSk2wTQOZNHLPZA",
        "children": []
      },
      {
        "id": "http://rdfh.ch/lists/9999/yCMCZvd_RaCr9a75VXse9A",
        "name": "l2n3 '",
        "labels": [
          {
            "value": "List 2, Node 3",
            "language": "en"
          }
        ],
        "comments": [],
        "position": 2,
        "hasRootNode": "http://rdfh.ch/lists/9999/gsUgVoeiSk2wTQOZNHLPZA",
        "children": []
      }
    ]
  }
}


if __name__ == "__main__":
    pytest.main([__file__])
