from typing import Any
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from dsp_tools.commands.create.create_on_server.group_users import _add_all_memberships
from dsp_tools.commands.create.create_on_server.group_users import _add_one_membership
from dsp_tools.commands.create.create_on_server.group_users import _add_user_to_groups
from dsp_tools.commands.create.create_on_server.group_users import _construct_group_lookup
from dsp_tools.commands.create.create_on_server.group_users import _create_all_users
from dsp_tools.commands.create.create_on_server.group_users import _create_one_group
from dsp_tools.commands.create.create_on_server.group_users import _create_one_user
from dsp_tools.commands.create.create_on_server.group_users import create_groups
from dsp_tools.commands.create.create_on_server.group_users import create_users
from dsp_tools.commands.create.create_on_server.group_users import get_existing_group_to_iri_lookup
from dsp_tools.commands.create.models.input_problems import CollectedProblems
from dsp_tools.commands.create.models.input_problems import ProblemType
from dsp_tools.commands.create.models.input_problems import UploadProblem
from dsp_tools.commands.create.models.parsed_project import ParsedGroup
from dsp_tools.commands.create.models.parsed_project import ParsedGroupDescription
from dsp_tools.commands.create.models.parsed_project import ParsedUser
from dsp_tools.commands.create.models.parsed_project import ParsedUserMemberShipInfo
from dsp_tools.commands.create.models.server_project_info import GroupNameToIriLookup
from dsp_tools.commands.create.models.server_project_info import UserNameToIriLookup
from test.unittests.commands.create.constants import PROJECT_IRI
from test.unittests.commands.create.constants import SHORTNAME

USER_1_IRI = "http://rdfh.ch/users/testuser1IRI"
USER_2_IRI = "http://rdfh.ch/users/testuser2IRI"


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


@pytest.fixture
def parsed_user_1() -> ParsedUser:
    return ParsedUser(
        username="testuser1",
        email="testuser1@example.com",
        given_name="Test",
        family_name="User One",
        password="password123",
        lang="en",
    )


@pytest.fixture
def parsed_user_2() -> ParsedUser:
    return ParsedUser(
        username="testuser2",
        email="testuser2@example.com",
        given_name="Test",
        family_name="User Two",
        password="password456",
        lang="de",
    )


@pytest.fixture
def parsed_users(parsed_user_1: ParsedUser, parsed_user_2: ParsedUser) -> list[ParsedUser]:
    return [parsed_user_1, parsed_user_2]


@pytest.fixture
def user_membership_admin() -> ParsedUserMemberShipInfo:
    return ParsedUserMemberShipInfo(username="testuser1", is_admin=True, groups=["editors", "reviewers"])


@pytest.fixture
def user_membership_regular() -> ParsedUserMemberShipInfo:
    return ParsedUserMemberShipInfo(username="testuser2", is_admin=False, groups=["readers"])


@pytest.fixture
def user_memberships(
    user_membership_admin: ParsedUserMemberShipInfo, user_membership_regular: ParsedUserMemberShipInfo
) -> list[ParsedUserMemberShipInfo]:
    return [user_membership_admin, user_membership_regular]


@pytest.fixture
def mock_user_client() -> Mock:
    return Mock()


@pytest.fixture
def mock_auth() -> Mock:
    mock = Mock()
    mock.server = "http://0.0.0.0:3333"
    return mock


@pytest.fixture
def user_lookup() -> UserNameToIriLookup:
    lookup = UserNameToIriLookup()
    lookup.add_iri("testuser1", USER_1_IRI)
    lookup.add_iri("testuser2", USER_2_IRI)
    return lookup


@pytest.fixture
def group_lookup_with_groups() -> GroupNameToIriLookup:
    return GroupNameToIriLookup(
        name2iri={
            "editors": "http://rdfh.ch/groups/4123/editors",
            "readers": "http://rdfh.ch/groups/4123/readers",
            "reviewers": "http://rdfh.ch/groups/4123/reviewers",
        },
        shortname=SHORTNAME,
    )


