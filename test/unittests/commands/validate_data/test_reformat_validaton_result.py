import pytest
from rdflib import RDFS
from rdflib import SH
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.commands.validate_data.models.input_problems import ContentRegexProblem
from dsp_tools.commands.validate_data.models.input_problems import DuplicateValueProblem
from dsp_tools.commands.validate_data.models.input_problems import FileValueProblem
from dsp_tools.commands.validate_data.models.input_problems import GenericProblem
from dsp_tools.commands.validate_data.models.input_problems import LinkedResourceDoesNotExistProblem
from dsp_tools.commands.validate_data.models.input_problems import LinkTargetTypeMismatchProblem
from dsp_tools.commands.validate_data.models.input_problems import MaxCardinalityProblem
from dsp_tools.commands.validate_data.models.input_problems import MinCardinalityProblem
from dsp_tools.commands.validate_data.models.input_problems import NonExistentCardinalityProblem
from dsp_tools.commands.validate_data.models.input_problems import ValueTypeProblem
from dsp_tools.commands.validate_data.models.validation import DetailBaseInfo
from dsp_tools.commands.validate_data.models.validation import ResultGenericViolation
from dsp_tools.commands.validate_data.models.validation import ResultLinkTargetViolation
from dsp_tools.commands.validate_data.models.validation import ResultMaxCardinalityViolation
from dsp_tools.commands.validate_data.models.validation import ResultMinCardinalityViolation
from dsp_tools.commands.validate_data.models.validation import ResultNonExistentCardinalityViolation
from dsp_tools.commands.validate_data.models.validation import ResultPatternViolation
from dsp_tools.commands.validate_data.models.validation import ResultUniqueValueViolation
from dsp_tools.commands.validate_data.models.validation import ResultValueTypeViolation
from dsp_tools.commands.validate_data.models.validation import UnexpectedComponent
from dsp_tools.commands.validate_data.models.validation import ValidationResultBaseInfo
from dsp_tools.commands.validate_data.reformat_validaton_result import _extract_base_info_of_resource_results
from dsp_tools.commands.validate_data.reformat_validaton_result import _query_one_with_detail
from dsp_tools.commands.validate_data.reformat_validaton_result import _query_one_without_detail
from dsp_tools.commands.validate_data.reformat_validaton_result import _reformat_one_validation_result
from dsp_tools.commands.validate_data.reformat_validaton_result import _separate_result_types
from test.unittests.commands.validate_data.constants import DATA
from test.unittests.commands.validate_data.constants import KNORA_API
from test.unittests.commands.validate_data.constants import ONTO


class TestExtractBaseInfo:
    def test_not_resource(self, report_not_resource: tuple[Graph, Graph]) -> None:
        validation_g, onto_data_g = report_not_resource
        results = _extract_base_info_of_resource_results(validation_g, onto_data_g)
        assert not results

    def test_no_detail(self, report_min_card: tuple[Graph, Graph, ValidationResultBaseInfo]) -> None:
        validation_g, onto_data_g, _ = report_min_card
        results = _extract_base_info_of_resource_results(validation_g, onto_data_g)
        assert len(results) == 1
        found_result = results[0]
        assert found_result.resource_iri == DATA.id_card_one
        assert found_result.res_class_type == ONTO.ClassInheritedCardinalityOverwriting
        assert found_result.result_path == ONTO.testBoolean
        assert found_result.source_constraint_component == SH.MinCountConstraintComponent
        assert not found_result.detail

    def test_with_detail(self, report_value_type_simpletext: tuple[Graph, Graph, ValidationResultBaseInfo]) -> None:
        validation_g, onto_data_g, _ = report_value_type_simpletext
        results = _extract_base_info_of_resource_results(validation_g, onto_data_g)
        assert len(results) == 1
        found_result = results[0]
        assert found_result.resource_iri == DATA.id_simpletext
        assert found_result.res_class_type == ONTO.ClassWithEverything
        assert found_result.result_path == ONTO.testTextarea
        assert found_result.source_constraint_component == SH.NodeConstraintComponent
        detail = found_result.detail
        assert isinstance(detail, DetailBaseInfo)
        assert detail.source_constraint_component == SH.MinCountConstraintComponent


