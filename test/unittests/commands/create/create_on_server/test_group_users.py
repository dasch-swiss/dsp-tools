from typing import Any
from unittest.mock import Mock

import pytest

from dsp_tools.commands.create.create_on_server.group_users import _construct_group_lookup
from dsp_tools.commands.create.create_on_server.group_users import get_group_to_iri_lookup
from dsp_tools.commands.create.models.server_project_info import GroupNameToIriLookup
from test.unittests.commands.create.constants import PROJECT_IRI


@pytest.fixture
def other_project_iri() -> str:
    return "http://rdfh.ch/projects/anotherProject"


@pytest.fixture
def all_groups(other_project_iri: str) -> list[dict[str, Any]]:
    return [
        {
            "id": "http://rdfh.ch/groups/4123/group1",
            "name": "testgroupEditors",
            "descriptions": [],
            "project": {
                "id": PROJECT_IRI,
                "shortname": "systematic-tp",
            },
        },
        {
            "id": "http://rdfh.ch/groups/4123/group2",
            "name": "testgroupReaders",
            "descriptions": [],
            "project": {
                "id": PROJECT_IRI,
                "shortname": "systematic-tp",
            },
        },
        {
            "id": "http://rdfh.ch/groups/4123/group3",
            "name": "otherProjectGroup",
            "descriptions": [],
            "project": {
                "id": other_project_iri,
                "shortname": "another-project",
            },
        },
    ]


class TestConstructGroupLookup:
    def test_filters_by_project_iri(self, all_groups: list[dict[str, Any]]) -> None:
        result = _construct_group_lookup(all_groups, PROJECT_IRI)

        assert len(result.name2iri) == 2
        assert result.check_exists("testgroupEditors")
        assert result.check_exists("testgroupReaders")
        assert not result.check_exists("otherProjectGroup")

    def test_maps_names_to_iris_correctly(self, all_groups: list[dict[str, Any]]) -> None:
        result = _construct_group_lookup(all_groups, PROJECT_IRI)

        assert result.get_iri("testgroupEditors") == "http://rdfh.ch/groups/4123/group1"
        assert result.get_iri("testgroupReaders") == "http://rdfh.ch/groups/4123/group2"
        assert result.get_iri("otherProjectGroup") is None

    def test_empty_groups_list(self) -> None:
        result = _construct_group_lookup([], PROJECT_IRI)

        assert len(result.name2iri) == 0
        assert isinstance(result, GroupNameToIriLookup)

    def test_no_matching_project(self, all_groups: list[dict[str, Any]]) -> None:
        non_existent_project_iri = "http://rdfh.ch/projects/nonExistent"
        result = _construct_group_lookup(all_groups, non_existent_project_iri)

        assert len(result.name2iri) == 0

    def test_only_target_project_groups(self) -> None:
        groups = [
            {
                "id": "http://rdfh.ch/groups/4123/group1",
                "name": "onlyGroup",
                "descriptions": [],
                "project": {
                    "id": PROJECT_IRI,
                    "shortname": "systematic-tp",
                },
            }
        ]
        result = _construct_group_lookup(groups, PROJECT_IRI)

        assert len(result.name2iri) == 1
        assert result.get_iri("onlyGroup") == "http://rdfh.ch/groups/4123/group1"


class TestGetGroupToIriLookup:
    def test_calls_client_and_constructs_lookup(self, all_groups: list[dict[str, Any]]) -> None:
        mock_client = Mock()
        mock_client.get_all_groups.return_value = all_groups

        result = get_group_to_iri_lookup(mock_client, PROJECT_IRI)

        mock_client.get_all_groups.assert_called_once()
        assert isinstance(result, GroupNameToIriLookup)
        assert len(result.name2iri) == 2
        assert result.check_exists("testgroupEditors")
        assert result.check_exists("testgroupReaders")

    def test_handles_empty_groups(self) -> None:
        mock_client = Mock()
        mock_client.get_all_groups.return_value = []

        result = get_group_to_iri_lookup(mock_client, PROJECT_IRI)

        mock_client.get_all_groups.assert_called_once()
        assert isinstance(result, GroupNameToIriLookup)
        assert len(result.name2iri) == 0

    def test_integration_with_mock_client(self) -> None:
        mock_client = Mock()
        mock_client.get_all_groups.return_value = [
            {
                "id": "http://rdfh.ch/groups/4123/testGroup",
                "name": "testGroup",
                "descriptions": [],
                "project": {
                    "id": PROJECT_IRI,
                    "shortname": "test-project",
                },
            }
        ]

        result = get_group_to_iri_lookup(mock_client, PROJECT_IRI)
        assert result.get_iri("testGroup") == "http://rdfh.ch/groups/4123/testGroup"


if __name__ == "__main__":
    pytest.main([__file__])
