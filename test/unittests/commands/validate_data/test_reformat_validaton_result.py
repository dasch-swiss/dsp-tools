import pytest
from rdflib import RDF
from rdflib import SH
from rdflib import Graph
from rdflib import Namespace

from dsp_tools.commands.validate_data.models.input_problems import ContentRegexViolation
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

ONTO = Namespace("http://0.0.0.0:3333/ontology/9999/onto/v2#")
DATA = Namespace("http://data/")
KNORA_API = Namespace("http://api.knora.org/ontology/knora-api/v2#")


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


class TestQueryGraphContent:
    def test_value_type_mismatch(self, graph_value_type_mismatch: Graph, data_value_type_mismatch: Graph) -> None:
        bn = next(graph_value_type_mismatch.subjects(SH.sourceConstraintComponent, SH.NodeConstraintComponent))
        result = _query_for_one_content_validation_result(bn, graph_value_type_mismatch, data_value_type_mismatch)
        assert result.source_constraint_component == SH.NodeConstraintComponent
        assert result.res_iri == DATA.value_type_mismatch
        assert result.res_class == ONTO.ClassWithEverything
        assert result.property == ONTO.testColor
        assert result.results_message == "ColorValue"
        assert result.value_type == KNORA_API.TextValue

    def test_wrong_regex_content(self, graph_wrong_regex_content: Graph, data_wrong_regex_content: Graph) -> None:
        bn = next(graph_wrong_regex_content.subjects(SH.sourceConstraintComponent, SH.NodeConstraintComponent))
        result = _query_for_one_content_validation_result(bn, graph_wrong_regex_content, data_wrong_regex_content)
        assert result.source_constraint_component == SH.NodeConstraintComponent
        assert result.res_iri == DATA.geoname_not_number
        assert result.res_class == ONTO.ClassWithEverything
        assert result.property == ONTO.testGeoname
        assert result.results_message == "The value must be a valid geoname code"
        assert result.detail_bn_component == SH.PatternConstraintComponent
        assert result.value_type == KNORA_API.GeonameValue
        assert result.value == "this-is-not-a-valid-code"


class TestReformatContentViolation:
    def test_value_type(self, violation_value_type: ContentValidationResult) -> None:
        result = _reformat_one_content_validation_result(violation_value_type)
        assert isinstance(result, ValueTypeViolation)
        assert result.res_id == "id_2"
        assert result.res_type == "onto:ClassWithEverything"
        assert result.prop_name == "onto:testColor"
        assert result.actual_type == "TextValue"
        assert result.expected_type == "ColorValue"

    def test_violation_regex(self, violation_regex: ContentValidationResult) -> None:
        result = _reformat_one_content_validation_result(violation_regex)
        assert isinstance(result, ContentRegexViolation)
        assert result.res_id == "geoname_not_number"
        assert result.res_type == "onto:ClassWithEverything"
        assert result.prop_name == "onto:testGeoname"
        assert result.expected_format == "The value must be a valid geoname code"
        assert result.actual_content == "this-is-not-a-valid-code"

    def test_unknown(self, violation_unknown_content: ContentValidationResult) -> None:
        result = _reformat_one_content_validation_result(violation_unknown_content)
        assert isinstance(result, UnexpectedComponent)
        assert result.component_type == str(SH.UniqueLangConstraintComponent)


if __name__ == "__main__":
    pytest.main([__file__])
