"""end to end tests for project class"""

import unittest

import pytest

from dsp_tools.commands.project.models.project import Project
from dsp_tools.models.langstring import LangString, Languages
from dsp_tools.utils.connection import Connection
from dsp_tools.utils.connection_live import ConnectionLive

# ruff: noqa: PT009 (pytest-unittest-assertion) (remove this line when pytest is used instead of unittest)


# https://stackoverflow.com/questions/26405380/how-do-i-correctly-setup-and-teardown-for-my-pytest-class-with-tests
# MockConnection
# Move to unittests


class TestProject(unittest.TestCase):
    logo_file = "logo.gif"
    con: Connection

    def setUp(self) -> None:
        """
        Creates a connection to DSP-API.
        For each test method, a new TestCase instance is created, so setUp() is executed before each test method.
        """
        self.con = ConnectionLive(server="http://0.0.0.0:3333")
        self.con.login(email="root@example.com", password="test")

    def tearDown(self) -> None:
        """
        Logs out from DSP-API.
        For each test method, a new TestCase instance is created, so tearDown() is executed after each test method.
        """
        self.con.logout()

    def test_Project(self) -> None:
        project = Project(
            con=self.con,
            iri="http://rdfh.ch/test",
            shortcode="0FF0",
            shortname="test_project",
            longname="Test Project",
            description=LangString({Languages.EN: "This is a test project", Languages.DE: "Das ist ein Testprojekt"}),
            keywords={"test", "project"},
            selfjoin=False,
            status=True,
            logo=self.logo_file,
        )

        self.assertIsNotNone(project)
        self.assertEqual(project.iri, "http://rdfh.ch/test")
        self.assertEqual(project.shortcode, "0FF0")
        self.assertEqual(project.shortname, "test_project")
        self.assertEqual(project.longname, "Test Project")
        self.assertEqual(project.description["en"], "This is a test project")
        self.assertEqual(project.description["de"], "Das ist ein Testprojekt")
        self.assertEqual(project.selfjoin, False)
        self.assertEqual(project.status, True)
        self.assertEqual(project.keywords, {"test", "project"})

    def test_project_read(self) -> None:
        project = Project(con=self.con, iri="http://rdfh.ch/projects/0001").read()

        self.assertEqual(project.iri, "http://rdfh.ch/projects/0001")
        self.assertEqual(project.shortcode, "0001")
        self.assertEqual(project.shortname, "anything")
        self.assertEqual(project.longname, "Anything Project")
        self.assertEqual(project.description[None], "Anything Project")
        self.assertEqual(project.selfjoin, False)
        self.assertEqual(project.status, True)

    def test_project_create(self) -> None:
        project = Project(
            con=self.con,
            shortcode="0FF0",
            shortname="new_project",
            longname="New test project",
            description=LangString({Languages.EN: "New project", Languages.DE: "Neues Projekt"}),
            keywords={"test", "project", "new"},
            selfjoin=False,
            status=True,
            logo=self.logo_file,
        )
        new_project = project.create()
        self.assertIsNotNone(new_project)
        self.assertEqual(new_project.shortcode, "0FF0")
        self.assertEqual(new_project.shortname, "new_project")
        self.assertEqual(new_project.longname, "New test project")
        self.assertEqual(new_project.description["en"], "New project")
        self.assertEqual(new_project.description["de"], "Neues Projekt")
        self.assertEqual(new_project.keywords, {"test", "project", "new"})
        self.assertEqual(new_project.selfjoin, False)
        self.assertEqual(new_project.status, True)
        self.assertEqual(new_project.keywords, {"test", "project", "new"})


if __name__ == "__main__":
    pytest.main([__file__])
