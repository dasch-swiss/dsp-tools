# mypy: disable-error-code="method-assign,no-untyped-def"

import pytest
from rdflib import RDF
from rdflib import RDFS
from rdflib import SH
from rdflib import XSD
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.commands.validate_data.models.input_problems import ProblemType
from dsp_tools.commands.validate_data.models.input_problems import Severity
from dsp_tools.commands.validate_data.models.validation import DetailBaseInfo
from dsp_tools.commands.validate_data.models.validation import QueryInfo
from dsp_tools.commands.validate_data.models.validation import UnexpectedComponent
from dsp_tools.commands.validate_data.models.validation import ValidationReportGraphs
from dsp_tools.commands.validate_data.models.validation import ValidationResult
from dsp_tools.commands.validate_data.models.validation import ValidationResultBaseInfo
from dsp_tools.commands.validate_data.models.validation import ViolationType
from dsp_tools.commands.validate_data.process_validation_report.query_validation_result import (
    _extract_base_info_of_resource_results,
)
from dsp_tools.commands.validate_data.process_validation_report.query_validation_result import _get_all_main_result_bns
from dsp_tools.commands.validate_data.process_validation_report.query_validation_result import (
    _get_resource_iri_and_type,
)
from dsp_tools.commands.validate_data.process_validation_report.query_validation_result import _query_all_results
from dsp_tools.commands.validate_data.process_validation_report.query_validation_result import _query_one_with_detail
from dsp_tools.commands.validate_data.process_validation_report.query_validation_result import _query_one_without_detail
from dsp_tools.commands.validate_data.process_validation_report.query_validation_result import _separate_result_types
from dsp_tools.commands.validate_data.process_validation_report.query_validation_result import reformat_validation_graph
from dsp_tools.utils.rdflib_constants import DATA
from dsp_tools.utils.rdflib_constants import KNORA_API
from test.unittests.commands.validate_data.constants import IN_BUILT_ONTO
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
    assert result.severity == Severity.VIOLATION
    assert result.input_value == "target_res_without_representation_1"
    assert result.input_type == "in-built:TestNormalResource"
    assert result.expected == "Representation"


def test_separate_bns_of_results(
    report_target_resource_wrong_type: tuple[Graph, Graph], report_not_resource: tuple[Graph, Graph]
):
    val_g1, _ = report_target_resource_wrong_type
    val_g2, _ = report_not_resource
    combined_g = val_g1 + val_g2
    extracted_bns = _get_all_main_result_bns(combined_g)
    node1 = next(combined_g.subjects(SH.focusNode, DATA.region_isRegionOf_resource_not_a_representation))
    node2 = next(combined_g.subjects(SH.focusNode, DATA.value_id_simpletext))
    assert extracted_bns == {node1, node2}


