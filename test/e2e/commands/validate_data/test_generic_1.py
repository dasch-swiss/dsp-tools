from pathlib import Path
from typing import Iterator

import pytest

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.project.create.project_create import create_project
from dsp_tools.commands.validate_data.api_clients import ShaclValidator
from dsp_tools.commands.validate_data.api_connection import ApiConnection
from dsp_tools.commands.validate_data.models.input_problems import ProblemType
from dsp_tools.commands.validate_data.models.validation import ValidationReportGraphs
from dsp_tools.commands.validate_data.query_validation_result import reformat_validation_graph
from dsp_tools.commands.validate_data.validate_data import _get_parsed_graphs
from dsp_tools.commands.validate_data.validate_data import _get_validation_result
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


class TestCheckConforms:
    @pytest.mark.usefixtures("_create_projects")
    def test_cardinality_correct(self, api_con: ApiConnection, shacl_validator: ShaclValidator) -> None:
        file = Path("testdata/validate-data/generic/cardinality_correct.xml")
        graphs = _get_parsed_graphs(api_con, file)
        cardinality_correct = _get_validation_result(graphs, shacl_validator, None)
        assert cardinality_correct.conforms

    @pytest.mark.usefixtures("_create_projects")
    def test_content_correct(self, api_con: ApiConnection, shacl_validator: ShaclValidator) -> None:
        file = Path("testdata/validate-data/generic/content_correct.xml")
        graphs = _get_parsed_graphs(api_con, file)
        content_correct = _get_validation_result(graphs, shacl_validator, None)
        assert content_correct.conforms

    @pytest.mark.usefixtures("_create_projects")
    def test_minimal_correct(self, api_con: ApiConnection, shacl_validator: ShaclValidator) -> None:
        file = Path("testdata/validate-data/generic/minimal_correct.xml")
        graphs = _get_parsed_graphs(api_con, file)
        minimal_correct = _get_validation_result(graphs, shacl_validator, None)
        assert minimal_correct.conforms

    def test_unique_value_violation(self, unique_value_violation: ValidationReportGraphs) -> None:
        assert not unique_value_violation.conforms

    @pytest.mark.usefixtures("_create_projects")
    def test_file_value_correct(self, api_con: ApiConnection, shacl_validator: ShaclValidator) -> None:
        file = Path("testdata/validate-data/generic/file_value_correct.xml")
        graphs = _get_parsed_graphs(api_con, file)
        file_value_correct = _get_validation_result(graphs, shacl_validator, None)
        assert file_value_correct.conforms

    def test_file_value_cardinality_violation(self, file_value_violation: ValidationReportGraphs) -> None:
        assert not file_value_violation.conforms

    @pytest.mark.usefixtures("_create_projects")
    def test_dsp_inbuilt_correct(self, api_con: ApiConnection, shacl_validator: ShaclValidator) -> None:
        file = Path("testdata/validate-data/generic/dsp_inbuilt_correct.xml")
        graphs = _get_parsed_graphs(api_con, file)
        dsp_inbuilt_correct = _get_validation_result(graphs, shacl_validator, None)
        assert dsp_inbuilt_correct.conforms

    def test_dsp_inbuilt_violation(self, dsp_inbuilt_violation: ValidationReportGraphs) -> None:
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


if __name__ == "__main__":
    pytest.main([__file__])
