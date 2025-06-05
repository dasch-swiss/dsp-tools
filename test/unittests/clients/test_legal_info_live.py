# mypy: disable-error-code="method-assign,no-untyped-def"
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from dsp_tools.clients.legal_info_client_live import HTTP_LACKING_PERMISSIONS
from dsp_tools.clients.legal_info_client_live import LegalInfoClientLive
from dsp_tools.clients.legal_info_client_live import _is_last_page
from dsp_tools.error.exceptions import BadCredentialsError
from dsp_tools.error.exceptions import BaseError
from dsp_tools.utils.request_utils import RequestParameters

AUTH = Mock()
AUTH.get_token = Mock(return_value="tkn")


LICENSE_1 = {
    "id": "http://rdfh.ch/1",
    "uri": "https://uri.org/1",
    "labelEn": "label 1",
    "isRecommended": True,
    "isEnabled": True,
}

LICENSE_2 = {
    "id": "http://rdfh.ch/2",
    "uri": "https://uri.org/2",
    "labelEn": "label 2",
    "isRecommended": True,
    "isEnabled": True,
}

DATA_PAGE_1_OF_1 = {
    "data": [
        LICENSE_1,
    ],
    "pagination": {"pageSize": 1, "totalItems": 1, "totalPages": 1, "currentPage": 1},
}

PAGE_1_OF_2 = {"data": [LICENSE_1], "pagination": {"pageSize": 1, "totalItems": 2, "totalPages": 2, "currentPage": 1}}

PAGE_2_OF_2 = {"data": [LICENSE_2], "pagination": {"pageSize": 1, "totalItems": 2, "totalPages": 2, "currentPage": 2}}


class TestPostCopyrightHolders:
    @patch("dsp_tools.clients.legal_info_client_live.log_response")
    @patch("dsp_tools.clients.legal_info_client_live.log_request")
    def test_log_request(self, log_request: Mock, log_response: Mock):  # noqa: ARG002
        client = LegalInfoClientLive("http://api.com", "9999", AUTH)
        params = RequestParameters(
            method="POST",
            url="http://api.com/admin/projects/shortcode/9999/legal-info/copyright-holders",
            data={"data": ["1"]},
            timeout=60,
        )
        with patch("dsp_tools.clients.legal_info_client_live.requests.post") as post_mock:
            post_mock.return_value = Mock(status_code=200, ok=True)
            response = client._post_and_log_request("copyright-holders", ["1"])
        assert response.status_code == 200
        assert response.ok
        log_request_call_params = log_request.call_args_list[0].args[0]
        assert isinstance(log_request_call_params, RequestParameters)
        del log_request_call_params.headers
        assert log_request_call_params == params

    @patch("dsp_tools.clients.legal_info_client_live.log_response")
    @patch("dsp_tools.clients.legal_info_client_live.log_request")
    def test_post_ok(self, log_request: Mock, log_response: Mock):  # noqa: ARG002
        client = LegalInfoClientLive("http://api.com", "9999", AUTH)
        params = RequestParameters(
            method="POST",
            url="http://api.com/admin/projects/shortcode/9999/legal-info/copyright-holders",
            data={"data": ["1"]},
            timeout=60,
            headers={"Content-Type": "application/json", "Authorization": "Bearer tkn"},
        )
        with patch("dsp_tools.clients.legal_info_client_live.requests.post") as post_mock:
            post_mock.return_value = Mock(status_code=200, ok=True)
            client._post_and_log_request("copyright-holders", ["1"])
            post_mock.assert_called_once_with(
                url=params.url, headers=params.headers, data=params.data_serialized, timeout=params.timeout
            )

    def test_client_post_copyright_holders_lacking_permissions(self):
        client = LegalInfoClientLive("http://api.com", "9999", AUTH)
        expected_response = Mock(status_code=HTTP_LACKING_PERMISSIONS, ok=False)
        client._post_and_log_request = Mock(return_value=expected_response)
        with pytest.raises(BadCredentialsError):
            client.post_copyright_holders(["1"])

    def test_client_post_copyright_holders_unknown_status_code(self):
        client = LegalInfoClientLive("http://api.com", "9999", AUTH)
        expected_response = Mock(status_code=404, ok=False)
        client._post_and_log_request = Mock(return_value=expected_response)
        with pytest.raises(BaseError):
            client.post_copyright_holders(["1"])


