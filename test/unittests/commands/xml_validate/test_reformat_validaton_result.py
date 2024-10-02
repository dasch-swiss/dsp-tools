import pytest
from rdflib import RDF
from rdflib import SH
from rdflib import Graph
from rdflib import Namespace
from rdflib import URIRef

from dsp_tools.commands.xml_validate.reformat_validaton_result import _extract_one_violation

VALIDATION_PREFIXES = """
    @prefix onto: <http://0.0.0.0:3333/ontology/9999/onto/v2#> .
    @prefix sh: <http://www.w3.org/ns/shacl#> .
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
    """

ONTO = Namespace("http://0.0.0.0:3333/ontology/9999/onto/v2#")


@pytest.fixture
def min_count_violation() -> Graph:
    gstr = f"""{VALIDATION_PREFIXES}
    [ a sh:ValidationResult ;
            sh:focusNode <http://data/id_min_card> ;
            sh:resultMessage "1-n" ;
            sh:resultPath onto:testGeoname ;
            sh:resultSeverity sh:Violation ;
            sh:sourceConstraintComponent sh:MinCountConstraintComponent ;
            sh:sourceShape [ ] ] .
    """
    g = Graph()
    g.parse(data=gstr, format="ttl")
    return g


@pytest.fixture
def data() -> Graph:
    gstr = "<http://data/id_min_card> a <http://0.0.0.0:3333/ontology/9999/onto/v2#ClassMixedCard> ."
    g = Graph()
    g.parse(data=gstr, format="ttl")
    return g


def test_extract_one_violation(min_count_violation: Graph, data: Graph) -> None:
    bn = next(min_count_violation.subjects(RDF.type, SH.ValidationResult))
    result = _extract_one_violation(bn, min_count_violation, data)
    assert result.source_constraint_component == SH.MinCountConstraintComponent
    assert result.res_iri == URIRef("http://data/id_min_card")
    assert result.res_class == ONTO.ClassMixedCard
    assert result.property == ONTO.testGeoname
    assert result.results_message == "1-n"


if __name__ == "__main__":
    pytest.main([__file__])
