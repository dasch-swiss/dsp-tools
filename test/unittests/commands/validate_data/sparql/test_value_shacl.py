import pytest
from rdflib import RDF
from rdflib import SH
from rdflib import Graph

from dsp_tools.commands.validate_data.models.api_responses import OneList
from dsp_tools.commands.validate_data.sparql.value_shacl import _add_property_shapes_to_class_shapes
from dsp_tools.commands.validate_data.sparql.value_shacl import _construct_link_value_shape
from dsp_tools.commands.validate_data.sparql.value_shacl import _construct_one_property_type_shape_based_on_object_type
from dsp_tools.commands.validate_data.sparql.value_shacl import _construct_one_property_type_text_value
from test.unittests.commands.validate_data.constants import API_SHAPES
from test.unittests.commands.validate_data.constants import ONTO


def test_construct_one_property_type_shape_based_on_object_type(one_res_one_prop: Graph) -> None:
    res = _construct_one_property_type_shape_based_on_object_type(
        one_res_one_prop, "knora-api:BooleanValue", "api-shapes:BooleanValue_ClassShape"
    )
    assert len(res) == 3
    assert next(res.objects(ONTO.testBoolean_PropShape, SH.path)) == ONTO.testBoolean
    assert next(res.objects(ONTO.testBoolean_PropShape, RDF.type)) == SH.PropertyShape
    assert next(res.objects(ONTO.testBoolean_PropShape, SH.node)) == API_SHAPES.BooleanValue_ClassShape


def test_construct_link_value_shape(link_prop: Graph) -> None:
    res = _construct_link_value_shape(link_prop)
    assert len(res) == 4
    assert next(res.objects(ONTO.testHasLinkTo_PropShape, SH.path)) == ONTO.testHasLinkTo
    assert next(res.objects(ONTO.testHasLinkTo_PropShape, RDF.type)) == SH.PropertyShape
    assert set(res.objects(ONTO.testHasLinkTo_PropShape, SH.node)) == {
        API_SHAPES.LinkValue_ClassShape,
        ONTO.testHasLinkTo_NodeShape,
    }


def test_construct_one_property_type_text_value(one_richtext_prop: Graph) -> None:
    res = _construct_one_property_type_text_value(
        one_richtext_prop, "salsah-gui:Richtext", "api-shapes:FormattedTextValue_ClassShape"
    )
    assert len(res) == 3
    assert next(res.objects(ONTO.testRichtext_PropShape, SH.path)) == ONTO.testRichtext
    assert next(res.objects(ONTO.testRichtext_PropShape, RDF.type)) == SH.PropertyShape
    assert next(res.objects(ONTO.testRichtext_PropShape, SH.node)) == API_SHAPES.FormattedTextValue_ClassShape


def test_add_property_shapes_to_class_shapes(card_1: Graph) -> None:
    res = _add_property_shapes_to_class_shapes(card_1)
    assert len(res) == 1
    assert next(res.objects(ONTO.ClassMixedCard, SH.property)) == ONTO.testBoolean_PropShape


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
            "labels": [{"value": "List", "language": "en"}],
            "comments": [
                {
                    "value": "This is the second list and contains characters that need to be escaped in turtle.",
                    "language": "en",
                }
            ],
            "isRootNode": True,
        },
        "children": [
            {
                "id": "http://rdfh.ch/lists/9999/UPnCJdK9Rc6i7tTdFwEAtQ",
                "name": "l2n1 \\ or",
                "labels": [{"value": "List 2, Node 1", "language": "en"}],
                "comments": [],
                "position": 0,
                "hasRootNode": "http://rdfh.ch/lists/9999/gsUgVoeiSk2wTQOZNHLPZA",
                "children": [],
            },
            {
                "id": "http://rdfh.ch/lists/9999/kTNIti9UQ3qYzQKgW1_hxA",
                "name": 'l2n2 "',
                "labels": [{"value": "List 2, Node 2", "language": "en"}],
                "comments": [],
                "position": 1,
                "hasRootNode": "http://rdfh.ch/lists/9999/gsUgVoeiSk2wTQOZNHLPZA",
                "children": [],
            },
            {
                "id": "http://rdfh.ch/lists/9999/yCMCZvd_RaCr9a75VXse9A",
                "name": "l2n3 '",
                "labels": [{"value": "List 2, Node 3", "language": "en"}],
                "comments": [],
                "position": 2,
                "hasRootNode": "http://rdfh.ch/lists/9999/gsUgVoeiSk2wTQOZNHLPZA",
                "children": [],
            },
        ],
    },
}

if __name__ == "__main__":
    pytest.main([__file__])
