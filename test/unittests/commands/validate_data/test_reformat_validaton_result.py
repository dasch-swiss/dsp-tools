import pytest
from rdflib import RDF
from rdflib import SH
from rdflib import Graph
from rdflib import Namespace

from dsp_tools.commands.validate_data.models.input_problems import MaxCardinalityViolation
from dsp_tools.commands.validate_data.models.input_problems import MinCardinalityViolation
from dsp_tools.commands.validate_data.models.input_problems import NonExistentCardinalityViolation
from dsp_tools.commands.validate_data.models.input_problems import ValueTypeViolation
from dsp_tools.commands.validate_data.models.validation import CardinalityValidationResult
from dsp_tools.commands.validate_data.models.validation import ContentValidationResult
from dsp_tools.commands.validate_data.models.validation import UnexpectedComponent
from dsp_tools.commands.validate_data.reformat_validaton_result import _query_for_one_cardinality_validation_result
from dsp_tools.commands.validate_data.reformat_validaton_result import _query_for_one_content_validation_result
from dsp_tools.commands.validate_data.reformat_validaton_result import _reformat_one_cardinality_validation_result
from dsp_tools.commands.validate_data.reformat_validaton_result import _reformat_one_content_validation_result

VALIDATION_PREFIXES = """
    @prefix onto: <http://0.0.0.0:3333/ontology/9999/onto/v2#> .
    @prefix sh: <http://www.w3.org/ns/shacl#> .
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
    """

ONTO = Namespace("http://0.0.0.0:3333/ontology/9999/onto/v2#")
DATA = Namespace("http://data/")
KNORA_API = Namespace("http://api.knora.org/ontology/knora-api/v2#")


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
def data_value_type_mismatch() -> Graph:
    gstr = """
    <http://data/id_2> a <http://0.0.0.0:3333/ontology/9999/onto/v2#ClassWithEverything> .
    <http://data/value-iri> a <http://api.knora.org/ontology/knora-api/v2#TextValue> .
    """
    g = Graph()
    g.parse(data=gstr, format="ttl")
    return g


@pytest.fixture
def graph_value_type_mismatch() -> Graph:
    gstr = f'''{VALIDATION_PREFIXES}
    [] a sh:ValidationReport ;
    sh:result _:bn1 .

    [] a sh:ValidationReport ;
    sh:conforms false ;
    sh:result [ 
            a sh:ValidationResult ;
            sh:detail _:bn1 ;
            sh:focusNode <http://data/id_2> ;
            sh:resultMessage """Value does not have shape
                 <http://api.knora.org/ontology/knora-api/shapes/v2#ColorValue_ClassShape>""" ;
            sh:resultPath onto:testColor ;
            sh:resultSeverity sh:Violation ;
            sh:sourceConstraintComponent sh:NodeConstraintComponent ;
            sh:sourceShape onto:testColor_PropShape ;
            sh:value <http://data/value-iri> 
            ] .
    
    _:bn1 a sh:ValidationResult ;
    sh:focusNode <http://data/value-iri> ;
    sh:resultMessage "ColorValue" ;
    sh:resultSeverity sh:Violation ;
    sh:sourceConstraintComponent sh:ClassConstraintComponent ;
    sh:sourceShape <http://api.knora.org/ontology/knora-api/shapes/v2#ColorValue_ClassShape> ;
    sh:value <http://data/value-iri> .
    '''
    g = Graph()
    g.parse(data=gstr, format="ttl")
    return g


@pytest.fixture
def data_wrong_regex_content() -> Graph:
    gstr = """
    <http://data/geoname_not_number> a <http://0.0.0.0:3333/ontology/9999/onto/v2#ClassWithEverything> .
    <http://data/value-iri> a <http://api.knora.org/ontology/knora-api/v2#TextValue> .
    """
    g = Graph()
    g.parse(data=gstr, format="ttl")
    return g


@pytest.fixture
def graph_wrong_regex_content() -> Graph:
    gstr = f"""{VALIDATION_PREFIXES}
    [] a sh:ValidationReport ;
    sh:result _:bn1 .
    
    [] a sh:ValidationReport ;
    sh:conforms false ;
    sh:result [ a sh:ValidationResult ;
            sh:detail _:bn1 ;
            sh:focusNode <http://data/geoname_not_number> ;
            sh:resultMessage "Value does not have shape 
                                        <http://api.knora.org/ontology/knora-api/shapes/v2#GeonameValue_ClassShape>" ;
            sh:resultPath ns1:testGeoname ;
            sh:resultSeverity sh:Violation ;
            sh:sourceConstraintComponent sh:NodeConstraintComponent ;
            sh:sourceShape ns1:testGeoname_PropShape ;
            sh:value <http://data/value-iri> ] .
            
    _:bn1 a sh:ValidationResult ;
    sh:focusNode <http://data/value-iri> ;
    sh:resultMessage "The value must be a valid geoname code" ;
    sh:resultPath ns3:geonameValueAsGeonameCode ;
    sh:resultSeverity sh:Violation ;
    sh:sourceConstraintComponent sh:PatternConstraintComponent ;
    sh:sourceShape ns2:geonameValueAsGeonameCode_Shape ;
    sh:value "llllllllllllllllll" .
    """
    g = Graph()
    g.parse(data=gstr, format="ttl")
    return g


