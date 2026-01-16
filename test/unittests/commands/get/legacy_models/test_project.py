from typing import Any

import pytest

from dsp_tools.commands.get.legacy_models.project import Project
from dsp_tools.commands.get.legacy_models.project import create_project_from_json
from dsp_tools.error.exceptions import BaseError
from dsp_tools.legacy_models.langstring import create_lang_string


def _make_valid_project_json() -> dict[str, Any]:
    return {
        "id": "http://rdfh.ch/projects/0001",
        "shortcode": "0001",
        "shortname": "testproj",
        "longname": "Test Project",
        "description": [{"language": "en", "value": "A test project"}],
        "keywords": ["test", "project"],
        "enabledLicenses": ["CC-BY-4.0"],
    }


class TestCreateProjectFromJson:
    """Tests for the create_project_from_json factory function."""

    def test_valid_json(self) -> None:
        json_obj = _make_valid_project_json()
        project = create_project_from_json(json_obj)
        assert project.iri == "http://rdfh.ch/projects/0001"
        assert project.shortcode == "0001"
        assert project.shortname == "testproj"
        assert project.longname == "Test Project"
        assert project.keywords == frozenset({"test", "project"})
        assert project.enabled_licenses == frozenset({"CC-BY-4.0"})

    def test_missing_optional_fields_use_defaults(self) -> None:
        # Keywords and enabledLicenses are optional, default to empty frozenset
        json_obj = _make_valid_project_json()
        del json_obj["keywords"]
        del json_obj["enabledLicenses"]
        project = create_project_from_json(json_obj)
        assert project.keywords == frozenset()
        assert project.enabled_licenses == frozenset()

    def test_missing_description_uses_empty_langstring(self) -> None:
        json_obj = _make_valid_project_json()
        del json_obj["description"]
        project = create_project_from_json(json_obj)
        assert project.description == create_lang_string()

    @pytest.mark.parametrize(
        ("missing_field", "error_fragment"),
        [
            ("id", "iri is missing"),
            ("shortcode", "Shortcode is missing"),
            ("shortname", "Shortname is missing"),
            ("longname", "Longname is missing"),
        ],
    )
    def test_missing_required_field(self, missing_field: str, error_fragment: str) -> None:
        json_obj = _make_valid_project_json()
        del json_obj[missing_field]
        with pytest.raises(BaseError, match=error_fragment):
            create_project_from_json(json_obj)


class TestProjectToDefinitionFileObj:
    """Tests for Project.to_definition_file_obj serialization."""

    def test_frozenset_converted_to_list(self) -> None:
        # Verifies that frozenset fields are converted to lists for JSON serialization
        project = Project(
            iri="http://rdfh.ch/projects/0001",
            shortcode="0001",
            shortname="testproj",
            longname="Test Project",
            description=create_lang_string({"en": "Test"}),
            keywords=frozenset({"kw1", "kw2"}),
            enabled_licenses=frozenset({"CC-BY-4.0"}),
        )
        result = project.to_definition_file_obj()
        assert isinstance(result["keywords"], list)
        assert set(result["keywords"]) == {"kw1", "kw2"}
        assert isinstance(result["enabled_licenses"], list)
        assert result["enabled_licenses"] == ["CC-BY-4.0"]

    def test_serialization_structure(self) -> None:
        project = Project(
            iri="http://rdfh.ch/projects/0001",
            shortcode="0001",
            shortname="testproj",
            longname="Test Project",
            description=create_lang_string({"en": "Test"}),
            keywords=frozenset(),
            enabled_licenses=frozenset(),
        )
        result = project.to_definition_file_obj()
        assert result["shortcode"] == "0001"
        assert result["shortname"] == "testproj"
        assert result["longname"] == "Test Project"
        assert "descriptions" in result
        # IRI should not be in definition file output
        assert "iri" not in result
        assert "id" not in result
