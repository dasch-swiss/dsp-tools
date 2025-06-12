"""end to end tests for user class"""

import unittest

import pytest

from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.clients.connection import Connection
from dsp_tools.clients.connection_live import ConnectionLive
from dsp_tools.commands.project.legacy_models.user import User
from dsp_tools.legacy_models.langstring import Languages

# ruff: noqa: PT009 (pytest-unittest-assertion) (remove this line when pytest is used instead of unittest)


# define variables for testing
iri_project_0001 = "http://rdfh.ch/projects/0001"
iri_project_0FFF = "http://rdfh.ch/projects/00FF"
iri_group_thing_searcher = "http://rdfh.ch/groups/0001/thing-searcher"
iri_group_images_reviewer = "http://rdfh.ch/groups/00FF/images-reviewer"


class TestUser(unittest.TestCase):
    con: Connection

    def setUp(self) -> None:
        """
        Creates a connection to DSP-API.
        For each test method, a new TestCase instance is created, so setUp() is executed before each test method.
        """
        auth = AuthenticationClientLive("http://0.0.0.0:3333", "root@example.com", "test")
        self.con = ConnectionLive("http://0.0.0.0:3333", auth)

    def test_user_create(self) -> None:
        user = User(
            con=self.con,
            username="wilee1",
            email="wilee.coyote1@canyon.com",
            givenName="Wile E.1",
            familyName="Coyote1",
            password="BeepBeep1",
            lang=Languages.EN,
            status=True,
            in_projects={iri_project_0001: True},
            in_groups={iri_group_thing_searcher},
        ).create()
        self.assertEqual(user.username, "wilee1")
        self.assertEqual(user.email, "wilee.coyote1@canyon.com")
        self.assertEqual(user.givenName, "Wile E.1")
        self.assertEqual(user.familyName, "Coyote1")
        self.assertTrue(user.status)
        self.assertEqual(user.lang, Languages.EN)
        self.assertEqual(user.in_projects, {iri_project_0001: True})
        self.assertEqual(user.in_groups, {iri_group_thing_searcher})

    def test_user_read_by_iri(self) -> None:
        user = User(con=self.con, iri="http://rdfh.ch/users/normaluser").read()
        self.assertEqual(user.iri, "http://rdfh.ch/users/normaluser")
        self.assertEqual(user.username, "normaluser")
        self.assertEqual(user.familyName, "User")
        self.assertEqual(user.givenName, "Normal")
        self.assertEqual(user.lang, Languages.DE)
        self.assertTrue(user.status)
        self.assertEqual(user.in_projects, {})

    def test_user_create_and_read_by_email(self) -> None:
        User(
            con=self.con,
            username="wilee2",
            email="wilee.coyote2@canyon.com",
            givenName="Wile E.2",
            familyName="Coyote2",
            password="BeepBeep2",
            lang=Languages.EN,
            status=True,
            in_projects={iri_project_0001: True},
            in_groups={iri_group_thing_searcher},
        ).create()
        user = User(con=self.con, email="wilee.coyote2@canyon.com").read()
        self.assertEqual(user.username, "wilee2")
        self.assertEqual(user.familyName, "Coyote2")
        self.assertEqual(user.givenName, "Wile E.2")
        self.assertEqual(user.lang, Languages.EN)
        self.assertTrue(user.status)
        self.assertEqual(user.in_projects, {iri_project_0001: True})
        self.assertEqual(user.in_groups, {iri_group_thing_searcher})

    def test_user_get_all_users(self) -> None:
        all_users = User.getAllUsers(self.con)
        for user in all_users:
            self.assertIsNotNone(user.iri)


if __name__ == "__main__":
    pytest.main([__file__])