class TestGetResourceIRIs:
    def test_with_detail_user_facing_info_there(self, report_value_type_simpletext):
        _, onto_data_g, base_info = report_value_type_simpletext
        query_info = QueryInfo(base_info.result_bn, DATA.id_simpletext, ONTO.ClassWithEverything)
        resource_iri, resource_type, user_facing_prop = _get_resource_iri_and_type(
            query_info, ONTO.testTextarea, onto_data_g, {KNORA_API.TextValue}
        )
        assert resource_iri == DATA.id_simpletext
        assert resource_type == ONTO.ClassWithEverything
        assert user_facing_prop == ONTO.testTextarea

    def test_no_detail_user_facing_info_there(self, report_value_type):
        _, onto_data_g, base_info = report_value_type
        query_info = QueryInfo(base_info.result_bn, DATA.id_uri, ONTO.ClassWithEverything)
        resource_iri, resource_type, user_facing_prop = _get_resource_iri_and_type(
            query_info, ONTO.testUriValue, onto_data_g, {KNORA_API.TextValue}
        )
        assert resource_iri == DATA.id_uri
        assert resource_type == ONTO.ClassWithEverything
        assert user_facing_prop == ONTO.testUriValue

    def test_no_detail_user_facing_prop_is_knora_prop(self, report_archive_missing_legal_info):
        validation_g, onto_data_g = report_archive_missing_legal_info
        result_bn = next(validation_g.subjects(RDF.type, SH.ValidationResult))
        query_info = QueryInfo(result_bn, DATA.value_bitstream_no_legal_info, KNORA_API.ArchiveFileValue)
        resource_iri, resource_type, user_facing_prop = _get_resource_iri_and_type(
            query_info, KNORA_API.hasLicense, onto_data_g, {KNORA_API.ArchiveFileValue}
        )
        assert resource_iri == DATA.bitstream_no_legal_info
        assert resource_type == ONTO.TestArchiveRepresentation
        assert user_facing_prop == KNORA_API.hasLicense


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
        assert result.severity == SH.Violation
        assert result.input_value == DATA.target_res_without_representation_1
        assert result.input_type == IN_BUILT_ONTO.TestNormalResource
        assert result.expected == Literal("http://api.knora.org/ontology/knora-api/v2#Representation")

    def test_report_archive_missing_legal_info(self, report_archive_missing_legal_info: tuple[Graph, Graph]) -> None:
        validation_g, onto_data_g = report_archive_missing_legal_info
        extracted_results, unexpected_components = _query_all_results(validation_g, onto_data_g)
        assert not unexpected_components
        assert len(extracted_results) == 1
        result = extracted_results.pop(0)
        assert isinstance(result, ValidationResult)
        assert result.violation_type == ViolationType.GENERIC
        assert result.res_iri == DATA.bitstream_no_legal_info
        assert result.res_class == ONTO.TestArchiveRepresentation
        assert result.property == KNORA_API.hasLicense
        assert result.severity == SH.Warning
        assert not result.input_value
        assert not result.input_type
        assert result.expected == Literal("Files and IIIF-URIs require a reference to a license.")

    def test_result_geoname_not_number(self, report_regex: tuple[Graph, Graph, ValidationResultBaseInfo]) -> None:
        res, data, _ = report_regex
        extracted_results, unexpected_components = _query_all_results(res, data)
        assert not unexpected_components
        assert len(extracted_results) == 1
        result = extracted_results.pop(0)
        assert isinstance(result, ValidationResult)
        assert result.violation_type == ViolationType.PATTERN
        assert result.severity == SH.Violation
        assert result.res_iri == DATA.geoname_not_number
        assert result.res_class == ONTO.ClassWithEverything
        assert result.property == ONTO.testGeoname
        assert result.expected == Literal("The value must be a valid geoname code")
        assert result.input_value == Literal("this-is-not-a-valid-code")


class TestExtractBaseInfo:
    def test_no_detail(self, report_min_card: tuple[Graph, Graph, ValidationResultBaseInfo]) -> None:
        validation_g, onto_data_g, _ = report_min_card
        results = _extract_base_info_of_resource_results(validation_g, onto_data_g)
        assert len(results) == 1
        found_result = results[0]
        assert found_result.focus_node_iri == DATA.id_card_one
        assert found_result.focus_node_type == ONTO.ClassInheritedCardinalityOverwriting
        assert found_result.result_path == ONTO.testBoolean
        assert found_result.source_constraint_component == SH.MinCountConstraintComponent
        assert found_result.severity == SH.Violation
        assert not found_result.detail

    def test_still_image_file(
        self, report_image_missing_legal_info: tuple[Graph, Graph, ValidationResultBaseInfo]
    ) -> None:
        validation_g, onto_data_g, _ = report_image_missing_legal_info
        results = _extract_base_info_of_resource_results(validation_g, onto_data_g)
        assert len(results) == 1
        found_result = results[0]
        assert found_result.focus_node_iri == DATA.image_no_legal_info
        assert found_result.focus_node_type == ONTO.TestStillImageRepresentation
        assert found_result.result_path == KNORA_API.hasLicense
        assert found_result.source_constraint_component == SH.MinCountConstraintComponent
        assert found_result.severity == SH.Warning
        assert not found_result.detail

    def test_with_detail(self, report_value_type_simpletext: tuple[Graph, Graph, ValidationResultBaseInfo]) -> None:
        validation_g, onto_data_g, _ = report_value_type_simpletext
        results = _extract_base_info_of_resource_results(validation_g, onto_data_g)
        assert len(results) == 1
        found_result = results[0]
        assert found_result.focus_node_iri == DATA.id_simpletext
        assert found_result.focus_node_type == ONTO.ClassWithEverything
        assert found_result.result_path == ONTO.testTextarea
        assert found_result.source_constraint_component == SH.NodeConstraintComponent
        assert found_result.severity == SH.Violation
        detail = found_result.detail
        assert isinstance(detail, DetailBaseInfo)
        assert detail.source_constraint_component == SH.MinCountConstraintComponent


