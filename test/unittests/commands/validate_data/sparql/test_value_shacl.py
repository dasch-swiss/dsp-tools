import pytest
from rdflib import RDF
from rdflib import SH
from rdflib import Graph
from rdflib import URIRef

from dsp_tools.commands.validate_data.models.api_responses import OneList
from dsp_tools.commands.validate_data.models.api_responses import SHACLListInfo
from dsp_tools.commands.validate_data.sparql.value_shacl import _add_property_shapes_to_class_shapes
from dsp_tools.commands.validate_data.sparql.value_shacl import _construct_link_value_shape
from dsp_tools.commands.validate_data.sparql.value_shacl import _construct_one_list_node_shape
from dsp_tools.commands.validate_data.sparql.value_shacl import _construct_one_list_property_shape_with_collection
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
    assert len(res) == 3
    expected_props = {ONTO.testBoolean_PropShape, API_SHAPES.rdfsLabel_Shape}
    assert set(res.objects(ONTO.ClassMixedCard, SH.property)) == expected_props


class TestConstructListNode:
    def test_node_space(self) -> None:
        test_list = OneList(
            list_iri="http://rdfh.ch/lists/9999/test",
            list_name="list",
            nodes=["l2n1 space"],
        )
        result = _construct_one_list_node_shape(test_list)
        nodeshape_iri = URIRef("http://rdfh.ch/lists/9999/test")
        assert next(result.subjects(RDF.type, SH.NodeShape)) == nodeshape_iri

    def test_node_backslash(self) -> None:
        test_list = OneList(
            list_iri="http://rdfh.ch/lists/9999/test",
            list_name="list",
            nodes=["l2n1 \\ or"],
        )
        result = _construct_one_list_node_shape(test_list)
        nodeshape_iri = URIRef("http://rdfh.ch/lists/9999/test")
        assert next(result.subjects(RDF.type, SH.NodeShape)) == nodeshape_iri

    def test_node_double_quote(self) -> None:
        test_list = OneList(
            list_iri="http://rdfh.ch/lists/9999/test",
            list_name="list",
            nodes=['l2n2"'],
        )
        result = _construct_one_list_node_shape(test_list)
        nodeshape_iri = URIRef("http://rdfh.ch/lists/9999/test")
        assert next(result.subjects(RDF.type, SH.NodeShape)) == nodeshape_iri

    def test_node_apostrophe(self) -> None:
        test_list = OneList(
            list_iri="http://rdfh.ch/lists/9999/test",
            list_name="list",
            nodes=["l2n3'"],
        )
        result = _construct_one_list_node_shape(test_list)
        nodeshape_iri = URIRef("http://rdfh.ch/lists/9999/test")
        assert next(result.subjects(RDF.type, SH.NodeShape)) == nodeshape_iri

    def test_list_special(self) -> None:
        test_list = OneList(
            list_iri="http://rdfh.ch/lists/9999/test",
            list_name="secondList \\ ",
            nodes=["a"],
        )
        result = _construct_one_list_node_shape(test_list)
        nodeshape_iri = URIRef("http://rdfh.ch/lists/9999/test")
        assert next(result.subjects(RDF.type, SH.NodeShape)) == nodeshape_iri

    def test_list_double_quote(self) -> None:
        test_list = OneList(
            list_iri="http://rdfh.ch/lists/9999/test",
            list_name='secondList " ',
            nodes=["a"],
        )
        result = _construct_one_list_node_shape(test_list)
        nodeshape_iri = URIRef("http://rdfh.ch/lists/9999/test")
        assert next(result.subjects(RDF.type, SH.NodeShape)) == nodeshape_iri

    def test_list_single_quote(self) -> None:
        test_list = OneList(
            list_iri="http://rdfh.ch/lists/9999/test",
            list_name='secondList " ',
            nodes=["a"],
        )
        result = _construct_one_list_node_shape(test_list)
        nodeshape_iri = URIRef("http://rdfh.ch/lists/9999/test")
        assert next(result.subjects(RDF.type, SH.NodeShape)) == nodeshape_iri

    def test_construct_one_list_property_shape_with_collection_one(self) -> None:
        test_info = SHACLListInfo(
            list_iri=URIRef("http://rdfh.ch/lists/9999/test"),
            sh_path=ONTO.testListProp,
            sh_message="Test",
            sh_in=["one"],
        )
        result = _construct_one_list_property_shape_with_collection(test_info)
        number_of_strings_in_list = 1
        assert len(list(result.objects(predicate=RDF.first))) == number_of_strings_in_list

    def test_construct_one_list_property_shape_with_collection_three(self) -> None:
        test_info = SHACLListInfo(
            list_iri=URIRef("http://rdfh.ch/lists/9999/test"),
            sh_path=ONTO.testListProp,
            sh_message="Test",
            sh_in=["one", "two", "three"],
        )
        result = _construct_one_list_property_shape_with_collection(test_info)
        number_of_strings_in_list = 3
        assert len(list(result.objects(predicate=RDF.first))) == number_of_strings_in_list


if __name__ == "__main__":
    pytest.main([__file__])