class TestSeparateResultTypes:
    def test_result_id_card_one(self, report_min_card: tuple[Graph, Graph, ValidationResultBaseInfo]) -> None:
        res_g, onto_data_g, _ = report_min_card
        no_detail, with_detail = _separate_result_types(res_g, onto_data_g)
        assert len(no_detail) == 1
        assert len(with_detail) == 0
        assert no_detail[0].resource_iri == DATA.id_card_one

    def test_result_id_simpletext(
        self, report_value_type_simpletext: tuple[Graph, Graph, ValidationResultBaseInfo]
    ) -> None:
        res_g, onto_data_g, _ = report_value_type_simpletext
        no_detail, with_detail = _separate_result_types(res_g, onto_data_g)
        assert len(no_detail) == 0
        assert len(with_detail) == 1
        assert with_detail[0].resource_iri == DATA.id_simpletext

    def test_result_id_uri(self, report_value_type: tuple[Graph, Graph, ValidationResultBaseInfo]) -> None:
        res_g, onto_data_g, _ = report_value_type
        no_detail, with_detail = _separate_result_types(res_g, onto_data_g)
        assert len(no_detail) == 0
        assert len(with_detail) == 1
        assert with_detail[0].resource_iri == DATA.id_uri

    def test_result_geoname_not_number(self, report_regex: tuple[Graph, Graph, ValidationResultBaseInfo]) -> None:
        res_g, onto_data_g, _ = report_regex
        no_detail, with_detail = _separate_result_types(res_g, onto_data_g)
        assert len(no_detail) == 0
        assert len(with_detail) == 1
        assert with_detail[0].resource_iri == DATA.geoname_not_number

    def test_result_id_closed_constraint(
        self, report_closed_constraint: tuple[Graph, Graph, ValidationResultBaseInfo]
    ) -> None:
        res_g, onto_data_g, _ = report_closed_constraint
        no_detail, with_detail = _separate_result_types(res_g, onto_data_g)
        assert len(no_detail) == 1
        assert len(with_detail) == 0
        assert no_detail[0].resource_iri == DATA.id_closed_constraint

    def test_result_id_max_card(self, report_max_card: tuple[Graph, Graph, ValidationResultBaseInfo]) -> None:
        res_g, onto_data_g, _ = report_max_card
        no_detail, with_detail = _separate_result_types(res_g, onto_data_g)
        assert len(no_detail) == 1
        assert len(with_detail) == 0
        assert no_detail[0].resource_iri == DATA.id_max_card

    def test_report_unique_value_literal(
        self, report_unique_value_literal: tuple[Graph, Graph, ValidationResultBaseInfo]
    ) -> None:
        res_g, onto_data_g, _ = report_unique_value_literal
        no_detail, with_detail = _separate_result_types(res_g, onto_data_g)
        assert len(no_detail) == 1
        assert len(with_detail) == 0
        assert no_detail[0].resource_iri == DATA.identical_values_valueHas

    def test_report_unique_value_iri(
        self, report_unique_value_iri: tuple[Graph, Graph, ValidationResultBaseInfo]
    ) -> None:
        res_g, onto_data_g, _ = report_unique_value_iri
        no_detail, with_detail = _separate_result_types(res_g, onto_data_g)
        assert len(no_detail) == 1
        assert len(with_detail) == 0
        assert no_detail[0].resource_iri == DATA.identical_values_LinkValue