class TestConstructGroupLookup:
    def test_filters_by_project_iri(self, all_groups: list[dict[str, Any]]):
        result = _construct_group_lookup(all_groups, PROJECT_IRI, SHORTNAME)

        assert len(result.name2iri) == 4
        assert result.check_exists("testgroupEditors")
        assert result.check_exists(f"{SHORTNAME}:testgroupEditors")
        assert result.check_exists("testgroupReaders")
        assert result.check_exists(f"{SHORTNAME}:testgroupReaders")
        assert not result.check_exists("otherProjectGroup")

    def test_maps_names_to_iris_correctly(self, all_groups: list[dict[str, Any]]):
        result = _construct_group_lookup(all_groups, PROJECT_IRI, SHORTNAME)
        assert result.get_iri("testgroupEditors") == "http://rdfh.ch/groups/4123/group1"
        assert result.get_iri("testgroupReaders") == "http://rdfh.ch/groups/4123/group2"
        assert result.get_iri("otherProjectGroup") is None

    def test_empty_groups_list(self):
        result = _construct_group_lookup([], PROJECT_IRI, SHORTNAME)
        assert len(result.name2iri) == 0
        assert isinstance(result, GroupNameToIriLookup)

    def test_no_matching_project(self, all_groups: list[dict[str, Any]]):
        non_existent_project_iri = "http://rdfh.ch/projects/nonExistent"
        result = _construct_group_lookup(all_groups, non_existent_project_iri, SHORTNAME)
        assert len(result.name2iri) == 0

    def test_only_target_project_groups(self):
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
    def test_calls_client_and_constructs_lookup(self, all_groups: list[dict[str, Any]]):
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

    def test_handles_empty_groups(self):
        mock_client = Mock()
        mock_client.get_all_groups.return_value = []
        result = get_existing_group_to_iri_lookup(mock_client, PROJECT_IRI, SHORTNAME)
        mock_client.get_all_groups.assert_called_once()
        assert isinstance(result, GroupNameToIriLookup)
        assert len(result.name2iri) == 0

    def test_integration_with_mock_client(self):
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
    def test_successful_creation(self, parsed_group_1: ParsedGroup, mock_group_client: Mock):
        expected_iri = "http://rdfh.ch/groups/4123/newGroup"
        mock_group_client.create_new_group.return_value = expected_iri
        result = _create_one_group(parsed_group_1, mock_group_client, PROJECT_IRI)
        assert result == expected_iri
        mock_group_client.create_new_group.assert_called_once()

    def test_failed_creation_returns_problem(self, parsed_group_1: ParsedGroup, mock_group_client: Mock):
        mock_group_client.create_new_group.return_value = None
        result = _create_one_group(parsed_group_1, mock_group_client, PROJECT_IRI)
        assert isinstance(result, UploadProblem)
        assert result.problematic_object == "editors"
        assert result.problem == ProblemType.GROUP_COULD_NOT_BE_CREATED


class TestCreateGroups:
    def test_creates_all_new_groups(
        self, parsed_groups: list[ParsedGroup], mock_group_client: Mock, empty_group_lookup: GroupNameToIriLookup
    ):
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
    ):
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
    ):
        mock_group_client.create_new_group.side_effect = [None, "http://rdfh.ch/groups/4123/readers"]
        result_lookup, problems = create_groups(parsed_groups, mock_group_client, PROJECT_IRI, empty_group_lookup)
        assert isinstance(problems, CollectedProblems)
        assert len(problems.problems) == 1
        assert problems.problems[0].problematic_object == "editors"
        assert problems.problems[0].problem == ProblemType.GROUP_COULD_NOT_BE_CREATED
        assert not result_lookup.check_exists("editors")
        assert result_lookup.check_exists("readers")

    def test_mixed_scenario(self, mock_group_client: Mock):
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

    def test_all_groups_already_exist(self, parsed_groups: list[ParsedGroup], mock_group_client: Mock):
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


