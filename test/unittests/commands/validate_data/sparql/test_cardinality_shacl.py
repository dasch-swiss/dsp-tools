import pytest
from rdflib import RDF
from rdflib import SH
from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.commands.validate_data.sparql.cardinality_shacl import _construct_0_1_cardinality
from dsp_tools.commands.validate_data.sparql.cardinality_shacl import _construct_0_n_cardinality
from dsp_tools.commands.validate_data.sparql.cardinality_shacl import _construct_1_cardinality
from dsp_tools.commands.validate_data.sparql.cardinality_shacl import _construct_1_n_cardinality
from dsp_tools.commands.validate_data.sparql.cardinality_shacl import _construct_all_cardinalities
from dsp_tools.commands.validate_data.sparql.cardinality_shacl import _construct_resource_nodeshape
from dsp_tools.commands.validate_data.sparql.cardinality_shacl import construct_cardinality_node_shapes
from dsp_tools.utils.rdflib_constants import DASH
from test.unittests.commands.validate_data.constants import ONTO


class TestCheckTripleNumbersOnto:
    def test_nodeshape(self, onto_for_cardinality: Graph) -> None:
        result = _construct_resource_nodeshape(onto_for_cardinality)
        number_of_resource_classes = 12
        triples_cls_nodeshape = 13 * number_of_resource_classes
        assert len(result) == triples_cls_nodeshape

    def test_cardinality_1(self, onto_for_cardinality: Graph) -> None:
        result = _construct_1_cardinality(onto_for_cardinality)
        number_of_occurrences_in_onto = 2
        triples_card_1 = 7 * number_of_occurrences_in_onto
        assert len(result) == triples_card_1

    def test_cardinality_0_1(self, onto_for_cardinality: Graph) -> None:
        result = _construct_0_1_cardinality(onto_for_cardinality)
        number_of_occurrences_in_onto = 5
        triples_card_0_1 = 7 * number_of_occurrences_in_onto
        assert len(result) == triples_card_0_1

    def test_cardinality_0_n(self, onto_for_cardinality: Graph) -> None:
        result = _construct_0_n_cardinality(onto_for_cardinality)
        number_of_occurrences_in_onto = 22  # Inheritance included
        triples_card_0_n = 3 * number_of_occurrences_in_onto
        assert len(result) == triples_card_0_n

    def test_cardinality_1_n(self, onto_for_cardinality: Graph) -> None:
        result = _construct_1_n_cardinality(onto_for_cardinality)
        number_of_occurrences_in_onto = 1
        triples_card_1_n = 6 * number_of_occurrences_in_onto
        assert len(result) == triples_card_1_n


def test_construct_cardinality_node_shapes(onto_for_cardinality: Graph) -> None:
    result = construct_cardinality_node_shapes(onto_for_cardinality)
    expected_classes = {
        ONTO.ClassInheritedCardinality,
        ONTO.ClassMixedCard,
        ONTO.CardOneResource,
        ONTO.ClassWithEverything,
        ONTO.TestStillImageRepresentation,
        ONTO.ClassInheritedCardinalityOverwriting,
        ONTO.TestArchiveRepresentation,
        ONTO.TestAudioRepresentation,
        ONTO.TestDocumentRepresentation,
        ONTO.TestMovingImageRepresentation,
        ONTO.TestStillImageRepresentation,
        ONTO.TestTextRepresentation,
        URIRef("http://0.0.0.0:3333/ontology/9999/second-onto/v2#SecondOntoClass"),
    }
    result_classes = set(result.subjects(DASH.closedByTypes, Literal(True)))
    assert result_classes == expected_classes


def test_construct_resource_nodeshape_one_res(one_res_one_prop: Graph) -> None:
    result = _construct_resource_nodeshape(one_res_one_prop)
    subjects = {iri for x in result.triples((None, None, None)) if not isinstance(iri := x[0], BNode)}
    assert len(subjects) == 1
    subject_iri = subjects.pop()
    assert subject_iri == ONTO.CardOneResource
    node_triples = list(result.triples((subject_iri, None, None)))
    num_triples = 5
    assert len(node_triples) == num_triples
    assert next(result.subjects(RDF.type, SH.NodeShape)) == subject_iri
    assert next(result.objects(subject_iri, DASH.closedByTypes)) == Literal(True)
    assert isinstance(next(result.objects(subject_iri, SH.property)), BNode)


def test_construct_resource_nodeshape_no_res(one_bool_prop: Graph) -> None:
    result = _construct_resource_nodeshape(one_bool_prop)
    assert len(result) == 0


class Test1:
    def test_good(self, card_1: Graph) -> None:
        result = _construct_1_cardinality(card_1)
        assert len(result) == 7
        bn = next(result.subjects(RDF.type, SH.PropertyShape))
        shape_iri = next(result.subjects(SH.property, bn))
        assert shape_iri == ONTO.ClassMixedCard
        assert str(next(result.objects(bn, SH.minCount))) == "1"
        assert str(next(result.objects(bn, SH.maxCount))) == "1"
        assert next(result.objects(bn, SH.path)) == ONTO.testBoolean
        assert next(result.objects(bn, SH.severity)) == SH.Violation
        assert str(next(result.objects(bn, SH.message))) == "Cardinality 1"

    def test_good_link_value(self, link_prop_card_1: Graph) -> None:
        result = _construct_1_cardinality(link_prop_card_1)
        assert len(result) == 7
        bn = next(result.subjects(RDF.type, SH.PropertyShape))
        shape_iri = next(result.subjects(SH.property, bn))
        assert shape_iri == ONTO.ClassMixedCard
        assert str(next(result.objects(bn, SH.minCount))) == "1"
        assert str(next(result.objects(bn, SH.maxCount))) == "1"
        assert next(result.objects(bn, SH.path)) == ONTO.testHasLinkToCardOneResource
        assert next(result.objects(bn, SH.severity)) == SH.Violation
        assert str(next(result.objects(bn, SH.message))) == "Cardinality 1"

    def test_empty_0_1(self, card_0_1: Graph) -> None:
        result = _construct_1_cardinality(card_0_1)
        assert len(result) == 0

    def test_empty_1_n(self, card_1_n: Graph) -> None:
        result = _construct_1_cardinality(card_1_n)
        assert len(result) == 0

    def test_empty_0_n(self, card_0_n: Graph) -> None:
        result = _construct_1_cardinality(card_0_n)
        assert len(result) == 0


