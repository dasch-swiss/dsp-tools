# mypy: disable-error-code="no-untyped-def"

from pathlib import Path
from typing import Never
from typing import assert_never
from typing import cast

import pytest
from rdflib import SH
from rdflib import BNode
from rdflib import URIRef

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.cli.args import ValidateDataConfig
from dsp_tools.cli.args import ValidationSeverity
from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.commands.validate_data.models.input_problems import ProblemType
from dsp_tools.commands.validate_data.models.input_problems import SortedProblems
from dsp_tools.commands.validate_data.models.input_problems import UnknownClassesInData
from dsp_tools.commands.validate_data.models.validation import DetailBaseInfo
from dsp_tools.commands.validate_data.models.validation import ValidationReportGraphs
from dsp_tools.commands.validate_data.process_validation_report.get_user_validation_message import sort_user_problems
from dsp_tools.commands.validate_data.process_validation_report.query_validation_result import (
    _extract_base_info_of_resource_results,
)
from dsp_tools.commands.validate_data.process_validation_report.query_validation_result import reformat_validation_graph
from dsp_tools.commands.validate_data.shacl_cli_validator import ShaclCliValidator
from dsp_tools.commands.validate_data.validate_data import _get_validation_status
from dsp_tools.commands.validate_data.validate_data import _validate_data
from dsp_tools.commands.validate_data.validation.check_duplicate_files import check_for_duplicate_files
from dsp_tools.commands.validate_data.validation.get_validation_report import get_validation_report
from dsp_tools.utils.rdflib_constants import DASH
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedResource
from test.e2e.commands.validate_data.util import prepare_data_for_validation_from_file

# ruff: noqa: ARG001 Unused function argument


CONFIG = ValidateDataConfig(
    xml_file=Path(),
    save_graph_dir=None,
    severity=ValidationSeverity.INFO,
    ignore_duplicate_files_warning=False,
    is_on_prod_server=False,
    skip_ontology_validation=False,
)


@pytest.fixture(scope="module")
def authentication(creds: ServerCredentials) -> AuthenticationClient:
    auth = AuthenticationClientLive(server=creds.server, email=creds.user, password=creds.password)
    return auth


@pytest.fixture(scope="module")
def every_violation_combination_once_info(
    create_generic_project, authentication, shacl_validator: ShaclCliValidator
) -> tuple[ValidationReportGraphs, list[ParsedResource]]:
    file = Path("testdata/validate-data/generic/every_violation_combination_once.xml")
    graphs, _, parsed_resources = prepare_data_for_validation_from_file(file, authentication)
    g = get_validation_report(graphs, shacl_validator)
    return g, parsed_resources


