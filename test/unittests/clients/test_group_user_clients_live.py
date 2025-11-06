# mypy: disable-error-code="no-untyped-def"

from typing import Any
from unittest.mock import Mock
from unittest.mock import patch

import pytest
import requests

from dsp_tools.clients.group_user_clients_live import GroupClientLive
from dsp_tools.error.custom_warnings import DspToolsUnexpectedStatusCodeWarning
from dsp_tools.error.exceptions import DspToolsRequestException
from test.unittests.clients.constants import API_URL
from test.unittests.clients.constants import GROUP_IRI
from test.unittests.clients.constants import PROJECT_IRI


@pytest.fixture
def group_client() -> GroupClientLive:
    return GroupClientLive(api_url=API_URL)


@pytest.fixture
def new_group() -> dict[str, Any]:
    return {
        "name": "NewGroup",
        "descriptions": [
            {"value": "NewGroupDescription", "language": "en"},
            {"value": "NeueGruppenBeschreibung", "language": "de"},
        ],
        "project": PROJECT_IRI,
    }


class TestGroupClientLiveGetGroup:
    def test_get_all_groups_success(self, group_client: GroupClientLive) -> None:
        mock_response = Mock(status_code=200, ok=True, headers={})
        mock_response.json.return_value = {
            "groups": [
                {
                    "id": GROUP_IRI,
                    "name": "testgroup",
                    "descriptions": [],
                    "project": {
                        "id": PROJECT_IRI,
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
        assert result[0]["name"] == "testgroup"
        assert result[0]["id"] == GROUP_IRI
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
            with pytest.warns(DspToolsUnexpectedStatusCodeWarning):
                result = group_client.get_all_groups()
        assert result == []


class TestGroupClientCreateNewGroup:
    """response

        {
        "group": {
            "id": "http://rdfh.ch/groups/9999/krZ2lP_NTBSbfbX2BSvhiw",
            "name": "NewGroup",
            "descriptions": [
                {
                    "value": "NewGroupDescription",
                    "language": "en"
                },
                {
                    "value": "NeueGruppenBeschreibung",
                    "language": "de"
                }
            ],
            "project": {
                "id": "http://rdfh.ch/projects/zimXRcPvRxeXS-6veIrB7A"
        }
    }
    """

    def test_success(self, group_client: GroupClientLive, new_group) -> None:
        mock_response = Mock(status_code=200, ok=True, headers={})
        mock_response.json.return_value = {
            "group": {
                "id": GROUP_IRI,
                "name": "NewGroup",
                "descriptions": [
                    {"value": "NewGroupDescription", "language": "en"},
                    {"value": "NeueGruppenBeschreibung", "language": "de"},
                ],
                "project": {"id": PROJECT_IRI},
            }
        }
        with patch("dsp_tools.clients.group_user_clients_live.requests.post", return_value=mock_response) as mock_post:
            result = group_client.create_new_group(new_group)
        assert result == GROUP_IRI
        assert mock_post.call_args[0][0] == f"{group_client.api_url}/admin/groups"

    def test_request_exception(self, group_client: GroupClientLive, new_group) -> None:
        with patch(
            "dsp_tools.clients.group_user_clients_live.requests.post", side_effect=requests.ReadTimeout("Timeout")
        ):
            with pytest.raises(DspToolsRequestException):
                group_client.create_new_group(new_group)

    def test_non_ok_response(self, group_client: GroupClientLive, new_group) -> None:
        mock_response = Mock(status_code=500, ok=False, headers={}, text="Internal Server Error")
        mock_response.json.return_value = {}
        with patch("dsp_tools.clients.group_user_clients_live.requests.post", return_value=mock_response):
            with pytest.warns(DspToolsUnexpectedStatusCodeWarning):
                result = group_client.create_new_group(new_group)
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__])
