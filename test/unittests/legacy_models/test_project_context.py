from typing import Any
from unittest.mock import Mock

import pytest

from dsp_tools.error.exceptions import BaseError
from dsp_tools.legacy_models.projectContext import create_project_context


@pytest.fixture
def mock_connection() -> Mock:
    return Mock()


class TestCreateProjectContext:
    """Tests for the create_project_context factory function."""

    def test_creates_group_map(self, mock_connection: Mock) -> None:
        mock_connection.get.side_effect = [
            {
                "projects": [
                    {"id": "http://rdfh.ch/projects/0001", "shortcode": "0001", "shortname": "testproj"},
                ]
            },
            {
                "groups": [
                    {
                        "id": "http://rdfh.ch/groups/0001/mygroup",
                        "name": "MyGroup",
                        "project": {"id": "http://rdfh.ch/projects/0001"},
                    }
                ]
            },
        ]
        ctx = create_project_context(mock_connection, "0001")
        assert ctx.group_map == {"testproj:MyGroup": "http://rdfh.ch/groups/0001/mygroup"}
        assert ctx.project_name == "testproj"

    def test_returns_project_name_for_shortcode(self, mock_connection: Mock) -> None:
        mock_connection.get.side_effect = [
            {
                "projects": [
                    {"id": "http://rdfh.ch/projects/0001", "shortcode": "0001", "shortname": "proj1"},
                    {"id": "http://rdfh.ch/projects/0002", "shortcode": "0002", "shortname": "proj2"},
                ]
            },
            {"groups": []},
        ]
        ctx = create_project_context(mock_connection, "0002")
        assert ctx.project_name == "proj2"

    def test_returns_none_for_unknown_shortcode(self, mock_connection: Mock) -> None:
        mock_connection.get.side_effect = [
            {
                "projects": [
                    {"id": "http://rdfh.ch/projects/0001", "shortcode": "0001", "shortname": "testproj"},
                ]
            },
            {"groups": []},
        ]
        ctx = create_project_context(mock_connection, "9999")
        assert ctx.project_name is None

    def test_handles_groups_api_error(self, mock_connection: Mock) -> None:
        # When groups API fails, group_map should be empty
        def get_side_effect(route: str) -> dict[str, Any]:
            if route == "/admin/projects":
                return {"projects": [{"id": "p1", "shortcode": "0001", "shortname": "testproj"}]}
            elif route == "/admin/groups":
                raise BaseError("Groups API error")
            return {}

        mock_connection.get.side_effect = get_side_effect
        ctx = create_project_context(mock_connection, "0001")
        assert ctx.group_map == {}
        assert ctx.project_name == "testproj"

    def test_multiple_groups_from_multiple_projects(self, mock_connection: Mock) -> None:
        mock_connection.get.side_effect = [
            {
                "projects": [
                    {"id": "http://rdfh.ch/projects/0001", "shortcode": "0001", "shortname": "proj1"},
                    {"id": "http://rdfh.ch/projects/0002", "shortcode": "0002", "shortname": "proj2"},
                ]
            },
            {
                "groups": [
                    {
                        "id": "http://rdfh.ch/groups/0001/group1",
                        "name": "Group1",
                        "project": {"id": "http://rdfh.ch/projects/0001"},
                    },
                    {
                        "id": "http://rdfh.ch/groups/0002/group2",
                        "name": "Group2",
                        "project": {"id": "http://rdfh.ch/projects/0002"},
                    },
                ]
            },
        ]
        ctx = create_project_context(mock_connection, "0001")
        assert ctx.group_map == {
            "proj1:Group1": "http://rdfh.ch/groups/0001/group1",
            "proj2:Group2": "http://rdfh.ch/groups/0002/group2",
        }