class Test01:
    def test_good(self, card_0_1: Graph) -> None:
        result = _construct_0_1_cardinality(card_0_1)
        assert len(result) == 7
        bn = next(result.subjects(RDF.type, SH.PropertyShape))
        shape_iri = next(result.subjects(SH.property, bn))
        assert shape_iri == ONTO.ClassMixedCard
        assert str(next(result.objects(bn, SH.minCount))) == "0"
        assert str(next(result.objects(bn, SH.maxCount))) == "1"
        assert next(result.objects(bn, SH.path)) == ONTO.testDecimalSimpleText
        assert next(result.objects(bn, SH.severity)) == SH.Violation
        assert str(next(result.objects(bn, SH.message))) == "Cardinality 0-1"

    def test_good_link_value(self, link_prop_card_01: Graph) -> None:
        result = _construct_0_1_cardinality(link_prop_card_01)
        assert len(result) == 7
        bn = next(result.subjects(RDF.type, SH.PropertyShape))
        shape_iri = next(result.subjects(SH.property, bn))
        assert shape_iri == ONTO.ClassMixedCard
        assert str(next(result.objects(bn, SH.minCount))) == "0"
        assert str(next(result.objects(bn, SH.maxCount))) == "1"
        assert next(result.objects(bn, SH.path)) == ONTO.testHasLinkToCardOneResource
        assert next(result.objects(bn, SH.severity)) == SH.Violation
        assert str(next(result.objects(bn, SH.message))) == "Cardinality 0-1"

    def test_empty_1(self, card_1: Graph) -> None:
        result = _construct_0_1_cardinality(card_1)
        assert len(result) == 0

    def test_empty_1_n(self, card_1_n: Graph) -> None:
        result = _construct_0_1_cardinality(card_1_n)
        assert len(result) == 0

    def test_empty_0_n(self, card_0_n: Graph) -> None:
        result = _construct_0_1_cardinality(card_0_n)
        assert len(result) == 0


class Test1N:
    def test_good(self, card_1_n: Graph) -> None:
        result = _construct_1_n_cardinality(card_1_n)
        assert len(result) == 6
        bn = next(result.subjects(RDF.type, SH.PropertyShape))
        shape_iri = next(result.subjects(SH.property, bn))
        assert shape_iri == ONTO.ClassMixedCard
        assert str(next(result.objects(bn, SH.minCount))) == "1"
        assert next(result.objects(bn, SH.path)) == ONTO.testGeoname
        assert next(result.objects(bn, SH.severity)) == SH.Violation
        assert str(next(result.objects(bn, SH.message))) == "Cardinality 1-n"

    def test_empty_1(self, card_1: Graph) -> None:
        result = _construct_1_n_cardinality(card_1)
        assert len(result) == 0

    def test_empty_1_n(self, card_0_1: Graph) -> None:
        result = _construct_1_n_cardinality(card_0_1)
        assert len(result) == 0

    def test_empty_0_n(self, card_0_n: Graph) -> None:
        result = _construct_1_n_cardinality(card_0_n)
        assert len(result) == 0


class Test0N:
    def test_good(self, card_0_n: Graph) -> None:
        result = _construct_0_n_cardinality(card_0_n)
        assert len(result) == 3
        bn = next(result.subjects(RDF.type, SH.PropertyShape))
        shape_iri = next(result.subjects(SH.property, bn))
        assert shape_iri == ONTO.ClassMixedCard
        assert next(result.objects(bn, SH.path)) == ONTO.testSimpleText

    def test_empty_1_n(self, card_1_n: Graph) -> None:
        result = _construct_0_n_cardinality(card_1_n)
        assert len(result) == 0

    def test_empty_1(self, card_1: Graph) -> None:
        result = _construct_0_n_cardinality(card_1)
        assert len(result) == 0

    def test_empty_0_1(self, card_0_1: Graph) -> None:
        result = _construct_0_n_cardinality(card_0_1)
        assert len(result) == 0


def test_construct_all_cardinalities(one_res_one_prop: Graph) -> None:
    result = _construct_all_cardinalities(one_res_one_prop)
    assert len(result) == 7
    bn = next(result.subjects(RDF.type, SH.PropertyShape))
    shape_iri = next(result.subjects(SH.property, bn))
    assert shape_iri == ONTO.CardOneResource
    assert str(next(result.objects(bn, SH.minCount))) == "1"
    assert str(next(result.objects(bn, SH.maxCount))) == "1"
    assert next(result.objects(bn, SH.path)) == ONTO.testBoolean
    assert next(result.objects(bn, SH.severity)) == SH.Violation
    assert str(next(result.objects(bn, SH.message))) == "Cardinality 1"


if __name__ == "__main__":
    pytest.main([__file__])
