from pathlib import Path
from typing import Iterator
from typing import Never
from typing import assert_never
from typing import cast

import pytest
from rdflib import BNode
from rdflib import URIRef

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.project.create.project_create_all import create_project
from dsp_tools.commands.validate_data.api_clients import ShaclValidator
from dsp_tools.commands.validate_data.api_connection import ApiConnection
from dsp_tools.commands.validate_data.get_user_validation_message import _filter_out_duplicate_problems
from dsp_tools.commands.validate_data.models.input_problems import ProblemType
from dsp_tools.commands.validate_data.models.validation import DetailBaseInfo
from dsp_tools.commands.validate_data.models.validation import ValidationReportGraphs
from dsp_tools.commands.validate_data.query_validation_result import _extract_base_info_of_resource_results
from dsp_tools.commands.validate_data.query_validation_result import reformat_validation_graph
from dsp_tools.commands.validate_data.validate_data import _get_parsed_graphs
from dsp_tools.commands.validate_data.validate_data import _get_validation_result
from dsp_tools.models.custom_warnings import DspToolsUserWarning
from test.e2e.setup_testcontainers.ports import ExternalContainerPorts
from test.e2e.setup_testcontainers.setup import get_containers


@pytest.fixture(scope="module")
def container_ports() -> Iterator[ExternalContainerPorts]:
    with get_containers() as metadata:
        yield metadata.ports


@pytest.fixture(scope="module")
def creds(container_ports: ExternalContainerPorts) -> ServerCredentials:
    return ServerCredentials(
        "root@example.com",
        "test",
        f"http://0.0.0.0:{container_ports.api}",
        f"http://0.0.0.0:{container_ports.ingest}",
    )


@pytest.fixture(scope="module")
def _create_projects(creds: ServerCredentials) -> None:
    assert create_project(Path("testdata/validate-data/generic/project.json"), creds)


@pytest.fixture(scope="module")
def api_con(container_ports: ExternalContainerPorts) -> ApiConnection:
    return ApiConnection(f"http://0.0.0.0:{container_ports.api}")


@pytest.fixture(scope="module")
def shacl_validator(api_con: ApiConnection) -> ShaclValidator:
    return ShaclValidator(api_con)


@pytest.fixture(scope="module")
def unique_value_violation(
    _create_projects: Iterator[None], api_con: ApiConnection, shacl_validator: ShaclValidator
) -> ValidationReportGraphs:
    file = Path("testdata/validate-data/generic/unique_value_violation.xml")
    graphs = _get_parsed_graphs(api_con, file)
    return _get_validation_result(graphs, shacl_validator, None)


@pytest.fixture(scope="module")
def file_value_violation(
    _create_projects: Iterator[None], api_con: ApiConnection, shacl_validator: ShaclValidator
) -> ValidationReportGraphs:
    file = Path("testdata/validate-data/generic/file_value_violation.xml")
    graphs = _get_parsed_graphs(api_con, file)
    return _get_validation_result(graphs, shacl_validator, None)


@pytest.fixture(scope="module")
def dsp_inbuilt_violation(
    _create_projects: Iterator[None], api_con: ApiConnection, shacl_validator: ShaclValidator
) -> ValidationReportGraphs:
    file = Path("testdata/validate-data/generic/dsp_inbuilt_violation.xml")
    graphs = _get_parsed_graphs(api_con, file)
    return _get_validation_result(graphs, shacl_validator, None)


@pytest.fixture(scope="module")
def cardinality_violation(
    _create_projects: Iterator[None], api_con: ApiConnection, shacl_validator: ShaclValidator
) -> ValidationReportGraphs:
    file = Path("testdata/validate-data/generic/cardinality_violation.xml")
    graphs = _get_parsed_graphs(api_con, file)
    return _get_validation_result(graphs, shacl_validator, None)


@pytest.fixture(scope="module")
def content_violation(
    _create_projects: Iterator[None], api_con: ApiConnection, shacl_validator: ShaclValidator
) -> ValidationReportGraphs:
    file = Path("testdata/validate-data/generic/content_violation.xml")
    graphs = _get_parsed_graphs(api_con, file)
    return _get_validation_result(graphs, shacl_validator, None)


@pytest.fixture(scope="module")
def value_type_violation(
    _create_projects: Iterator[None], api_con: ApiConnection, shacl_validator: ShaclValidator
) -> ValidationReportGraphs:
    file = Path("testdata/validate-data/generic/value_type_violation.xml")
    match = r"Angular brackets in the format of <text> were found in text properties with encoding=utf8"
    with pytest.warns(DspToolsUserWarning, match=match):
        graphs = _get_parsed_graphs(api_con, file)
    return _get_validation_result(graphs, shacl_validator, None)


