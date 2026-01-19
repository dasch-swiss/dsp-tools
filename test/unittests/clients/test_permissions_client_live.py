from http import HTTPStatus
from unittest.mock import Mock
from unittest.mock import patch

import pytest
from requests import RequestException

from dsp_tools.clients.exceptions import FatalNonOkApiResponseCode
from dsp_tools.clients.permissions_client_live import PermissionsClientLive
from dsp_tools.error.exceptions import BadCredentialsError
from dsp_tools.utils.exceptions import DspToolsRequestException

AUTH = Mock()
AUTH.get_token = Mock(return_value="tkn")
AUTH.server = "http://0.0.0.0:3333"


class TestGetProjectDoaps:
    @patch("dsp_tools.clients.permissions_client_live.log_response")
    @patch("dsp_tools.clients.permissions_client_live.log_request")
    @patch("dsp_tools.clients.permissions_client_live.requests.get")
    def test_success(self, get_mock: Mock, log_request: Mock, log_response: Mock) -> None:  # noqa: ARG002
        client = PermissionsClientLive(
            server="http://0.0.0.0:3333",
            auth=AUTH,
            project_iri="http://rdfh.ch/projects/test",
        )
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"default_object_access_permissions": [{"id": "doap1"}, {"id": "doap2"}]}
        get_mock.return_value = mock_response

        result = client.get_project_doaps()

        assert result == [{"id": "doap1"}, {"id": "doap2"}]
        get_mock.assert_called_once()

    @patch("dsp_tools.clients.permissions_client_live.log_response")
    @patch("dsp_tools.clients.permissions_client_live.log_request")
    @patch("dsp_tools.clients.permissions_client_live.requests.get")
    def test_forbidden(self, get_mock: Mock, log_request: Mock, log_response: Mock) -> None:  # noqa: ARG002
        client = PermissionsClientLive(
            server="http://0.0.0.0:3333",
            auth=AUTH,
            project_iri="http://rdfh.ch/projects/test",
        )
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = HTTPStatus.FORBIDDEN
        get_mock.return_value = mock_response

        with pytest.raises(BadCredentialsError) as exc_info:
            client.get_project_doaps()
        assert "permission" in str(exc_info.value).lower()

    @patch("dsp_tools.clients.permissions_client_live.log_response")
    @patch("dsp_tools.clients.permissions_client_live.log_request")
    @patch("dsp_tools.clients.permissions_client_live.requests.get")
    def test_other_error(self, get_mock: Mock, log_request: Mock, log_response: Mock) -> None:  # noqa: ARG002
        client = PermissionsClientLive(
            server="http://0.0.0.0:3333",
            auth=AUTH,
            project_iri="http://rdfh.ch/projects/test",
        )
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 500
        mock_response.text = "Internal error"
        get_mock.return_value = mock_response

        with pytest.raises(FatalNonOkApiResponseCode):
            client.get_project_doaps()

    @patch("dsp_tools.clients.permissions_client_live.log_request")
    @patch("dsp_tools.clients.permissions_client_live.requests.get")
    def test_request_exception(self, get_mock: Mock, log_request: Mock) -> None:  # noqa: ARG002
        client = PermissionsClientLive(
            server="http://0.0.0.0:3333",
            auth=AUTH,
            project_iri="http://rdfh.ch/projects/test",
        )
        get_mock.side_effect = RequestException("Connection error")

        with pytest.raises(DspToolsRequestException):
            client.get_project_doaps()


