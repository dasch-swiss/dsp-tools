# mypy: disable-error-code="no-untyped-def"

from dsp_tools.commands.create.models.create_problems import InputProblem
from dsp_tools.commands.create.models.create_problems import InputProblemType
from dsp_tools.commands.create.models.parsed_project import DefaultPermissions
from dsp_tools.commands.create.models.parsed_project import ParsedPermissions
from dsp_tools.commands.create.models.parsed_project import ParsedProject
from dsp_tools.commands.create.models.parsed_project import ParsedProjectMetadata
from dsp_tools.commands.create.models.parsed_project import ParsedUser
from dsp_tools.commands.create.models.parsed_project import ParsedUserMemberShipInfo
from dsp_tools.commands.create.parsing.parse_project import _parse_all_ontologies
from dsp_tools.commands.create.parsing.parse_project import _parse_groups
from dsp_tools.commands.create.parsing.parse_project import _parse_lists
from dsp_tools.commands.create.parsing.parse_project import _parse_metadata
from dsp_tools.commands.create.parsing.parse_project import _parse_one_group
from dsp_tools.commands.create.parsing.parse_project import _parse_one_user
from dsp_tools.commands.create.parsing.parse_project import _parse_permissions
from dsp_tools.commands.create.parsing.parse_project import _parse_users
from dsp_tools.commands.create.parsing.parse_project import parse_project


class TestParseProject:
    def test_parse_project_success(self, project_json_systematic):
        result = parse_project(project_json_systematic, "http://0.0.0.0:3333")
        assert isinstance(result, ParsedProject)
        assert isinstance(result.prefixes, dict)
        assert isinstance(result.project_metadata, ParsedProjectMetadata)
        assert isinstance(result.permissions, ParsedPermissions)
        assert isinstance(result.groups, list)
        assert isinstance(result.users, list)
        assert isinstance(result.lists, list)
        assert isinstance(result.ontologies, list)
        assert result.project_metadata.shortcode == "4123"
        assert result.project_metadata.shortname == "systematic-tp"
        assert len(result.ontologies) == 2
        assert len(result.lists) == 2
        assert len(result.groups) == 2
        assert len(result.users) == 6

    def test_parse_project_failure(self, minimal_failing_project):
        result = parse_project(minimal_failing_project, "http://0.0.0.0:3333")
        assert isinstance(result, list)
        assert len(result) == 1


class TestParseMetadata:
    def test_parse_metadata_complete(self, project_json_systematic):
        result = _parse_metadata(project_json_systematic["project"])
        assert isinstance(result, ParsedProjectMetadata)
        assert result.shortcode == "4123"
        assert result.shortname == "systematic-tp"
        assert result.longname == "systematic test project"
        expected_descriptions = {
            "en": "A systematic test project",
            "de": "Ein systematisches Testprojekt",
            "rm": "Rumantsch descripziun",
        }
        assert result.descriptions == expected_descriptions
        assert result.keywords == ["test", "testing"]
        assert len(result.enabled_licenses) == 3


class TestParsePermissions:
    def test_parse_permissions_without_overrule(self, project_json_create, prefixes):
        result = _parse_permissions(project_json_create["project"], prefixes)
        assert isinstance(result, ParsedPermissions)
        assert result.default_permissions == DefaultPermissions.PRIVATE
        assert result.overrule_private is None
        assert result.overrule_limited_view is False

    def test_parse_permissions_with_overrule_all(self, project_json_systematic, prefixes):
        result = _parse_permissions(project_json_systematic["project"], prefixes)
        assert isinstance(result, ParsedPermissions)
        assert result.default_permissions == DefaultPermissions.PUBLIC
        assert result.overrule_private == ["asdf"]
        assert result.overrule_limited_view is True

    def test_parse_permissions_with_overrule_some(self, prefixes):
        proj = {
            "default_permissions": "public",
            "default_permissions_overrule": {
                "private": ["my-onto:PrivateResource", "my-onto:privateProp"],
                "limited_view": [
                    "my-onto:Image1",
                    "my-onto:Image2",
                ],
            },
        }
        result = _parse_permissions(proj, prefixes)
        assert isinstance(result, ParsedPermissions)
        assert result.default_permissions == "public"
        assert result.overrule_private is None
        assert result.overrule_limited_view is True


class TestParseGroups:
    def test_parse_groups_empty(self, project_json_create):
        result = _parse_groups(project_json_create["project"])
        assert len(result) == 1

    def test_parse_groups_with_groups(self, project_json_systematic):
        result = _parse_groups(project_json_systematic["project"])
        assert len(result) == 2

    def test_parse_groups_missing_key(self, minimal_project_json):
        result = _parse_groups(minimal_project_json)
        assert len(result) == 0

    def test_parse_one_group(self, project_json_create):
        result = _parse_one_group(project_json_create["project"]["groups"][0])
        assert result.name == "testGroup"
        assert len(result.descriptions) == 2
        en_desc = next(x for x in result.descriptions if x.lang == "en")
        assert en_desc.text == "Test group"
        de_desc = next(x for x in result.descriptions if x.lang == "de")
        assert de_desc.text == "Testgruppe"