@pytest.fixture(scope="module")
def every_violation_combination_once(
    _create_projects: Iterator[None], api_con: ApiConnection, shacl_validator: ShaclValidator
) -> ValidationReportGraphs:
    file = Path("testdata/validate-data/generic/every_violation_combination_once.xml")
    graphs = _get_parsed_graphs(api_con, file)
    return _get_validation_result(graphs, shacl_validator, None)


def test_cardinality_violation(cardinality_violation: ValidationReportGraphs) -> None:
    assert not cardinality_violation.conforms


def test_reformat_cardinality_violation(cardinality_violation: ValidationReportGraphs) -> None:
    result = reformat_validation_graph(cardinality_violation)
    expected_info_tuples = [
        ("id_card_one", ProblemType.MIN_CARD),
        ("id_closed_constraint", ProblemType.NON_EXISTING_CARD),
        ("id_max_card", ProblemType.MAX_CARD),
        ("id_min_card", ProblemType.MIN_CARD),
        ("super_prop_no_card", ProblemType.NON_EXISTING_CARD),
    ]
    assert not result.unexpected_results
    assert len(result.problems) == len(expected_info_tuples)
    sorted_problems = sorted(result.problems, key=lambda x: x.res_id)
    for one_result, expected_info in zip(sorted_problems, expected_info_tuples):
        assert one_result.res_id == expected_info[0]
        assert one_result.problem_type == expected_info[1]


def test_content_violation(content_violation: ValidationReportGraphs) -> None:
    assert not content_violation.conforms


def test_reformat_content_violation(content_violation: ValidationReportGraphs) -> None:
    result = reformat_validation_graph(content_violation)
    assert not result.unexpected_results
    sorted_problems = sorted(result.problems, key=lambda x: x.res_id)
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
        ("empty_label", "rdfs:label", "The label must be a non-empty string"),
        ("empty_text_rich", "onto:testRichtext", "The value must be a non-empty string"),
        ("empty_text_simple", "onto:testTextarea", "The value must be a non-empty string"),
        ("geoname_not_number", "onto:testGeoname", "The value must be a valid geoname code"),
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
            "A stand-off link must target an existing resource.",
        ),
        ("text_only_whitespace_simple", "onto:testTextarea", "The value must be a non-empty string"),
    ]
    assert len(result.problems) == len(expected_info_tuples)
    for one_result, expected_info in zip(sorted_problems, expected_info_tuples):
        assert one_result.res_id == expected_info[0]
        assert one_result.prop_name == expected_info[1]
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


def test_value_type_violation(value_type_violation: ValidationReportGraphs) -> None:
    assert not value_type_violation.conforms


def test_reformat_value_type_violation(value_type_violation: ValidationReportGraphs) -> None:
    result = reformat_validation_graph(value_type_violation)
    assert not result.unexpected_results
    # "is_link_should_be_text" gives two types of validation errors, this function removes the duplicates
    filtered_problems = _filter_out_duplicate_problems(result.problems)
    flattened_problems = [item for sublist in filtered_problems for item in sublist]
    sorted_problems = sorted(flattened_problems, key=lambda x: x.res_id)
    expected_info_tuples = [
        ("bool_wrong_value_type", "This property requires a BooleanValue", "onto:testBoolean"),
        ("color_wrong_value_type", "This property requires a ColorValue", "onto:testColor"),
        ("date_wrong_value_type", "This property requires a DateValue", "onto:testSubDate1"),
        ("decimal_wrong_value_type", "This property requires a DecimalValue", "onto:testDecimalSimpleText"),
        ("geoname_wrong_value_type", "This property requires a GeonameValue", "onto:testGeoname"),
        ("integer_wrong_value_type", "This property requires a IntValue", "onto:testIntegerSimpleText"),
        ("is_date_should_be_simpletext", "This property requires a TextValue", "onto:testTextarea"),
        ("is_link_should_be_integer", "This property requires a IntValue", "onto:testIntegerSpinbox"),
        ("is_link_should_be_text", "TextValue without formatting", "onto:testTextarea"),
        ("link_wrong_value_type", "This property requires a LinkValue", "onto:testHasLinkTo"),
        ("list_wrong_value_type", "This property requires a ListValue", "onto:testListProp"),
        ("richtext_wrong_value_type", "TextValue with formatting", "onto:testRichtext"),
        ("simpletext_wrong_value_type", "TextValue without formatting", "onto:testTextarea"),
        ("time_wrong_value_type", "This property requires a TimeValue", "onto:testTimeValue"),
        ("uri_wrong_value_type", "This property requires a UriValue", "onto:testUriValue"),
    ]
    assert len(sorted_problems) == len(expected_info_tuples)
    for one_result, expected_info in zip(sorted_problems, expected_info_tuples):
        assert one_result.problem_type == ProblemType.VALUE_TYPE_MISMATCH
        assert one_result.res_id == expected_info[0]
        assert one_result.expected == expected_info[1]
        assert one_result.prop_name == expected_info[2]


