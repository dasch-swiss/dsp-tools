from test.unittests.commands.xmlupload.connection_mock import ConnectionMockBase

import pytest

from dsp_tools.commands.project.models.project import Project
from dsp_tools.models.langstring import LangString, Languages
from dsp_tools.utils.connection import Connection


@pytest.fixture()
def con() -> Connection:
    return ConnectionMockBase()


def test_return_values(con: Connection) -> None:
    project = Project(
        con=con,
        iri="http://rdfh.ch/test",
        shortcode="0FF0",
        shortname="test_project",
        longname="Test Project",
        description=LangString({Languages.EN: "This is a test project", Languages.DE: "Das ist ein Testprojekt"}),
        keywords={"test", "project"},
        selfjoin=False,
        status=True,
        logo="logo.gif",
    )

    assert project.iri == "http://rdfh.ch/test"
    assert project.shortcode == "0FF0"
    assert project.shortname == "test_project"
    assert project.longname == "Test Project"
    assert project.description["en"] == "This is a test project"
    assert project.description["de"] == "Das ist ein Testprojekt"
    assert project.selfjoin is False
    assert project.status is True


if __name__ == "__main__":
    pytest.main([__file__])