class TestWithReportGraphs:
    """
    These tests, focus confirm that the larger steps from the validate-data function behave as expected.
    Because of this, the code flow has to be copied from the primary calling function.
    It is not possible to test these steps properly without a stack.
    """

    def test_extract_identifiers_of_resource_results(
        self, every_violation_combination_once_info: tuple[ValidationReportGraphs, list[ParsedResource]]
    ) -> None:
        report_graphs, parsed_resources = every_violation_combination_once_info
        report_and_onto = report_graphs.validation_graph + report_graphs.onto_graph
        data_and_onto = report_graphs.data_graph + report_graphs.onto_graph
        result = _extract_base_info_of_resource_results(report_and_onto, data_and_onto)
        result_sorted = sorted(result, key=lambda x: str(x.focus_node_iri))
        # To query and identify the validation properly
        # we rely on knowing whether a result contains a sh:detail (those with BNodes) and those without.
        # This is something that we do not have an influence on directly
        # as the sh:detail is created by the SHACL engine and is based on the SHACL-shape.
        # If we changed a SHACL shape this may influence whether a result does or does not have a BNode
        # and consequently how we must query for it.
        expected_info = [
            (URIRef("http://data/bitstream_no_legal_info"), SH.MinCountConstraintComponent, None, None),
            (URIRef("http://data/bitstream_no_legal_info"), SH.MinCountConstraintComponent, None, None),
            (URIRef("http://data/bitstream_no_legal_info"), SH.MinCountConstraintComponent, None, None),
            (URIRef("http://data/date_month_does_not_exist"), SH.OrConstraintComponent, None, None),
            (URIRef("http://data/date_month_does_not_exist"), SH.OrConstraintComponent, None, None),
            (URIRef("http://data/date_range_first_is_ce_second_bce"), DASH.CoExistsWithConstraintComponent, None, None),
            (URIRef("http://data/date_range_wrong_yyyy"), SH.LessThanOrEqualsConstraintComponent, None, None),
            (URIRef("http://data/empty_label"), SH.PatternConstraintComponent, None, None),
            (URIRef("http://data/geoname_not_number"), SH.PatternConstraintComponent, None, None),
            (URIRef("http://data/id_card_one"), SH.MinCountConstraintComponent, None, None),
            (URIRef("http://data/id_closed_constraint"), DASH.ClosedByTypesConstraintComponent, None, None),
            (URIRef("http://data/id_max_card"), SH.MaxCountConstraintComponent, None, None),
            (URIRef("http://data/id_missing_file_value"), SH.MinCountConstraintComponent, None, None),
            (URIRef("http://data/identical_values"), SH.SPARQLConstraintComponent, None, None),
            (URIRef("http://data/image_no_legal_info"), SH.MinCountConstraintComponent, None, None),
            (URIRef("http://data/image_no_legal_info"), SH.MinCountConstraintComponent, None, None),
            (URIRef("http://data/image_no_legal_info"), SH.MinCountConstraintComponent, None, None),
            (URIRef("http://data/inexistent_license_iri"), SH.InConstraintComponent, None, None),
            (URIRef("http://data/label_with_newline"), DASH.SingleLineConstraintComponent, None, None),
            (
                URIRef("http://data/link_target_non_existent"),
                SH.NodeConstraintComponent,
                BNode,
                SH.ClassConstraintComponent,
            ),
            (
                URIRef("http://data/link_target_wrong_class"),
                SH.NodeConstraintComponent,
                BNode,
                SH.ClassConstraintComponent,
            ),
            (
                URIRef("http://data/link_to_resource_in_db"),
                SH.NodeConstraintComponent,
                BNode,
                SH.ClassConstraintComponent,
            ),
            (
                URIRef("http://data/list_node_non_existent"),
                SH.NodeConstraintComponent,
                BNode,
                SH.InConstraintComponent,
            ),
            (URIRef("http://data/missing_seqnum"), DASH.CoExistsWithConstraintComponent, None, None),
            (URIRef("http://data/richtext_standoff_link_nonexistent"), SH.ClassConstraintComponent, None, None),
            (
                URIRef("http://data/simpletext_wrong_value_type"),
                SH.NodeConstraintComponent,
                BNode,
                SH.MinCountConstraintComponent,
            ),
            (URIRef("http://data/uri_wrong_value_type"), SH.ClassConstraintComponent, None, None),
            (URIRef("http://data/video_segment_start_larger_than_end"), SH.LessThanConstraintComponent, None, None),
            (URIRef("http://data/video_segment_wrong_bounds"), SH.MinInclusiveConstraintComponent, None, None),
            (URIRef("http://data/video_segment_wrong_bounds"), SH.MinExclusiveConstraintComponent, None, None),
        ]
        assert len(result) == len(expected_info)
        for result_info, expected in zip(result_sorted, expected_info):
            assert result_info.focus_node_iri == expected[0]
            if result_info.focus_node_iri == URIRef("http://data/video_segment_wrong_bounds"):
                assert result_info.source_constraint_component in [
                    SH.MinInclusiveConstraintComponent,
                    SH.MinExclusiveConstraintComponent,
                ]
            else:
                assert result_info.source_constraint_component == expected[1], result_info.focus_node_iri
            if expected[2] is None:
                assert not result_info.detail
            else:
                detail_base_info = result_info.detail
                assert isinstance(detail_base_info, DetailBaseInfo)
                assert isinstance(detail_base_info.detail_bn, expected[2]), result_info.focus_node_iri
                assert detail_base_info.source_constraint_component == expected[3], result_info.focus_node_iri

    def test_reformat_every_constraint_once(
        self, every_violation_combination_once_info: tuple[ValidationReportGraphs, list[ParsedResource]]
    ) -> None:
        report, parsed_resources = every_violation_combination_once_info
        assert not report.conforms
        expected_violations = [
            ("date_month_does_not_exist", ProblemType.GENERIC),
            ("date_month_does_not_exist", ProblemType.GENERIC),
            ("date_range_first_is_ce_second_bce", ProblemType.GENERIC),
            ("date_range_wrong_yyyy", ProblemType.GENERIC),
            ("empty_label", ProblemType.INPUT_REGEX),
            ("geoname_not_number", ProblemType.INPUT_REGEX),
            ("id_card_one", ProblemType.MIN_CARD),
            ("id_closed_constraint", ProblemType.NON_EXISTING_CARD),
            ("id_max_card", ProblemType.MAX_CARD),
            ("id_missing_file_value", ProblemType.FILE_VALUE_MISSING),
            ("identical_values", ProblemType.DUPLICATE_VALUE),
            ("inexistent_license_iri", ProblemType.GENERIC),
            ("label_with_newline", ProblemType.GENERIC),
            ("link_target_non_existent", ProblemType.INEXISTENT_LINKED_RESOURCE),
            ("link_target_wrong_class", ProblemType.LINK_TARGET_TYPE_MISMATCH),
            ("list_node_non_existent", ProblemType.GENERIC),
            ("missing_seqnum", ProblemType.GENERIC),
            ("richtext_standoff_link_nonexistent", ProblemType.INEXISTENT_LINKED_RESOURCE),
            ("simpletext_wrong_value_type", ProblemType.VALUE_TYPE_MISMATCH),
            ("uri_wrong_value_type", ProblemType.VALUE_TYPE_MISMATCH),
            ("video_segment_start_larger_than_end", ProblemType.GENERIC),
            ("video_segment_wrong_bounds", ProblemType.GENERIC),  # once for start that is less than zero
            ("video_segment_wrong_bounds", ProblemType.GENERIC),  # once for the end that is zero
        ]
        expected_warnings = [
            (None, ProblemType.FILE_DUPLICATE),
            ("bitstream_no_legal_info", ProblemType.GENERIC),
            ("bitstream_no_legal_info", ProblemType.GENERIC),
            ("bitstream_no_legal_info", ProblemType.GENERIC),
            ("image_no_legal_info", ProblemType.GENERIC),
            ("image_no_legal_info", ProblemType.GENERIC),
            ("image_no_legal_info", ProblemType.GENERIC),
        ]
        expected_info = [("link_to_resource_in_db", ProblemType.INEXISTENT_LINKED_RESOURCE)]
        result = reformat_validation_graph(report)
        duplicate_files = check_for_duplicate_files(parsed_resources)
        sorted_problems = sort_user_problems(result, duplicate_files)
        alphabetically_sorted_violations = sorted(sorted_problems.unique_violations, key=lambda x: str(x.res_id))
        alphabetically_sorted_warnings = sorted(sorted_problems.user_warnings, key=lambda x: str(x.res_id))
        alphabetically_sorted_info = sorted(sorted_problems.user_info, key=lambda x: str(x.res_id))
        assert len(sorted_problems.unique_violations) == len(expected_violations)
        assert len(sorted_problems.user_warnings) == len(expected_warnings)
        assert len(sorted_problems.user_info) == len(expected_info)
        assert not sorted_problems.unexpected_shacl_validation_components
        assert not result.unexpected_results
        for one_result, expected_e in zip(alphabetically_sorted_violations, expected_violations):
            assert one_result.res_id == expected_e[0]
            assert one_result.problem_type == expected_e[1]
        for one_result, expected_w in zip(alphabetically_sorted_warnings, expected_warnings):
            assert one_result.problem_type == expected_w[1]
            assert one_result.res_id == expected_w[0]
        for one_result, expected_i in zip(alphabetically_sorted_info, expected_info):
            assert one_result.problem_type == expected_i[1]
            assert one_result.res_id == expected_i[0]
        assert not _get_validation_status(sorted_problems, is_on_prod=True)
        assert not _get_validation_status(sorted_problems, is_on_prod=False)


