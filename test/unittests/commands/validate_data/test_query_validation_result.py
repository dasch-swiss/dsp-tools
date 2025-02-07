import pytest
from rdflib import RDFS
from rdflib import SH
from rdflib import XSD
from rdflib import Graph
from rdflib import Literal

from dsp_tools.commands.validate_data.models.input_problems import ProblemType
from dsp_tools.commands.validate_data.models.validation import DetailBaseInfo
from dsp_tools.commands.validate_data.models.validation import UnexpectedComponent
from dsp_tools.commands.validate_data.models.validation import ValidationReportGraphs
from dsp_tools.commands.validate_data.models.validation import ValidationResult
from dsp_tools.commands.validate_data.models.validation import ValidationResultBaseInfo
from dsp_tools.commands.validate_data.models.validation import ViolationType
from dsp_tools.commands.validate_data.query_validation_result import _extract_base_info_of_resource_results
from dsp_tools.commands.validate_data.query_validation_result import _query_all_results
from dsp_tools.commands.validate_data.query_validation_result import _query_one_with_detail
from dsp_tools.commands.validate_data.query_validation_result import _query_one_without_detail
from dsp_tools.commands.validate_data.query_validation_result import _reformat_one_validation_result
from dsp_tools.commands.validate_data.query_validation_result import _separate_result_types
from dsp_tools.commands.validate_data.query_validation_result import reformat_validation_graph
from test.unittests.commands.validate_data.constants import DATA
from test.unittests.commands.validate_data.constants import IN_BUILT_ONTO
from test.unittests.commands.validate_data.constants import KNORA_API
from test.unittests.commands.validate_data.constants import ONTO


def test_reformat_validation_graph(report_target_resource_wrong_type: tuple[Graph, Graph]) -> None:
    validation_g, onto_data_g = report_target_resource_wrong_type
    report = ValidationReportGraphs(
        conforms=False,
        validation_graph=validation_g,
        shacl_graph=Graph(),
        onto_graph=onto_data_g,
        data_graph=onto_data_g,
    )
    result_all_problems = reformat_validation_graph(report)
    assert not result_all_problems.unexpected_results
    assert len(result_all_problems.problems) == 1
    result = result_all_problems.problems.pop(0)
    assert result.problem_type == ProblemType.LINK_TARGET_TYPE_MISMATCH
    assert result.res_id == "region_isRegionOf_resource_not_a_representation"
    assert result.res_type == "Region"
    assert result.prop_name == "isRegionOf"
    assert result.input_value == "target_res_without_representation_1"
    assert result.input_type == "in-built:TestNormalResource"
    assert result.expected == "Representation"


