# mypy: disable-error-code="method-assign,no-untyped-def"
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from dsp_tools.models.exceptions import BadCredentialsError
from dsp_tools.models.exceptions import BaseError
from dsp_tools.utils.legal_info_client_live import HTTP_INSUFFICIENT_CREDENTIALS
from dsp_tools.utils.legal_info_client_live import LegalInfoClientLive
from dsp_tools.utils.request_utils import RequestParameters

AUTH = Mock()


class TestPostCopyrightHolders:
    @patch("dsp_tools.utils.legal_info_client_live.log_response")
    @patch("dsp_tools.utils.legal_info_client_live.log_request")
    def test_client_post_copyright_holders_ok(self, log_request: Mock, log_response: Mock):  # noqa: ARG002
        client = LegalInfoClientLive("http://api.com", "9999", AUTH)
        params = RequestParameters(
            method="POST",
            url="http://api.com/admin/projects/shortcode/9999/legal-info/copyright-holders",
            data={"data": ["1"]},
            timeout=60,
        )
        with patch("dsp_tools.utils.legal_info_client_live.requests.post") as post_mock:
            post_mock.return_value = Mock(status_code=200, ok=True)
            response = client._post_and_log_request("copyright-holders", ["1"])
        assert response.status_code == 200
        assert response.ok
        log_request_call_params = log_request.call_args_list[0].args[0]
        assert isinstance(log_request_call_params, RequestParameters)
        del log_request_call_params.headers
        assert log_request_call_params == params

    def test_client_post_copyright_holders_insufficient_credentials(self):
        client = LegalInfoClientLive("http://api.com", "9999", AUTH)
        expected_response = Mock(status_code=HTTP_INSUFFICIENT_CREDENTIALS, ok=False)
        client._post_and_log_request = Mock(return_value=expected_response)
        with pytest.raises(BadCredentialsError):
            client.post_copyright_holders(["1"])

    def test_client_post_copyright_holders_unknown_status_code(self):
        client = LegalInfoClientLive("http://api.com", "9999", AUTH)
        expected_response = Mock(status_code=10000, ok=False)
        client._post_and_log_request = Mock(return_value=expected_response)
        with pytest.raises(BaseError):
            client.post_copyright_holders(["1"])
