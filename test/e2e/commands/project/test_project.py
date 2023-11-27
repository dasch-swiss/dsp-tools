"""end to end tests for project class"""

# ruff: noqa: D101 (undocumented-public-class)
# ruff: noqa: D102 (undocumented-public-method)

import unittest

import pytest

from dsp_tools.commands.project.models.project import Project
from dsp_tools.models.langstring import LangString, Languages
from dsp_tools.utils.connection import Connection
from dsp_tools.utils.connection_live import ConnectionLive


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

    def test_project_update(self) -> None:
        project = Project(
            con=self.con,
            shortcode="0FF1",
            shortname="update_project",
            longname="Update Project",
            description=LangString({Languages.EN: "Project to be updated", Languages.DE: "Update-Projekt"}),
            keywords={"test", "project"},
            selfjoin=False,
            status=True,
            logo=self.logo_file,
        ).create()

        project.shortname = "update_project"
        project.longname = "Update Project"
        project.addDescription("fr", "Projet modifié")
        project.rmDescription("de")
        project.selfjoin = True
        project.status = False
        project.rmKeyword("project")
        project.addKeyword("updated")
        updated_project = project.update()

        self.assertEqual(updated_project.shortcode, "0FF1")
        self.assertEqual(updated_project.shortname, "update_project")
        self.assertEqual(updated_project.longname, "Update Project")
        self.assertEqual(updated_project.description["en"], "Project to be updated")
        self.assertEqual(updated_project.description["fr"], "Projet modifié")
        self.assertEqual(updated_project.selfjoin, True)
        self.assertEqual(updated_project.status, False)
        self.assertEqual(updated_project.keywords, {"test", "updated"})

    def test_project_delete(self) -> None:
        project = Project(
            con=self.con,
            shortcode="0FF2",
            shortname="delete_project",
            longname="Delete Project",
            description=LangString({Languages.EN: "Project to be deleted", Languages.DE: "Lösch-Projekt"}),
            keywords={"test", "project", "delete"},
            selfjoin=False,
            status=True,
            logo=self.logo_file,
        ).create()

        deleted_project = project.delete()

        self.assertEqual(deleted_project.shortcode, "0FF2")
        self.assertEqual(deleted_project.shortname, "delete_project")
        self.assertEqual(deleted_project.longname, "Delete Project")
        self.assertEqual(deleted_project.description["en"], "Project to be deleted")
        self.assertEqual(deleted_project.description["de"], "Lösch-Projekt")
        self.assertEqual(deleted_project.selfjoin, False)
        self.assertEqual(deleted_project.status, False)
        self.assertEqual(deleted_project.keywords, {"test", "project", "delete"})


if __name__ == "__main__":
    pytest.main([__file__])
