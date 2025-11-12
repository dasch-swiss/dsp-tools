# mypy: disable-error-code="no-untyped-def"

from typing import Any
from unittest.mock import Mock
from unittest.mock import patch

import pytest
import requests
from requests import JSONDecodeError

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.group_user_clients_live import GroupClientLive
from dsp_tools.clients.group_user_clients_live import UserClientLive
from dsp_tools.error.custom_warnings import DspToolsUnexpectedStatusCodeWarning
from dsp_tools.error.exceptions import BadCredentialsError
from dsp_tools.error.exceptions import DspToolsRequestException
from dsp_tools.error.exceptions import FatalNonOkApiResponseCode
from test.unittests.clients.constants import API_URL
from test.unittests.clients.constants import GROUP_IRI
from test.unittests.clients.constants import PROJECT_IRI
from test.unittests.clients.constants import USER_IRI


@pytest.fixture
def mock_auth() -> Mock:
    auth = Mock(spec=AuthenticationClient)
    auth.get_token.return_value = "test-token-123"
    auth.server = "http://0.0.0.0:3333"
    return auth


@pytest.fixture
def group_client(mock_auth) -> GroupClientLive:
    return GroupClientLive(API_URL, mock_auth)


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


@pytest.fixture
def user_client(mock_auth) -> UserClientLive:
    return UserClientLive(API_URL, mock_auth)