@pytest.mark.usefixtures("create_generic_project")
def test_check_for_unknown_resource_classes(authentication) -> None:
    file = Path("testdata/validate-data/generic/unknown_classes.xml")
    graphs, used_iris, parsed_resources = prepare_data_for_validation_from_file(file, authentication)
    result = _validate_data(graphs, used_iris, parsed_resources, CONFIG)
    assert not result.no_problems
    problems = result.problems
    assert isinstance(problems, UnknownClassesInData)
    expected = {"onto:NonExisting", "unknown:ClassWithEverything", "unknownClass"}
    assert problems.unknown_classes == expected


@pytest.mark.usefixtures("create_generic_project")
def test_reformat_content_violation(authentication) -> None:
    file = Path("testdata/validate-data/generic/content_violation.xml")
    graphs, used_iris, parsed_resources = prepare_data_for_validation_from_file(file, authentication)
    result = _validate_data(graphs, used_iris, parsed_resources, CONFIG)
    msg_end_date_larger_than_start = "The end date must be equal or later than the start date."
    expected_info_tuples = [
        (
            "comment_on_value_empty",
            "onto:testUriValue",
            "The comment on the value must be a non-empty string",
        ),
        (
            "comment_on_value_whitespace",
            "onto:testUriValue",
            "The comment on the value must be a non-empty string",
        ),
        (
            "date_end_day_does_not_exist",
            "onto:testSubDate1",
            "The entered date cannot be parsed into a valid date. It may have issues with the month and/or day number.",
        ),
        (
            "date_end_month_does_not_exist",
            "onto:testSubDate1",
            "The entered date cannot be parsed into a valid date. It may have issues with the month and/or day number.",
        ),
        (
            "date_range_first_is_ce_second_bce",
            "onto:testSubDate1",
            "The start date may not be later than the end date. Please take a look if your eras are correct.",
        ),
        ("date_range_wrong_mixed_precision", "onto:testSubDate1", msg_end_date_larger_than_start),
        ("date_range_wrong_year_full_GREGORIAN", "onto:testSubDate1", msg_end_date_larger_than_start),
        ("date_range_wrong_year_full_ISLAMIC", "onto:testSubDate1", msg_end_date_larger_than_start),
        ("date_range_wrong_year_full_JULIAN", "onto:testSubDate1", msg_end_date_larger_than_start),
        ("date_range_wrong_year_good_month_wrong", "onto:testSubDate1", msg_end_date_larger_than_start),
        ("date_range_wrong_year_month_good_day_wrong", "onto:testSubDate1", msg_end_date_larger_than_start),
        ("date_range_wrong_yyyy", "onto:testSubDate1", msg_end_date_larger_than_start),
        ("date_range_wrong_yyyy_mm", "onto:testSubDate1", msg_end_date_larger_than_start),
        (
            "date_single_month_does_not_exist",
            "onto:testSubDate1",
            "The entered date cannot be parsed into a valid date. It may have issues with the month and/or day number.",
        ),
        (
            "date_single_month_does_not_exist",
            "onto:testSubDate1",
            "The entered date cannot be parsed into a valid date. It may have issues with the month and/or day number.",
        ),
        ("empty_label", "rdfs:label", "The label must be a non-empty string without newlines."),
        ("empty_text_rich", "onto:testRichtext", "The value must be a non-empty string"),
        ("empty_text_simple", "onto:testTextarea", "The value must be a non-empty string"),
        ("geoname_not_number", "onto:testGeoname", "The value must be a valid geoname code"),
        ("label_with_newline", "rdfs:label", "The label must be a non-empty string without newlines."),
        ("link_target_non_existent", "onto:testHasLinkTo", "other"),
        ("link_target_wrong_class", "onto:testHasLinkToCardOneResource", "id_9_target"),
        (
            "list_name_attrib_empty",
            "onto:testListProp",
            (
                "A valid node from the list 'firstList' must be used with this property "
                "(input displayed in format 'listName / NodeName')."
            ),
        ),
        (
            "list_name_non_existent",
            "onto:testListProp",
            (
                "A valid node from the list 'firstList' must be used with this property "
                "(input displayed in format 'listName / NodeName')."
            ),
        ),
        (
            "list_node_non_existent",
            "onto:testListProp",
            (
                "A valid node from the list 'firstList' must be used with this property "
                "(input displayed in format 'listName / NodeName')."
            ),
        ),
        (
            "richtext_standoff_link_nonexistent",
            "hasStandoffLinkTo",
            "non_existing",
        ),
        (
            "simple_text_with_newlines",
            "onto:testSimpleText",
            "The value must be a non-empty string without newlines.",
        ),
        ("text_only_whitespace_simple", "onto:testTextarea", "The value must be a non-empty string"),
        (
            "wrong_list_used",
            "onto:testListProp",
            (
                "A valid node from the list 'firstList' must be used with this property "
                "(input displayed in format 'listName / NodeName')."
            ),
        ),
    ]
    sorted_problems = result.problems
    assert isinstance(sorted_problems, SortedProblems)
    assert len(sorted_problems.unique_violations) == len(expected_info_tuples)
    assert not sorted_problems.user_warnings
    assert not sorted_problems.user_info
    assert not sorted_problems.unexpected_shacl_validation_components
    alphabetically_sorted = sorted(sorted_problems.unique_violations, key=lambda x: str(x.res_id))
    for one_result, expected_info in zip(alphabetically_sorted, expected_info_tuples):
        assert one_result.res_id == expected_info[0]
        assert one_result.prop_name == expected_info[1]
        # depending on the ProblemType, the string we want to test against is in a different parameter
        if one_result.problem_type == ProblemType.INPUT_REGEX:
            assert one_result.expected == expected_info[2]
        elif one_result.problem_type == ProblemType.GENERIC:
            assert one_result.message == expected_info[2]
        elif one_result.problem_type == ProblemType.LINK_TARGET_TYPE_MISMATCH:
            assert one_result.input_value == expected_info[2]
        elif one_result.problem_type == ProblemType.INEXISTENT_LINKED_RESOURCE:
            assert one_result.input_value == expected_info[2]
        else:
            nev: Never = cast(Never, one_result.problem_type)
            assert_never(nev)
    assert not _get_validation_status(sorted_problems, is_on_prod=True)
    assert not _get_validation_status(sorted_problems, is_on_prod=False)