class TestCreateOneUser:
    def test_creates_new_user(self, parsed_user_1: ParsedUser, mock_user_client: Mock):
        mock_user_client.get_user_iri_by_username.return_value = None
        mock_user_client.post_new_user.return_value = USER_1_IRI
        result = _create_one_user(parsed_user_1, mock_user_client)
        assert result == USER_1_IRI
        mock_user_client.get_user_iri_by_username.assert_called_once_with("testuser1")
        mock_user_client.post_new_user.assert_called_once()

    def test_returns_existing_user_iri(self, parsed_user_1: ParsedUser, mock_user_client: Mock):
        mock_user_client.get_user_iri_by_username.return_value = USER_2_IRI
        result = _create_one_user(parsed_user_1, mock_user_client)
        assert result == USER_2_IRI
        mock_user_client.get_user_iri_by_username.assert_called_once_with("testuser1")
        mock_user_client.post_new_user.assert_not_called()

    def test_returns_none_when_creation_fails(self, parsed_user_1: ParsedUser, mock_user_client: Mock):
        mock_user_client.get_user_iri_by_username.return_value = None
        mock_user_client.post_new_user.return_value = None
        result = _create_one_user(parsed_user_1, mock_user_client)
        assert result is None
        mock_user_client.get_user_iri_by_username.assert_called_once_with("testuser1")
        mock_user_client.post_new_user.assert_called_once()


class TestCreateAllUsers:
    def test_creates_all_new_users_successfully(self, parsed_users: list[ParsedUser], mock_user_client: Mock):
        mock_user_client.get_user_iri_by_username.return_value = None
        mock_user_client.post_new_user.side_effect = [USER_1_IRI, USER_2_IRI]
        lookup, problems = _create_all_users(parsed_users, mock_user_client)
        assert len(problems) == 0
        assert lookup.get_iri("testuser1") == USER_1_IRI
        assert lookup.get_iri("testuser2") == USER_2_IRI
        assert mock_user_client.post_new_user.call_count == 2

    def test_handles_existing_users(self, parsed_users: list[ParsedUser], mock_user_client: Mock):
        mock_user_client.get_user_iri_by_username.side_effect = [USER_1_IRI, None]
        mock_user_client.post_new_user.return_value = USER_2_IRI
        lookup, problems = _create_all_users(parsed_users, mock_user_client)
        assert len(problems) == 0
        assert lookup.get_iri("testuser1") == USER_1_IRI
        assert lookup.get_iri("testuser2") == USER_2_IRI
        assert mock_user_client.post_new_user.call_count == 1

    def test_handles_creation_failures(self, parsed_users: list[ParsedUser], mock_user_client: Mock):
        mock_user_client.get_user_iri_by_username.return_value = None
        mock_user_client.post_new_user.side_effect = [None, USER_2_IRI]
        lookup, problems = _create_all_users(parsed_users, mock_user_client)
        assert len(problems) == 1
        assert problems[0].problematic_object == "testuser1"
        assert problems[0].problem == ProblemType.USER_COULD_NOT_BE_CREATED
        assert lookup.get_iri("testuser1") is None
        assert lookup.get_iri("testuser2") == USER_2_IRI

    def test_handles_all_failures(self, parsed_users: list[ParsedUser], mock_user_client: Mock):
        mock_user_client.get_user_iri_by_username.return_value = None
        mock_user_client.post_new_user.return_value = None
        _, problems = _create_all_users(parsed_users, mock_user_client)
        assert len(problems) == 2
        assert problems[0].problematic_object == "testuser1"
        assert problems[1].problematic_object == "testuser2"
        assert all(p.problem == ProblemType.USER_COULD_NOT_BE_CREATED for p in problems)