class TestDeleteDoap:
    @patch("dsp_tools.clients.permissions_client_live.log_response")
    @patch("dsp_tools.clients.permissions_client_live.log_request")
    @patch("dsp_tools.clients.permissions_client_live.requests.delete")
    def test_success(self, delete_mock: Mock, log_request: Mock, log_response: Mock) -> None:  # noqa: ARG002
        client = PermissionsClientLive(
            server="http://0.0.0.0:3333",
            auth=AUTH,
            project_iri="http://rdfh.ch/projects/test",
        )
        mock_response = Mock()
        mock_response.ok = True
        delete_mock.return_value = mock_response
        result = client.delete_doap("http://test.iri/doap")
        delete_mock.assert_called_once()
        assert result is True

    @patch("dsp_tools.clients.permissions_client_live.log_response")
    @patch("dsp_tools.clients.permissions_client_live.log_request")
    @patch("dsp_tools.clients.permissions_client_live.requests.delete")
    def test_forbidden(self, delete_mock: Mock, log_request: Mock, log_response: Mock) -> None:  # noqa: ARG002
        client = PermissionsClientLive(
            server="http://0.0.0.0:3333",
            auth=AUTH,
            project_iri="http://rdfh.ch/projects/test",
        )
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = HTTPStatus.FORBIDDEN
        delete_mock.return_value = mock_response
        with pytest.raises(BadCredentialsError):
            client.delete_doap("http://test.iri/doap")

    @patch("dsp_tools.clients.permissions_client_live.log_response")
    @patch("dsp_tools.clients.permissions_client_live.log_request")
    @patch("dsp_tools.clients.permissions_client_live.requests.delete")
    def test_other_error(self, delete_mock: Mock, log_request: Mock, log_response: Mock) -> None:  # noqa: ARG002
        client = PermissionsClientLive(
            server="http://0.0.0.0:3333",
            auth=AUTH,
            project_iri="http://rdfh.ch/projects/test",
        )
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_response.text = "Not found"
        delete_mock.return_value = mock_response
        result = client.delete_doap("http://test.iri/doap")
        assert result is False

    @patch("dsp_tools.clients.permissions_client_live.log_request")
    @patch("dsp_tools.clients.permissions_client_live.requests.delete")
    def test_request_exception(self, delete_mock: Mock, log_request: Mock) -> None:  # noqa: ARG002
        client = PermissionsClientLive(
            server="http://0.0.0.0:3333",
            auth=AUTH,
            project_iri="http://rdfh.ch/projects/test",
        )
        delete_mock.side_effect = RequestException("Connection error")
        with pytest.raises(DspToolsRequestException):
            client.delete_doap("http://test.iri/doap")


class TestCreateNewDoap:
    @patch("dsp_tools.clients.permissions_client_live.log_response")
    @patch("dsp_tools.clients.permissions_client_live.log_request")
    @patch("dsp_tools.clients.permissions_client_live.requests.post")
    def test_success(self, post_mock: Mock, log_request: Mock, log_response: Mock) -> None:  # noqa: ARG002
        client = PermissionsClientLive(
            server="http://0.0.0.0:3333",
            auth=AUTH,
            project_iri="http://rdfh.ch/projects/test",
        )
        mock_response = Mock()
        mock_response.ok = True
        post_mock.return_value = mock_response
        result = client.create_new_doap({"forProject": "http://rdfh.ch/projects/test"})
        assert result is True
        post_mock.assert_called_once()

    @patch("dsp_tools.clients.permissions_client_live.log_response")
    @patch("dsp_tools.clients.permissions_client_live.log_request")
    @patch("dsp_tools.clients.permissions_client_live.requests.post")
    def test_forbidden(self, post_mock: Mock, log_request: Mock, log_response: Mock) -> None:  # noqa: ARG002
        client = PermissionsClientLive(
            server="http://0.0.0.0:3333",
            auth=AUTH,
            project_iri="http://rdfh.ch/projects/test",
        )
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = HTTPStatus.FORBIDDEN
        post_mock.return_value = mock_response

        with pytest.raises(BadCredentialsError):
            client.create_new_doap({"forProject": "http://rdfh.ch/projects/test"})

    @patch("dsp_tools.clients.permissions_client_live.log_response")
    @patch("dsp_tools.clients.permissions_client_live.log_request")
    @patch("dsp_tools.clients.permissions_client_live.requests.post")
    def test_other_error(self, post_mock: Mock, log_request: Mock, log_response: Mock) -> None:  # noqa: ARG002
        client = PermissionsClientLive(
            server="http://0.0.0.0:3333",
            auth=AUTH,
            project_iri="http://rdfh.ch/projects/test",
        )
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 400
        mock_response.text = "Bad request"
        post_mock.return_value = mock_response

        with pytest.raises(FatalNonOkApiResponseCode):
            client.create_new_doap({"forProject": "http://rdfh.ch/projects/test"})

    @patch("dsp_tools.clients.permissions_client_live.log_request")
    @patch("dsp_tools.clients.permissions_client_live.requests.post")
    def test_request_exception(self, post_mock: Mock, log_request: Mock) -> None:  # noqa: ARG002
        client = PermissionsClientLive(
            server="http://0.0.0.0:3333",
            auth=AUTH,
            project_iri="http://rdfh.ch/projects/test",
        )
        post_mock.side_effect = RequestException("Connection error")
        with pytest.raises(DspToolsRequestException):
            client.create_new_doap({"forProject": "http://rdfh.ch/projects/test"})
