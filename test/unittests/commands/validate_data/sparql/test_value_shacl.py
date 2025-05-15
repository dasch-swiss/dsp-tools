# mypy: disable-error-code="method-assign,no-untyped-def"

import pytest
from rdflib import RDF
from rdflib import SH
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.commands.validate_data.models.api_responses import AllProjectLists
from dsp_tools.commands.validate_data.models.api_responses import OneList
from dsp_tools.commands.validate_data.models.api_responses import SHACLListInfo
from dsp_tools.commands.validate_data.sparql.value_shacl import _add_property_shapes_to_class_shapes
from dsp_tools.commands.validate_data.sparql.value_shacl import _construct_link_value_shape
from dsp_tools.commands.validate_data.sparql.value_shacl import _construct_link_value_type_shapes_to_class_shapes
from dsp_tools.commands.validate_data.sparql.value_shacl import _construct_one_list_node_shape
from dsp_tools.commands.validate_data.sparql.value_shacl import _construct_one_list_property_shape_with_collection
from dsp_tools.commands.validate_data.sparql.value_shacl import _construct_one_property_type_text_value
from dsp_tools.commands.validate_data.sparql.value_shacl import _construct_value_type_shapes_to_class_shapes
from dsp_tools.commands.validate_data.sparql.value_shacl import construct_property_shapes
from dsp_tools.utils.rdflib_constants import API_SHAPES
from dsp_tools.utils.rdflib_constants import KNORA_API
from test.unittests.commands.validate_data.constants import ONTO


def test_construct_property_shapes(res_and_props_with_simpletext):
    proj_li = AllProjectLists([])
    res = construct_property_shapes(res_and_props_with_simpletext, proj_li)
    trip_counts = {
        ONTO.ClassWithEverything: 4,
        ONTO.testBoolean_PropShape: 4,
        ONTO.testSimpleText_PropShape: 5,
        ONTO.testDecimalSimpleText_PropShape: 4,
    }
    for shape, num_triples in trip_counts.items():
        created_triples = list(res.triples((shape, None, None)))
        assert len(created_triples) == num_triples

    total_triples = sum(trip_counts.values())
    assert len(res) == total_triples


def test_construct_link_value_shape(link_prop: Graph) -> None:
    res = _construct_link_value_shape(link_prop)
    assert len(res) == 3
    assert next(res.objects(ONTO.testHasLinkTo_PropShape, SH.path)) == ONTO.testHasLinkTo
    assert next(res.objects(ONTO.testHasLinkTo_PropShape, RDF.type)) == SH.PropertyShape
    assert next(res.objects(ONTO.testHasLinkTo_PropShape, SH.node)) == ONTO.testHasLinkTo_NodeShape


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
    expected_props = {ONTO.testBoolean_PropShape}
    assert set(res.objects(ONTO.ClassMixedCard, SH.property)) == expected_props


def test_construct_value_type_shapes_to_class_shapes_literal(card_1: Graph) -> None:
    res = _construct_value_type_shapes_to_class_shapes(card_1)
    prop_iri = ONTO.testBoolean_PropShape
    assert next(res.objects(prop_iri, SH.path)) == ONTO.testBoolean
    assert next(res.objects(prop_iri, URIRef("http://www.w3.org/ns/shacl#class"))) == KNORA_API.BooleanValue
    assert next(res.objects(prop_iri, SH.message)) == Literal("This property requires a BooleanValue")
    assert len(res) == 4


def test_construct_value_type_shapes_to_class_shapes_link_value(link_prop_card_1: Graph) -> None:
    res = _construct_value_type_shapes_to_class_shapes(link_prop_card_1)
    assert len(res) == 0


def test_construct_link_value_type_shapes_to_class_shapes_literal(card_1: Graph) -> None:
    res = _construct_link_value_type_shapes_to_class_shapes(card_1)
    assert len(res) == 0


def test_construct_link_value_type_shapes_to_class_shapes_link_value(link_prop_card_1: Graph) -> None:
    res = _construct_link_value_type_shapes_to_class_shapes(link_prop_card_1)
    prop_iri = ONTO.testHasLinkToCardOneResource_PropShape
    assert next(res.objects(prop_iri, SH.path)) == ONTO.testHasLinkToCardOneResource
    assert next(res.objects(prop_iri, URIRef("http://www.w3.org/ns/shacl#class"))) == KNORA_API.LinkValue
    assert next(res.objects(prop_iri, SH.message)) == Literal("This property requires a LinkValue")
    assert len(res) == 4


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