class TestSeparateResultTypes:
    def test_result_id_card_one(self, report_min_card: tuple[Graph, Graph, ValidationResultBaseInfo]) -> None:
        res_g, onto_data_g, _ = report_min_card
        no_detail, with_detail = _separate_result_types(res_g, onto_data_g)
        assert len(no_detail) == 1
        assert len(with_detail) == 0
        assert no_detail[0].focus_node_iri == DATA.id_card_one

    def test_result_id_simpletext(
        self, report_value_type_simpletext: tuple[Graph, Graph, ValidationResultBaseInfo]
    ) -> None:
        res_g, onto_data_g, _ = report_value_type_simpletext
        no_detail, with_detail = _separate_result_types(res_g, onto_data_g)
        assert len(no_detail) == 0
        assert len(with_detail) == 1
        assert with_detail[0].focus_node_iri == DATA.id_simpletext

    def test_result_id_uri(self, report_value_type: tuple[Graph, Graph, ValidationResultBaseInfo]) -> None:
        res_g, onto_data_g, _ = report_value_type
        no_detail, with_detail = _separate_result_types(res_g, onto_data_g)
        assert len(no_detail) == 1
        assert len(with_detail) == 0
        assert no_detail[0].focus_node_iri == DATA.id_uri

    def test_result_geoname_not_number(self, report_regex: tuple[Graph, Graph, ValidationResultBaseInfo]) -> None:
        res_g, onto_data_g, _ = report_regex
        no_detail, with_detail = _separate_result_types(res_g, onto_data_g)
        assert len(no_detail) == 1
        assert len(with_detail) == 0
        assert no_detail[0].focus_node_iri == DATA.geoname_not_number

    def test_result_id_closed_constraint(
        self, report_closed_constraint: tuple[Graph, Graph, ValidationResultBaseInfo]
    ) -> None:
        res_g, onto_data_g, _ = report_closed_constraint
        no_detail, with_detail = _separate_result_types(res_g, onto_data_g)
        assert len(no_detail) == 1
        assert len(with_detail) == 0
        assert no_detail[0].focus_node_iri == DATA.id_closed_constraint

    def test_result_id_max_card(self, report_max_card: tuple[Graph, Graph, ValidationResultBaseInfo]) -> None:
        res_g, onto_data_g, _ = report_max_card
        no_detail, with_detail = _separate_result_types(res_g, onto_data_g)
        assert len(no_detail) == 1
        assert len(with_detail) == 0
        assert no_detail[0].focus_node_iri == DATA.id_max_card

    def test_report_unique_value_literal(
        self, report_unique_value_literal: tuple[Graph, Graph, ValidationResultBaseInfo]
    ) -> None:
        res_g, onto_data_g, _ = report_unique_value_literal
        no_detail, with_detail = _separate_result_types(res_g, onto_data_g)
        assert len(no_detail) == 1
        assert len(with_detail) == 0
        assert no_detail[0].focus_node_iri == DATA.identical_values_valueHas

    def test_report_unique_value_iri(
        self, report_unique_value_iri: tuple[Graph, Graph, ValidationResultBaseInfo]
    ) -> None:
        res_g, onto_data_g, _ = report_unique_value_iri
        no_detail, with_detail = _separate_result_types(res_g, onto_data_g)
        assert len(no_detail) == 1
        assert len(with_detail) == 0
        assert no_detail[0].focus_node_iri == DATA.identical_values_LinkValue


