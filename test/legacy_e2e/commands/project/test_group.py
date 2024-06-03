"""end to end tests for group class"""

import unittest
from typing import cast

import pytest

from dsp_tools.commands.project.models.group import Group
from dsp_tools.models.langstring import LangString
from dsp_tools.models.langstring import Languages
from dsp_tools.utils.connection import Connection
from dsp_tools.utils.connection_live import ConnectionLive

# ruff: noqa: PT009 (pytest-unittest-assertion) (remove this line when pytest is used instead of unittest)


class TestGroup(unittest.TestCase):
    test_project = "http://rdfh.ch/projects/0001"
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

    def test_group_getAllGroups(self) -> None:
        """
        Retrieve all groups
        :return: None
        """
        groups = Group.getAllGroups(self.con)
        group_ids = [group.iri for group in groups]
        group_ids_expected = [
            "http://rdfh.ch/groups/00FF/images-reviewer",
            "http://rdfh.ch/groups/0001/thing-searcher",
        ]
        self.assertTrue(set(group_ids).issuperset(set(group_ids_expected)))

    def test_group_create(self) -> None:
        """
        Create a group
        :return: None
        """
        group = Group(
            con=self.con,
            name="Group create",
            descriptions=LangString({Languages.EN: "This is group create"}),
            project=self.test_project,
            status=True,
            selfjoin=False,
        )

        self.assertEqual(group.name, "Group create")
        self.assertCountEqual(
            cast(list[dict[str, str]], group.descriptions.toJsonObj()),
            [{"language": "en", "value": "This is group create"}],
        )
        self.assertEqual(group.project, self.test_project)
        self.assertTrue(group.status)
        self.assertFalse(group.selfjoin)

    def test_group_read(self) -> None:
        """
        Read an existing group
        :return: None
        """
        group = Group(con=self.con, iri="http://rdfh.ch/groups/0001/thing-searcher").read()
        self.assertEqual(group.name, "Thing searcher")
        self.assertEqual(group.project, self.test_project)
        self.assertTrue(group.status)
        self.assertTrue(group.selfjoin)

    def test_Group_delete(self) -> None:
        """
        Mark an existing group as deleted (it will not be deleted completely from the triplestore, but status set to
        False)
        :return: None
        """
        group = Group(
            con=self.con,
            name="Group delete",
            descriptions=LangString({Languages.EN: "This is group delete"}),
            project=self.test_project,
            status=True,
            selfjoin=False,
        )
        group = group.create()

        deleted_group = group.delete()
        self.assertEqual(deleted_group.name, "Group delete")
        self.assertCountEqual(
            cast(list[dict[str, str]], deleted_group.descriptions.toJsonObj()),
            [{"language": "en", "value": "This is group delete"}],
        )
        self.assertEqual(deleted_group.project, self.test_project)
        self.assertFalse(deleted_group.status)
        self.assertFalse(deleted_group.selfjoin)


if __name__ == "__main__":
    pytest.main([__file__])