@pytest.mark.usefixtures("create_generic_project")
def test_reformat_cardinality_violation(authentication) -> None:
    file = Path("testdata/validate-data/generic/cardinality_violation.xml")
    graphs, used_iris, parsed_resource = prepare_data_for_validation_from_file(file, authentication)
    result = _validate_data(graphs, used_iris, parsed_resource, CONFIG)
    assert not result.no_problems
    expected_info_tuples = [
        ("id_card_one", ProblemType.MIN_CARD),
        ("id_closed_constraint", ProblemType.NON_EXISTING_CARD),
        ("id_max_card", ProblemType.MAX_CARD),
        ("id_min_card", ProblemType.MIN_CARD),
        ("super_prop_no_card", ProblemType.NON_EXISTING_CARD),
    ]
    sorted_problems = result.problems
    assert isinstance(sorted_problems, SortedProblems)
    assert len(sorted_problems.unique_violations) == len(expected_info_tuples)
    assert not sorted_problems.user_warnings
    assert not sorted_problems.user_info
    assert not sorted_problems.unexpected_shacl_validation_components
    alphabetically_sorted = sorted(sorted_problems.unique_violations, key=lambda x: str(x.res_id))
    for one_result, expected_info in zip(alphabetically_sorted, expected_info_tuples):
        assert one_result.res_id == expected_info[0]
        assert one_result.problem_type == expected_info[1]
    assert not _get_validation_status(sorted_problems, is_on_prod=True)
    assert not _get_validation_status(sorted_problems, is_on_prod=False)