class TestAddOneMembership:
    def test_adds_regular_member_successfully(
        self, user_membership_regular: ParsedUserMemberShipInfo, mock_user_client: Mock
    ):
        mock_user_client.add_user_as_project_member.return_value = True
        problems = _add_one_membership(user_membership_regular, USER_2_IRI, PROJECT_IRI, mock_user_client)
        assert len(problems) == 0
        mock_user_client.add_user_as_project_member.assert_called_once_with(USER_2_IRI, PROJECT_IRI)
        mock_user_client.add_user_as_project_admin.assert_not_called()

    def test_adds_admin_member_successfully(
        self, user_membership_admin: ParsedUserMemberShipInfo, mock_user_client: Mock
    ):
        mock_user_client.add_user_as_project_member.return_value = True
        mock_user_client.add_user_as_project_admin.return_value = True
        problems = _add_one_membership(user_membership_admin, USER_1_IRI, PROJECT_IRI, mock_user_client)
        assert len(problems) == 0
        mock_user_client.add_user_as_project_member.assert_called_once_with(USER_1_IRI, PROJECT_IRI)
        mock_user_client.add_user_as_project_admin.assert_called_once_with(USER_1_IRI, PROJECT_IRI)

    def test_handles_member_addition_failure(
        self, user_membership_regular: ParsedUserMemberShipInfo, mock_user_client: Mock
    ):
        mock_user_client.add_user_as_project_member.return_value = False
        problems = _add_one_membership(user_membership_regular, USER_2_IRI, PROJECT_IRI, mock_user_client)
        assert len(problems) == 1
        assert problems[0].problematic_object == "testuser2"
        assert problems[0].problem == ProblemType.PROJECT_MEMBERSHIP_COULD_NOT_BE_ADDED

    def test_handles_admin_addition_failure(
        self, user_membership_admin: ParsedUserMemberShipInfo, mock_user_client: Mock
    ):
        mock_user_client.add_user_as_project_member.return_value = True
        mock_user_client.add_user_as_project_admin.return_value = False
        problems = _add_one_membership(user_membership_admin, USER_1_IRI, PROJECT_IRI, mock_user_client)
        assert len(problems) == 1
        assert problems[0].problematic_object == "testuser1"
        assert problems[0].problem == ProblemType.PROJECT_ADMIN_COULD_NOT_BE_ADDED

    def test_handles_both_membership_and_admin_failures(
        self, user_membership_admin: ParsedUserMemberShipInfo, mock_user_client: Mock
    ):
        mock_user_client.add_user_as_project_member.return_value = False
        mock_user_client.add_user_as_project_admin.return_value = False
        problems = _add_one_membership(user_membership_admin, USER_1_IRI, PROJECT_IRI, mock_user_client)
        assert len(problems) == 2
        assert problems[0].problem == ProblemType.PROJECT_MEMBERSHIP_COULD_NOT_BE_ADDED
        assert problems[1].problem == ProblemType.PROJECT_ADMIN_COULD_NOT_BE_ADDED