class TestQueryWithoutDetail:
    def test_result_id_card_one(self, report_min_card: tuple[Graph, Graph, ValidationResultBaseInfo]) -> None:
        res, data, info = report_min_card
        result = _query_one_without_detail(info, res, data)
        assert isinstance(result, ValidationResult)
        assert result.violation_type == ViolationType.MIN_CARD
        assert result.res_iri == info.focus_node_iri
        assert result.res_class == info.focus_node_type
        assert result.property == ONTO.testBoolean
        assert result.severity == SH.Violation
        assert result.expected == Literal("1")

    def test_result_id_closed_constraint(
        self, report_closed_constraint: tuple[Graph, Graph, ValidationResultBaseInfo]
    ) -> None:
        res, data, info = report_closed_constraint
        result = _query_one_without_detail(info, res, data)
        assert isinstance(result, ValidationResult)
        assert result.violation_type == ViolationType.NON_EXISTING_CARD
        assert result.res_iri == info.focus_node_iri
        assert result.res_class == info.focus_node_type
        assert result.severity == SH.Violation
        assert result.property == ONTO.testIntegerSimpleText

    def test_result_id_max_card(self, report_max_card: tuple[Graph, Graph, ValidationResultBaseInfo]) -> None:
        res, data, info = report_max_card
        result = _query_one_without_detail(info, res, data)
        assert isinstance(result, ValidationResult)
        assert result.violation_type == ViolationType.MAX_CARD
        assert result.res_iri == info.focus_node_iri
        assert result.res_class == info.focus_node_type
        assert result.property == ONTO.testHasLinkToCardOneResource
        assert result.severity == SH.Violation
        assert result.expected == Literal("1")

    def test_result_empty_label(self, report_empty_label: tuple[Graph, ValidationResultBaseInfo]) -> None:
        graphs, info = report_empty_label
        result = _query_one_without_detail(info, graphs, Graph())
        assert isinstance(result, ValidationResult)
        assert result.violation_type == ViolationType.PATTERN
        assert result.res_iri == info.focus_node_iri
        assert result.res_class == info.focus_node_type
        assert result.property == RDFS.label
        assert result.severity == SH.Violation
        assert result.expected == Literal("The label must be a non-empty string")
        assert result.input_value == Literal(" ")

    def test_unique_value_literal(
        self, report_unique_value_literal: tuple[Graph, Graph, ValidationResultBaseInfo]
    ) -> None:
        res, data, info = report_unique_value_literal
        result = _query_one_without_detail(info, res, data)
        assert isinstance(result, ValidationResult)
        assert result.violation_type == ViolationType.UNIQUE_VALUE
        assert result.res_iri == info.focus_node_iri
        assert result.res_class == info.focus_node_type
        assert result.severity == SH.Violation
        assert result.property == ONTO.testGeoname
        assert result.input_value == Literal("00111111")

    def test_unique_value_iri(self, report_unique_value_iri: tuple[Graph, Graph, ValidationResultBaseInfo]) -> None:
        res, data, info = report_unique_value_iri
        result = _query_one_without_detail(info, res, data)
        assert isinstance(result, ValidationResult)
        assert result.violation_type == ViolationType.UNIQUE_VALUE
        assert result.res_iri == info.focus_node_iri
        assert result.res_class == info.focus_node_type
        assert result.severity == SH.Violation
        assert result.property == ONTO.testHasLinkTo
        assert result.input_value == DATA.link_valueTarget_id

    def test_coexist_with(self, report_coexist_with: tuple[Graph, Graph, ValidationResultBaseInfo]) -> None:
        validation_g, data, info = report_coexist_with
        result = _query_one_without_detail(info, validation_g, data)
        assert isinstance(result, ValidationResult)
        assert result.violation_type == ViolationType.SEQNUM_IS_PART_OF
        assert result.res_iri == info.focus_node_iri
        assert result.res_class == info.focus_node_type
        assert result.severity == SH.Violation
        assert result.message == Literal("The property seqnum must be used together with isPartOf")
        assert not result.property
        assert not result.input_value

    def test_report_coexist_with_date(
        self, report_coexist_with_date: tuple[Graph, Graph, ValidationResultBaseInfo]
    ) -> None:
        validation_g, data, info = report_coexist_with_date
        result = _query_one_without_detail(info, validation_g, data)
        assert isinstance(result, ValidationResult)
        assert result.violation_type == ViolationType.GENERIC
        assert result.res_iri == info.focus_node_iri
        assert result.res_class == info.focus_node_type
        assert result.severity == SH.Violation
        assert result.message == Literal("date message")
        assert result.property == info.result_path
        assert result.input_value == Literal("GREGORIAN:CE:2000:BCE:1900", datatype=XSD.string)

    def test_image_missing_legal_info(
        self, report_image_missing_legal_info: tuple[Graph, Graph, ValidationResultBaseInfo]
    ) -> None:
        res, data, info = report_image_missing_legal_info
        result = _query_one_without_detail(info, res, data)
        assert isinstance(result, ValidationResult)
        assert result.violation_type == ViolationType.GENERIC
        assert result.res_iri == info.focus_node_iri
        assert result.res_class == info.focus_node_type
        assert result.severity == SH.Warning
        assert result.property == KNORA_API.hasLicense
        assert result.expected == Literal("Files and IIIF-URIs require a reference to a license.")

    def test_result_id_uri(self, report_value_type: tuple[Graph, Graph, ValidationResultBaseInfo]) -> None:
        res, data, info = report_value_type
        result = _query_one_without_detail(info, res, data)
        assert isinstance(result, ValidationResult)
        assert result.violation_type == ViolationType.VALUE_TYPE
        assert result.res_iri == info.focus_node_iri
        assert result.res_class == info.focus_node_type
        assert result.property == ONTO.testUriValue
        assert result.severity == SH.Violation
        assert result.expected == Literal("This property requires a UriValue")
        assert result.input_type == KNORA_API.TextValue

    def test_report_min_inclusive(self, report_min_inclusive: tuple[Graph, Graph, ValidationResultBaseInfo]) -> None:
        res, data, info = report_min_inclusive
        result = _query_one_without_detail(info, res, data)
        assert isinstance(result, ValidationResult)
        assert result.violation_type == ViolationType.GENERIC
        assert result.res_iri == info.focus_node_iri
        assert result.res_class == info.focus_node_type
        assert result.property == KNORA_API.hasSegmentBounds
        assert result.severity == SH.Violation
        assert result.message == Literal("The interval start must be a non-negative integer or decimal.")
        assert result.input_value == Literal("-2.0", datatype=XSD.decimal)

    def test_report_single_line_constraint_component(self, report_single_line_constraint_component) -> None:
        res, data, info = report_single_line_constraint_component
        result = _query_one_without_detail(info, res, data)
        assert isinstance(result, ValidationResult)
        assert result.violation_type == ViolationType.GENERIC
        assert result.res_iri == info.focus_node_iri
        assert result.res_class == info.focus_node_type
        assert result.severity == SH.Violation
        assert result.property == KNORA_API.hasCopyrightHolder
        assert result.message == Literal("The copyright holder must be a string without newlines.")
        assert result.input_value == Literal(
            """FirstLine
Second Line"""
        )

    def test_report_date_single_month_does_not_exist(
        self, report_date_single_month_does_not_exist: tuple[Graph, Graph, ValidationResultBaseInfo]
    ) -> None:
        res, data, info = report_date_single_month_does_not_exist
        result = _query_one_without_detail(info, res, data)
        assert isinstance(result, ValidationResult)
        assert result.violation_type == ViolationType.GENERIC
        assert result.res_iri == info.focus_node_iri
        assert result.res_class == info.focus_node_type
        assert result.property == ONTO.testSubDate1
        assert result.severity == SH.Violation
        assert result.message == Literal("date message")
        assert result.input_value == Literal("GREGORIAN:CE:1800-22", datatype=XSD.string)

    def test_report_date_range_wrong_yyyy(
        self, report_date_range_wrong_yyyy: tuple[Graph, Graph, ValidationResultBaseInfo]
    ) -> None:
        res, data, info = report_date_range_wrong_yyyy
        result = _query_one_without_detail(info, res, data)
        assert isinstance(result, ValidationResult)
        assert result.violation_type == ViolationType.GENERIC
        assert result.res_iri == info.focus_node_iri
        assert result.res_class == info.focus_node_type
        assert result.property == ONTO.testSubDate1
        assert result.severity == SH.Violation
        assert result.message == Literal("date message")
        assert result.input_value == Literal("GREGORIAN:CE:2000:CE:1900", datatype=XSD.string)

    def test_report_date_range_wrong_to_ignore(
        self, report_date_range_wrong_to_ignore: tuple[Graph, Graph, ValidationResultBaseInfo]
    ) -> None:
        res, data, info = report_date_range_wrong_to_ignore
        result = _query_one_without_detail(info, res, data)
        assert not result

    def test_report_standoff_link_target_is_iri(
        self, report_standoff_link_target_is_iri: tuple[Graph, Graph, ValidationResultBaseInfo]
    ) -> None:
        res, data, info = report_standoff_link_target_is_iri
        result = _query_one_without_detail(info, res, data)
        assert isinstance(result, ValidationResult)
        assert result.violation_type == ViolationType.LINK_TARGET
        assert result.res_iri == info.focus_node_iri
        assert result.res_class == info.focus_node_type
        assert result.property == KNORA_API.hasStandoffLinkTo
        assert result.severity == SH.Violation
        assert result.message == Literal("A stand-off link must target an existing resource.")
        assert result.input_value == URIRef("http://rdfh.ch/4123/DiAmYQzQSzC7cdTo6OJMYA")

    def test_unknown(self, result_unknown_component: tuple[Graph, ValidationResultBaseInfo]) -> None:
        graphs, info = result_unknown_component
        result = _query_one_without_detail(info, graphs, Graph())
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
        assert result.res_iri == info.focus_node_iri
        assert result.res_class == info.focus_node_type
        assert result.property == ONTO.testTextarea
        assert result.severity == SH.Violation
        assert result.expected == Literal("TextValue without formatting")
        assert result.input_type == KNORA_API.TextValue

    def test_link_target_non_existent(
        self, report_link_target_non_existent: tuple[Graph, Graph, ValidationResultBaseInfo]
    ) -> None:
        res, data, info = report_link_target_non_existent
        result = _query_one_with_detail(info, res, data)
        assert isinstance(result, ValidationResult)
        assert result.violation_type == ViolationType.LINK_TARGET
        assert result.res_iri == info.focus_node_iri
        assert result.res_class == info.focus_node_type
        assert result.property == ONTO.testHasLinkTo
        assert result.severity == SH.Violation
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
        assert result.res_iri == info.focus_node_iri
        assert result.res_class == info.focus_node_type
        assert result.severity == SH.Violation
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
        assert result.res_iri == info.focus_node_iri
        assert result.res_class == info.focus_node_type
        assert result.severity == SH.Violation
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
        assert result.res_iri == info.focus_node_iri
        assert result.res_class == info.focus_node_type
        assert result.severity == SH.Violation
        assert result.property == ONTO.testListProp
        assert result.message == Literal("A valid node from the list 'firstList' must be used with this property.")
        assert result.input_value == Literal("firstList / other")

    def test_report_single_line_constraint_component_content_is_value(
        self, report_single_line_constraint_component_content_is_value
    ) -> None:
        res, data, info = report_single_line_constraint_component_content_is_value
        result = _query_one_with_detail(info, res, data)
        assert isinstance(result, ValidationResult)
        assert result.violation_type == ViolationType.GENERIC
        assert result.res_iri == info.focus_node_iri
        assert result.res_class == info.focus_node_type
        assert result.severity == SH.Violation
        assert result.property == ONTO.testSimpleText
        assert result.message == Literal("The value must be a non-empty string without newlines.")
        assert result.input_value == Literal(
            """This may not

have newlines"""
        )