class TestQueryAllResults:
    def test_link_target_inexistent(self, report_target_resource_wrong_type: tuple[Graph, Graph]) -> None:
        validation_g, onto_data_g = report_target_resource_wrong_type
        extracted_results, unexpected_components = _query_all_results(validation_g, onto_data_g)
        assert not unexpected_components
        assert len(extracted_results) == 1
        result = extracted_results.pop(0)
        assert isinstance(result, ValidationResult)
        assert result.violation_type == ViolationType.LINK_TARGET
        assert result.res_iri == DATA.region_isRegionOf_resource_not_a_representation
        assert result.res_class == KNORA_API.Region
        assert result.property == KNORA_API.isRegionOf
        assert result.input_value == DATA.target_res_without_representation_1
        assert result.input_type == IN_BUILT_ONTO.TestNormalResource
        assert result.expected == Literal("http://api.knora.org/ontology/knora-api/v2#Representation")


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
        assert isinstance(result, ValidationResult)
        assert result.violation_type == ViolationType.MIN_CARD
        assert result.res_iri == info.resource_iri
        assert result.res_class == info.res_class_type
        assert result.property == ONTO.testBoolean
        assert result.expected == Literal("1")

    def test_result_id_closed_constraint(
        self, report_closed_constraint: tuple[Graph, Graph, ValidationResultBaseInfo]
    ) -> None:
        res, _, info = report_closed_constraint
        result = _query_one_without_detail(info, res)
        assert isinstance(result, ValidationResult)
        assert result.violation_type == ViolationType.NON_EXISTING_CARD
        assert result.res_iri == info.resource_iri
        assert result.res_class == info.res_class_type
        assert result.property == ONTO.testIntegerSimpleText

    def test_result_id_max_card(self, report_max_card: tuple[Graph, Graph, ValidationResultBaseInfo]) -> None:
        res, _, info = report_max_card
        result = _query_one_without_detail(info, res)
        assert isinstance(result, ValidationResult)
        assert result.violation_type == ViolationType.MAX_CARD
        assert result.res_iri == info.resource_iri
        assert result.res_class == info.res_class_type
        assert result.property == ONTO.testHasLinkToCardOneResource
        assert result.expected == Literal("1")

    def test_result_empty_label(self, report_empty_label: tuple[Graph, ValidationResultBaseInfo]) -> None:
        graphs, info = report_empty_label
        result = _query_one_without_detail(info, graphs)
        assert isinstance(result, ValidationResult)
        assert result.violation_type == ViolationType.PATTERN
        assert result.res_iri == info.resource_iri
        assert result.res_class == info.res_class_type
        assert result.property == RDFS.label
        assert result.expected == Literal("The label must be a non-empty string")
        assert result.input_value == Literal(" ")

    def test_unique_value_literal(
        self, report_unique_value_literal: tuple[Graph, Graph, ValidationResultBaseInfo]
    ) -> None:
        res, _, info = report_unique_value_literal
        result = _query_one_without_detail(info, res)
        assert isinstance(result, ValidationResult)
        assert result.violation_type == ViolationType.UNIQUE_VALUE
        assert result.res_iri == info.resource_iri
        assert result.res_class == info.res_class_type
        assert result.property == ONTO.testGeoname
        assert result.input_value == Literal("00111111")

    def test_unique_value_iri(self, report_unique_value_iri: tuple[Graph, Graph, ValidationResultBaseInfo]) -> None:
        res, _, info = report_unique_value_iri
        result = _query_one_without_detail(info, res)
        assert isinstance(result, ValidationResult)
        assert result.violation_type == ViolationType.UNIQUE_VALUE
        assert result.res_iri == info.resource_iri
        assert result.res_class == info.res_class_type
        assert result.property == ONTO.testHasLinkTo
        assert result.input_value == DATA.link_valueTarget_id

    def test_coexist_with(self, report_coexist_with: tuple[Graph, Graph, ValidationResultBaseInfo]) -> None:
        validation_g, _, info = report_coexist_with
        result = _query_one_without_detail(info, validation_g)
        assert isinstance(result, ValidationResult)
        assert result.violation_type == ViolationType.SEQNUM_IS_PART_OF
        assert result.res_iri == info.resource_iri
        assert result.res_class == info.res_class_type
        assert result.message == Literal("The property seqnum must be used together with isPartOf")
        assert not result.property

    def test_unknown(self, result_unknown_component: tuple[Graph, ValidationResultBaseInfo]) -> None:
        graphs, info = result_unknown_component
        result = _query_one_without_detail(info, graphs)
        assert isinstance(result, UnexpectedComponent)
        assert result.component_type == str(SH.UniqueLangConstraintComponent)