class TestAddUserToGroups:
    def test_adds_user_to_all_groups_successfully(
        self,
        user_membership_admin: ParsedUserMemberShipInfo,
        mock_user_client: Mock,
        group_lookup_with_groups: GroupNameToIriLookup,
    ):
        mock_user_client.add_user_to_custom_groups.return_value = True
        problems = _add_user_to_groups(user_membership_admin, USER_1_IRI, mock_user_client, group_lookup_with_groups)
        assert len(problems) == 0
        mock_user_client.add_user_to_custom_groups.assert_called_once_with(
            USER_1_IRI,
            ["http://rdfh.ch/groups/4123/editors", "http://rdfh.ch/groups/4123/reviewers"],
        )

    def test_handles_group_addition_failure(
        self,
        user_membership_admin: ParsedUserMemberShipInfo,
        mock_user_client: Mock,
        group_lookup_with_groups: GroupNameToIriLookup,
    ):
        mock_user_client.add_user_to_custom_groups.return_value = False
        problems = _add_user_to_groups(user_membership_admin, USER_1_IRI, mock_user_client, group_lookup_with_groups)
        assert len(problems) == 1
        assert problems[0].problematic_object == "testuser1"
        assert problems[0].problem == ProblemType.USER_COULD_NOT_BE_ADDED_TO_GROUP

    def test_handles_groups_not_found(self, mock_user_client: Mock, group_lookup_with_groups: GroupNameToIriLookup):
        membership = ParsedUserMemberShipInfo(username="testuser1", is_admin=False, groups=["nonexistent"])
        problems = _add_user_to_groups(membership, USER_1_IRI, mock_user_client, group_lookup_with_groups)
        assert len(problems) == 1
        assert problems[0].problematic_object == "testuser1"
        assert problems[0].problem == ProblemType.USER_GROUPS_NOT_FOUND
        mock_user_client.add_user_to_custom_groups.assert_not_called()

    def test_handles_mixed_found_and_not_found_groups(
        self, mock_user_client: Mock, group_lookup_with_groups: GroupNameToIriLookup
    ):
        membership = ParsedUserMemberShipInfo(
            username="testuser1", is_admin=False, groups=["editors", "nonexistent", "readers"]
        )
        mock_user_client.add_user_to_custom_groups.return_value = True
        problems = _add_user_to_groups(membership, USER_1_IRI, mock_user_client, group_lookup_with_groups)
        assert len(problems) == 1
        assert problems[0].problem == ProblemType.USER_GROUPS_NOT_FOUND
        mock_user_client.add_user_to_custom_groups.assert_called_once_with(
            USER_1_IRI,
            ["http://rdfh.ch/groups/4123/editors", "http://rdfh.ch/groups/4123/readers"],
        )

    def test_handles_no_groups(self, mock_user_client: Mock, group_lookup_with_groups: GroupNameToIriLookup):
        membership = ParsedUserMemberShipInfo(username="testuser1", is_admin=False, groups=[])
        problems = _add_user_to_groups(membership, USER_1_IRI, mock_user_client, group_lookup_with_groups)
        assert len(problems) == 0
        mock_user_client.add_user_to_custom_groups.assert_not_called()

    def test_handles_both_addition_failure_and_groups_not_found(
        self, mock_user_client: Mock, group_lookup_with_groups: GroupNameToIriLookup
    ):
        membership = ParsedUserMemberShipInfo(username="testuser1", is_admin=False, groups=["editors", "nonexistent"])
        mock_user_client.add_user_to_custom_groups.return_value = False
        problems = _add_user_to_groups(membership, USER_1_IRI, mock_user_client, group_lookup_with_groups)
        assert len(problems) == 2
        assert problems[0].problem == ProblemType.USER_COULD_NOT_BE_ADDED_TO_GROUP
        assert problems[1].problem == ProblemType.USER_GROUPS_NOT_FOUND