class TestQueryFileValueViolations:
    def test_missing_file_value(self, report_missing_file_value: tuple[Graph, ValidationResultBaseInfo]) -> None:
        graphs, info = report_missing_file_value
        result = _query_one_without_detail(info, graphs, Graph())
        assert isinstance(result, ValidationResult)
        assert result.violation_type == ViolationType.MIN_CARD
        assert result.res_iri == info.focus_node_iri
        assert result.res_class == info.focus_node_type
        assert result.severity == SH.Violation
        assert result.property == KNORA_API.hasMovingImageFileValue
        assert result.expected == Literal("Cardinality 1")

    def test_report_file_closed_constraint(
        self, report_file_closed_constraint: tuple[Graph, Graph, ValidationResultBaseInfo]
    ) -> None:
        results_g, data, info = report_file_closed_constraint
        result = _query_one_without_detail(info, results_g, data)
        assert isinstance(result, ValidationResult)
        assert result.violation_type == ViolationType.FILE_VALUE_PROHIBITED
        assert result.res_iri == info.focus_node_iri
        assert result.res_class == info.focus_node_type
        assert result.severity == SH.Violation
        assert result.property == KNORA_API.hasMovingImageFileValue
        assert result.input_value == Literal("file.mp4", datatype=XSD.string)

    def test_file_value_for_resource_without_representation(
        self, file_value_for_resource_without_representation: tuple[Graph, ValidationResultBaseInfo]
    ) -> None:
        graphs, info = file_value_for_resource_without_representation
        result = _query_one_without_detail(info, graphs, Graph())
        assert isinstance(result, ValidationResult)
        assert result.violation_type == ViolationType.FILE_VALUE_PROHIBITED
        assert result.res_iri == info.focus_node_iri
        assert result.res_class == info.focus_node_type
        assert result.severity == SH.Violation
        assert result.property == KNORA_API.hasMovingImageFileValue


if __name__ == "__main__":
    pytest.main([__file__])