@pytest.fixture
def new_user() -> dict[str, Any]:
    return {
        "username": "testuser",
        "email": "test@example.com",
        "givenName": "Test",
        "familyName": "User",
        "password": "test123",
        "status": True,
        "lang": "en",
        "systemAdmin": False,
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
        assert result[1]["id"] == "http://rdfh.ch/groups/4123/anotherGroupId"
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

    def test_forbidden(self, group_client: GroupClientLive, new_group) -> None:
        mock_response = Mock(status_code=403, ok=False, headers={}, text="Forbidden")
        mock_response.json.side_effect = JSONDecodeError("Expecting value", "", 0)
        with patch("dsp_tools.clients.group_user_clients_live.requests.post", return_value=mock_response):
            with pytest.raises(BadCredentialsError):
                group_client.create_new_group(new_group)


class TestUserClientLiveGetUserIriByUsername:
    def test_success(self, user_client: UserClientLive) -> None:
        mock_response = Mock(status_code=200, ok=True, headers={})
        mock_response.json.return_value = {"user": {"id": USER_IRI, "username": "testuser"}}
        with patch("dsp_tools.clients.group_user_clients_live.requests.get", return_value=mock_response) as mock_get:
            result = user_client.get_user_iri_by_username("testuser")
        assert result == USER_IRI
        assert mock_get.call_args[1]["url"] == f"{user_client.api_url}/admin/users/username/testuser"

    def test_not_found(self, user_client: UserClientLive) -> None:
        mock_response = Mock(status_code=404, ok=False, headers={}, text="User not found")
        mock_response.json.return_value = {"message": "User with username 'nonexistent' not found"}
        with patch("dsp_tools.clients.group_user_clients_live.requests.get", return_value=mock_response):
            result = user_client.get_user_iri_by_username("nonexistent")
        assert result is None

    def test_forbidden(self, user_client: UserClientLive) -> None:
        mock_response = Mock(status_code=403, ok=False, headers={}, text="forbidden")
        mock_response.json.side_effect = JSONDecodeError("Expecting value", "", 0)
        with patch("dsp_tools.clients.group_user_clients_live.requests.get", return_value=mock_response):
            with pytest.raises(BadCredentialsError):
                user_client.get_user_iri_by_username("testuser")

    def test_timeout(self, user_client: UserClientLive) -> None:
        with patch(
            "dsp_tools.clients.group_user_clients_live.requests.get", side_effect=requests.ReadTimeout("Timeout")
        ):
            with pytest.raises(DspToolsRequestException):
                user_client.get_user_iri_by_username("testuser")

    def test_server_error(self, user_client: UserClientLive) -> None:
        mock_response = Mock(status_code=500, ok=False, headers={}, text="Internal Server Error")
        mock_response.json.return_value = {}
        with patch("dsp_tools.clients.group_user_clients_live.requests.get", return_value=mock_response):
            with pytest.warns(DspToolsUnexpectedStatusCodeWarning):
                result = user_client.get_user_iri_by_username("testuser")
        assert result is None


class TestUserClientLivePostNewUser:
    def test_success(self, user_client: UserClientLive, new_user) -> None:
        mock_response = Mock(status_code=200, ok=True, headers={})
        mock_response.json.return_value = {"user": {"id": USER_IRI, "username": "testuser"}}
        with patch("dsp_tools.clients.group_user_clients_live.requests.post", return_value=mock_response) as mock_post:
            result = user_client.post_new_user(new_user)
        assert result == USER_IRI
        assert mock_post.call_args[1]["url"] == f"{user_client.api_url}/admin/users"

    def test_bad_request(self, user_client: UserClientLive, new_user) -> None:
        mock_response = Mock(status_code=400, ok=False, headers={}, text="User already exists")
        mock_response.json.return_value = {}
        with patch("dsp_tools.clients.group_user_clients_live.requests.post", return_value=mock_response):
            with pytest.raises(FatalNonOkApiResponseCode):
                user_client.post_new_user(new_user)

    def test_forbidden(self, user_client: UserClientLive, new_user) -> None:
        mock_response = Mock(status_code=403, ok=False, headers={}, text="forbidden")
        mock_response.json.side_effect = JSONDecodeError("Expecting value", "", 0)
        with patch("dsp_tools.clients.group_user_clients_live.requests.post", return_value=mock_response):
            with pytest.raises(BadCredentialsError):
                user_client.post_new_user(new_user)

    def test_timeout(self, user_client: UserClientLive, new_user) -> None:
        with patch(
            "dsp_tools.clients.group_user_clients_live.requests.post", side_effect=requests.ReadTimeout("Timeout")
        ):
            with pytest.raises(DspToolsRequestException):
                user_client.post_new_user(new_user)

    def test_server_error(self, user_client: UserClientLive, new_user) -> None:
        mock_response = Mock(status_code=500, ok=False, headers={}, text="Internal Server Error")
        mock_response.json.return_value = {}
        with patch("dsp_tools.clients.group_user_clients_live.requests.post", return_value=mock_response):
            with pytest.warns(DspToolsUnexpectedStatusCodeWarning):
                result = user_client.post_new_user(new_user)
        assert result is None


class TestUserClientLiveAddUserToProject:
    def test_success(self, user_client: UserClientLive) -> None:
        mock_response = Mock(status_code=200, ok=True, headers={})
        mock_response.json.return_value = {"user": {"id": USER_IRI}}
        with patch("dsp_tools.clients.group_user_clients_live.requests.post", return_value=mock_response) as mock_post:
            result = user_client.add_user_to_project(USER_IRI, PROJECT_IRI)
        assert result is True
        expected_url = (
            f"{user_client.api_url}/admin/users/iri/http%3A%2F%2Frdfh.ch%2Fusers%2Ftestuser-iri"
            "/project-memberships/http%3A%2F%2Frdfh.ch%2Fprojects%2FprojectIRI"
        )
        assert mock_post.call_args[1]["url"] == expected_url

    def test_forbidden(self, user_client: UserClientLive) -> None:
        mock_response = Mock(status_code=403, ok=False, headers={}, text="forbidden")
        mock_response.json.side_effect = JSONDecodeError("Expecting value", "", 0)
        with patch("dsp_tools.clients.group_user_clients_live.requests.post", return_value=mock_response):
            with pytest.raises(BadCredentialsError):
                user_client.add_user_to_project(USER_IRI, PROJECT_IRI)

    def test_timeout(self, user_client: UserClientLive) -> None:
        with patch(
            "dsp_tools.clients.group_user_clients_live.requests.post", side_effect=requests.ReadTimeout("Timeout")
        ):
            with pytest.raises(DspToolsRequestException):
                user_client.add_user_to_project(USER_IRI, PROJECT_IRI)

    def test_server_error(self, user_client: UserClientLive) -> None:
        mock_response = Mock(status_code=500, ok=False, headers={}, text="Internal Server Error")
        mock_response.json.return_value = {}
        with patch("dsp_tools.clients.group_user_clients_live.requests.post", return_value=mock_response):
            with pytest.warns(DspToolsUnexpectedStatusCodeWarning):
                result = user_client.add_user_to_project(USER_IRI, PROJECT_IRI)
        assert result is False


class TestUserClientLiveAddUserAsProjectAdmin:
    def test_success(self, user_client: UserClientLive) -> None:
        mock_response = Mock(status_code=200, ok=True, headers={})
        mock_response.json.return_value = {"user": {"id": USER_IRI}}
        with patch("dsp_tools.clients.group_user_clients_live.requests.post", return_value=mock_response) as mock_post:
            result = user_client.add_user_as_project_admin(USER_IRI, PROJECT_IRI)
        assert result is True
        expected_url = (
            f"{user_client.api_url}/admin/users/iri/http%3A%2F%2Frdfh.ch%2Fusers%2Ftestuser-iri"
            "/project-admin-memberships/http%3A%2F%2Frdfh.ch%2Fprojects%2FprojectIRI"
        )
        assert mock_post.call_args[1]["url"] == expected_url

    def test_forbidden(self, user_client: UserClientLive) -> None:
        mock_response = Mock(status_code=403, ok=False, headers={}, text="forbidden")
        mock_response.json.side_effect = JSONDecodeError("Expecting value", "", 0)
        with patch("dsp_tools.clients.group_user_clients_live.requests.post", return_value=mock_response):
            with pytest.raises(BadCredentialsError):
                user_client.add_user_as_project_admin(USER_IRI, PROJECT_IRI)

    def test_timeout(self, user_client: UserClientLive) -> None:
        with patch(
            "dsp_tools.clients.group_user_clients_live.requests.post", side_effect=requests.ReadTimeout("Timeout")
        ):
            with pytest.raises(DspToolsRequestException):
                user_client.add_user_as_project_admin(USER_IRI, PROJECT_IRI)

    def test_server_error(self, user_client: UserClientLive) -> None:
        mock_response = Mock(status_code=500, ok=False, headers={}, text="Internal Server Error")
        mock_response.json.return_value = {}
        with patch("dsp_tools.clients.group_user_clients_live.requests.post", return_value=mock_response):
            with pytest.warns(DspToolsUnexpectedStatusCodeWarning):
                result = user_client.add_user_as_project_admin(USER_IRI, PROJECT_IRI)
        assert result is False


class TestUserClientLiveAddUserToCustomGroup:
    def test_all_success(self, user_client: UserClientLive) -> None:
        mock_response = Mock(status_code=200, ok=True, headers={})
        mock_response.json.return_value = {"user": {"id": USER_IRI}}
        with patch("dsp_tools.clients.group_user_clients_live.requests.post", return_value=mock_response):
            result = user_client.add_user_to_custom_group(
                USER_IRI, [GROUP_IRI, "http://rdfh.ch/groups/4123/iri-testgroup2"]
            )
        assert result is True

    def test_partial_failure(self, user_client: UserClientLive) -> None:
        mock_success = Mock(status_code=200, ok=True, headers={})
        mock_success.json.return_value = {"user": {"id": USER_IRI}}
        mock_failure = Mock(status_code=500, ok=False, headers={}, text="Internal Server Error")
        mock_failure.json.return_value = {}
        with patch("dsp_tools.clients.group_user_clients_live.requests.post", side_effect=[mock_success, mock_failure]):
            with pytest.warns(DspToolsUnexpectedStatusCodeWarning):
                result = user_client.add_user_to_custom_group(
                    USER_IRI, [GROUP_IRI, "http://rdfh.ch/groups/4123/iri-testgroup2"]
                )
        assert result is False

    def test_all_failure(self, user_client: UserClientLive) -> None:
        mock_failure = Mock(status_code=500, ok=False, headers={}, text="Internal Server Error")
        mock_failure.json.return_value = {}
        with patch("dsp_tools.clients.group_user_clients_live.requests.post", return_value=mock_failure):
            with pytest.warns(DspToolsUnexpectedStatusCodeWarning):
                result = user_client.add_user_to_custom_group(
                    USER_IRI, [GROUP_IRI, "http://rdfh.ch/groups/4123/iri-testgroup2"]
                )
        assert result is False

    def test_empty_list(self, user_client: UserClientLive) -> None:
        result = user_client.add_user_to_custom_group(USER_IRI, [])
        assert result is True


class TestUserClientLiveAddUserToOneGroup:
    def test_success(self, user_client: UserClientLive) -> None:
        mock_response = Mock(status_code=200, ok=True, headers={})
        mock_response.json.return_value = {"user": {"id": USER_IRI}}
        user_iri_encoded = "http%3A%2F%2Frdfh.ch%2Fusers%2Ftestuser-iri"
        with patch("dsp_tools.clients.group_user_clients_live.requests.post", return_value=mock_response) as mock_post:
            result = user_client._add_user_to_one_group(user_iri_encoded, GROUP_IRI)
        assert result is True
        expected_url = (
            f"{user_client.api_url}/admin/users/iri/{user_iri_encoded}"
            "/group-memberships/http%3A%2F%2Frdfh.ch%2Fgroups%2F4123%2Firi-testgroup"
        )
        assert mock_post.call_args[1]["url"] == expected_url

    def test_forbidden(self, user_client: UserClientLive) -> None:
        mock_response = Mock(status_code=403, ok=False, headers={}, text="forbidden")
        mock_response.json.side_effect = JSONDecodeError("Expecting value", "", 0)
        user_iri_encoded = "http%3A%2F%2Frdfh.ch%2Fusers%2Ftestuser-iri"
        with patch("dsp_tools.clients.group_user_clients_live.requests.post", return_value=mock_response):
            with pytest.raises(BadCredentialsError):
                user_client._add_user_to_one_group(user_iri_encoded, GROUP_IRI)

    def test_timeout(self, user_client: UserClientLive) -> None:
        user_iri_encoded = "http%3A%2F%2Frdfh.ch%2Fusers%2Ftestuser-iri"
        with patch(
            "dsp_tools.clients.group_user_clients_live.requests.post", side_effect=requests.ReadTimeout("Timeout")
        ):
            with pytest.raises(DspToolsRequestException):
                user_client._add_user_to_one_group(user_iri_encoded, GROUP_IRI)

    def test_server_error(self, user_client: UserClientLive) -> None:
        mock_response = Mock(status_code=500, ok=False, headers={}, text="Internal Server Error")
        mock_response.json.return_value = {}
        user_iri_encoded = "http%3A%2F%2Frdfh.ch%2Fusers%2Ftestuser-iri"
        with patch("dsp_tools.clients.group_user_clients_live.requests.post", return_value=mock_response):
            with pytest.warns(DspToolsUnexpectedStatusCodeWarning):
                result = user_client._add_user_to_one_group(user_iri_encoded, GROUP_IRI)
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__])
