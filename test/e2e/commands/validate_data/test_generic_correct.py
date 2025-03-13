from pathlib import Path
from typing import Iterator

import pytest
from rdflib import BNode
from rdflib import URIRef

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.project.create.project_create import create_project
from dsp_tools.commands.validate_data.api_clients import ShaclValidator
from dsp_tools.commands.validate_data.api_connection import ApiConnection
from dsp_tools.commands.validate_data.models.input_problems import ProblemType
from dsp_tools.commands.validate_data.models.input_problems import UnknownClassesInData
from dsp_tools.commands.validate_data.models.validation import DetailBaseInfo
from dsp_tools.commands.validate_data.models.validation import RDFGraphs
from dsp_tools.commands.validate_data.models.validation import ValidationReportGraphs
from dsp_tools.commands.validate_data.query_validation_result import _extract_base_info_of_resource_results
from dsp_tools.commands.validate_data.query_validation_result import reformat_validation_graph
from dsp_tools.commands.validate_data.validate_data import _check_for_unknown_resource_classes
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
def api_con(container_ports: ExternalContainerPorts) -> ApiConnection:
    return ApiConnection(f"http://0.0.0.0:{container_ports.api}")


@pytest.fixture(scope="module")
def shacl_validator(api_con: ApiConnection) -> ShaclValidator:
    return ShaclValidator(api_con)


@pytest.fixture(scope="module")
def _create_projects(creds: ServerCredentials) -> None:
    assert create_project(Path("testdata/validate-data/generic/project.json"), creds)


@pytest.fixture(scope="module")
def unknown_classes_graphs(_create_projects: Iterator[None], api_con: ApiConnection) -> RDFGraphs:
    file = Path("testdata/validate-data/generic/unknown_classes.xml")
    return _get_parsed_graphs(api_con, file)


@pytest.fixture(scope="module")
def every_combination_once(
    _create_projects: Iterator[None], api_con: ApiConnection, shacl_validator: ShaclValidator
) -> ValidationReportGraphs:
    file = Path("testdata/validate-data/generic/every_combination_once.xml")
    graphs = _get_parsed_graphs(api_con, file)
    return _get_validation_result(graphs, shacl_validator, None)


def test_check_for_unknown_resource_classes(unknown_classes_graphs: RDFGraphs) -> None:
    result = _check_for_unknown_resource_classes(unknown_classes_graphs)
    assert isinstance(result, UnknownClassesInData)
    expected = {"onto:NonExisting", "unknown:ClassWithEverything", "unknownClass"}
    assert result.unknown_classes == expected


def test_extract_identifiers_of_resource_results(every_combination_once: ValidationReportGraphs) -> None:
    report_and_onto = every_combination_once.validation_graph + every_combination_once.onto_graph
    data_and_onto = every_combination_once.data_graph + every_combination_once.onto_graph
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


def test_every_combination_once(every_combination_once: ValidationReportGraphs) -> None:
    assert not every_combination_once.conforms


def test_reformat_every_constraint_once(every_combination_once: ValidationReportGraphs) -> None:
    result = reformat_validation_graph(every_combination_once)
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

    @pytest.mark.usefixtures("_create_projects")
    def test_file_value_correct(self, api_con: ApiConnection, shacl_validator: ShaclValidator) -> None:
        file = Path("testdata/validate-data/generic/file_value_correct.xml")
        graphs = _get_parsed_graphs(api_con, file)
        file_value_correct = _get_validation_result(graphs, shacl_validator, None)
        assert file_value_correct.conforms

    @pytest.mark.usefixtures("_create_projects")
    def test_dsp_inbuilt_correct(self, api_con: ApiConnection, shacl_validator: ShaclValidator) -> None:
        file = Path("testdata/validate-data/generic/dsp_inbuilt_correct.xml")
        graphs = _get_parsed_graphs(api_con, file)
        dsp_inbuilt_correct = _get_validation_result(graphs, shacl_validator, None)
        assert dsp_inbuilt_correct.conforms
