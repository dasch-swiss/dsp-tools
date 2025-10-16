# mypy: disable-error-code="no-untyped-def"

from dsp_tools.commands.create.models.parsed_project import ParsedGroup
from dsp_tools.commands.create.models.parsed_project import ParsedPermissions
from dsp_tools.commands.create.models.parsed_project import ParsedProject
from dsp_tools.commands.create.models.parsed_project import ParsedProjectMetadata
from dsp_tools.commands.create.parsing.parse_project import _parse_all_ontologies
from dsp_tools.commands.create.parsing.parse_project import _parse_groups
from dsp_tools.commands.create.parsing.parse_project import _parse_lists
from dsp_tools.commands.create.parsing.parse_project import _parse_metadata
from dsp_tools.commands.create.parsing.parse_project import _parse_permissions
from dsp_tools.commands.create.parsing.parse_project import _parse_users
from dsp_tools.commands.create.parsing.parse_project import parse_project
from dsp_tools.commands.create.parsing.parsing_utils import create_prefix_lookup


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
    def test_parse_permissions_without_overrule(self, project_json_create):
        result = _parse_permissions(project_json_create["project"])
        assert isinstance(result, ParsedPermissions)
        assert result.default_permissions == "public"
        assert result.default_permissions_overrule is None

    def test_parse_permissions_with_overrule(self, project_json_systematic):
        result = _parse_permissions(project_json_systematic["project"])
        assert isinstance(result, ParsedPermissions)
        assert result.default_permissions == "public"
        assert result.default_permissions_overrule is not None
        assert "private" in result.default_permissions_overrule
        assert "limited_view" in result.default_permissions_overrule
        assert result.default_permissions_overrule["limited_view"] == "all"


class TestParseGroups:
    def test_parse_groups_empty(self, project_json_create):
        result = _parse_groups(project_json_create["project"])
        assert len(result) == 0

    def test_parse_groups_with_groups(self, project_json_systematic):
        result = _parse_groups(project_json_systematic["project"])
        assert len(result) == 3
        assert all(isinstance(g, ParsedGroup) for g in result)

    def test_parse_groups_missing_key(self, minimal_project_json):
        result = _parse_groups(minimal_project_json)
        assert len(result) == 0


class TestParseUsers:
    def test_parse_users_empty(self, project_json_create):
        result = _parse_users(project_json_create["project"])
        assert len(result) == 0

    def test_parse_users_with_users(self, project_json_systematic):
        result = _parse_users(project_json_systematic["project"])
        assert len(result) == 7

    def test_parse_users_missing_key(self, minimal_project_json):
        result = _parse_users(minimal_project_json)
        assert len(result) == 0


class TestParseLists:
    def test_parse_lists_empty(self, minimal_project_json):
        result = _parse_lists(minimal_project_json)
        assert len(result) == 0

    def test_parse_lists_with_lists(self, project_json_create):
        result = _parse_lists(project_json_create["project"])
        assert len(result) == 2


class TestParseAllOntologies:
    def test_parse_all_ontologies_create_project(self, project_json_create):
        prefix_lookup = create_prefix_lookup(project_json_create, "http://0.0.0.0:3333")
        ontos, failures = _parse_all_ontologies(project_json_create["project"], prefix_lookup)
        assert len(ontos) == 3
        assert len(failures) == 0

    def test_parse_all_ontologies_systematic(self):
        pass
        # TODO: implement a failure route


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
        assert len(result.groups) == 3
        assert len(result.users) == 7

    def test_parse_project_failure(self):
        pass
        # TODO: implement a failure route
