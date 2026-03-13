# ruff: noqa: ARG002

from http import HTTPStatus
from unittest.mock import Mock
from unittest.mock import patch

import pytest
from requests import RequestException

from dsp_tools.clients.resource_client_live import ResourceClientLive
from dsp_tools.error.exceptions import BadCredentialsError
from dsp_tools.utils.exceptions import DspToolsRequestException
from dsp_tools.utils.request_utils import ResponseCodeAndText

AUTH = Mock()
AUTH.get_token = Mock(return_value="tkn")

RESOURCE_JSON: dict[str, str] = {"@type": "knora-api:Resource", "rdfs:label": "test"}


@pytest.fixture
def client() -> ResourceClientLive:
    return ResourceClientLive("http://api.com", AUTH)


class TestPostResource:
    @patch("dsp_tools.clients.resource_client_live.log_response")
    @patch("dsp_tools.clients.resource_client_live.log_request")
    def test_ok_returns_iri(self, log_req: Mock, log_resp: Mock, client: ResourceClientLive) -> None:
        mock_response = Mock(status_code=HTTPStatus.OK, ok=True)
        mock_response.json.return_value = {"@id": "http://rdfh.ch/resource/1"}
        with patch.object(client._session, "post", return_value=mock_response):
            result = client.post_resource(RESOURCE_JSON, resource_has_bitstream=False)
        assert result == "http://rdfh.ch/resource/1"

    @patch("dsp_tools.clients.resource_client_live.log_response")
    @patch("dsp_tools.clients.resource_client_live.log_request")
    def test_forbidden_raises_bad_credentials(self, log_req: Mock, log_resp: Mock, client: ResourceClientLive) -> None:
        mock_response = Mock(status_code=HTTPStatus.FORBIDDEN, ok=False)
        with patch.object(client._session, "post", return_value=mock_response):
            with pytest.raises(BadCredentialsError):
                client.post_resource(RESOURCE_JSON, resource_has_bitstream=False)

    @patch("dsp_tools.clients.resource_client_live.log_response")
    @patch("dsp_tools.clients.resource_client_live.log_request")
    def test_non_ok_returns_response_code_and_text(
        self, log_req: Mock, log_resp: Mock, client: ResourceClientLive
    ) -> None:
        mock_response = Mock(status_code=500, ok=False, text="Internal Server Error")
        with patch.object(client._session, "post", return_value=mock_response):
            result = client.post_resource(RESOURCE_JSON, resource_has_bitstream=False)
        assert isinstance(result, ResponseCodeAndText)
        assert result.status_code == 500
        assert result.text == "Internal Server Error"

    @patch("dsp_tools.clients.resource_client_live.log_response")
    @patch("dsp_tools.clients.resource_client_live.log_request")
    def test_request_exception_raises_dsp_tools_exception(
        self, log_req: Mock, log_resp: Mock, client: ResourceClientLive
    ) -> None:
        with patch.object(client._session, "post", side_effect=RequestException("Connection refused")):
            with pytest.raises(DspToolsRequestException):
                client.post_resource(RESOURCE_JSON, resource_has_bitstream=False)

    @patch("dsp_tools.clients.resource_client_live.log_response")
    @patch("dsp_tools.clients.resource_client_live.log_request")
    def test_bitstream_true_adds_header(self, log_req: Mock, log_resp: Mock, client: ResourceClientLive) -> None:
        mock_response = Mock(status_code=HTTPStatus.OK, ok=True)
        mock_response.json.return_value = {"@id": "http://rdfh.ch/resource/1"}
        with patch.object(client._session, "post", return_value=mock_response) as post_mock:
            client.post_resource(RESOURCE_JSON, resource_has_bitstream=True)
        called_headers = post_mock.call_args.kwargs["headers"]
        assert called_headers.get("X-Asset-Ingested") == "true"

    @patch("dsp_tools.clients.resource_client_live.log_response")
    @patch("dsp_tools.clients.resource_client_live.log_request")
    def test_bitstream_false_omits_header(self, log_req: Mock, log_resp: Mock, client: ResourceClientLive) -> None:
        mock_response = Mock(status_code=HTTPStatus.OK, ok=True)
        mock_response.json.return_value = {"@id": "http://rdfh.ch/resource/1"}
        with patch.object(client._session, "post", return_value=mock_response) as post_mock:
            client.post_resource(RESOURCE_JSON, resource_has_bitstream=False)
        called_headers = post_mock.call_args.kwargs["headers"]
        assert "X-Asset-Ingested" not in called_headers
