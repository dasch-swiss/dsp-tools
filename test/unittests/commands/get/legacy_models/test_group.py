from typing import Any
from unittest.mock import Mock

import pytest

from dsp_tools.commands.get.legacy_models.group import Group
from dsp_tools.commands.get.legacy_models.group import create_group_from_json
from dsp_tools.commands.get.legacy_models.group import get_all_groups_for_project
from dsp_tools.error.exceptions import BaseError
from dsp_tools.legacy_models.langstring import create_lang_string


@pytest.fixture
def mock_connection() -> Mock:
    return Mock()


def _make_valid_group_json() -> dict[str, Any]:
    return {
        "id": "http://rdfh.ch/groups/0001/thing-searcher",
        "name": "Thing searcher",
        "descriptions": [{"language": "en", "value": "A group for searching things"}],
        "project": {"id": "http://rdfh.ch/projects/0001"},
        "selfjoin": False,
        "status": True,
    }


class TestCreateGroupFromJson:
    """Tests for the create_group_from_json factory function."""

    def test_valid_json(self) -> None:
        json_obj = _make_valid_group_json()
        group = create_group_from_json(json_obj)
        assert group.iri == "http://rdfh.ch/groups/0001/thing-searcher"
        assert group.name == "Thing searcher"
        assert group.project == "http://rdfh.ch/projects/0001"
        assert group.selfjoin is False
        assert group.status is True

    def test_missing_descriptions_uses_empty_langstring(self) -> None:
        # Descriptions are optional and default to empty LangString
        json_obj = _make_valid_group_json()
        del json_obj["descriptions"]
        group = create_group_from_json(json_obj)
        assert group.descriptions == create_lang_string()

    @pytest.mark.parametrize(
        ("missing_field", "error_fragment"),
        [
            ("id", '"id" is missing'),
            ("name", '"name" is missing'),
            ("project", '"project" is missing'),
            ("selfjoin", "selfjoin is missing"),
            ("status", "Status is missing"),
        ],
    )
    def test_missing_required_field(self, missing_field: str, error_fragment: str) -> None:
        # All required fields follow same pattern: missing → BaseError
        json_obj = _make_valid_group_json()
        del json_obj[missing_field]
        with pytest.raises(BaseError, match=error_fragment):
            create_group_from_json(json_obj)

    def test_missing_nested_project_id(self) -> None:
        # Distinct from missing project: key exists but lacks nested id
        json_obj = _make_valid_group_json()
        json_obj["project"] = {}
        with pytest.raises(BaseError, match='has no "id"'):
            create_group_from_json(json_obj)


class TestGroupToDefinitionFileObj:
    """Tests for Group.to_definition_file_obj serialization."""

    def test_serialization_structure(self) -> None:
        group = Group(
            iri="http://rdfh.ch/groups/0001/test",
            name="TestGroup",
            project="http://rdfh.ch/projects/0001",
            selfjoin=True,
            status=True,
            descriptions=create_lang_string({"en": "Test description"}),
        )
        result = group.to_definition_file_obj()
        assert result["name"] == "TestGroup"
        assert result["selfjoin"] is True
        assert result["status"] is True
        assert "descriptions" in result
        # IRI should not be in output (not part of definition file format)
        assert "iri" not in result
        assert "project" not in result


class TestGetAllGroupsForProject:
    """Tests for the get_all_groups_for_project API function."""

    def test_filters_by_project_iri(self, mock_connection: Mock) -> None:
        # Tests the list comprehension filter logic
        mock_connection.get.return_value = {
            "groups": [
                {
                    "id": "http://rdfh.ch/groups/0001/group1",
                    "name": "Group1",
                    "project": {"id": "http://rdfh.ch/projects/0001"},
                    "selfjoin": False,
                    "status": True,
                },
                {
                    "id": "http://rdfh.ch/groups/0002/group2",
                    "name": "Group2",
                    "project": {"id": "http://rdfh.ch/projects/0002"},
                    "selfjoin": True,
                    "status": True,
                },
                {
                    "id": "http://rdfh.ch/groups/0001/group3",
                    "name": "Group3",
                    "project": {"id": "http://rdfh.ch/projects/0001"},
                    "selfjoin": False,
                    "status": False,
                },
            ]
        }
        result = get_all_groups_for_project(mock_connection, "http://rdfh.ch/projects/0001")
        assert len(result) == 2
        assert result[0].name == "Group1"
        assert result[1].name == "Group3"

    def test_returns_empty_when_no_match(self, mock_connection: Mock) -> None:
        mock_connection.get.return_value = {
            "groups": [
                {
                    "id": "http://rdfh.ch/groups/0002/group",
                    "name": "Group",
                    "project": {"id": "http://rdfh.ch/projects/0002"},
                    "selfjoin": False,
                    "status": True,
                },
            ]
        }
        result = get_all_groups_for_project(mock_connection, "http://rdfh.ch/projects/0001")
        assert result == []

    def test_returns_empty_when_no_groups(self, mock_connection: Mock) -> None:
        mock_connection.get.return_value = {"groups": []}
        result = get_all_groups_for_project(mock_connection, "http://rdfh.ch/projects/0001")
        assert result == []