class TestAddAllMemberships:
    def test_adds_all_memberships_successfully(
        self,
        user_memberships: list[ParsedUserMemberShipInfo],
        user_lookup: UserNameToIriLookup,
        group_lookup_with_groups: GroupNameToIriLookup,
        mock_user_client: Mock,
    ):
        mock_user_client.add_user_as_project_member.return_value = True
        mock_user_client.add_user_as_project_admin.return_value = True
        mock_user_client.add_user_to_custom_groups.return_value = True
        problems = _add_all_memberships(
            user_memberships, user_lookup, group_lookup_with_groups, mock_user_client, PROJECT_IRI
        )
        assert len(problems) == 0
        assert mock_user_client.add_user_as_project_member.call_count == 2
        assert mock_user_client.add_user_as_project_admin.call_count == 1
        assert mock_user_client.add_user_to_custom_groups.call_count == 2

    def test_skips_users_not_in_lookup(
        self,
        group_lookup_with_groups: GroupNameToIriLookup,
        mock_user_client: Mock,
    ):
        memberships = [ParsedUserMemberShipInfo(username="nonexistentuser", is_admin=True, groups=["editors"])]
        empty_lookup = UserNameToIriLookup()
        problems = _add_all_memberships(
            memberships, empty_lookup, group_lookup_with_groups, mock_user_client, PROJECT_IRI
        )
        assert len(problems) == 0
        mock_user_client.add_user_as_project_member.assert_not_called()
        mock_user_client.add_user_as_project_admin.assert_not_called()
        mock_user_client.add_user_to_custom_groups.assert_not_called()

    def test_handles_membership_failures(
        self,
        user_memberships: list[ParsedUserMemberShipInfo],
        user_lookup: UserNameToIriLookup,
        group_lookup_with_groups: GroupNameToIriLookup,
        mock_user_client: Mock,
    ):
        mock_user_client.add_user_as_project_member.return_value = False
        mock_user_client.add_user_as_project_admin.return_value = False
        mock_user_client.add_user_to_custom_groups.return_value = False
        problems = _add_all_memberships(
            user_memberships, user_lookup, group_lookup_with_groups, mock_user_client, PROJECT_IRI
        )
        assert len(problems) == 5
        membership_problems = [p for p in problems if p.problem == ProblemType.PROJECT_MEMBERSHIP_COULD_NOT_BE_ADDED]
        admin_problems = [p for p in problems if p.problem == ProblemType.PROJECT_ADMIN_COULD_NOT_BE_ADDED]
        group_problems = [p for p in problems if p.problem == ProblemType.USER_COULD_NOT_BE_ADDED_TO_GROUP]
        assert len(membership_problems) == 2
        assert len(admin_problems) == 1
        assert len(group_problems) == 2


class TestCreateUsers:
    def test_creates_users_and_adds_memberships_successfully(
        self,
        parsed_users: list[ParsedUser],
        user_memberships: list[ParsedUserMemberShipInfo],
        group_lookup_with_groups: GroupNameToIriLookup,
        mock_auth: Mock,
    ):
        mock_client = Mock()
        mock_client.get_user_iri_by_username.return_value = None
        mock_client.post_new_user.side_effect = [USER_1_IRI, USER_2_IRI]
        mock_client.add_user_as_project_member.return_value = True
        mock_client.add_user_as_project_admin.return_value = True
        mock_client.add_user_to_custom_groups.return_value = True
        mock_user_client_class = Mock(return_value=mock_client)
        with patch("dsp_tools.commands.create.create_on_server.group_users.UserClientLive", mock_user_client_class):
            result = create_users(parsed_users, user_memberships, group_lookup_with_groups, mock_auth, PROJECT_IRI)
        assert result is None
        mock_user_client_class.assert_called_once_with("http://0.0.0.0:3333", mock_auth)

    def test_handles_mixed_success_and_failure(
        self,
        parsed_users: list[ParsedUser],
        user_memberships: list[ParsedUserMemberShipInfo],
        group_lookup_with_groups: GroupNameToIriLookup,
        mock_auth: Mock,
    ):
        mock_client = Mock()
        mock_client.get_user_iri_by_username.return_value = None
        mock_client.post_new_user.side_effect = [None, USER_2_IRI]
        mock_client.add_user_as_project_member.return_value = True
        mock_client.add_user_as_project_admin.return_value = True
        mock_client.add_user_to_custom_groups.return_value = True
        mock_user_client_class = Mock(return_value=mock_client)
        with patch("dsp_tools.commands.create.create_on_server.group_users.UserClientLive", mock_user_client_class):
            result = create_users(parsed_users, user_memberships, group_lookup_with_groups, mock_auth, PROJECT_IRI)
        assert isinstance(result, CollectedProblems)
        assert len(result.problems) == 1
        assert result.problems[0].problem == ProblemType.USER_COULD_NOT_BE_CREATED


if __name__ == "__main__":
    pytest.main([__file__])
