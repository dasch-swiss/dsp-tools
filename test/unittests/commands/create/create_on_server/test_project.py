

from http import HTTPStatus
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from dsp_tools.clients.exceptions import ProjectNotFoundError
from dsp_tools.commands.create.create_on_server.project import create_project
from dsp_tools.commands.create.exceptions import UnableToCreateProjectError
from dsp_tools.commands.create.models.parsed_project import ParsedProjectMetadata
from dsp_tools.utils.request_utils import ResponseCodeAndText
from test.unittests.commands.create.constants import PROJECT_IRI

NEW_PROJECT_IRI = "http://rdfh.ch/projects/newProjectIRI"

DO_NOT_EXIST_IF_EXISTS = False


@pytest.fixture
def mock_auth() -> Mock:
    auth = Mock()
    auth.server = "http://0.0.0.0:3333"
    return auth


@pytest.fixture
def parsed_project() -> Mock:
    project = Mock(spec=ParsedProjectMetadata)
    project.shortcode = "9999"
    project.shortname = "name"
    return project


@pytest.fixture
def serialized_project() -> dict[str, str]:
    return {"shortcode": "9999", "shortname": "test-project"}


@patch("dsp_tools.commands.create.create_on_server.project.ProjectClientLive")
@patch("builtins.input")
def test_project_exists_user_continues(
    mock_input: Mock,
    mock_client_class: Mock,
    mock_auth: Mock,
    parsed_project: Mock,
):
    mock_client = Mock()
    mock_client.get_project_iri.return_value = PROJECT_IRI
    mock_client_class.return_value = mock_client
    mock_input.return_value = "y"

    result = create_project(parsed_project, mock_auth, DO_NOT_EXIST_IF_EXISTS)

    assert result == PROJECT_IRI
    mock_client_class.assert_called_once_with(mock_auth.server, mock_auth)
    mock_client.get_project_iri.assert_called_once_with(parsed_project.shortcode)


@patch("dsp_tools.commands.create.create_on_server.project.ProjectClientLive")
@patch("dsp_tools.commands.create.create_on_server.project.sys.exit")
def test_project_exit_through_flag(
    mock_exit: Mock,
    mock_client_class: Mock,
    mock_auth: Mock,
    parsed_project: Mock,
):
    mock_client = Mock()
    mock_client.get_project_iri.return_value = PROJECT_IRI
    mock_client_class.return_value = mock_client
    mock_exit.side_effect = SystemExit(0)

    with pytest.raises(SystemExit):
        create_project(parsed_project, mock_auth, True)

    mock_client_class.assert_called_once_with(mock_auth.server, mock_auth)
    mock_client.get_project_iri.assert_called_once_with(parsed_project.shortcode)
    mock_exit.assert_called_once_with(0)


@patch("dsp_tools.commands.create.create_on_server.project.ProjectClientLive")
@patch("dsp_tools.commands.create.create_on_server.project.sys.exit")
@patch("builtins.input")
def test_project_exists_user_exits(
    mock_input: Mock,
    mock_exit: Mock,
    mock_client_class: Mock,
    mock_auth: Mock,
    parsed_project: Mock,
):
    mock_client = Mock()
    mock_client.get_project_iri.return_value = PROJECT_IRI
    mock_client_class.return_value = mock_client
    mock_input.return_value = "n"
    mock_exit.side_effect = SystemExit(1)

    with pytest.raises(SystemExit):
        create_project(parsed_project, mock_auth, DO_NOT_EXIST_IF_EXISTS)

    mock_client_class.assert_called_once_with(mock_auth.server, mock_auth)
    mock_client.get_project_iri.assert_called_once_with(parsed_project.shortcode)
    mock_exit.assert_called_once_with(1)


@patch("dsp_tools.commands.create.create_on_server.project.ProjectClientLive")
@patch("dsp_tools.commands.create.create_on_server.project.serialise_project")
def test_project_does_not_exist_successful_creation(
    mock_serialise: Mock,
    mock_client_class: Mock,
    mock_auth: Mock,
    parsed_project: Mock,
    serialized_project: dict[str, str],
):
    mock_client = Mock()
    mock_client.get_project_iri.side_effect = ProjectNotFoundError("Project not found")
    mock_client.post_new_project.return_value = NEW_PROJECT_IRI
    mock_client_class.return_value = mock_client
    mock_serialise.return_value = serialized_project

    result = create_project(parsed_project, mock_auth, DO_NOT_EXIST_IF_EXISTS)

    assert result == NEW_PROJECT_IRI
    mock_client_class.assert_called_once_with(mock_auth.server, mock_auth)
    mock_client.get_project_iri.assert_called_once_with(parsed_project.shortcode)
    mock_serialise.assert_called_once_with(parsed_project)
    mock_client.post_new_project.assert_called_once_with(serialized_project)


@patch("dsp_tools.commands.create.create_on_server.project.ProjectClientLive")
@patch("dsp_tools.commands.create.create_on_server.project.serialise_project")
@patch("dsp_tools.commands.create.create_on_server.project.is_server_error")
def test_project_does_not_exist_server_error(
    mock_is_server_error: Mock,
    mock_serialise: Mock,
    mock_client_class: Mock,
    mock_auth: Mock,
    parsed_project: Mock,
    serialized_project: dict[str, str],
):
    mock_client = Mock()
    mock_client.get_project_iri.side_effect = ProjectNotFoundError("Project not found")
    error_response = ResponseCodeAndText(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, text="Internal Server Error")
    mock_client.post_new_project.return_value = error_response
    mock_client_class.return_value = mock_client
    mock_serialise.return_value = serialized_project
    mock_is_server_error.return_value = True

    with pytest.raises(UnableToCreateProjectError):
        create_project(parsed_project, mock_auth, DO_NOT_EXIST_IF_EXISTS)

    mock_client_class.assert_called_once_with(mock_auth.server, mock_auth)
    mock_client.get_project_iri.assert_called_once_with(parsed_project.shortcode)
    mock_serialise.assert_called_once_with(parsed_project)
    mock_client.post_new_project.assert_called_once_with(serialized_project)
    mock_is_server_error.assert_called_once_with(error_response)


@patch("dsp_tools.commands.create.create_on_server.project.ProjectClientLive")
@patch("dsp_tools.commands.create.create_on_server.project.serialise_project")
@patch("dsp_tools.commands.create.create_on_server.project.is_server_error")
def test_project_does_not_exist_client_error(
    mock_is_server_error: Mock,
    mock_serialise: Mock,
    mock_client_class: Mock,
    mock_auth: Mock,
    parsed_project: Mock,
    serialized_project: dict[str, str],
):
    mock_client = Mock()
    mock_client.get_project_iri.side_effect = ProjectNotFoundError("Project not found")
    error_response = ResponseCodeAndText(status_code=HTTPStatus.BAD_REQUEST, text="Bad Request")
    mock_client.post_new_project.return_value = error_response
    mock_client_class.return_value = mock_client
    mock_serialise.return_value = serialized_project
    mock_is_server_error.return_value = False

    with pytest.raises(UnableToCreateProjectError):
        create_project(parsed_project, mock_auth, DO_NOT_EXIST_IF_EXISTS)

    mock_client_class.assert_called_once_with(mock_auth.server, mock_auth)
    mock_client.get_project_iri.assert_called_once_with(parsed_project.shortcode)
    mock_serialise.assert_called_once_with(parsed_project)
    mock_client.post_new_project.assert_called_once_with(serialized_project)
    mock_is_server_error.assert_called_once_with(error_response)
