# mypy: disable-error-code="method-assign,no-untyped-def"

import pytest
from rdflib import RDF
from rdflib import SH
from rdflib import XSD
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.commands.validate_data.models.api_responses import OneList
from dsp_tools.commands.validate_data.models.api_responses import OneNode
from dsp_tools.commands.validate_data.sparql.value_shacl import _add_property_shapes_to_class_shapes
from dsp_tools.commands.validate_data.sparql.value_shacl import _construct_link_value_shape
from dsp_tools.commands.validate_data.sparql.value_shacl import _construct_link_value_type_shapes_to_class_shapes
from dsp_tools.commands.validate_data.sparql.value_shacl import _construct_one_list_node_shape
from dsp_tools.commands.validate_data.sparql.value_shacl import _construct_one_property_type_text_value
from dsp_tools.commands.validate_data.sparql.value_shacl import _construct_value_type_shapes_to_class_shapes
from dsp_tools.commands.validate_data.sparql.value_shacl import construct_property_shapes
from dsp_tools.utils.rdflib_constants import API_SHAPES
from dsp_tools.utils.rdflib_constants import KNORA_API
from test.unittests.commands.validate_data.constants import ONTO


def test_construct_property_shapes(res_and_props_with_simpletext):
    res = construct_property_shapes(res_and_props_with_simpletext, [])
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
            nodes=[OneNode("l2n1 space", "http://rdfh.ch/lists/9999/l2n1")],
        )
        result = _construct_one_list_node_shape(test_list)
        nodeshape_iri = URIRef("http://rdfh.ch/lists/9999/test")
        assert next(result.subjects(RDF.type, SH.NodeShape)) == nodeshape_iri

    def test_node_backslash(self) -> None:
        test_list = OneList(
            list_iri="http://rdfh.ch/lists/9999/test",
            list_name="list",
            nodes=[OneNode("l2n1 \\ or", "http://rdfh.ch/lists/9999/l2n1or")],
        )
        result = _construct_one_list_node_shape(test_list)
        nodeshape_iri = URIRef("http://rdfh.ch/lists/9999/test")
        assert next(result.subjects(RDF.type, SH.NodeShape)) == nodeshape_iri

    def test_node_double_quote(self) -> None:
        test_list = OneList(
            list_iri="http://rdfh.ch/lists/9999/test",
            list_name="list",
            nodes=[OneNode('l2n2"', "http://rdfh.ch/lists/9999/l2n2")],
        )
        result = _construct_one_list_node_shape(test_list)
        nodeshape_iri = URIRef("http://rdfh.ch/lists/9999/test")
        assert next(result.subjects(RDF.type, SH.NodeShape)) == nodeshape_iri

    def test_node_apostrophe(self) -> None:
        test_list = OneList(
            list_iri="http://rdfh.ch/lists/9999/test",
            list_name="list",
            nodes=[OneNode("l2n3'", "http://rdfh.ch/lists/9999/l2n3")],
        )
        result = _construct_one_list_node_shape(test_list)
        nodeshape_iri = URIRef("http://rdfh.ch/lists/9999/test")
        assert next(result.subjects(RDF.type, SH.NodeShape)) == nodeshape_iri

    def test_list_special(self) -> None:
        test_list = OneList(
            list_iri="http://rdfh.ch/lists/9999/test",
            list_name="secondList \\ ",
            nodes=[OneNode("a", "http://rdfh.ch/lists/9999/a")],
        )
        result = _construct_one_list_node_shape(test_list)
        nodeshape_iri = URIRef("http://rdfh.ch/lists/9999/test")
        assert next(result.subjects(RDF.type, SH.NodeShape)) == nodeshape_iri

    def test_list_double_quote(self) -> None:
        test_list = OneList(
            list_iri="http://rdfh.ch/lists/9999/test",
            list_name='secondList " ',
            nodes=[OneNode("a", "http://rdfh.ch/lists/9999/a")],
        )
        result = _construct_one_list_node_shape(test_list)
        nodeshape_iri = URIRef("http://rdfh.ch/lists/9999/test")
        assert next(result.subjects(RDF.type, SH.NodeShape)) == nodeshape_iri

    def test_list_single_quote(self) -> None:
        test_list = OneList(
            list_iri="http://rdfh.ch/lists/9999/test",
            list_name='secondList " ',
            nodes=[OneNode("a", "http://rdfh.ch/lists/9999/a")],
        )
        result = _construct_one_list_node_shape(test_list)
        nodeshape_iri = URIRef("http://rdfh.ch/lists/9999/test")
        assert next(result.subjects(RDF.type, SH.NodeShape)) == nodeshape_iri

    def test_one_node(self) -> None:
        test_list = OneList(
            list_iri="http://rdfh.ch/lists/9999/test",
            list_name="list",
            nodes=[OneNode("l2n1 space", "http://rdfh.ch/lists/9999/l2n1")],
        )
        result = _construct_one_list_node_shape(test_list)
        nodeshape_iri = URIRef("http://rdfh.ch/lists/9999/test")
        assert next(result.subjects(RDF.type, SH.NodeShape)) == nodeshape_iri
        assert next(result.objects(nodeshape_iri, SH.severity)) == SH.Violation
        nd_bn = next(result.objects(nodeshape_iri, SH.property))
        assert next(result.objects(nd_bn, RDF.type)) == SH.PropertyShape
        assert next(result.objects(nd_bn, SH.path)) == KNORA_API.listValueAsListNode
        number_of_list_nodes = 1
        assert len(list(result.objects(predicate=RDF.first))) == number_of_list_nodes
        expected_msg = (
            "A valid node from the list 'list' must be used with this property "
            "(input displayed in format 'listName / NodeName')."
        )
        assert next(result.objects(nd_bn, SH.message)) == Literal(expected_msg, datatype=XSD.string)

    def test_three_nodes(self) -> None:
        test_list = OneList(
            list_iri="http://rdfh.ch/lists/9999/test",
            list_name="list",
            nodes=[
                OneNode("one", "http://rdfh.ch/lists/9999/1"),
                OneNode("two", "http://rdfh.ch/lists/9999/2"),
                OneNode("three", "http://rdfh.ch/lists/9999/3"),
            ],
        )
        result = _construct_one_list_node_shape(test_list)
        nodeshape_iri = URIRef("http://rdfh.ch/lists/9999/test")
        assert next(result.subjects(RDF.type, SH.NodeShape)) == nodeshape_iri
        assert next(result.objects(nodeshape_iri, SH.severity)) == SH.Violation
        nd_bn = next(result.objects(nodeshape_iri, SH.property))
        assert next(result.objects(nd_bn, RDF.type)) == SH.PropertyShape
        assert next(result.objects(nd_bn, SH.path)) == KNORA_API.listValueAsListNode
        number_of_list_nodes = 3
        assert len(list(result.objects(predicate=RDF.first))) == number_of_list_nodes
        expected_msg = (
            "A valid node from the list 'list' must be used with this property "
            "(input displayed in format 'listName / NodeName')."
        )
        assert next(result.objects(nd_bn, SH.message)) == Literal(expected_msg, datatype=XSD.string)


if __name__ == "__main__":
    pytest.main([__file__])