class TestGetEnabledLicenses:
    def test_get_enabled_license_page(self):
        client = LegalInfoClientLive("http://api.com", "9999", AUTH)
        first_response = Mock(status_code=200, ok=True)
        first_response.json.return_value = PAGE_1_OF_2
        second_response = Mock(status_code=200, ok=True)
        second_response.json.return_value = PAGE_2_OF_2
        with patch.object(
            LegalInfoClientLive,
            attribute="_get_one_license_page",
            side_effect=[first_response, second_response],
        ):
            response = client.get_licenses_of_a_project()
            assert response == [LICENSE_1, LICENSE_2]

    def test_get_enabled_license_page_no_license(self):
        client = LegalInfoClientLive("http://api.com", "9999", AUTH)
        get_mock = Mock(
            status_code=200,
            ok=True,
        )
        get_mock.json.return_value = {
            "data": [],
            "pagination": {"pageSize": 0, "totalItems": 0, "totalPages": 1, "currentPage": 1},
        }
        with patch.object(
            LegalInfoClientLive,
            attribute="_get_one_license_page",
            side_effect=[get_mock],
        ):
            response = client.get_licenses_of_a_project(enabled_only=True)
            assert response == []

    @patch("dsp_tools.clients.legal_info_client_live.log_response")
    @patch("dsp_tools.clients.legal_info_client_live.log_request")
    def test_get_one_license_page(self, log_request: Mock, log_response: Mock):  # noqa: ARG002
        client = LegalInfoClientLive("http://api.com", "9999", AUTH)
        params = RequestParameters(
            method="GET",
            url="http://api.com/admin/projects/shortcode/9999/legal-info/licenses?page=1&page-size=25&order=Asc&showOnlyEnabled=true",
            timeout=60,
            headers={"Content-Type": "application/json", "Authorization": "Bearer tkn"},
        )
        with patch("dsp_tools.clients.legal_info_client_live.requests.get") as get_mock:
            mock_response = Mock(status_code=200, ok=True)
            mock_response.json.return_value = DATA_PAGE_1_OF_1
            get_mock.return_value = mock_response
            response = client._get_one_license_page(page_num=1, enabled_only=True)
            get_mock.assert_called_once_with(url=params.url, headers=params.headers, timeout=params.timeout)
        assert response.json() == DATA_PAGE_1_OF_1

    def test_insufficient_credentials(self):
        client = LegalInfoClientLive("http://api.com", "9999", AUTH)
        mock_response = Mock(status_code=HTTP_LACKING_PERMISSIONS, ok=False)
        mock_response.json.return_value = {}
        mock_response.headers = {}
        with patch("dsp_tools.clients.legal_info_client_live.requests.get") as get_mock:
            get_mock.return_value = mock_response
            with pytest.raises(BadCredentialsError):
                client._get_one_license_page(page_num=1, enabled_only=True)

    def test_unknown_status_code(self):
        client = LegalInfoClientLive("http://api.com", "9999", AUTH)
        mock_response = Mock(status_code=404, ok=False)
        mock_response.json.return_value = {}
        mock_response.headers = {}
        with patch("dsp_tools.clients.legal_info_client_live.requests.get") as get_mock:
            get_mock.return_value = mock_response
            with pytest.raises(BaseError):
                client._get_one_license_page(page_num=1, enabled_only=True)


def test_is_last_page_no():
    assert not _is_last_page(PAGE_1_OF_2)


def test_is_last_page_yes():
    assert _is_last_page(DATA_PAGE_1_OF_1)