@pytest.mark.usefixtures("create_generic_project")
def test_reformat_value_type_violation(authentication) -> None:
    file = Path("testdata/validate-data/generic/value_type_violation.xml")
    graphs, used_iris, parsed_resource = prepare_data_for_validation_from_file(file, authentication)
    result = _validate_data(graphs, used_iris, parsed_resource, CONFIG)
    assert not result.no_problems
    expected_info_tuples = [
        ("bool_wrong_value_type", "This property requires a BooleanValue", "onto:testBoolean"),
        ("color_wrong_value_type", "This property requires a ColorValue", "onto:testColor"),
        ("date_wrong_value_type", "This property requires a DateValue", "onto:testSubDate1"),
        ("decimal_wrong_value_type", "This property requires a DecimalValue", "onto:testDecimalSimpleText"),
        ("geoname_wrong_value_type", "This property requires a GeonameValue", "onto:testGeoname"),
        ("integer_wrong_value_type", "This property requires a IntValue", "onto:testIntegerSimpleText"),
        ("is_date_should_be_simpletext", "This property requires a TextValue", "onto:testTextarea"),
        ("is_link_should_be_text", "TextValue without formatting", "onto:testTextarea"),
        ("is_text_should_be_integer", "This property requires a IntValue", "onto:testIntegerSpinbox"),
        ("link_wrong_value_type", "This property requires a LinkValue", "onto:testHasLinkTo"),
        ("list_wrong_value_type", "This property requires a ListValue", "onto:testListProp"),
        ("richtext_wrong_value_type", "TextValue with formatting", "onto:testRichtext"),
        ("simpletext_wrong_value_type", "TextValue without formatting", "onto:testTextarea"),
        ("time_wrong_value_type", "This property requires a TimeValue", "onto:testTimeValue"),
        ("uri_wrong_value_type", "This property requires a UriValue", "onto:testUriValue"),
    ]
    sorted_problems = result.problems
    assert isinstance(sorted_problems, SortedProblems)
    assert len(sorted_problems.unique_violations) == len(expected_info_tuples)
    assert not sorted_problems.user_warnings
    assert not sorted_problems.user_info
    assert not sorted_problems.unexpected_shacl_validation_components
    alphabetically_sorted = sorted(sorted_problems.unique_violations, key=lambda x: str(x.res_id))
    for one_result, expected_info in zip(alphabetically_sorted, expected_info_tuples):
        assert one_result.problem_type == ProblemType.VALUE_TYPE_MISMATCH
        assert one_result.res_id == expected_info[0]
        assert one_result.expected == expected_info[1]
        assert one_result.prop_name == expected_info[2]
    assert not _get_validation_status(sorted_problems, is_on_prod=True)
    assert not _get_validation_status(sorted_problems, is_on_prod=False)


