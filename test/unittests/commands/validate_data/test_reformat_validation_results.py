import pytest

from dsp_tools.commands.validate_data.models.input_problems import ProblemType
from dsp_tools.commands.validate_data.models.input_problems import Severity
from dsp_tools.commands.validate_data.models.validation import ValidationResult
from dsp_tools.commands.validate_data.process_validation_report.reformat_validation_results import (
    _reformat_one_validation_result,
)


class TestReformatResult:
    def test_min(self, extracted_min_card: ValidationResult) -> None:
        result = _reformat_one_validation_result(extracted_min_card)
        assert result.problem_type == ProblemType.MIN_CARD
        assert result.res_id == "id_card_one"
        assert result.res_type == "onto:ClassInheritedCardinalityOverwriting"
        assert result.prop_name == "onto:testBoolean"
        assert result.severity == Severity.VIOLATION
        assert result.expected == "1"

    def test_max(self, extracted_max_card: ValidationResult) -> None:
        result = _reformat_one_validation_result(extracted_max_card)
        assert result.problem_type == ProblemType.MAX_CARD
        assert result.res_id == "id_max_card"
        assert result.res_type == "onto:ClassMixedCard"
        assert result.prop_name == "onto:testDecimalSimpleText"
        assert result.severity == Severity.VIOLATION
        assert result.expected == "0-1"

    def test_violation_empty_label(self, extracted_empty_label: ValidationResult) -> None:
        result = _reformat_one_validation_result(extracted_empty_label)
        assert result.problem_type == ProblemType.INPUT_REGEX
        assert result.res_id == "empty_label"
        assert result.res_type == "onto:ClassWithEverything"
        assert result.prop_name == "rdfs:label"
        assert result.severity == Severity.VIOLATION
        assert result.expected == "The label must be a non-empty string"
        assert result.input_value == " "

    def test_closed(self, extracted_closed_constraint: ValidationResult) -> None:
        result = _reformat_one_validation_result(extracted_closed_constraint)
        assert result.problem_type == ProblemType.NON_EXISTING_CARD
        assert result.res_id == "id_closed_constraint"
        assert result.res_type == "onto:CardOneResource"
        assert result.prop_name == "onto:testIntegerSimpleText"
        assert result.severity == Severity.VIOLATION

    def test_value_type_simpletext(self, extracted_value_type_simpletext: ValidationResult) -> None:
        result = _reformat_one_validation_result(extracted_value_type_simpletext)
        assert result.problem_type == ProblemType.VALUE_TYPE_MISMATCH
        assert result.res_id == "id_simpletext"
        assert result.res_type == "onto:ClassWithEverything"
        assert result.prop_name == "onto:testTextarea"
        assert result.severity == Severity.VIOLATION
        assert result.input_type == "TextValue"
        assert result.expected == "TextValue without formatting"

    def test_value_type(self, extracted_value_type: ValidationResult) -> None:
        result = _reformat_one_validation_result(extracted_value_type)
        assert result.problem_type == ProblemType.VALUE_TYPE_MISMATCH
        assert result.res_id == "id_uri"
        assert result.res_type == "onto:ClassWithEverything"
        assert result.prop_name == "onto:testUriValue"
        assert result.severity == Severity.VIOLATION
        assert result.input_type == "TextValue"
        assert result.expected == "This property requires a UriValue"

    def test_violation_regex(self, extracted_regex: ValidationResult) -> None:
        result = _reformat_one_validation_result(extracted_regex)
        assert result.problem_type == ProblemType.INPUT_REGEX
        assert result.res_id == "geoname_not_number"
        assert result.res_type == "onto:ClassWithEverything"
        assert result.prop_name == "onto:testGeoname"
        assert result.severity == Severity.VIOLATION
        assert result.expected == "The value must be a valid geoname code"
        assert result.input_value == "this-is-not-a-valid-code"

    def test_link_target_non_existent(self, extracted_link_target_non_existent: ValidationResult) -> None:
        result = _reformat_one_validation_result(extracted_link_target_non_existent)
        assert result.problem_type == ProblemType.INEXISTENT_LINKED_RESOURCE
        assert result.res_id == "link_target_non_existent"
        assert result.res_type == "onto:ClassWithEverything"
        assert result.prop_name == "onto:testHasLinkTo"
        assert result.severity == Severity.VIOLATION
        assert result.input_value == "other"

    def test_link_target_wrong_class(self, extracted_link_target_wrong_class: ValidationResult) -> None:
        result = _reformat_one_validation_result(extracted_link_target_wrong_class)
        assert result.problem_type == ProblemType.LINK_TARGET_TYPE_MISMATCH
        assert result.res_id == "link_target_wrong_class"
        assert result.res_type == "onto:ClassWithEverything"
        assert result.prop_name == "onto:testHasLinkToCardOneResource"
        assert result.severity == Severity.VIOLATION
        assert result.input_value == "id_9_target"
        assert result.input_type == "onto:ClassWithEverything"
        assert result.expected == "onto:CardOneResource"

    def test_unique_value_literal(self, extracted_unique_value_literal: ValidationResult) -> None:
        result = _reformat_one_validation_result(extracted_unique_value_literal)
        assert result.problem_type == ProblemType.DUPLICATE_VALUE
        assert result.res_id == "identical_values_valueHas"
        assert result.res_type == "onto:ClassWithEverything"
        assert result.prop_name == "onto:testGeoname"
        assert result.severity == Severity.VIOLATION
        assert result.input_value == "00111111"

    def test_unique_value_iri(self, extracted_unique_value_iri: ValidationResult) -> None:
        result = _reformat_one_validation_result(extracted_unique_value_iri)
        assert result.problem_type == ProblemType.DUPLICATE_VALUE
        assert result.res_id == "identical_values_LinkValue"
        assert result.res_type == "onto:ClassWithEverything"
        assert result.prop_name == "onto:testHasLinkTo"
        assert result.severity == Severity.VIOLATION
        assert result.input_value == "link_valueTarget_id"

    def test_unknown_list_node(self, extracted_unknown_list_node: ValidationResult) -> None:
        result = _reformat_one_validation_result(extracted_unknown_list_node)
        assert result.problem_type == ProblemType.GENERIC
        assert result.res_id == "list_node_non_existent"
        assert result.res_type == "onto:ClassWithEverything"
        assert result.prop_name == "onto:testListProp"
        assert result.severity == Severity.VIOLATION
        assert result.message == "A valid node from the list 'firstList' must be used with this property."
        assert result.input_value == "firstList / other"

    def test_unknown_list_name(self, extracted_unknown_list_name: ValidationResult) -> None:
        result = _reformat_one_validation_result(extracted_unknown_list_name)
        assert result.problem_type == ProblemType.GENERIC
        assert result.res_id == "list_name_non_existent"
        assert result.res_type == "onto:ClassWithEverything"
        assert result.prop_name == "onto:testListProp"
        assert result.severity == Severity.VIOLATION
        assert result.message == "A valid node from the list 'firstList' must be used with this property."
        assert result.input_value == "other / n1"

    def test_min_inclusive(self, extracted_min_inclusive: ValidationResult) -> None:
        result = _reformat_one_validation_result(extracted_min_inclusive)
        assert result.problem_type == ProblemType.GENERIC
        assert result.res_id == "video_segment_negative_bounds"
        assert result.res_type == "VideoSegment"
        assert result.prop_name == "hasSegmentBounds"
        assert result.severity == Severity.VIOLATION
        assert result.message == "The interval start must be a non-negative integer or decimal."
        assert result.input_value == "-2.0"

    def test_missing_file_value(self, extracted_missing_file_value: ValidationResult) -> None:
        result = _reformat_one_validation_result(extracted_missing_file_value)
        assert result.problem_type == ProblemType.FILE_VALUE_MISSING
        assert result.res_id == "id_video_missing"
        assert result.res_type == "onto:TestMovingImageRepresentation"
        assert result.prop_name == "bitstream"
        assert result.severity == Severity.VIOLATION
        assert result.expected == "This resource requires a file with one of the following extensions: 'mp4'"

    def test_image_missing_legal_info(self, extracted_image_missing_legal_info: ValidationResult) -> None:
        result = _reformat_one_validation_result(extracted_image_missing_legal_info)
        assert result.problem_type == ProblemType.GENERIC
        assert result.res_id == "image_no_legal_info"
        assert result.res_type == "onto:TestStillImageRepresentation"
        assert result.prop_name == "bitstream / iiif-uri"
        assert result.severity == Severity.WARNING
        assert result.expected == "Files and IIIF-URIs require a reference to a license."

    def test_single_line_constraint_component(
        self, extracted_single_line_constraint_component: ValidationResult
    ) -> None:
        result = _reformat_one_validation_result(extracted_single_line_constraint_component)
        assert result.problem_type == ProblemType.GENERIC
        assert result.res_id == "copyright_holder_with_newline"
        assert result.res_type == "onto:TestArchiveRepresentation"
        assert result.prop_name == "bitstream / iiif-uri"
        assert result.severity == Severity.VIOLATION
        assert result.message == "The copyright holder must be a string without newlines."
        assert result.input_value == "with newline"

    def test_file_value_for_resource_without_representation(
        self, extracted_file_value_for_resource_without_representation: ValidationResult
    ) -> None:
        result = _reformat_one_validation_result(extracted_file_value_for_resource_without_representation)
        assert result.problem_type == ProblemType.FILE_VALUE_PROHIBITED
        assert result.res_id == "id_resource_without_representation"
        assert result.res_type == "onto:ClassWithEverything"
        assert result.prop_name == "bitstream / iiif-uri"
        assert result.severity == Severity.VIOLATION

    def test_seqnum_is_part_of(self, extracted_coexist_with: ValidationResult) -> None:
        result = _reformat_one_validation_result(extracted_coexist_with)
        assert result.problem_type == ProblemType.GENERIC
        assert result.res_id == "missing_seqnum"
        assert result.res_type == "in-built:TestStillImageRepresentationWithSeqnum"
        assert result.prop_name == "seqnum or isPartOf"
        assert result.severity == Severity.VIOLATION
        assert result.message == "Coexist message from knora-api turtle"

    def test_date_single_month_does_not_exist(
        self, extracted_date_single_month_does_not_exist: ValidationResult
    ) -> None:
        result = _reformat_one_validation_result(extracted_date_single_month_does_not_exist)
        assert result.problem_type == ProblemType.GENERIC
        assert result.res_id == "date_month_does_not_exist"
        assert result.res_type == "onto:ClassWithEverything"
        assert result.prop_name == "onto:testSubDate1"
        assert result.severity == Severity.VIOLATION
        assert result.message == "date message"
        assert result.input_value == "1800-22"


if __name__ == "__main__":
    pytest.main([__file__])
