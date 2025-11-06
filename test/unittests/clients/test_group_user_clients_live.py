from unittest.mock import Mock
from unittest.mock import patch

import pytest
import requests

from dsp_tools.clients.group_user_clients_live import GroupClientLive
from dsp_tools.error.exceptions import BadCredentialsError
from dsp_tools.error.exceptions import DspToolsRequestException
from dsp_tools.error.exceptions import FatalNonOkApiResponseCode

from dsp_tools.error.custom_warnings import DspToolsUnexpectedStatusCodeWarning

@pytest.fixture
def api_url() -> str:
    return "http://0.0.0.0:3333"


@pytest.fixture
def group_client(api_url: str) -> GroupClientLive:
    return GroupClientLive(api_url=api_url)


class TestGroupClientLive:
    def test_get_all_groups_success(self, group_client: GroupClientLive) -> None:
        mock_response = Mock(status_code=200, ok=True, headers={})
        mock_response.json.return_value = {
            "groups": [
                {
                    "id": "http://rdfh.ch/groups/4123/K6tppNTITqGY1nLvxdDL9A",
                    "name": "testgroupEditors",
                    "descriptions": [],
                    "project": {
                        "id": "http://rdfh.ch/projects/DPCEKkIjTYe9ApkgwBTWeg",
                        "shortname": "systematic-tp",
                    },
                },
                {
                    "id": "http://rdfh.ch/groups/4123/anotherGroupId",
                    "name": "testgroupReaders",
                    "descriptions": [],
                    "project": {
                        "id": "http://rdfh.ch/projects/anotherProject",
                        "shortname": "another-project",
                    },
                },
            ]
        }
        with patch("dsp_tools.clients.group_user_clients_live.requests.get", return_value=mock_response) as mock_get:
            result = group_client.get_all_groups()

        assert len(result) == 2
        assert result[0]["name"] == "testgroupEditors"
        assert result[0]["id"] == "http://rdfh.ch/groups/4123/K6tppNTITqGY1nLvxdDL9A"
        assert result[1]["name"] == "testgroupReaders"
        assert mock_get.call_args[0][0] == f"{group_client.api_url}/admin/groups"

    def test_get_all_groups_empty(self, group_client: GroupClientLive) -> None:
        mock_response = Mock(status_code=200, ok=True, headers={})
        mock_response.json.return_value = {"groups": []}
        with patch("dsp_tools.clients.group_user_clients_live.requests.get", return_value=mock_response):
            result = group_client.get_all_groups()

        assert result == []

    def test_get_all_groups_timeout(self, group_client: GroupClientLive) -> None:
        with patch(
            "dsp_tools.clients.group_user_clients_live.requests.get", side_effect=requests.ReadTimeout("Timeout")
        ):
            with pytest.raises(DspToolsRequestException):
                group_client.get_all_groups()

    def test_get_all_groups_server_error(self, group_client: GroupClientLive) -> None:
        mock_response = Mock(status_code=500, ok=False, headers={}, text="Internal Server Error")
        mock_response.json.return_value = {}
        with patch("dsp_tools.clients.group_user_clients_live.requests.get", return_value=mock_response):
            with pytest.raises(FatalNonOkApiResponseCode):
                group_client.get_all_groups()

    def test_get_all_groups_connection_error(self, group_client: GroupClientLive) -> None:
        with patch(
            "dsp_tools.clients.group_user_clients_live.requests.get",
            side_effect=requests.ConnectionError("Connection failed"),
        ):
            with pytest.raises(DspToolsRequestException):
                group_client.get_all_groups()


if __name__ == "__main__":
    pytest.main([__file__])
