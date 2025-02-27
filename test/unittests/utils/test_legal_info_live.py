# mypy: disable-error-code="method-assign,no-untyped-def"
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from dsp_tools.models.exceptions import BadCredentialsError
from dsp_tools.models.exceptions import BaseError
from dsp_tools.utils.legal_info_client_live import HTTP_INSUFFICIENT_CREDENTIALS
from dsp_tools.utils.legal_info_client_live import LegalInfoClientLive
from dsp_tools.utils.legal_info_client_live import _segment_data
from dsp_tools.utils.request_utils import RequestParameters

AUTH = Mock()


class TestPostCopyrightHolders:
    @patch("dsp_tools.utils.legal_info_client_live.log_request")
    @patch("dsp_tools.utils.legal_info_client_live.log_response")
    def test_client_post_copyright_holders_ok(self, log_request: Mock, log_response: Mock):
        client = LegalInfoClientLive("http://api.com", "9999", AUTH)
        expected_response = Mock(status_code=200, ok=True)
        client._post_and_log_request = Mock(return_value=expected_response)
        params = RequestParameters(
            method="POST",
            url="http://api.com/admin/projects/shortcode/9999/copyright-holders",
            data={"data": ["1"]},
            timeout=60,
        )

        client._post_and_log_request("copyright-holders", ["1"])
        log_request.assert_called_once_with(params)
        log_response.assert_called_once_with(expected_response)

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


def test_segment_data_more_than_limit():
    data_list = [str(x) for x in range(203)]
    result = _segment_data(data_list)
    assert len(result) == 3
    assert result[0][0] == "0"
    assert result[0][-1] == "99"
    assert result[1][0] == "100"
    assert result[1][-1] == "199"
    assert result[2][0] == "200"
    assert result[2][-1] == "202"


def test_segment_data_less_than_limit():
    data_list = [str(x) for x in range(4)]
    result = _segment_data(data_list)
    assert len(result) == 1
    assert len(result[0]) == 4
