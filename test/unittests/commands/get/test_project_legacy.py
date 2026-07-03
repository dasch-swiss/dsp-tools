from unittest.mock import Mock

import pytest

from dsp_tools.commands.get.legacy_models.project import Project


def _base_json_obj() -> dict[str, object]:
    return {
        "id": "http://rdfh.ch/projects/test",
        "shortcode": "0FF0",
        "shortname": "test_project",
        "longname": "Test Project",
        "description": [{"language": "en", "value": "This is a test project"}],
        "keywords": ["test"],
        "ontologies": ["http://rdfh.ch/ontologies/test"],
        "selfjoin": False,
        "status": True,
    }


class TestDataSideLegalInfo:
    def test_from_json_obj_with_all_legal_fields(self) -> None:
        json_obj = _base_json_obj() | {
            "dataLicense": "http://rdfh.ch/licenses/cc-by-4.0",
            "dataCopyrightHolder": "The Holder",
            "defaultDataAuthorship": ["Author One", "Author Two"],
        }
        project = Project.fromJsonObj(Mock(), json_obj)
        result = project.createDefinitionFileObj()
        assert result["data_license"] == "http://rdfh.ch/licenses/cc-by-4.0"
        assert result["data_copyright_holder"] == "The Holder"
        assert result["default_data_authorship"] == ["Author One", "Author Two"]

    def test_from_json_obj_without_legal_fields(self) -> None:
        project = Project.fromJsonObj(Mock(), _base_json_obj())
        result = project.createDefinitionFileObj()
        assert "data_license" not in result
        assert "data_copyright_holder" not in result
        assert "default_data_authorship" not in result

    def test_create_definition_file_obj_omits_empty_authorship(self) -> None:
        json_obj = _base_json_obj() | {
            "dataLicense": "http://rdfh.ch/licenses/cc-by-4.0",
            "defaultDataAuthorship": [],
        }
        project = Project.fromJsonObj(Mock(), json_obj)
        result = project.createDefinitionFileObj()
        assert result["data_license"] == "http://rdfh.ch/licenses/cc-by-4.0"
        assert "data_copyright_holder" not in result
        assert "default_data_authorship" not in result


if __name__ == "__main__":
    pytest.main([__file__])
