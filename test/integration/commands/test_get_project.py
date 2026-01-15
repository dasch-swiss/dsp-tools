import pytest

from dsp_tools.commands.get.legacy_models.project import Project
from dsp_tools.legacy_models.langstring import Languages
from dsp_tools.legacy_models.langstring import create_lang_string


@pytest.fixture
def project() -> Project:
    return Project(
        iri="http://rdfh.ch/test",
        shortcode="0FF0",
        shortname="test_project",
        longname="Test Project",
        description=create_lang_string(
            {
                Languages.EN: "This is a test project",
                Languages.DE: "Das ist ein Testprojekt",
            }
        ),
        keywords=frozenset(),
        enabled_licenses=frozenset(),
    )


def test_return_values(project: Project) -> None:
    assert project.iri == "http://rdfh.ch/test"
    assert project.shortcode == "0FF0"
    assert project.shortname == "test_project"
    assert project.longname == "Test Project"
    assert project.description["en"] == "This is a test project"
    assert project.description["de"] == "Das ist ein Testprojekt"
    assert project.keywords == frozenset()


if __name__ == "__main__":
    pytest.main([__file__])