class TestQueryWithoutDetail:
    def test_result_id_card_one(self, report_min_card: tuple[Graph, Graph, ValidationResultBaseInfo]) -> None:
        res, _, info = report_min_card
        result = _query_one_without_detail(info, res)
        assert isinstance(result, ResultMinCardinalityViolation)
        assert result.res_iri == info.resource_iri
        assert result.res_class == info.res_class_type
        assert result.property == ONTO.testBoolean
        assert result.results_message == "1"

    def test_result_id_closed_constraint(
        self, report_closed_constraint: tuple[Graph, Graph, ValidationResultBaseInfo]
    ) -> None:
        res, _, info = report_closed_constraint
        result = _query_one_without_detail(info, res)
        assert isinstance(result, ResultNonExistentCardinalityViolation)
        assert result.res_iri == info.resource_iri
        assert result.res_class == info.res_class_type
        assert result.property == ONTO.testIntegerSimpleText

    def test_result_id_max_card(self, report_max_card: tuple[Graph, Graph, ValidationResultBaseInfo]) -> None:
        res, _, info = report_max_card
        result = _query_one_without_detail(info, res)
        assert isinstance(result, ResultMaxCardinalityViolation)
        assert result.res_iri == info.resource_iri
        assert result.res_class == info.res_class_type
        assert result.property == ONTO.testHasLinkToCardOneResource
        assert result.results_message == "1"

    def test_result_empty_label(self, report_empty_label: tuple[Graph, Graph, ValidationResultBaseInfo]) -> None:
        res, _, info = report_empty_label
        result = _query_one_without_detail(info, res)
        assert isinstance(result, ResultPatternViolation)
        assert result.res_iri == info.resource_iri
        assert result.res_class == info.res_class_type
        assert result.property == RDFS.label
        assert result.results_message == "The label must be a non-empty string"
        assert result.actual_value == " "

    def test_unique_value_literal(
        self, report_unique_value_literal: tuple[Graph, Graph, ValidationResultBaseInfo]
    ) -> None:
        res, _, info = report_unique_value_literal
        result = _query_one_without_detail(info, res)
        assert isinstance(result, ResultUniqueValueViolation)
        assert result.res_iri == info.resource_iri
        assert result.res_class == info.res_class_type
        assert result.property == ONTO.testGeoname
        assert result.actual_value == Literal("00111111")

    def test_unique_value_iri(self, report_unique_value_iri: tuple[Graph, Graph, ValidationResultBaseInfo]) -> None:
        res, _, info = report_unique_value_iri
        result = _query_one_without_detail(info, res)
        assert isinstance(result, ResultUniqueValueViolation)
        assert result.res_iri == info.resource_iri
        assert result.res_class == info.res_class_type
        assert result.property == ONTO.testHasLinkTo
        assert result.actual_value == DATA.link_valueTarget_id

    def test_unknown(self, result_unknown_component: tuple[Graph, Graph, ValidationResultBaseInfo]) -> None:
        res, _, info = result_unknown_component
        result = _query_one_without_detail(info, res)
        assert isinstance(result, UnexpectedComponent)
        assert result.component_type == str(SH.UniqueLangConstraintComponent)


class TestQueryWithDetail:
    def test_result_id_simpletext(
        self, report_value_type_simpletext: tuple[Graph, Graph, ValidationResultBaseInfo]
    ) -> None:
        res, data, info = report_value_type_simpletext
        result = _query_one_with_detail(info, res, data)
        assert isinstance(result, ResultValueTypeViolation)
        assert result.res_iri == info.resource_iri
        assert result.res_class == info.res_class_type
        assert result.property == ONTO.testTextarea
        assert result.results_message == "TextValue without formatting"
        assert result.actual_value_type == KNORA_API.TextValue

    def test_result_id_uri(self, report_value_type: tuple[Graph, Graph, ValidationResultBaseInfo]) -> None:
        res, data, info = report_value_type
        result = _query_one_with_detail(info, res, data)
        assert isinstance(result, ResultValueTypeViolation)
        assert result.res_iri == info.resource_iri
        assert result.res_class == info.res_class_type
        assert result.property == ONTO.testUriValue
        assert result.results_message == "UriValue"
        assert result.actual_value_type == KNORA_API.TextValue

    def test_result_geoname_not_number(self, report_regex: tuple[Graph, Graph, ValidationResultBaseInfo]) -> None:
        res, data, info = report_regex
        result = _query_one_with_detail(info, res, data)
        assert isinstance(result, ResultPatternViolation)
        assert result.res_iri == info.resource_iri
        assert result.res_class == info.res_class_type
        assert result.property == ONTO.testGeoname
        assert result.results_message == "The value must be a valid geoname code"
        assert result.actual_value == "this-is-not-a-valid-code"

    def test_link_target_non_existent(
        self, report_link_target_non_existent: tuple[Graph, Graph, ValidationResultBaseInfo]
    ) -> None:
        res, data, info = report_link_target_non_existent
        result = _query_one_with_detail(info, res, data)
        assert isinstance(result, ResultLinkTargetViolation)
        assert result.res_iri == info.resource_iri
        assert result.res_class == info.res_class_type
        assert result.property == ONTO.testHasLinkTo
        assert result.expected_type == KNORA_API.Resource
        assert result.target_iri == URIRef("http://data/other")
        assert not result.target_resource_type

    def test_link_target_wrong_class(
        self, report_link_target_wrong_class: tuple[Graph, Graph, ValidationResultBaseInfo]
    ) -> None:
        res, data, info = report_link_target_wrong_class
        result = _query_one_with_detail(info, res, data)
        assert isinstance(result, ResultLinkTargetViolation)
        assert result.res_iri == info.resource_iri
        assert result.res_class == info.res_class_type
        assert result.property == ONTO.testHasLinkToCardOneResource
        assert result.expected_type == ONTO.CardOneResource
        assert result.target_iri == URIRef("http://data/id_9_target")
        assert result.target_resource_type == ONTO.ClassWithEverything

    def test_report_unknown_list_name(
        self, report_unknown_list_name: tuple[Graph, Graph, ValidationResultBaseInfo]
    ) -> None:
        res, data, info = report_unknown_list_name
        result = _query_one_with_detail(info, res, data)
        assert isinstance(result, ResultGenericViolation)
        assert result.res_iri == info.resource_iri
        assert result.res_class == info.res_class_type
        assert result.property == ONTO.testListProp
        assert result.results_message == "The list that should be used with this property is 'firstList'."
        assert result.actual_value == "other"

    def test_report_unknown_list_node(
        self, report_unknown_list_node: tuple[Graph, Graph, ValidationResultBaseInfo]
    ) -> None:
        res, data, info = report_unknown_list_node
        result = _query_one_with_detail(info, res, data)
        assert isinstance(result, ResultGenericViolation)
        assert result.res_iri == info.resource_iri
        assert result.res_class == info.res_class_type
        assert result.property == ONTO.testListProp
        assert result.results_message == "Unknown list node for list 'firstList'."
        assert result.actual_value == "other"


