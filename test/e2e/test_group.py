"""end to end tests for group class"""
import unittest
from typing import cast

import pytest

from dsp_tools.models.connection import Connection
from dsp_tools.models.group import Group
from dsp_tools.models.langstring import LangString, Languages


class TestGroup(unittest.TestCase):  # pylint: disable=missing-class-docstring
    test_project = "http://rdfh.ch/projects/0001"

    def setUp(self) -> None:
        """
        is executed before all tests; sets up a connection and logs in as user root
        """
        self.con = Connection("http://0.0.0.0:3333")
        self.con.login("root@example.com", "test")

    def test_group_getAllGroups(self) -> None:
        """
        Retrieve all groups
        :return: None
        """
        groups = Group.getAllGroups(self.con)
        group_ids = []
        for group in groups:
            group_ids.append(group.id)

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
        group = Group(con=self.con, id="http://rdfh.ch/groups/0001/thing-searcher").read()
        self.assertEqual(group.name, "Thing searcher")
        self.assertEqual(group.project, self.test_project)
        self.assertTrue(group.status)
        self.assertTrue(group.selfjoin)

    def test_Group_update(self) -> None:
        """
        Update an existing group
        :return: None
        """
        group = Group(
            con=self.con,
            name="Group update",
            descriptions=LangString({Languages.EN: "This is group update"}),
            project=self.test_project,
            status=True,
            selfjoin=False,
        )
        group = group.create()

        group.name = "Group update - modified"
        group.descriptions = LangString({"en": "This is group update - modified"})
        group.selfjoin = True
        group.status = False
        updated_group = group.update()

        self.assertIsNotNone(updated_group)
        updated_group = cast(Group, updated_group)
        self.assertEqual(updated_group.name, "Group update - modified")
        self.assertCountEqual(
            cast(list[dict[str, str]], updated_group.descriptions.toJsonObj()),
            [{"language": "en", "value": "This is group update - modified"}],
        )
        self.assertEqual(updated_group.project, self.test_project)
        self.assertFalse(updated_group.status)
        self.assertTrue(updated_group.selfjoin)

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

    def tearDown(self) -> None:
        """
        is executed after all tests are run through; performs a log out
        """
        self.con.logout()


if __name__ == "__main__":
    pytest.main([__file__])
