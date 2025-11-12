from typing import Any
from unittest.mock import Mock

import pytest

from dsp_tools.commands.create.create_on_server.group_users import _construct_group_lookup
from dsp_tools.commands.create.create_on_server.group_users import _create_one_group
from dsp_tools.commands.create.create_on_server.group_users import create_groups
from dsp_tools.commands.create.create_on_server.group_users import get_existing_group_to_iri_lookup
from dsp_tools.commands.create.models.input_problems import CollectedProblems
from dsp_tools.commands.create.models.input_problems import ProblemType
from dsp_tools.commands.create.models.input_problems import UploadProblem
from dsp_tools.commands.create.models.parsed_project import ParsedGroup
from dsp_tools.commands.create.models.parsed_project import ParsedGroupDescription
from dsp_tools.commands.create.models.server_project_info import GroupNameToIriLookup
from test.unittests.commands.create.constants import PROJECT_IRI
from test.unittests.commands.create.constants import SHORTNAME


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


@pytest.fixture
def parsed_group_1() -> ParsedGroup:
    return ParsedGroup(
        name="editors",
        descriptions=[
            ParsedGroupDescription(lang="en", text="Editors group"),
            ParsedGroupDescription(lang="de", text="Editoren Gruppe"),
        ],
    )


@pytest.fixture
def parsed_group_2() -> ParsedGroup:
    return ParsedGroup(
        name="readers",
        descriptions=[
            ParsedGroupDescription(lang="en", text="Readers group"),
        ],
    )


@pytest.fixture
def parsed_groups(parsed_group_1: ParsedGroup, parsed_group_2: ParsedGroup) -> list[ParsedGroup]:
    return [parsed_group_1, parsed_group_2]


@pytest.fixture
def mock_group_client() -> Mock:
    return Mock()


@pytest.fixture
def empty_group_lookup() -> GroupNameToIriLookup:
    return GroupNameToIriLookup(name2iri={}, shortname=SHORTNAME)


@pytest.fixture
def group_lookup_with_existing() -> GroupNameToIriLookup:
    return GroupNameToIriLookup(name2iri={"editors": "http://rdfh.ch/groups/4123/existing"}, shortname=SHORTNAME)


class TestConstructGroupLookup:
    def test_filters_by_project_iri(self, all_groups: list[dict[str, Any]]) -> None:
        result = _construct_group_lookup(all_groups, PROJECT_IRI, SHORTNAME)

        assert len(result.name2iri) == 4
        assert result.check_exists("testgroupEditors")
        assert result.check_exists(f"{SHORTNAME}:testgroupEditors")
        assert result.check_exists("testgroupReaders")
        assert result.check_exists(f"{SHORTNAME}:testgroupReaders")
        assert not result.check_exists("otherProjectGroup")

    def test_maps_names_to_iris_correctly(self, all_groups: list[dict[str, Any]]) -> None:
        result = _construct_group_lookup(all_groups, PROJECT_IRI, SHORTNAME)
        assert result.get_iri("testgroupEditors") == "http://rdfh.ch/groups/4123/group1"
        assert result.get_iri("testgroupReaders") == "http://rdfh.ch/groups/4123/group2"
        assert result.get_iri("otherProjectGroup") is None

    def test_empty_groups_list(self) -> None:
        result = _construct_group_lookup([], PROJECT_IRI, SHORTNAME)
        assert len(result.name2iri) == 0
        assert isinstance(result, GroupNameToIriLookup)

    def test_no_matching_project(self, all_groups: list[dict[str, Any]]) -> None:
        non_existent_project_iri = "http://rdfh.ch/projects/nonExistent"
        result = _construct_group_lookup(all_groups, non_existent_project_iri, SHORTNAME)
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
        result = _construct_group_lookup(groups, PROJECT_IRI, SHORTNAME)
        assert len(result.name2iri) == 2
        assert result.get_iri("onlyGroup") == "http://rdfh.ch/groups/4123/group1"
        assert result.get_iri(f"{SHORTNAME}:onlyGroup") == "http://rdfh.ch/groups/4123/group1"


class TestGetGroupToIriLookup:
    def test_calls_client_and_constructs_lookup(self, all_groups: list[dict[str, Any]]) -> None:
        mock_client = Mock()
        mock_client.get_all_groups.return_value = all_groups
        result = get_existing_group_to_iri_lookup(mock_client, PROJECT_IRI, SHORTNAME)
        mock_client.get_all_groups.assert_called_once()
        assert isinstance(result, GroupNameToIriLookup)
        assert len(result.name2iri) == 4
        assert result.check_exists("testgroupEditors")
        assert result.check_exists(f"{SHORTNAME}:testgroupEditors")
        assert result.check_exists("testgroupReaders")
        assert result.check_exists(f"{SHORTNAME}:testgroupReaders")

    def test_handles_empty_groups(self) -> None:
        mock_client = Mock()
        mock_client.get_all_groups.return_value = []
        result = get_existing_group_to_iri_lookup(mock_client, PROJECT_IRI, SHORTNAME)
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
        result = get_existing_group_to_iri_lookup(mock_client, PROJECT_IRI, SHORTNAME)
        assert result.get_iri("testGroup") == "http://rdfh.ch/groups/4123/testGroup"


