import pytest
from rdflib import RDF
from rdflib import SH
from rdflib import Graph
from rdflib import Namespace

from dsp_tools.commands.xml_validate.models.input_problems import MaxCardinalityViolation
from dsp_tools.commands.xml_validate.models.input_problems import MinCardinalityViolation
from dsp_tools.commands.xml_validate.models.input_problems import NonExistentCardinalityViolation
from dsp_tools.commands.xml_validate.models.validation import UnexpectedComponent
from dsp_tools.commands.xml_validate.models.validation import ValidationResult
from dsp_tools.commands.xml_validate.reformat_validaton_result import _extract_one_violation
from dsp_tools.commands.xml_validate.reformat_validaton_result import _reformat_one_violation
from dsp_tools.commands.xml_validate.reformat_validaton_result import _separate_different_results

VALIDATION_PREFIXES = """
    @prefix onto: <http://0.0.0.0:3333/ontology/9999/onto/v2#> .
    @prefix sh: <http://www.w3.org/ns/shacl#> .
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
    """

ONTO = Namespace("http://0.0.0.0:3333/ontology/9999/onto/v2#")
DATA = Namespace("http://data/")


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
def data_min_count_violation() -> Graph:
    gstr = "<http://data/id_min_card> a <http://0.0.0.0:3333/ontology/9999/onto/v2#ClassMixedCard> ."
    g = Graph()
    g.parse(data=gstr, format="ttl")
    return g


@pytest.fixture
def data_class_constraint_component() -> Graph:
    gstr = "<http://data/id_2> a <http://0.0.0.0:3333/ontology/9999/onto/v2#ClassWithEverything> ."
    g = Graph()
    g.parse(data=gstr, format="ttl")
    return g


@pytest.fixture
def class_constraint_component() -> Graph:
    gstr = f"""{VALIDATION_PREFIXES}
    [] a sh:ValidationReport ;
    sh:result _:bn1 .

    [] a sh:ValidationReport ;
    sh:conforms false ;
    sh:result [ 
            a sh:ValidationResult ;
            sh:detail _:bn1 ;
            sh:focusNode <http://data/id_2> ;
            sh:resultMessage "Value does not have shape
                 <http://api.knora.org/ontology/knora-api/shapes/v2#ColorValue_ClassShape>" ;
            sh:resultPath onto:testColor ;
            sh:resultSeverity sh:Violation ;
            sh:sourceConstraintComponent sh:NodeConstraintComponent ;
            sh:sourceShape onto:testColor_PropShape ;
            sh:value <http://data/7a65dc11-de6d-4a6c-85ed-72cf346c153e> 
            ] .
    
    _:bn1 a sh:ValidationResult ;
    sh:focusNode <http://data/7a65dc11-de6d-4a6c-85ed-72cf346c153e> ;
    sh:resultMessage "Object must be a of type 'ColorValue'." ;
    sh:resultSeverity sh:Violation ;
    sh:sourceConstraintComponent sh:ClassConstraintComponent ;
    sh:sourceShape <http://api.knora.org/ontology/knora-api/shapes/v2#ColorValue_ClassShape> ;
    sh:value <http://data/7a65dc11-de6d-4a6c-85ed-72cf346c153e> .
    """
    g = Graph()
    g.parse(data=gstr, format="ttl")
    return g


@pytest.fixture
def violation_min_card() -> ValidationResult:
    return ValidationResult(
        source_constraint_component=SH.MinCountConstraintComponent,
        res_iri=DATA.id_min_card,
        res_class=ONTO.ClassMixedCard,
        property=ONTO.testGeoname,
        results_message="1-n",
    )


@pytest.fixture
def violation_max_card() -> ValidationResult:
    return ValidationResult(
        source_constraint_component=SH.MaxCountConstraintComponent,
        res_iri=DATA.id_max_card,
        res_class=ONTO.ClassMixedCard,
        property=ONTO.testDecimalSimpleText,
        results_message="0-1",
    )


@pytest.fixture
def violation_closed() -> ValidationResult:
    return ValidationResult(
        source_constraint_component=SH.ClosedConstraintComponent,
        res_iri=DATA.id_closed_constraint,
        res_class=ONTO.CardOneResource,
        property=ONTO.testIntegerSimpleText,
        results_message="Predicate ns3:testIntegerSimpleText is not allowed (closed shape)",
    )


@pytest.fixture
def violation_unknown() -> ValidationResult:
    return ValidationResult(
        source_constraint_component=SH.UniqueLangConstraintComponent,
        res_iri=DATA.id,
        res_class=ONTO.ClassMixedCard,
        property=ONTO.testIntegerSimpleText,
        results_message="This is a constraint that is not checked in the data and should never appear.",
    )


def test_separate_different_results(class_constraint_component: Graph, min_count_violation: Graph) -> None:
    test_g = class_constraint_component + min_count_violation
    result = _separate_different_results(test_g)
    assert len(result.node_constraint_component) == 1
    assert len(result.detail_bns) == 1
    assert len(result.cardinality_components) == 1


def test_extract_one_violation(min_count_violation: Graph, data_min_count_violation: Graph) -> None:
    bn = next(min_count_violation.subjects(RDF.type, SH.ValidationResult))
    result = _extract_one_violation(bn, min_count_violation, data_min_count_violation)
    assert result.source_constraint_component == SH.MinCountConstraintComponent
    assert result.res_iri == DATA.id_min_card
    assert result.res_class == ONTO.ClassMixedCard
    assert result.property == ONTO.testGeoname
    assert result.results_message == "1-n"


class TestReformatViolation:
    def test_min(self, violation_min_card: ValidationResult) -> None:
        result = _reformat_one_violation(violation_min_card)
        assert isinstance(result, MinCardinalityViolation)
        assert result.res_id == "id_min_card"
        assert result.res_type == "onto:ClassMixedCard"
        assert result.prop_name == "onto:testGeoname"
        assert result.expected_cardinality == "1-n"

    def test_max(self, violation_max_card: ValidationResult) -> None:
        result = _reformat_one_violation(violation_max_card)
        assert isinstance(result, MaxCardinalityViolation)
        assert result.res_id == "id_max_card"
        assert result.res_type == "onto:ClassMixedCard"
        assert result.prop_name == "onto:testDecimalSimpleText"
        assert result.expected_cardinality == "0-1"

    def test_closed(self, violation_closed: ValidationResult) -> None:
        result = _reformat_one_violation(violation_closed)
        assert isinstance(result, NonExistentCardinalityViolation)
        assert result.res_id == "id_closed_constraint"
        assert result.res_type == "onto:CardOneResource"
        assert result.prop_name == "onto:testIntegerSimpleText"

    def test_unknown(self, violation_unknown: ValidationResult) -> None:
        result = _reformat_one_violation(violation_unknown)
        assert isinstance(result, UnexpectedComponent)
        assert result.component_type == str(SH.UniqueLangConstraintComponent)


if __name__ == "__main__":
    pytest.main([__file__])