@pytest.fixture
def violation_min_card() -> CardinalityValidationResult:
    return CardinalityValidationResult(
        source_constraint_component=SH.MinCountConstraintComponent,
        res_iri=DATA.id_min_card,
        res_class=ONTO.ClassMixedCard,
        property=ONTO.testGeoname,
        results_message="1-n",
    )


@pytest.fixture
def violation_max_card() -> CardinalityValidationResult:
    return CardinalityValidationResult(
        source_constraint_component=SH.MaxCountConstraintComponent,
        res_iri=DATA.id_max_card,
        res_class=ONTO.ClassMixedCard,
        property=ONTO.testDecimalSimpleText,
        results_message="0-1",
    )


@pytest.fixture
def violation_closed() -> CardinalityValidationResult:
    return CardinalityValidationResult(
        source_constraint_component=SH.ClosedConstraintComponent,
        res_iri=DATA.id_closed_constraint,
        res_class=ONTO.CardOneResource,
        property=ONTO.testIntegerSimpleText,
        results_message="Predicate ns3:testIntegerSimpleText is not allowed (closed shape)",
    )


@pytest.fixture
def violation_value_type() -> ContentValidationResult:
    return ContentValidationResult(
        source_constraint_component=SH.NodeConstraintComponent,
        res_iri=DATA.id_2,
        res_class=ONTO.ClassWithEverything,
        property=ONTO.testColor,
        results_message="ColorValue",
        value_type=KNORA_API.TextValue,
        detail_bn_component=SH.ClassConstraintComponent,
        value=None,
    )


@pytest.fixture
def violation_unknown_content() -> ContentValidationResult:
    return ContentValidationResult(
        source_constraint_component=SH.UniqueLangConstraintComponent,
        res_iri=DATA.id,
        res_class=ONTO.ClassMixedCard,
        property=ONTO.testIntegerSimpleText,
        results_message="This is a constraint that is not checked in the data and should never appear.",
        detail_bn_component=SH.AndConstraintComponent,
        value=None,
    )


class TestQueryCardinality:
    def test_query_for_one_cardinality_validation_result(
        self, min_count_violation: Graph, data_min_count_violation: Graph
    ) -> None:
        bn = next(min_count_violation.subjects(RDF.type, SH.ValidationResult))
        result = _query_for_one_cardinality_validation_result(bn, min_count_violation, data_min_count_violation)
        assert result.source_constraint_component == SH.MinCountConstraintComponent
        assert result.res_iri == DATA.id_min_card
        assert result.res_class == ONTO.ClassMixedCard
        assert result.property == ONTO.testGeoname
        assert result.results_message == "1-n"


class TestReformatCardinalityViolation:
    def test_min(self, violation_min_card: CardinalityValidationResult) -> None:
        result = _reformat_one_cardinality_validation_result(violation_min_card)
        assert isinstance(result, MinCardinalityViolation)
        assert result.res_id == "id_min_card"
        assert result.res_type == "onto:ClassMixedCard"
        assert result.prop_name == "onto:testGeoname"
        assert result.expected_cardinality == "1-n"

    def test_max(self, violation_max_card: CardinalityValidationResult) -> None:
        result = _reformat_one_cardinality_validation_result(violation_max_card)
        assert isinstance(result, MaxCardinalityViolation)
        assert result.res_id == "id_max_card"
        assert result.res_type == "onto:ClassMixedCard"
        assert result.prop_name == "onto:testDecimalSimpleText"
        assert result.expected_cardinality == "0-1"

    def test_closed(self, violation_closed: CardinalityValidationResult) -> None:
        result = _reformat_one_cardinality_validation_result(violation_closed)
        assert isinstance(result, NonExistentCardinalityViolation)
        assert result.res_id == "id_closed_constraint"
        assert result.res_type == "onto:CardOneResource"
        assert result.prop_name == "onto:testIntegerSimpleText"


class TestQueryContent:
    def test_query_graph_value_type_mismatch(
        self, graph_value_type_mismatch: Graph, data_value_type_mismatch: Graph
    ) -> None:
        bn = next(graph_value_type_mismatch.subjects(SH.sourceConstraintComponent, SH.NodeConstraintComponent))
        result = _query_for_one_content_validation_result(bn, graph_value_type_mismatch, data_value_type_mismatch)
        assert result.source_constraint_component == SH.NodeConstraintComponent
        assert result.res_iri == DATA.id_2
        assert result.res_class == ONTO.ClassWithEverything
        assert result.property == ONTO.testColor
        assert result.results_message == "ColorValue"
        assert result.value_type == KNORA_API.TextValue


class TestReformatContentViolation:
    def test_value_type(self, violation_value_type: ContentValidationResult) -> None:
        result = _reformat_one_content_validation_result(violation_value_type)
        assert isinstance(result, ValueTypeViolation)
        assert result.res_id == "id_2"
        assert result.res_type == "onto:ClassWithEverything"
        assert result.prop_name == "onto:testColor"
        assert result.actual_type == "TextValue"
        assert result.expected_type == "ColorValue"

    def test_unknown(self, violation_unknown_content: ContentValidationResult) -> None:
        result = _reformat_one_content_validation_result(violation_unknown_content)
        assert isinstance(result, UnexpectedComponent)
        assert result.component_type == str(SH.UniqueLangConstraintComponent)


if __name__ == "__main__":
    pytest.main([__file__])
