from typing import Any
from unittest.mock import Mock

import pytest

from dsp_tools.commands.get.legacy_models.group import PROJECT_ADMIN_GROUP
from dsp_tools.commands.get.legacy_models.group import PROJECT_MEMBER_GROUP
from dsp_tools.commands.get.legacy_models.user import _extract_permissions_and_groups
from dsp_tools.commands.get.legacy_models.user import _parse_language
from dsp_tools.commands.get.legacy_models.user import create_user_from_json
from dsp_tools.commands.get.legacy_models.user import get_all_users_for_project
from dsp_tools.error.exceptions import BaseError
from dsp_tools.legacy_models.langstring import Languages


@pytest.fixture
def mock_connection() -> Mock:
    return Mock()


class TestParseLanguage:
    """Tests for the _parse_language helper function."""

    @pytest.mark.parametrize("lang", ["en", "de", "fr", "it", "rm"])
    def test_valid_language(self, lang: str) -> None:
        # All valid language codes follow the same path
        result = _parse_language(lang)
        assert result is not None
        assert result.value == lang

    def test_invalid_language(self) -> None:
        # Error path: unknown language code
        with pytest.raises(BaseError, match="Invalid language string"):
            _parse_language("xx")

    def test_none_input(self) -> None:
        # None path: explicitly allowed, returns None
        assert _parse_language(None) is None


class TestExtractPermissionsAndGroups:
    """Tests for the _extract_permissions_and_groups helper function."""

    def test_project_member_sets_admin_false(self) -> None:
        # ProjectMember group sets in_projects[project] = False
        json_obj = {
            "permissions": {
                "groupsPerProject": {
                    "http://rdfh.ch/projects/0001": [PROJECT_MEMBER_GROUP],
                }
            }
        }
        _, in_projects = _extract_permissions_and_groups(json_obj)
        assert in_projects == {"http://rdfh.ch/projects/0001": False}

    def test_project_admin_sets_admin_true(self) -> None:
        # ProjectAdmin group sets in_projects[project] = True
        json_obj = {
            "permissions": {
                "groupsPerProject": {
                    "http://rdfh.ch/projects/0001": [PROJECT_ADMIN_GROUP],
                }
            }
        }
        _, in_projects = _extract_permissions_and_groups(json_obj)
        assert in_projects == {"http://rdfh.ch/projects/0001": True}

    def test_project_admin_overrides_project_member(self) -> None:
        # If user is both member and admin, admin wins
        json_obj = {
            "permissions": {
                "groupsPerProject": {
                    "http://rdfh.ch/projects/0001": [PROJECT_MEMBER_GROUP, PROJECT_ADMIN_GROUP],
                }
            }
        }
        _, in_projects = _extract_permissions_and_groups(json_obj)
        assert in_projects == {"http://rdfh.ch/projects/0001": True}

    def test_custom_groups_added_to_in_groups(self) -> None:
        # Custom groups are added to in_groups set
        custom_group = "http://rdfh.ch/groups/0001/custom-group"
        json_obj = {
            "permissions": {
                "groupsPerProject": {
                    "http://rdfh.ch/projects/0001": [PROJECT_MEMBER_GROUP, custom_group],
                }
            }
        }
        in_groups, _ = _extract_permissions_and_groups(json_obj)
        assert custom_group in in_groups

    def test_multiple_projects(self) -> None:
        # Handles multiple projects correctly
        json_obj = {
            "permissions": {
                "groupsPerProject": {
                    "http://rdfh.ch/projects/0001": [PROJECT_ADMIN_GROUP],
                    "http://rdfh.ch/projects/0002": [PROJECT_MEMBER_GROUP],
                }
            }
        }
        _, in_projects = _extract_permissions_and_groups(json_obj)
        assert in_projects == {
            "http://rdfh.ch/projects/0001": True,
            "http://rdfh.ch/projects/0002": False,
        }

    def test_no_permissions_key(self) -> None:
        # Missing permissions key returns empty collections
        json_obj: dict[str, Any] = {}
        in_groups, in_projects = _extract_permissions_and_groups(json_obj)
        assert in_groups == frozenset()
        assert in_projects == {}


def _make_valid_user_json() -> dict[str, Any]:
    return {
        "username": "testuser",
        "email": "test@example.org",
        "status": True,
        "givenName": "Test",
        "familyName": "User",
        "lang": "en",
        "permissions": {"groupsPerProject": {}},
    }


class TestCreateUserFromJson:
    """Tests for the create_user_from_json factory function."""

    def test_valid_json(self) -> None:
        json_obj = _make_valid_user_json()
        user = create_user_from_json(json_obj)
        assert user.username == "testuser"
        assert user.email == "test@example.org"
        assert user.status is True
        assert user.given_name == "Test"
        assert user.family_name == "User"
        assert user.lang == Languages.EN

    def test_optional_fields_none(self) -> None:
        # givenName, familyName, lang are optional
        json_obj = _make_valid_user_json()
        del json_obj["givenName"]
        del json_obj["familyName"]
        del json_obj["lang"]
        user = create_user_from_json(json_obj)
        assert user.given_name is None
        assert user.family_name is None
        assert user.lang is None

    @pytest.mark.parametrize(
        "missing_field",
        ["email", "username", "status"],
    )
    def test_missing_required_field(self, missing_field: str) -> None:
        json_obj = _make_valid_user_json()
        del json_obj[missing_field]
        with pytest.raises(BaseError, match=f'"{missing_field}" is missing'):
            create_user_from_json(json_obj)

    def test_multiple_missing_required_fields(self) -> None:
        # All missing fields are reported together
        json_obj = _make_valid_user_json()
        del json_obj["email"]
        del json_obj["username"]
        with pytest.raises(BaseError) as exc_info:
            create_user_from_json(json_obj)
        assert "email" in str(exc_info.value)
        assert "username" in str(exc_info.value)


class TestGetAllUsersForProject:
    """Tests for the get_all_users_for_project API function."""

    def test_returns_users_in_reverse_order(self, mock_connection: Mock) -> None:
        # Verifies reversal of user list
        mock_connection.get.return_value = {
            "members": [
                {"username": "user1", "email": "user1@test.org", "status": True},
                {"username": "user2", "email": "user2@test.org", "status": True},
            ]
        }
        result = get_all_users_for_project(mock_connection, "0001")
        assert result is not None
        assert len(result) == 2
        assert result[0].username == "user2"
        assert result[1].username == "user1"

    def test_returns_none_when_response_falsy(self, mock_connection: Mock) -> None:
        # First None condition: response itself is falsy
        mock_connection.get.return_value = {}
        result = get_all_users_for_project(mock_connection, "0001")
        assert result is None

    def test_returns_none_when_members_key_missing(self, mock_connection: Mock) -> None:
        # Second None condition: "members" key not in response
        mock_connection.get.return_value = {"other_key": []}
        result = get_all_users_for_project(mock_connection, "0001")
        assert result is None

    def test_returns_none_when_members_list_empty(self, mock_connection: Mock) -> None:
        # Third None condition: members list is empty
        mock_connection.get.return_value = {"members": []}
        result = get_all_users_for_project(mock_connection, "0001")
        assert result is None

    def test_uses_correct_route(self, mock_connection: Mock) -> None:
        mock_connection.get.return_value = {"members": []}
        get_all_users_for_project(mock_connection, "0001")
        mock_connection.get.assert_called_once_with("/admin/projects/shortcode/0001/members")
