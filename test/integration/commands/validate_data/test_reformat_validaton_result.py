import pytest
from rdflib import Graph
from rdflib import URIRef

from dsp_tools.commands.validate_data.reformat_validaton_result import _extract_identifiers_of_resource_results


@pytest.fixture
def every_combination_once_report() -> Graph:
    g = Graph()
    g.parse("testdata/validate-data/validation_reports/every_combination_once_report.ttl")
    return g


@pytest.fixture
def every_combination_once_data() -> Graph:
    g = Graph()
    g.parse("testdata/validate-data/validation_reports/every_combination_once_data.ttl")
    return g


def test_separate_different_result_types(
    every_combination_once_report: Graph, every_combination_once_data: Graph
) -> None:
    result = _extract_identifiers_of_resource_results(every_combination_once_report, every_combination_once_data)
    result_sorted = sorted(result, key=lambda x: x.focus_node_iri)
    expected_iris = [
        URIRef("http://data/geoname_not_number"),
        URIRef("http://data/id_card_one"),
        URIRef("http://data/id_closed_constraint"),
        URIRef("http://data/id_max_card"),
        URIRef("http://data/id_simpletext"),
        URIRef("http://data/id_uri"),
    ]
    for result_iri, expected_iri in zip(result_sorted, expected_iris):
        assert result_iri.focus_node_iri == expected_iri