@pytest.mark.usefixtures("create_generic_project")
def test_reformat_unique_value_violation(authentication) -> None:
    file = Path("testdata/validate-data/generic/unique_value_violation.xml")
    graphs, used_iris, parsed_resource = prepare_data_for_validation_from_file(file, authentication)
    result = _validate_data(graphs, used_iris, parsed_resource, CONFIG)
    assert not result.no_problems
    expected_ids = [
        "identical_values_LinkValue",
        "identical_values_listNode",
        "identical_values_richtext",
        "identical_values_valueAsString",
        "identical_values_valueHas",
    ]
    sorted_problems = result.problems
    assert isinstance(sorted_problems, SortedProblems)
    assert len(sorted_problems.unique_violations) == len(expected_ids)
    assert not sorted_problems.user_warnings
    assert not sorted_problems.user_info
    assert not sorted_problems.unexpected_shacl_validation_components
    alphabetically_sorted = sorted(sorted_problems.unique_violations, key=lambda x: str(x.res_id))
    for one_result, expected_id in zip(alphabetically_sorted, expected_ids):
        assert one_result.problem_type == ProblemType.DUPLICATE_VALUE
        assert one_result.res_id == expected_id
    assert not _get_validation_status(sorted_problems, is_on_prod=True)
    assert not _get_validation_status(sorted_problems, is_on_prod=False)


@pytest.mark.usefixtures("create_generic_project")
def test_reformat_file_value_violation(authentication) -> None:
    file = Path("testdata/validate-data/generic/file_value_violation.xml")
    graphs, used_iris, parsed_resource = prepare_data_for_validation_from_file(file, authentication)
    result = _validate_data(graphs, used_iris, parsed_resource, CONFIG)
    assert not result.no_problems
    expected_info_violation = [
        ("authorship_with_newline", ProblemType.GENERIC),
        ("copyright_holder_with_newline", ProblemType.GENERIC),
        ("empty_copyright_holder", ProblemType.INPUT_REGEX),
        ("empty_license", ProblemType.GENERIC),
        ("id_archive_missing", ProblemType.FILE_VALUE_MISSING),
        ("id_archive_unknown", ProblemType.FILE_VALUE_MISSING),
        ("id_audio_missing", ProblemType.FILE_VALUE_MISSING),
        ("id_audio_unknown", ProblemType.FILE_VALUE_MISSING),
        ("id_document_missing", ProblemType.FILE_VALUE_MISSING),
        ("id_document_unknown", ProblemType.FILE_VALUE_MISSING),
        ("id_resource_without_representation", ProblemType.FILE_VALUE_PROHIBITED),
        ("id_still_image_missing", ProblemType.FILE_VALUE_MISSING),
        ("id_still_image_unknown", ProblemType.FILE_VALUE_MISSING),
        ("id_text_missing", ProblemType.FILE_VALUE_MISSING),
        ("id_text_unknown", ProblemType.FILE_VALUE_MISSING),
        ("id_video_missing", ProblemType.FILE_VALUE_MISSING),
        ("id_video_unknown", ProblemType.FILE_VALUE_MISSING),
        ("id_wrong_file_type", ProblemType.FILE_VALUE_MISSING),
        ("inexistent_license_iri", ProblemType.GENERIC),
        ("license_not_enabled", ProblemType.GENERIC),
        ("unknown_authorship_id", ProblemType.INPUT_REGEX),
    ]
    sorted_problems = result.problems
    assert isinstance(sorted_problems, SortedProblems)
    alphabetically_sorted_violations = sorted(sorted_problems.unique_violations, key=lambda x: str(x.res_id))
    assert len(sorted_problems.unique_violations) == len(expected_info_violation)
    assert not sorted_problems.user_warnings
    assert not sorted_problems.user_info
    assert not sorted_problems.unexpected_shacl_validation_components
    for one_result, expected_info in zip(alphabetically_sorted_violations, expected_info_violation):
        assert one_result.problem_type == expected_info[1]
        assert one_result.res_id == expected_info[0]
    assert not _get_validation_status(sorted_problems, is_on_prod=True)
    assert not _get_validation_status(sorted_problems, is_on_prod=False)