class TestQueryWithDetail:
    def test_result_id_simpletext(
        self, report_value_type_simpletext: tuple[Graph, Graph, ValidationResultBaseInfo]
    ) -> None:
        res, data, info = report_value_type_simpletext
        result = _query_one_with_detail(info, res, data)
        assert isinstance(result, ValidationResult)
        assert result.violation_type == ViolationType.VALUE_TYPE
        assert result.res_iri == info.resource_iri
        assert result.res_class == info.res_class_type
        assert result.property == ONTO.testTextarea
        assert result.expected == Literal("TextValue without formatting")
        assert result.input_type == KNORA_API.TextValue

    def test_result_id_uri(self, report_value_type: tuple[Graph, Graph, ValidationResultBaseInfo]) -> None:
        res, data, info = report_value_type
        result = _query_one_with_detail(info, res, data)
        assert isinstance(result, ValidationResult)
        assert result.violation_type == ViolationType.VALUE_TYPE
        assert result.res_iri == info.resource_iri
        assert result.res_class == info.res_class_type
        assert result.property == ONTO.testUriValue
        assert result.expected == Literal("UriValue")
        assert result.input_type == KNORA_API.TextValue

    def test_result_geoname_not_number(self, report_regex: tuple[Graph, Graph, ValidationResultBaseInfo]) -> None:
        res, data, info = report_regex
        result = _query_one_with_detail(info, res, data)
        assert isinstance(result, ValidationResult)
        assert result.violation_type == ViolationType.PATTERN
        assert result.res_iri == info.resource_iri
        assert result.res_class == info.res_class_type
        assert result.property == ONTO.testGeoname
        assert result.expected == Literal("The value must be a valid geoname code")
        assert result.input_value == Literal("this-is-not-a-valid-code")

    def test_link_target_non_existent(
        self, report_link_target_non_existent: tuple[Graph, Graph, ValidationResultBaseInfo]
    ) -> None:
        res, data, info = report_link_target_non_existent
        result = _query_one_with_detail(info, res, data)
        assert isinstance(result, ValidationResult)
        assert result.violation_type == ViolationType.LINK_TARGET
        assert result.res_iri == info.resource_iri
        assert result.res_class == info.res_class_type
        assert result.property == ONTO.testHasLinkTo
        assert result.expected == KNORA_API.Resource
        assert result.input_value == DATA.other
        assert not result.input_type

    def test_link_target_wrong_class(
        self, report_link_target_wrong_class: tuple[Graph, Graph, ValidationResultBaseInfo]
    ) -> None:
        res, data, info = report_link_target_wrong_class
        result = _query_one_with_detail(info, res, data)
        assert isinstance(result, ValidationResult)
        assert result.violation_type == ViolationType.LINK_TARGET
        assert result.res_iri == info.resource_iri
        assert result.res_class == info.res_class_type
        assert result.property == ONTO.testHasLinkToCardOneResource
        assert result.expected == ONTO.CardOneResource
        assert result.input_value == DATA.id_9_target
        assert result.input_type == ONTO.ClassWithEverything

    def test_report_unknown_list_name(
        self, report_unknown_list_name: tuple[Graph, Graph, ValidationResultBaseInfo]
    ) -> None:
        res, data, info = report_unknown_list_name
        result = _query_one_with_detail(info, res, data)
        assert isinstance(result, ValidationResult)
        assert result.violation_type == ViolationType.GENERIC
        assert result.res_iri == info.resource_iri
        assert result.res_class == info.res_class_type
        assert result.property == ONTO.testListProp
        assert result.message == Literal("A valid node from the list 'firstList' must be used with this property.")
        assert result.input_value == Literal("other / n1")

    def test_report_unknown_list_node(
        self, report_unknown_list_node: tuple[Graph, Graph, ValidationResultBaseInfo]
    ) -> None:
        res, data, info = report_unknown_list_node
        result = _query_one_with_detail(info, res, data)
        assert isinstance(result, ValidationResult)
        assert result.violation_type == ViolationType.GENERIC
        assert result.res_iri == info.resource_iri
        assert result.res_class == info.res_class_type
        assert result.property == ONTO.testListProp
        assert result.message == Literal("A valid node from the list 'firstList' must be used with this property.")
        assert result.input_value == Literal("firstList / other")

    def test_report_min_inclusive(self, report_min_inclusive: tuple[Graph, Graph, ValidationResultBaseInfo]) -> None:
        res, data, info = report_min_inclusive
        result = _query_one_with_detail(info, res, data)
        assert isinstance(result, ValidationResult)
        assert result.violation_type == ViolationType.GENERIC
        assert result.res_iri == info.resource_iri
        assert result.res_class == info.res_class_type
        assert result.property == KNORA_API.hasSegmentBounds
        assert result.message == Literal("The interval start must be a non-negative integer or decimal.")
        assert result.input_value == Literal("-2.0", datatype=XSD.decimal)


class TestQueryFileValueViolations:
    def test_missing_file_value(self, report_missing_file_value: tuple[Graph, ValidationResultBaseInfo]) -> None:
        graphs, info = report_missing_file_value
        result = _query_one_without_detail(info, graphs)
        assert isinstance(result, ValidationResult)
        assert result.violation_type == ViolationType.FILE_VALUE
        assert result.res_iri == info.resource_iri
        assert result.res_class == info.res_class_type
        assert result.property == KNORA_API.hasMovingImageFileValue
        assert result.expected == Literal("A MovingImageRepresentation requires a file with the extension 'mp4'.")

    def test_file_value_cardinality_to_ignore(
        self, file_value_cardinality_to_ignore: tuple[Graph, ValidationResultBaseInfo]
    ) -> None:
        graphs, info = file_value_cardinality_to_ignore
        result = _query_one_without_detail(info, graphs)
        assert result is None

    def test_file_value_for_resource_without_representation(
        self, file_value_for_resource_without_representation: tuple[Graph, ValidationResultBaseInfo]
    ) -> None:
        graphs, info = file_value_for_resource_without_representation
        result = _query_one_without_detail(info, graphs)
        assert isinstance(result, ValidationResult)
        assert result.violation_type == ViolationType.FILEVALUE_PROHIBITED
        assert result.res_iri == info.resource_iri
        assert result.res_class == info.res_class_type
        assert result.property == KNORA_API.hasMovingImageFileValue


