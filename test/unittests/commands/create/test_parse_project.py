# mypy: disable-error-code="no-untyped-def"

from pathlib import Path

from dsp_tools.commands.create.models.parsed_ontology import ParsedOntology
from dsp_tools.commands.create.models.parsed_project import ParsedGroup
from dsp_tools.commands.create.models.parsed_project import ParsedList
from dsp_tools.commands.create.models.parsed_project import ParsedPermissions
from dsp_tools.commands.create.models.parsed_project import ParsedProject
from dsp_tools.commands.create.models.parsed_project import ParsedProjectMetadata
from dsp_tools.commands.create.models.parsed_project import ParsedUser
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
        result = _parse_all_ontologies(project_json_create["project"], prefix_lookup)
        assert len(result) == 3
        assert all(isinstance(o, ParsedOntology) for o in result)

        # Check ontology names
        onto_names = [o.name for o in result]
        assert "onto" in onto_names
        assert "second-onto" in onto_names
        assert "in-built" in onto_names

    def test_parse_all_ontologies_systematic(self, project_json_systematic):
        prefix_lookup = create_prefix_lookup(project_json_systematic, "http://0.0.0.0:3333")
        result = _parse_all_ontologies(project_json_systematic["project"], prefix_lookup)

        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(o, ParsedOntology) for o in result)

        # Check ontology names
        onto_names = [o.name for o in result]
        assert "testonto" in onto_names
        assert "testontoPermissions" in onto_names


class TestParseProject:
    def test_parse_project_with_path(self):
        project_path = Path("testdata/json-project/test-project-systematic.json")
        result = parse_project(project_path, "http://0.0.0.0:3333")

        assert isinstance(result, ParsedProject)
        assert isinstance(result.prefixes, dict)
        assert isinstance(result.project_metadata, ParsedProjectMetadata)
        assert isinstance(result.permissions, ParsedPermissions)
        assert isinstance(result.groups, list)
        assert isinstance(result.users, list)
        assert isinstance(result.lists, list)
        assert isinstance(result.ontologies, list)

        # Verify metadata
        assert result.project_metadata.shortcode == "4123"
        assert result.project_metadata.shortname == "systematic-tp"

        # Verify ontologies
        assert len(result.ontologies) == 2

        # Verify lists
        assert len(result.lists) == 2

        # Verify groups and users are present in systematic project
        assert len(result.groups) == 3
        assert len(result.users) == 7

    def test_parse_project_with_str_path(self):
        project_path = "testdata/json-project/test-project-systematic.json"
        result = parse_project(project_path, "http://0.0.0.0:3333")

        assert isinstance(result, ParsedProject)
        assert result.project_metadata.shortcode == "4123"

    def test_parse_project_with_dict(self, project_json_systematic):
        result = parse_project(project_json_systematic, "http://0.0.0.0:3333")

        assert isinstance(result, ParsedProject)
        assert result.project_metadata.shortcode == "4123"

    def test_parse_project_systematic(self):
        project_path = Path("testdata/json-project/test-project-systematic.json")
        result = parse_project(project_path, "http://0.0.0.0:3333")

        assert isinstance(result, ParsedProject)
        assert result.project_metadata.shortcode == "4123"
        assert result.project_metadata.shortname == "systematic-tp"

        # Verify groups
        assert len(result.groups) == 3

        # Verify users
        assert len(result.users) == 7

        # Verify lists
        assert len(result.lists) == 2

        # Verify ontologies
        assert len(result.ontologies) == 2

        # Verify permissions overrule
        assert result.permissions.default_permissions_overrule is not None

    def test_parse_project_complete_structure(self):
        project_path = Path("testdata/json-project/test-project-systematic.json")
        result = parse_project(project_path, "http://0.0.0.0:3333")

        # Verify all components are parsed correctly
        assert isinstance(result.prefixes, dict)
        assert len(result.prefixes) > 0
        assert "knora-api" in result.prefixes

        assert result.project_metadata.shortcode == "4123"
        assert result.project_metadata.shortname == "systematic-tp"
        assert result.project_metadata.longname == "systematic test project"
        assert len(result.project_metadata.keywords) == 2
        assert len(result.project_metadata.enabled_licenses) == 3

        assert result.permissions.default_permissions == "public"
        assert result.permissions.default_permissions_overrule is not None

        assert len(result.groups) == 3
        assert all(isinstance(g, ParsedGroup) for g in result.groups)

        assert len(result.users) == 7
        assert all(isinstance(u, ParsedUser) for u in result.users)

        assert len(result.lists) == 2
        assert all(isinstance(lst, ParsedList) for lst in result.lists)

        assert len(result.ontologies) == 2
        assert all(isinstance(o, ParsedOntology) for o in result.ontologies)

    def test_parse_project_prefixes_created(self):
        project_path = Path("testdata/json-project/test-project-systematic.json")
        result = parse_project(project_path, "http://0.0.0.0:3333")

        # Verify prefixes are created with correct structure
        assert "knora-api" in result.prefixes
        assert "testonto" in result.prefixes
        assert "testontoPermissions" in result.prefixes
        assert "foaf" in result.prefixes
        assert "externalOnto" in result.prefixes
        assert "dcterms" in result.prefixes

        # Verify prefix values are IRIs
        assert result.prefixes["knora-api"].startswith("http")
        assert result.prefixes["testonto"].startswith("http")
