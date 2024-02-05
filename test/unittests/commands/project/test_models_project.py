from test.unittests.commands.xmlupload.connection_mock import ConnectionMockBase

import pytest

from dsp_tools.commands.project.models.project import Project
from dsp_tools.models.langstring import LangString, Languages
from dsp_tools.utils.connection import Connection


@pytest.fixture()
def con() -> Connection:
    return ConnectionMockBase()


@pytest.fixture()
def project(con: Connection) -> Project:
    return Project(
        con=con,
        iri="http://rdfh.ch/test",
        shortcode="0FF0",
        shortname="test_project",
        longname="Test Project",
        description=LangString({Languages.EN: "This is a test project", Languages.DE: "Das ist ein Testprojekt"}),
        keywords=set(),
        selfjoin=False,
        status=True,
        logo="logo.gif",
    )


def test_return_values(project: Project) -> None:
    assert project.iri == "http://rdfh.ch/test"
    assert project.shortcode == "0FF0"
    assert project.shortname == "test_project"
    assert project.longname == "Test Project"
    assert project.description["en"] == "This is a test project"
    assert project.description["de"] == "Das ist ein Testprojekt"
    assert project.selfjoin is False
    assert project.status is True
    assert project.keywords == set()


def test_to_json_obj_create(project: Project) -> None:
    res_json = project._toJsonObj_create()
    expected = {
        "shortcode": "0FF0",
        "shortname": "test_project",
        "longname": "Test Project",
        "description": [
            {"language": "en", "value": "This is a test project"},
            {"language": "de", "value": "Das ist ein Testprojekt"},
        ],
        "selfjoin": False,
        "status": True,
    }
    assert res_json == expected


if __name__ == "__main__":
    pytest.main([__file__])