class TestQueryFileValueViolations:
    def test_missing_file_value(self, report_missing_file_value: tuple[Graph, Graph, ValidationResultBaseInfo]) -> None:
        res, _, info = report_missing_file_value
        result = _query_one_without_detail(info, res)
        assert isinstance(result, ResultMinCardinalityViolation)
        assert result.res_iri == info.resource_iri
        assert result.res_class == info.res_class_type
        assert result.property == KNORA_API.hasMovingImageFileValue
        assert result.results_message == "A MovingImageRepresentation requires a file with the extension 'mp4'."


class TestReformatResult:
    def test_min(self, extracted_min_card: ResultMinCardinalityViolation) -> None:
        result = _reformat_one_validation_result(extracted_min_card)
        assert isinstance(result, MinCardinalityProblem)
        assert result.res_id == "id_card_one"
        assert result.res_type == "onto:ClassInheritedCardinalityOverwriting"
        assert result.prop_name == "onto:testBoolean"
        assert result.expected_cardinality == "1"

    def test_max(self, extracted_max_card: ResultMaxCardinalityViolation) -> None:
        result = _reformat_one_validation_result(extracted_max_card)
        assert isinstance(result, MaxCardinalityProblem)
        assert result.res_id == "id_max_card"
        assert result.res_type == "onto:ClassMixedCard"
        assert result.prop_name == "onto:testDecimalSimpleText"
        assert result.expected_cardinality == "0-1"

    def test_violation_empty_label(self, extracted_empty_label: ResultPatternViolation) -> None:
        result = _reformat_one_validation_result(extracted_empty_label)
        assert isinstance(result, ContentRegexProblem)
        assert result.res_id == "empty_label"
        assert result.res_type == "onto:ClassWithEverything"
        assert result.prop_name == "rdfs:label"
        assert result.expected_format == "The label must be a non-empty string"
        assert not result.actual_content

    def test_closed(self, extracted_closed_constraint: ResultNonExistentCardinalityViolation) -> None:
        result = _reformat_one_validation_result(extracted_closed_constraint)
        assert isinstance(result, NonExistentCardinalityProblem)
        assert result.res_id == "id_closed_constraint"
        assert result.res_type == "onto:CardOneResource"
        assert result.prop_name == "onto:testIntegerSimpleText"

    def test_value_type_simpletext(self, extracted_value_type_simpletext: ResultValueTypeViolation) -> None:
        result = _reformat_one_validation_result(extracted_value_type_simpletext)
        assert isinstance(result, ValueTypeProblem)
        assert result.res_id == "id_simpletext"
        assert result.res_type == "onto:ClassWithEverything"
        assert result.prop_name == "onto:testTextarea"
        assert result.actual_type == "TextValue"
        assert result.expected_type == "TextValue without formatting"

    def test_value_type(self, extracted_value_type: ResultValueTypeViolation) -> None:
        result = _reformat_one_validation_result(extracted_value_type)
        assert isinstance(result, ValueTypeProblem)
        assert result.res_id == "id_uri"
        assert result.res_type == "onto:ClassWithEverything"
        assert result.prop_name == "onto:testUriValue"
        assert result.actual_type == "TextValue"
        assert result.expected_type == "UriValue"

    def test_violation_regex(self, extracted_regex: ResultPatternViolation) -> None:
        result = _reformat_one_validation_result(extracted_regex)
        assert isinstance(result, ContentRegexProblem)
        assert result.res_id == "geoname_not_number"
        assert result.res_type == "onto:ClassWithEverything"
        assert result.prop_name == "onto:testGeoname"
        assert result.expected_format == "The value must be a valid geoname code"
        assert result.actual_content == "this-is-not-a-valid-code"

    def test_link_target_non_existent(self, extracted_link_target_non_existent: ResultLinkTargetViolation) -> None:
        result = _reformat_one_validation_result(extracted_link_target_non_existent)
        assert isinstance(result, LinkedResourceDoesNotExistProblem)
        assert result.res_id == "link_target_non_existent"
        assert result.res_type == "onto:ClassWithEverything"
        assert result.prop_name == "onto:testHasLinkTo"
        assert result.link_target_id == "other"

    def test_link_target_wrong_class(self, extracted_link_target_wrong_class: ResultLinkTargetViolation) -> None:
        result = _reformat_one_validation_result(extracted_link_target_wrong_class)
        assert isinstance(result, LinkTargetTypeMismatchProblem)
        assert result.res_id == "link_target_wrong_class"
        assert result.res_type == "onto:ClassWithEverything"
        assert result.prop_name == "onto:testHasLinkToCardOneResource"
        assert result.link_target_id == "id_9_target"
        assert result.expected_type == "onto:CardOneResource"
        assert result.actual_type == "onto:ClassWithEverything"

    def test_unique_value_literal(self, extracted_unique_value_literal: ResultUniqueValueViolation) -> None:
        result = _reformat_one_validation_result(extracted_unique_value_literal)
        assert isinstance(result, DuplicateValueProblem)
        assert result.res_id == "identical_values_valueHas"
        assert result.res_type == "onto:ClassWithEverything"
        assert result.prop_name == "onto:testGeoname"
        assert result.actual_content == "00111111"

    def test_unique_value_iri(self, extracted_unique_value_iri: ResultUniqueValueViolation) -> None:
        result = _reformat_one_validation_result(extracted_unique_value_iri)
        assert isinstance(result, DuplicateValueProblem)
        assert result.res_id == "identical_values_LinkValue"
        assert result.res_type == "onto:ClassWithEverything"
        assert result.prop_name == "onto:testHasLinkTo"
        assert result.actual_content == "link_valueTarget_id"

    def test_unknown_list_node(self, extracted_unknown_list_node: ResultGenericViolation) -> None:
        result = _reformat_one_validation_result(extracted_unknown_list_node)
        assert isinstance(result, GenericProblem)
        assert result.res_id == "list_node_non_existent"
        assert result.res_type == "onto:ClassWithEverything"
        assert result.prop_name == "onto:testListProp"
        assert result.results_message == "Unknown list node for list 'firstList'."
        assert result.actual_content == "other"

    def test_unknown_list_name(self, extracted_unknown_list_name: ResultGenericViolation) -> None:
        result = _reformat_one_validation_result(extracted_unknown_list_name)
        assert isinstance(result, GenericProblem)
        assert result.res_id == "list_name_non_existent"
        assert result.res_type == "onto:ClassWithEverything"
        assert result.prop_name == "onto:testListProp"
        assert result.results_message == "The list that should be used with this property is 'firstList'."
        assert result.actual_content == "other"

    def test_missing_file_value(self, extracted_missing_file_value: ResultMinCardinalityViolation) -> None:
        result = _reformat_one_validation_result(extracted_missing_file_value)
        assert isinstance(result, FileValueProblem)
        assert result.res_id == "id_video_missing"
        assert result.res_type == "onto:TestMovingImageRepresentation"
        assert result.prop_name == "bitstream / iiif-uri"
        assert result.expected == "A MovingImageRepresentation requires a file with the extension 'mp4'."


if __name__ == "__main__":
    pytest.main([__file__])
