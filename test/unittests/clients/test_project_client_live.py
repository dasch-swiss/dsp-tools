# mypy: disable-error-code="no-untyped-def"

from http import HTTPStatus
from typing import Any
from unittest.mock import Mock
from unittest.mock import patch

import pytest
import requests

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.project_client_live import ProjectClientLive
from dsp_tools.error.exceptions import BadCredentialsError
from dsp_tools.error.exceptions import DspToolsRequestException
from dsp_tools.error.exceptions import FatalNonOkApiResponseCode
from dsp_tools.error.exceptions import ProjectNotFoundError
from dsp_tools.utils.request_utils import ResponseCodeAndText


@pytest.fixture
def api_url() -> str:
    return "http://0.0.0.0:3333"


@pytest.fixture
def mock_auth_client() -> Mock:
    mock = Mock(spec=AuthenticationClient)
    mock.server = "http://0.0.0.0:3333"
    mock.get_token.return_value = "test-token-123"
    return mock


@pytest.fixture
def project_client(api_url: str, mock_auth_client) -> ProjectClientLive:
    return ProjectClientLive(server=api_url, auth=mock_auth_client)


@pytest.fixture
def project_info() -> dict[str, Any]:
    return {
        "shortcode": "0003",
        "shortname": "test-proj",
        "longname": "Long Project Name",
        "description": [{"value": "project description", "language": "en"}],
        "keywords": ["Test"],
        "status": True,
        "selfjoin": False,
    }


class TestProjectGetIri:
    def test_get_project_iri_success(self, project_client: ProjectClientLive) -> None:
        mock_response = Mock(status_code=200, ok=True, headers={})
        mock_response.json.return_value = {
            "project": {
                "id": "http://rdfh.ch/projects/0001",
                "shortcode": "0001",
                "shortname": "test-project",
            }
        }
        with patch("dsp_tools.clients.project_client_live.requests.get", return_value=mock_response) as mock_get:
            result = project_client.get_project_iri("0001")
        assert result == "http://rdfh.ch/projects/0001"
        assert mock_get.call_args[0][0] == f"{project_client.server}/admin/projects/shortcode/0001"

    def test_get_project_iri_not_found(self, project_client: ProjectClientLive) -> None:
        mock_response = Mock(status_code=404, ok=False, headers={}, text="")
        mock_response.json.return_value = {}
        with patch("dsp_tools.clients.project_client_live.requests.get", return_value=mock_response):
            with pytest.raises(ProjectNotFoundError):
                project_client.get_project_iri("9999")

    def test_get_project_iri_timeout(self, project_client: ProjectClientLive) -> None:
        with patch("dsp_tools.clients.project_client_live.requests.get", side_effect=requests.ReadTimeout("Timeout")):
            with pytest.raises(DspToolsRequestException):
                project_client.get_project_iri("0001")

    def test_get_project_iri_other_error(self, project_client: ProjectClientLive) -> None:
        mock_response = Mock(status_code=500, ok=False, headers={}, text="Internal Server Error")
        mock_response.json.return_value = {}
        with patch("dsp_tools.clients.project_client_live.requests.get", return_value=mock_response):
            with pytest.raises(FatalNonOkApiResponseCode):
                project_client.get_project_iri("0001")


class TestPostNewProject:
    def test_good(self, project_client: ProjectClientLive, project_info: dict[str, Any]) -> None:
        mock_response = Mock(status_code=HTTPStatus.OK.value, ok=True, headers={})
        mock_response.json.return_value = {
            "project": {
                "id": "http://rdfh.ch/projects/0003",
                "shortcode": "0003",
                "shortname": "test-proj",
            }
        }
        with patch("dsp_tools.clients.project_client_live.requests.post", return_value=mock_response) as mock_post:
            result = project_client.post_new_project(project_info)
        assert result == "http://rdfh.ch/projects/0003"
        assert mock_post.call_args.args[0] == f"{project_client.server}/admin/projects"

    def test_exception(self, project_client: ProjectClientLive, project_info: dict[str, Any]) -> None:
        with patch("dsp_tools.clients.project_client_live.requests.post", side_effect=requests.ReadTimeout("Timeout")):
            with pytest.raises(DspToolsRequestException):
                project_client.post_new_project(project_info)

    def test_bad_credentials(self, project_client: ProjectClientLive, project_info: dict[str, Any]) -> None:
        mock_response = Mock(status_code=HTTPStatus.FORBIDDEN.value, ok=False, headers={}, text="Forbidden")
        mock_response.json.return_value = {}
        with patch("dsp_tools.clients.project_client_live.requests.post", return_value=mock_response):
            with pytest.raises(BadCredentialsError):
                project_client.post_new_project(project_info)

    def test_non_ok(self, project_client: ProjectClientLive, project_info: dict[str, Any]) -> None:
        mock_response = Mock(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value, ok=False, headers={}, text="Internal Server Error"
        )
        mock_response.json.return_value = {}
        with patch("dsp_tools.clients.project_client_live.requests.post", return_value=mock_response):
            result = project_client.post_new_project(project_info)
        assert isinstance(result, ResponseCodeAndText)
        assert result.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert result.text == "Internal Server Error"


if __name__ == "__main__":
    pytest.main([__file__])