@pytest.mark.usefixtures("create_generic_project")
def test_reformat_dsp_inbuilt_violation(authentication) -> None:
    file = Path("testdata/validate-data/generic/dsp_inbuilt_violation.xml")
    graphs, used_iris, parsed_resource = prepare_data_for_validation_from_file(file, authentication)
    result = _validate_data(graphs, used_iris, parsed_resource, CONFIG)
    assert not result.no_problems
    expected_info_tuples = [
        ("audio_segment_target_is_video", ProblemType.LINK_TARGET_TYPE_MISMATCH),
        ("audio_segment_target_non_existent", ProblemType.INEXISTENT_LINKED_RESOURCE),
        ("link_obj_target_non_existent", ProblemType.INEXISTENT_LINKED_RESOURCE),
        ("missing_isPartOf", ProblemType.GENERIC),
        ("missing_seqnum", ProblemType.GENERIC),
        ("non_existent_permissions_bitstream", ProblemType.GENERIC),
        ("non_existent_permissions_resource", ProblemType.GENERIC),
        ("non_existent_permissions_value", ProblemType.GENERIC),
        ("region_invalid_geometry", ProblemType.INPUT_REGEX),
        ("region_isRegionOf_resource_does_not_exist", ProblemType.INEXISTENT_LINKED_RESOURCE),
        ("region_isRegionOf_resource_not_a_representation", ProblemType.LINK_TARGET_TYPE_MISMATCH),
        ("target_must_be_a_representation", ProblemType.LINK_TARGET_TYPE_MISMATCH),
        ("target_must_be_an_image_representation", ProblemType.LINK_TARGET_TYPE_MISMATCH),
        ("video_segment_start_larger_than_end", ProblemType.GENERIC),
        ("video_segment_target_is_audio", ProblemType.LINK_TARGET_TYPE_MISMATCH),
        ("video_segment_target_non_existent", ProblemType.INEXISTENT_LINKED_RESOURCE),
        ("video_segment_wrong_bounds", ProblemType.GENERIC),  # once for start that is less than zero
        ("video_segment_wrong_bounds", ProblemType.GENERIC),  # once for the end that is zero
    ]
    sorted_problems = result.problems
    assert isinstance(sorted_problems, SortedProblems)
    assert len(sorted_problems.unique_violations) == len(expected_info_tuples)
    assert not sorted_problems.user_info
    assert not sorted_problems.unexpected_shacl_validation_components
    alphabetically_sorted = sorted(sorted_problems.unique_violations, key=lambda x: str(x.res_id))
    for one_result, expected_info in zip(alphabetically_sorted, expected_info_tuples):
        assert one_result.problem_type == expected_info[1]
        assert one_result.res_id == expected_info[0]
    assert not _get_validation_status(sorted_problems, is_on_prod=True)
    assert not _get_validation_status(sorted_problems, is_on_prod=False)


if __name__ == "__main__":
    pytest.main([__file__])
