# mypy: disable-error-code="no-untyped-def"

from http import HTTPStatus
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from dsp_tools.commands.create.create_on_server.ontology import _create_one_ontology
from dsp_tools.commands.create.create_on_server.ontology import _should_retry_request
from dsp_tools.commands.create.create_on_server.ontology import create_all_ontologies
from dsp_tools.commands.create.models.create_problems import CollectedProblems
from dsp_tools.commands.create.models.create_problems import UploadProblem
from dsp_tools.commands.create.models.create_problems import UploadProblemType
from dsp_tools.commands.create.models.parsed_ontology import ParsedOntology
from dsp_tools.utils.request_utils import ResponseCodeAndText
from test.unittests.commands.create.constants import PROJECT_IRI


@pytest.fixture
def onto_1():
    return ParsedOntology(
        name="test-onto", label="Test Ontology", comment="A test ontology", classes=[], properties=[], cardinalities=[]
    )


@pytest.fixture
def onto_2():
    return ParsedOntology(
        name="test-onto-2", label="Test Ontology 2", comment=None, classes=[], properties=[], cardinalities=[]
    )


class TestShouldRetryRequest:
    def test_bad_request_without_matching_pattern_returns_false(self):
        response = ResponseCodeAndText(status_code=HTTPStatus.BAD_REQUEST, text="Invalid ontology definition")
        assert _should_retry_request(response) is False

    def test_internal_server_error_returns_true(self):
        response = ResponseCodeAndText(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, text="Server error")
        assert _should_retry_request(response) is True


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
    @patch("dsp_tools.commands.create.create_on_server.ontology._should_retry_request")
    def test_success_after_retry(self, mock_should_retry, mock_serialise, onto_1):
        mock_client = MagicMock()
        first_response = ResponseCodeAndText(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, text="Server error")
        mock_client.post_new_ontology.side_effect = [first_response, None]
        mock_serialise.return_value = {"@graph": []}
        mock_should_retry.return_value = True
        result = _create_one_ontology(onto_1, PROJECT_IRI, mock_client)
        assert result is None
        assert mock_client.post_new_ontology.call_count == 2
        mock_should_retry.assert_called_once_with(first_response)

    @patch("dsp_tools.commands.create.create_on_server.ontology.serialise_ontology_graph_for_request")
    @patch("dsp_tools.commands.create.create_on_server.ontology._should_retry_request")
    def test_failure_after_retry(self, mock_should_retry, mock_serialise, onto_1):
        mock_client = MagicMock()
        first_response = ResponseCodeAndText(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, text="Server error 1")
        second_response = ResponseCodeAndText(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, text="Server error 2")
        mock_client.post_new_ontology.side_effect = [first_response, second_response]
        mock_serialise.return_value = {"@graph": []}
        mock_should_retry.return_value = True
        result = _create_one_ontology(onto_1, PROJECT_IRI, mock_client)
        assert isinstance(result, UploadProblem)
        assert result.problem == UploadProblemType.ONTOLOGY_COULD_NOT_BE_CREATED
        assert result.problematic_object == second_response.text
        assert mock_client.post_new_ontology.call_count == 2

    @patch("dsp_tools.commands.create.create_on_server.ontology.serialise_ontology_graph_for_request")
    @patch("dsp_tools.commands.create.create_on_server.ontology._should_retry_request")
    def test_non_retryable_failure(self, mock_should_retry, mock_serialise, onto_1):
        mock_client = MagicMock()
        error_text = "Invalid ontology definition"
        response = ResponseCodeAndText(status_code=HTTPStatus.BAD_REQUEST, text=error_text)
        mock_client.post_new_ontology.return_value = response
        mock_serialise.return_value = {"@graph": []}
        mock_should_retry.return_value = False
        result = _create_one_ontology(onto_1, PROJECT_IRI, mock_client)
        assert isinstance(result, UploadProblem)
        assert result.problem == UploadProblemType.ONTOLOGY_COULD_NOT_BE_CREATED
        assert result.problematic_object == error_text
        mock_client.post_new_ontology.assert_called_once()


class TestCreateAllOntologies:
    @patch("dsp_tools.commands.create.create_on_server.ontology._create_one_ontology")
    def test_all_ontologies_succeed(self, mock_create_one, onto_1, onto_2):
        ontologies = [onto_1, onto_2]
        mock_create_one.return_value = None
        mock_client = MagicMock()
        result = create_all_ontologies(ontologies, PROJECT_IRI, mock_client)
        assert result is None
        assert mock_create_one.call_count == 2

    @patch("dsp_tools.commands.create.create_on_server.ontology._create_one_ontology")
    def test_all_ontologies_fail(self, mock_create_one, onto_1, onto_2):
        ontologies = [onto_1, onto_2]
        problem1 = UploadProblem("Error 1", UploadProblemType.ONTOLOGY_COULD_NOT_BE_CREATED)
        problem2 = UploadProblem("Error 2", UploadProblemType.ONTOLOGY_COULD_NOT_BE_CREATED)
        mock_create_one.side_effect = [problem1, problem2]
        mock_client = MagicMock()
        result = create_all_ontologies(ontologies, PROJECT_IRI, mock_client)
        assert isinstance(result, CollectedProblems)
        assert len(result.problems) == 2

    @patch("dsp_tools.commands.create.create_on_server.ontology._create_one_ontology")
    def test_some_ontologies_fail(self, mock_create_one, onto_1, onto_2):
        ontology3 = ParsedOntology(
            name="test-onto-3", label="Test Ontology 3", comment=None, classes=[], properties=[], cardinalities=[]
        )
        ontologies = [onto_1, onto_2, ontology3]
        problem = UploadProblem("Error", UploadProblemType.ONTOLOGY_COULD_NOT_BE_CREATED)
        mock_create_one.side_effect = [None, problem, None]
        mock_client = MagicMock()
        result = create_all_ontologies(ontologies, PROJECT_IRI, mock_client)
        assert isinstance(result, CollectedProblems)
        assert len(result.problems) == 1
