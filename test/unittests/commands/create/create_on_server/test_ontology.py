# mypy: disable-error-code="no-untyped-def"

from http import HTTPStatus
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from dsp_tools.commands.create.create_on_server.ontology import _create_one_ontology
from dsp_tools.commands.create.create_on_server.ontology import create_all_ontologies
from dsp_tools.commands.create.models.create_problems import CollectedProblems
from dsp_tools.commands.create.models.create_problems import UploadProblem
from dsp_tools.commands.create.models.create_problems import UploadProblemType
from dsp_tools.commands.create.models.parsed_ontology import ParsedOntology
from dsp_tools.commands.create.models.server_project_info import ProjectIriLookup
from dsp_tools.utils.request_utils import ResponseCodeAndText
from test.unittests.commands.create.constants import PROJECT_IRI

ONTO_1_IRI = "http://0.0.0.0:3333/ontology/9999/onto-1/v2"
ONTO_2_IRI = "http://0.0.0.0:3333/ontology/9999/onto-2/v2"


@pytest.fixture
def onto_1():
    return ParsedOntology(
        name="onto-1", label="Test Ontology", comment="A test ontology", classes=[], properties=[], cardinalities=[]
    )


@pytest.fixture
def onto_2():
    return ParsedOntology(
        name="onto-2", label="Test Ontology 2", comment=None, classes=[], properties=[], cardinalities=[]
    )


class TestCreateOneOntology:
    @patch("dsp_tools.commands.create.create_on_server.ontology.serialise_ontology_graph_for_request")
    def test_success_on_first_attempt(self, mock_serialise, onto_1):
        mock_client = MagicMock()
        mock_client.post_new_ontology.return_value = None
        mock_serialise.return_value = {"@graph": []}
        result = _create_one_ontology(onto_1, PROJECT_IRI, mock_client)
        assert result is None
        mock_client.post_new_ontology.assert_called_once()

    @patch("dsp_tools.commands.create.create_on_server.ontology.serialise_ontology_graph_for_request")
    @patch("dsp_tools.commands.create.create_on_server.ontology.is_server_error")
    def test_success_after_retry(self, mock_is_server_error, mock_serialise, onto_1):
        mock_client = MagicMock()
        first_response = ResponseCodeAndText(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, text="Server error")
        mock_client.post_new_ontology.side_effect = [first_response, None]
        mock_serialise.return_value = {"@graph": []}
        mock_is_server_error.return_value = True
        result = _create_one_ontology(onto_1, PROJECT_IRI, mock_client)
        assert result is None
        assert mock_client.post_new_ontology.call_count == 2
        mock_is_server_error.assert_called_once_with(first_response)

    @patch("dsp_tools.commands.create.create_on_server.ontology.serialise_ontology_graph_for_request")
    @patch("dsp_tools.commands.create.create_on_server.ontology.is_server_error")
    def test_failure_after_retry(self, mock_is_server_error, mock_serialise, onto_1):
        mock_client = MagicMock()
        first_response = ResponseCodeAndText(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, text="Server error 1")
        second_response = ResponseCodeAndText(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, text="Server error 2")
        mock_client.post_new_ontology.side_effect = [first_response, second_response]
        mock_serialise.return_value = {"@graph": []}
        mock_is_server_error.return_value = True
        result = _create_one_ontology(onto_1, PROJECT_IRI, mock_client)
        assert isinstance(result, UploadProblem)
        assert result.problem == UploadProblemType.ONTOLOGY_COULD_NOT_BE_CREATED
        assert result.problematic_object == second_response.text
        assert mock_client.post_new_ontology.call_count == 2

    @patch("dsp_tools.commands.create.create_on_server.ontology.serialise_ontology_graph_for_request")
    @patch("dsp_tools.commands.create.create_on_server.ontology.is_server_error")
    def test_non_retryable_failure(self, mock_is_server_error, mock_serialise, onto_1):
        mock_client = MagicMock()
        error_text = "Invalid ontology definition"
        response = ResponseCodeAndText(status_code=HTTPStatus.BAD_REQUEST, text=error_text)
        mock_client.post_new_ontology.return_value = response
        mock_serialise.return_value = {"@graph": []}
        mock_is_server_error.return_value = False
        result = _create_one_ontology(onto_1, PROJECT_IRI, mock_client)
        assert isinstance(result, UploadProblem)
        assert result.problem == UploadProblemType.ONTOLOGY_COULD_NOT_BE_CREATED
        assert result.problematic_object == error_text
        mock_client.post_new_ontology.assert_called_once()


class TestCreateAllOntologies:
    @patch("dsp_tools.commands.create.create_on_server.ontology._create_one_ontology")
    def test_all_ontologies_succeed(self, mock_create_one, onto_1, onto_2):
        project_lookup = ProjectIriLookup(PROJECT_IRI)
        ontologies = [onto_1, onto_2]
        mock_create_one.side_effect = [ONTO_1_IRI, ONTO_2_IRI]
        mock_client = MagicMock()
        result_lookup, problems = create_all_ontologies(ontologies, project_lookup, mock_client)
        assert problems is None
        assert mock_create_one.call_count == 2
        expected_lookup = {onto_1.name: ONTO_1_IRI, onto_2.name: ONTO_2_IRI}
        assert result_lookup.onto_iris == expected_lookup

    @patch("dsp_tools.commands.create.create_on_server.ontology._create_one_ontology")
    def test_all_ontologies_fail(self, mock_create_one, onto_1, onto_2):
        project_lookup = ProjectIriLookup(PROJECT_IRI)
        ontologies = [onto_1, onto_2]
        problem1 = UploadProblem(onto_1.name, UploadProblemType.ONTOLOGY_COULD_NOT_BE_CREATED)
        problem2 = UploadProblem(onto_2.name, UploadProblemType.ONTOLOGY_COULD_NOT_BE_CREATED)
        mock_create_one.side_effect = [problem1, problem2]
        mock_client = MagicMock()
        result_lookup, problems = create_all_ontologies(ontologies, project_lookup, mock_client)
        assert isinstance(problems, CollectedProblems)
        assert len(problems.problems) == 2
        assert result_lookup.onto_iris == {}

    @patch("dsp_tools.commands.create.create_on_server.ontology._create_one_ontology")
    def test_some_ontologies_fail(self, mock_create_one, onto_1, onto_2):
        project_lookup = ProjectIriLookup(PROJECT_IRI)
        ontologies = [onto_1, onto_2]
        problem = UploadProblem(onto_2.name, UploadProblemType.ONTOLOGY_COULD_NOT_BE_CREATED)
        mock_create_one.side_effect = [ONTO_1_IRI, problem]
        mock_client = MagicMock()
        result_lookup, problems = create_all_ontologies(ontologies, project_lookup, mock_client)
        assert isinstance(problems, CollectedProblems)
        assert len(problems.problems) == 1
        assert problems.problems[0].problematic_object == onto_2.name
        assert result_lookup.onto_iris == {onto_1.name: ONTO_1_IRI}