def test_unique_value_violation(unique_value_violation: ValidationReportGraphs) -> None:
    assert not unique_value_violation.conforms


def test_file_value_cardinality_violation(file_value_violation: ValidationReportGraphs) -> None:
    assert not file_value_violation.conforms


def test_dsp_inbuilt_violation(dsp_inbuilt_violation: ValidationReportGraphs) -> None:
    assert not dsp_inbuilt_violation.conforms


class TestReformatValidationGraph:
    def test_reformat_unique_value_violation(self, unique_value_violation: ValidationReportGraphs) -> None:
        result = reformat_validation_graph(unique_value_violation)
        expected_ids = [
            "identical_values_LinkValue",
            "identical_values_listNode",
            "identical_values_valueAsString",
            "identical_values_valueHas",
        ]
        assert not result.unexpected_results
        assert len(result.problems) == len(expected_ids)
        sorted_problems = sorted(result.problems, key=lambda x: x.res_id)
        for one_result, expected_id in zip(sorted_problems, expected_ids):
            assert one_result.problem_type == ProblemType.DUPLICATE_VALUE
            assert one_result.res_id == expected_id

    def test_reformat_file_value_violation(self, file_value_violation: ValidationReportGraphs) -> None:
        result = reformat_validation_graph(file_value_violation)
        expected_info_tuples = [
            # each type of missing legal info (authorship, copyright, license) produces one violation
            ("bitstream_no_legal_info", ProblemType.GENERIC),
            ("bitstream_no_legal_info", ProblemType.GENERIC),
            ("bitstream_no_legal_info", ProblemType.GENERIC),
            ("empty_license", ProblemType.GENERIC),
            ("id_archive_missing", ProblemType.FILE_VALUE),
            ("id_archive_unknown", ProblemType.FILE_VALUE),
            ("id_audio_missing", ProblemType.FILE_VALUE),
            ("id_audio_unknown", ProblemType.FILE_VALUE),
            ("id_document_missing", ProblemType.FILE_VALUE),
            ("id_document_unknown", ProblemType.FILE_VALUE),
            ("id_resource_without_representation", ProblemType.FILE_VALUE_PROHIBITED),
            ("id_still_image_missing", ProblemType.FILE_VALUE),
            ("id_still_image_unknown", ProblemType.FILE_VALUE),
            ("id_text_missing", ProblemType.FILE_VALUE),
            ("id_text_unknown", ProblemType.FILE_VALUE),
            ("id_video_missing", ProblemType.FILE_VALUE),
            ("id_video_unknown", ProblemType.FILE_VALUE),
            ("id_wrong_file_type", ProblemType.FILE_VALUE),
            ("iiif_no_legal_info", ProblemType.GENERIC),
            ("iiif_no_legal_info", ProblemType.GENERIC),
            ("iiif_no_legal_info", ProblemType.GENERIC),
            ("image_no_legal_info", ProblemType.GENERIC),
            ("image_no_legal_info", ProblemType.GENERIC),
            ("image_no_legal_info", ProblemType.GENERIC),
            ("inexistent_license_iri", ProblemType.GENERIC),
        ]
        assert not result.unexpected_results
        assert len(result.problems) == len(expected_info_tuples)
        sorted_problems = sorted(result.problems, key=lambda x: x.res_id)
        for one_result, expected_info in zip(sorted_problems, expected_info_tuples):
            assert one_result.problem_type == expected_info[1]
            assert one_result.res_id == expected_info[0]

    def test_reformat_dsp_inbuilt_violation(self, dsp_inbuilt_violation: ValidationReportGraphs) -> None:
        result = reformat_validation_graph(dsp_inbuilt_violation)
        expected_info_tuples = [
            ("audio_segment_target_is_video", ProblemType.LINK_TARGET_TYPE_MISMATCH),
            ("audio_segment_target_non_existent", ProblemType.INEXISTENT_LINKED_RESOURCE),
            ("link_obj_target_non_existent", ProblemType.INEXISTENT_LINKED_RESOURCE),
            ("missing_isPartOf", ProblemType.GENERIC),
            ("missing_seqnum", ProblemType.GENERIC),
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
        assert not result.unexpected_results
        assert len(result.problems) == len(expected_info_tuples)
        sorted_problems = sorted(result.problems, key=lambda x: x.res_id)
        for one_result, expected_info in zip(sorted_problems, expected_info_tuples):
            assert one_result.problem_type == expected_info[1]
            assert one_result.res_id == expected_info[0]


def test_extract_identifiers_of_resource_results(every_violation_combination_once: ValidationReportGraphs) -> None:
    report_and_onto = every_violation_combination_once.validation_graph + every_violation_combination_once.onto_graph
    data_and_onto = every_violation_combination_once.data_graph + every_violation_combination_once.onto_graph
    result = _extract_base_info_of_resource_results(report_and_onto, data_and_onto)
    result_sorted = sorted(result, key=lambda x: str(x.focus_node_iri))
    expected_iris = [
        (URIRef("http://data/bitstream_no_legal_info"), None),
        (URIRef("http://data/bitstream_no_legal_info"), None),
        (URIRef("http://data/bitstream_no_legal_info"), None),
        (URIRef("http://data/empty_label"), None),
        (URIRef("http://data/geoname_not_number"), None),
        (URIRef("http://data/id_card_one"), None),
        (URIRef("http://data/id_closed_constraint"), None),
        (URIRef("http://data/id_max_card"), None),
        (URIRef("http://data/id_missing_file_value"), None),
        (URIRef("http://data/identical_values"), None),
        (URIRef("http://data/image_no_legal_info"), None),
        (URIRef("http://data/image_no_legal_info"), None),
        (URIRef("http://data/image_no_legal_info"), None),
        (URIRef("http://data/inexistent_license_iri"), None),
        (URIRef("http://data/link_target_non_existent"), BNode),
        (URIRef("http://data/link_target_wrong_class"), BNode),
        (URIRef("http://data/list_node_non_existent"), BNode),
        (URIRef("http://data/missing_seqnum"), None),
        (URIRef("http://data/richtext_standoff_link_nonexistent"), None),
        (URIRef("http://data/simpletext_wrong_value_type"), BNode),
        (URIRef("http://data/uri_wrong_value_type"), None),
        (URIRef("http://data/video_segment_start_larger_than_end"), None),
        (URIRef("http://data/video_segment_wrong_bounds"), None),
        (URIRef("http://data/video_segment_wrong_bounds"), None),
    ]
    assert len(result) == len(expected_iris)
    for result_info, expected_iri in zip(result_sorted, expected_iris):
        assert result_info.focus_node_iri == expected_iri[0]
        if expected_iri[1] is None:
            assert not result_info.detail
        else:
            detail_base_info = result_info.detail
            assert isinstance(detail_base_info, DetailBaseInfo)
            assert isinstance(detail_base_info.detail_bn, expected_iri[1])


def test_every_violation_combination_once(every_violation_combination_once: ValidationReportGraphs) -> None:
    assert not every_violation_combination_once.conforms


def test_reformat_every_constraint_once(every_violation_combination_once: ValidationReportGraphs) -> None:
    result = reformat_validation_graph(every_violation_combination_once)
    expected_info_tuples = [
        ("bitstream_no_legal_info", ProblemType.GENERIC),
        ("bitstream_no_legal_info", ProblemType.GENERIC),
        ("bitstream_no_legal_info", ProblemType.GENERIC),
        ("empty_label", ProblemType.INPUT_REGEX),
        ("geoname_not_number", ProblemType.INPUT_REGEX),
        ("id_card_one", ProblemType.MIN_CARD),
        ("id_closed_constraint", ProblemType.NON_EXISTING_CARD),
        ("id_max_card", ProblemType.MAX_CARD),
        ("id_missing_file_value", ProblemType.FILE_VALUE),
        ("identical_values", ProblemType.DUPLICATE_VALUE),
        ("image_no_legal_info", ProblemType.GENERIC),
        ("image_no_legal_info", ProblemType.GENERIC),
        ("image_no_legal_info", ProblemType.GENERIC),
        ("inexistent_license_iri", ProblemType.GENERIC),
        ("link_target_non_existent", ProblemType.INEXISTENT_LINKED_RESOURCE),
        ("link_target_wrong_class", ProblemType.LINK_TARGET_TYPE_MISMATCH),
        ("list_node_non_existent", ProblemType.GENERIC),
        ("missing_seqnum", ProblemType.GENERIC),
        ("richtext_standoff_link_nonexistent", ProblemType.GENERIC),
        ("simpletext_wrong_value_type", ProblemType.VALUE_TYPE_MISMATCH),
        ("uri_wrong_value_type", ProblemType.VALUE_TYPE_MISMATCH),
        ("video_segment_start_larger_than_end", ProblemType.GENERIC),
        ("video_segment_wrong_bounds", ProblemType.GENERIC),  # once for start that is less than zero
        ("video_segment_wrong_bounds", ProblemType.GENERIC),  # once for the end that is zero
    ]
    assert not result.unexpected_results
    sorted_problems = sorted(result.problems, key=lambda x: x.res_id)
    assert len(result.problems) == len(expected_info_tuples)
    for one_result, expected_info in zip(sorted_problems, expected_info_tuples):
        assert one_result.res_id == expected_info[0]
        assert one_result.problem_type == expected_info[1]


if __name__ == "__main__":
    pytest.main([__file__])