class TestParseUsers:
    def test_parse_users_empty(self, project_json_create):
        users, memberships, problems = _parse_users(project_json_create["project"])
        assert len(users) == 3
        assert len(memberships) == 3
        assert not problems

    def test_parse_users_with_users(self, project_json_systematic):
        users, memberships, problems = _parse_users(project_json_systematic["project"])
        assert len(users) == 6
        assert len(memberships) == 6
        assert not problems

    def test_parse_users_missing_key(self, minimal_project_json):
        users, memberships, problems = _parse_users(minimal_project_json)
        assert len(users) == 0
        assert len(memberships) == 0
        assert not problems

    def test_only_mandatory(self, project_json_create):
        user = project_json_create["project"]["users"][0]
        result = _parse_one_user(user)
        assert isinstance(result, tuple)
        parsed_u, parsed_mem = result
        assert parsed_u.username == "user_only_mandatory"
        assert parsed_u.email == "user-1@test.org"
        assert parsed_u.given_name == "user"
        assert parsed_u.family_name == "one"
        assert parsed_u.password == "111"
        assert parsed_u.lang == "en"
        assert parsed_mem.username == "user_only_mandatory"
        assert not parsed_mem.is_admin
        assert not parsed_mem.groups

    def test_admin(self, project_json_create):
        user = project_json_create["project"]["users"][1]
        result = _parse_one_user(user)
        assert isinstance(result, tuple)
        parsed_u, parsed_mem = result
        assert parsed_u.username == "User_admin"
        assert parsed_u.email == "user-2@test.org"
        assert parsed_u.given_name == "user"
        assert parsed_u.family_name == "two"
        assert parsed_u.password == "222"
        assert parsed_u.lang == "de"
        assert parsed_mem.username == "User_admin"
        assert parsed_mem.is_admin
        assert not parsed_mem.groups

    def test_with_group(self, project_json_create):
        user = project_json_create["project"]["users"][2]
        result = _parse_one_user(user)
        assert isinstance(result, tuple)
        parsed_u, parsed_mem = result
        assert parsed_u.username == "User_member_and_group"
        assert parsed_u.email == "user-3@test.org"
        assert parsed_u.given_name == "user"
        assert parsed_u.family_name == "three"
        assert parsed_u.password == "333"
        assert parsed_u.lang == "fr"
        assert parsed_mem.username == "User_member_and_group"
        assert not parsed_mem.is_admin
        assert parsed_mem.groups == ["testGroup"]

    def test_password_from_user_dict(self, monkeypatch):
        monkeypatch.setenv("DSP_USER_PASSWORD", "env_password")
        user_dict = {
            "username": "test_user",
            "email": "test@example.com",
            "givenName": "Test",
            "familyName": "User",
            "password": "dict_password",
        }
        result = _parse_one_user(user_dict)
        assert isinstance(result, tuple)
        parsed_u, parsed_mem = result
        assert isinstance(parsed_u, ParsedUser)
        assert isinstance(parsed_mem, ParsedUserMemberShipInfo)
        assert parsed_u.password == "dict_password"
        assert parsed_u.username == "test_user"
        assert parsed_u.email == "test@example.com"
        assert parsed_u.given_name == "Test"
        assert parsed_u.family_name == "User"
        assert parsed_u.lang == "en"

    def test_password_from_env_var(self, monkeypatch):
        monkeypatch.setenv("DSP_USER_PASSWORD", "env_password")
        user_dict = {
            "username": "test_user",
            "email": "test@example.com",
            "givenName": "Test",
            "familyName": "User",
            "password": "",
        }
        result = _parse_one_user(user_dict)
        assert isinstance(result, tuple)
        parsed_u, parsed_mem = result
        assert isinstance(parsed_u, ParsedUser)
        assert isinstance(parsed_mem, ParsedUserMemberShipInfo)
        assert parsed_u.password == "env_password"
        assert parsed_u.username == "test_user"

    def test_no_password_no_env_var(self, monkeypatch):
        monkeypatch.delenv("DSP_USER_PASSWORD", raising=False)
        user_dict = {
            "username": "test_user",
            "email": "test@example.com",
            "givenName": "Test",
            "familyName": "User",
            "password": "",
        }
        result = _parse_one_user(user_dict)
        assert isinstance(result, InputProblem)
        assert result.problematic_object == "test_user"
        assert result.problem == InputProblemType.USER_PASSWORD_NOT_SET


class TestParseLists:
    def test_parse_lists_empty(self, minimal_project_json):
        result, problems = _parse_lists(minimal_project_json)
        assert len(result) == 0
        assert not problems

    def test_parse_lists_with_lists(self, project_json_create):
        result, problems = _parse_lists(project_json_create["project"])
        assert len(result) == 2
        assert not problems


class TestParseAllOntologies:
    def test_parse_all_ontologies_create_project(self, project_json_create, prefixes):
        ontos, failures = _parse_all_ontologies(project_json_create["project"], prefixes)
        assert len(ontos) == 3
        assert len(failures) == 0

    def test_parse_all_ontologies_systematic(self, minimal_failing_project, prefixes):
        ontos, failures = _parse_all_ontologies(minimal_failing_project["project"], prefixes)
        assert len(ontos) == 0
        assert len(failures) == 1
        onto_fail = failures.pop(0)
        assert onto_fail.header == "During the parsing of the ontology 'onto' the following errors occurred"
        assert len(onto_fail.problems) == 1