class TestCreateOneGroup:
    def test_successful_creation(self, parsed_group_1: ParsedGroup, mock_group_client: Mock) -> None:
        expected_iri = "http://rdfh.ch/groups/4123/newGroup"
        mock_group_client.create_new_group.return_value = expected_iri
        result = _create_one_group(parsed_group_1, mock_group_client, PROJECT_IRI)
        assert result == expected_iri
        mock_group_client.create_new_group.assert_called_once()

    def test_failed_creation_returns_problem(self, parsed_group_1: ParsedGroup, mock_group_client: Mock) -> None:
        mock_group_client.create_new_group.return_value = None
        result = _create_one_group(parsed_group_1, mock_group_client, PROJECT_IRI)
        assert isinstance(result, UploadProblem)
        assert result.problematic_object == "editors"
        assert result.problem == ProblemType.GROUP_COULD_NOT_BE_CREATED


class TestCreateGroups:
    def test_creates_all_new_groups(
        self, parsed_groups: list[ParsedGroup], mock_group_client: Mock, empty_group_lookup: GroupNameToIriLookup
    ) -> None:
        mock_group_client.create_new_group.side_effect = [
            "http://rdfh.ch/groups/4123/editors",
            "http://rdfh.ch/groups/4123/readers",
        ]
        result_lookup, problems = create_groups(parsed_groups, mock_group_client, PROJECT_IRI, empty_group_lookup)
        assert problems is None
        assert result_lookup.check_exists("editors")
        assert result_lookup.check_exists("readers")
        assert result_lookup.get_iri("editors") == "http://rdfh.ch/groups/4123/editors"
        assert result_lookup.get_iri("readers") == "http://rdfh.ch/groups/4123/readers"
        assert mock_group_client.create_new_group.call_count == 2

    def test_skips_existing_groups(
        self,
        parsed_groups: list[ParsedGroup],
        mock_group_client: Mock,
        group_lookup_with_existing: GroupNameToIriLookup,
    ) -> None:
        mock_group_client.create_new_group.return_value = "http://rdfh.ch/groups/4123/readers"
        result_lookup, problems = create_groups(
            parsed_groups, mock_group_client, PROJECT_IRI, group_lookup_with_existing
        )
        assert problems is None
        assert result_lookup.check_exists("editors")
        assert result_lookup.get_iri("editors") == "http://rdfh.ch/groups/4123/existing"
        assert result_lookup.check_exists("readers")
        assert mock_group_client.create_new_group.call_count == 1

    def test_handles_creation_failures(
        self, parsed_groups: list[ParsedGroup], mock_group_client: Mock, empty_group_lookup: GroupNameToIriLookup
    ) -> None:
        mock_group_client.create_new_group.side_effect = [None, "http://rdfh.ch/groups/4123/readers"]
        result_lookup, problems = create_groups(parsed_groups, mock_group_client, PROJECT_IRI, empty_group_lookup)
        assert isinstance(problems, CollectedProblems)
        assert len(problems.problems) == 1
        assert problems.problems[0].problematic_object == "editors"
        assert problems.problems[0].problem == ProblemType.GROUP_COULD_NOT_BE_CREATED
        assert not result_lookup.check_exists("editors")
        assert result_lookup.check_exists("readers")

    def test_mixed_scenario(self, mock_group_client: Mock) -> None:
        groups = [
            ParsedGroup(name="existing", descriptions=[ParsedGroupDescription(lang="en", text="Existing")]),
            ParsedGroup(name="newSuccess", descriptions=[ParsedGroupDescription(lang="en", text="New Success")]),
            ParsedGroup(name="newFail", descriptions=[ParsedGroupDescription(lang="en", text="New Fail")]),
        ]
        lookup = GroupNameToIriLookup(name2iri={"existing": "http://rdfh.ch/groups/4123/existing"}, shortname=SHORTNAME)
        mock_group_client.create_new_group.side_effect = ["http://rdfh.ch/groups/4123/newSuccess", None]
        result_lookup, problems = create_groups(groups, mock_group_client, PROJECT_IRI, lookup)
        assert isinstance(problems, CollectedProblems)
        assert len(problems.problems) == 1
        assert problems.problems[0].problematic_object == "newFail"
        assert result_lookup.check_exists("existing")
        assert result_lookup.check_exists("newSuccess")
        assert not result_lookup.check_exists("newFail")
        assert mock_group_client.create_new_group.call_count == 2

    def test_all_groups_already_exist(self, parsed_groups: list[ParsedGroup], mock_group_client: Mock) -> None:
        lookup = GroupNameToIriLookup(
            name2iri={
                "editors": "http://rdfh.ch/groups/4123/editors",
                "readers": "http://rdfh.ch/groups/4123/readers",
            },
            shortname=SHORTNAME,
        )
        result_lookup, problems = create_groups(parsed_groups, mock_group_client, PROJECT_IRI, lookup)
        assert problems is None
        assert len(result_lookup.name2iri) == 2
        mock_group_client.create_new_group.assert_not_called()


if __name__ == "__main__":
    pytest.main([__file__])