class TestReformatResult:
    def test_min(self, extracted_min_card: ValidationResult) -> None:
        result = _reformat_one_validation_result(extracted_min_card)
        assert result.problem_type == ProblemType.MIN_CARD
        assert result.res_id == "id_card_one"
        assert result.res_type == "onto:ClassInheritedCardinalityOverwriting"
        assert result.prop_name == "onto:testBoolean"
        assert result.expected == "1"

    def test_max(self, extracted_max_card: ValidationResult) -> None:
        result = _reformat_one_validation_result(extracted_max_card)
        assert result.problem_type == ProblemType.MAX_CARD
        assert result.res_id == "id_max_card"
        assert result.res_type == "onto:ClassMixedCard"
        assert result.prop_name == "onto:testDecimalSimpleText"
        assert result.expected == "0-1"

    def test_violation_empty_label(self, extracted_empty_label: ValidationResult) -> None:
        result = _reformat_one_validation_result(extracted_empty_label)
        assert result.problem_type == ProblemType.INPUT_REGEX
        assert result.res_id == "empty_label"
        assert result.res_type == "onto:ClassWithEverything"
        assert result.prop_name == "rdfs:label"
        assert result.expected == "The label must be a non-empty string"
        assert result.input_value == " "

    def test_closed(self, extracted_closed_constraint: ValidationResult) -> None:
        result = _reformat_one_validation_result(extracted_closed_constraint)
        assert result.problem_type == ProblemType.NON_EXISTING_CARD
        assert result.res_id == "id_closed_constraint"
        assert result.res_type == "onto:CardOneResource"
        assert result.prop_name == "onto:testIntegerSimpleText"

    def test_value_type_simpletext(self, extracted_value_type_simpletext: ValidationResult) -> None:
        result = _reformat_one_validation_result(extracted_value_type_simpletext)
        assert result.problem_type == ProblemType.VALUE_TYPE_MISMATCH
        assert result.res_id == "id_simpletext"
        assert result.res_type == "onto:ClassWithEverything"
        assert result.prop_name == "onto:testTextarea"
        assert result.input_type == "TextValue"
        assert result.expected == "TextValue without formatting"

    def test_value_type(self, extracted_value_type: ValidationResult) -> None:
        result = _reformat_one_validation_result(extracted_value_type)
        assert result.problem_type == ProblemType.VALUE_TYPE_MISMATCH
        assert result.res_id == "id_uri"
        assert result.res_type == "onto:ClassWithEverything"
        assert result.prop_name == "onto:testUriValue"
        assert result.input_type == "TextValue"
        assert result.expected == "UriValue"

    def test_violation_regex(self, extracted_regex: ValidationResult) -> None:
        result = _reformat_one_validation_result(extracted_regex)
        assert result.problem_type == ProblemType.INPUT_REGEX
        assert result.res_id == "geoname_not_number"
        assert result.res_type == "onto:ClassWithEverything"
        assert result.prop_name == "onto:testGeoname"
        assert result.expected == "The value must be a valid geoname code"
        assert result.input_value == "this-is-not-a-valid-code"

    def test_link_target_non_existent(self, extracted_link_target_non_existent: ValidationResult) -> None:
        result = _reformat_one_validation_result(extracted_link_target_non_existent)
        assert result.problem_type == ProblemType.INEXISTENT_LINKED_RESOURCE
        assert result.res_id == "link_target_non_existent"
        assert result.res_type == "onto:ClassWithEverything"
        assert result.prop_name == "onto:testHasLinkTo"
        assert result.input_value == "other"

    def test_link_target_wrong_class(self, extracted_link_target_wrong_class: ValidationResult) -> None:
        result = _reformat_one_validation_result(extracted_link_target_wrong_class)
        assert result.problem_type == ProblemType.LINK_TARGET_TYPE_MISMATCH
        assert result.res_id == "link_target_wrong_class"
        assert result.res_type == "onto:ClassWithEverything"
        assert result.prop_name == "onto:testHasLinkToCardOneResource"
        assert result.input_value == "id_9_target"
        assert result.input_type == "onto:ClassWithEverything"
        assert result.expected == "onto:CardOneResource"

    def test_unique_value_literal(self, extracted_unique_value_literal: ValidationResult) -> None:
        result = _reformat_one_validation_result(extracted_unique_value_literal)
        assert result.problem_type == ProblemType.DUPLICATE_VALUE
        assert result.res_id == "identical_values_valueHas"
        assert result.res_type == "onto:ClassWithEverything"
        assert result.prop_name == "onto:testGeoname"
        assert result.input_value == "00111111"

    def test_unique_value_iri(self, extracted_unique_value_iri: ValidationResult) -> None:
        result = _reformat_one_validation_result(extracted_unique_value_iri)
        assert result.problem_type == ProblemType.DUPLICATE_VALUE
        assert result.res_id == "identical_values_LinkValue"
        assert result.res_type == "onto:ClassWithEverything"
        assert result.prop_name == "onto:testHasLinkTo"
        assert result.input_value == "link_valueTarget_id"

    def test_unknown_list_node(self, extracted_unknown_list_node: ValidationResult) -> None:
        result = _reformat_one_validation_result(extracted_unknown_list_node)
        assert result.problem_type == ProblemType.GENERIC
        assert result.res_id == "list_node_non_existent"
        assert result.res_type == "onto:ClassWithEverything"
        assert result.prop_name == "onto:testListProp"
        assert result.message == "A valid node from the list 'firstList' must be used with this property."
        assert result.input_value == "firstList / other"

    def test_unknown_list_name(self, extracted_unknown_list_name: ValidationResult) -> None:
        result = _reformat_one_validation_result(extracted_unknown_list_name)
        assert result.problem_type == ProblemType.GENERIC
        assert result.res_id == "list_name_non_existent"
        assert result.res_type == "onto:ClassWithEverything"
        assert result.prop_name == "onto:testListProp"
        assert result.message == "A valid node from the list 'firstList' must be used with this property."
        assert result.input_value == "other / n1"

    def test_min_inclusive(self, extracted_min_inclusive: ValidationResult) -> None:
        result = _reformat_one_validation_result(extracted_min_inclusive)
        assert result.problem_type == ProblemType.GENERIC
        assert result.res_id == "video_segment_negative_bounds"
        assert result.res_type == "VideoSegment"
        assert result.prop_name == "hasSegmentBounds"
        assert result.message == "The interval start must be a non-negative integer or decimal."
        assert result.input_value == "-2.0"

    def test_missing_file_value(self, extracted_missing_file_value: ValidationResult) -> None:
        result = _reformat_one_validation_result(extracted_missing_file_value)
        assert result.problem_type == ProblemType.FILE_VALUE
        assert result.res_id == "id_video_missing"
        assert result.res_type == "onto:TestMovingImageRepresentation"
        assert result.prop_name == "bitstream / iiif-uri"
        assert result.expected == "A MovingImageRepresentation requires a file with the extension 'mp4'."

    def test_file_value_for_resource_without_representation(
        self, extracted_file_value_for_resource_without_representation: ValidationResult
    ) -> None:
        result = _reformat_one_validation_result(extracted_file_value_for_resource_without_representation)
        assert result.problem_type == ProblemType.FILE_VALUE_PROHIBITED
        assert result.res_id == "id_resource_without_representation"
        assert result.res_type == "onto:ClassWithEverything"
        assert result.prop_name == "bitstream / iiif-uri"

    def test_seqnum_is_part_of(self, extracted_coexist_with: ValidationResult) -> None:
        result = _reformat_one_validation_result(extracted_coexist_with)
        assert result.problem_type == ProblemType.GENERIC
        assert result.res_id == "missing_seqnum"
        assert result.res_type == "in-built:TestStillImageRepresentationWithSeqnum"
        assert result.prop_name == "seqnum or isPartOf"
        assert result.message == "Coexist message from knora-api turtle"


if __name__ == "__main__":
    pytest.main([__file__])
