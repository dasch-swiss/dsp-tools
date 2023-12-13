"""end to end tests for user class"""

import unittest

import pytest

from dsp_tools.commands.project.models.user import User
from dsp_tools.models.langstring import Languages
from dsp_tools.utils.connection import Connection
from dsp_tools.utils.connection_live import ConnectionLive

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
        self.con = ConnectionLive(server="http://0.0.0.0:3333")
        self.con.login(email="root@example.com", password="test")

    def tearDown(self) -> None:
        """
        Logs out from DSP-API.
        For each test method, a new TestCase instance is created, so tearDown() is executed after each test method.
        """
        self.con.logout()

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
            sysadmin=True,
            in_projects={iri_project_0001: True},
            in_groups={iri_group_thing_searcher},
        ).create()
        self.assertEqual(user.username, "wilee1")
        self.assertEqual(user.email, "wilee.coyote1@canyon.com")
        self.assertEqual(user.givenName, "Wile E.1")
        self.assertEqual(user.familyName, "Coyote1")
        self.assertTrue(user.status)
        self.assertEqual(user.lang, Languages.EN)
        self.assertTrue(user.sysadmin)
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
        self.assertFalse(user.sysadmin)
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
            sysadmin=True,
            in_projects={iri_project_0001: True},
            in_groups={iri_group_thing_searcher},
        ).create()
        user = User(con=self.con, email="wilee.coyote2@canyon.com").read()
        self.assertEqual(user.username, "wilee2")
        self.assertEqual(user.familyName, "Coyote2")
        self.assertEqual(user.givenName, "Wile E.2")
        self.assertEqual(user.lang, Languages.EN)
        self.assertTrue(user.status)
        self.assertTrue(user.sysadmin)
        self.assertEqual(user.in_projects, {iri_project_0001: True})
        self.assertEqual(user.in_groups, {iri_group_thing_searcher})

    def test_user_delete(self) -> None:
        user = User(
            con=self.con,
            username="wilee3",
            email="wilee.coyote3@canyon.com",
            givenName="Wile E.3",
            familyName="Coyote3",
            password="BeepBeep3",
            lang=Languages.EN,
            status=True,
            sysadmin=True,
            in_projects={iri_project_0001: True},
            in_groups={iri_group_thing_searcher},
        ).create()
        self.assertTrue(user.status)
        updated_user = user.delete()
        # user still exists only status is set to false
        self.assertFalse(updated_user.status)

    def test_user_update_basic_information(self) -> None:
        user = User(
            con=self.con,
            username="wilee4",
            email="wilee.coyote4@canyon.com",
            givenName="Wile E.4",
            familyName="Coyote4",
            password="BeepBeep4",
            lang=Languages.EN,
            status=True,
            sysadmin=True,
            in_projects={iri_project_0001: True},
            in_groups={iri_group_thing_searcher},
        ).create()
        user.email = "roadrunner.geococcyx@canyon.com"
        user.username = "roadrunner"
        user.givenName = "roadrunner"
        user.familyName = "Geococcyx"
        user.lang = Languages.FR
        user.status = False
        user.sysadmin = False
        updated_user = user.update()
        self.assertEqual(updated_user.email, "roadrunner.geococcyx@canyon.com")
        self.assertEqual(updated_user.username, "roadrunner")
        self.assertEqual(updated_user.givenName, "roadrunner")
        self.assertEqual(updated_user.familyName, "Geococcyx")
        self.assertEqual(updated_user.lang, Languages.FR)
        self.assertFalse(updated_user.status)
        self.assertFalse(updated_user.sysadmin)

    def test_user_update_password(self) -> None:
        # the root user creates a new root user with the name wilee5
        wilee_email = "wilee.coyote5@canyon.com"
        wilee_new_pw = "BeepBeep5.2"
        wilee = User(
            con=self.con,
            username="wilee5",
            email=wilee_email,
            givenName="Wile E.5",
            familyName="Coyote5",
            password="BeepBeep5.1",
            lang=Languages.EN,
            status=True,
            sysadmin=True,
            in_projects={iri_project_0001: True},
            in_groups={iri_group_thing_searcher},
        ).create()

        # the root user changes wilee5's password
        wilee.password = wilee_new_pw
        wilee.update(requesterPassword="test")

        # wilee5 logs in with his new password,
        # and retrieves a User instance of himself
        # (this would fail if password update wasn't successful)
        con = ConnectionLive(server="http://0.0.0.0:3333")
        con.login(email=wilee_email, password=wilee_new_pw)
        wilee_updated_by_root = User(con=con, email=wilee_email).read()

        # wilee5 updates his own password (this would fail if password update wasn't successful)
        wilee_updated_by_root.password = "BeepBeep5.3"
        wilee_updated_by_himself = wilee_updated_by_root.update(requesterPassword=wilee_new_pw)
        self.assertIsNotNone(wilee_updated_by_himself)

    def test_user_add_to_group(self) -> None:
        user = User(
            con=self.con,
            username="wilee10",
            email="wilee.coyote10@canyon.com",
            givenName="Wile E.10",
            familyName="Coyote10",
            password="BeepBeep10",
            lang=Languages.EN,
            status=True,
            sysadmin=True,
            in_projects={iri_project_0001: True},
            in_groups={iri_group_images_reviewer},
        ).create()

        self.assertEqual(user.in_groups, {iri_group_images_reviewer})

        user.addToGroup(iri_group_thing_searcher)
        updated_user = user.update()
        self.assertEqual(
            updated_user.in_groups,
            {iri_group_thing_searcher, iri_group_images_reviewer},
        )

    def test_user_remove_from_group(self) -> None:
        user = User(
            con=self.con,
            username="wilee6",
            email="wilee.coyote6@canyon.com",
            givenName="Wile E.6",
            familyName="Coyote6",
            password="BeepBeep6",
            lang=Languages.EN,
            status=True,
            sysadmin=True,
            in_projects={iri_project_0001: True},
            in_groups={iri_group_images_reviewer},
        ).create()
        self.assertEqual(user.in_groups, {iri_group_images_reviewer})
        user.rmFromGroup(iri_group_images_reviewer)
        update_user = user.update()
        self.assertEqual(update_user.in_groups, set())

    def test_user_add_to_project(self) -> None:
        user = User(
            con=self.con,
            username="wilee7",
            email="wilee.coyote7@canyon.com",
            givenName="Wile E.7",
            familyName="Coyote7",
            password="BeepBeep7",
            lang=Languages.EN,
            status=True,
            sysadmin=True,
            in_projects={iri_project_0001: True},
            in_groups={iri_group_thing_searcher},
        ).create()
        user.addToProject(iri_project_0FFF, False)
        updated_user = user.update()
        self.assertEqual(updated_user.in_projects, {iri_project_0001: True, iri_project_0FFF: False})

    def test_user_remove_from_project(self) -> None:
        user = User(
            con=self.con,
            username="wilee8",
            email="wilee.coyote8@canyon.com",
            givenName="Wile E.8",
            familyName="Coyote8",
            password="BeepBeep8",
            lang=Languages.EN,
            status=True,
            sysadmin=True,
            in_projects={iri_project_0001: True},
            in_groups={iri_group_thing_searcher},
        ).create()
        self.assertEqual(user.in_projects, {iri_project_0001: True})
        user.rmFromProject(iri_project_0001)
        updated_user = user.update()
        self.assertEqual(updated_user.in_projects, {})

    def test_user_remove_as_project_admin(self) -> None:
        user = User(
            con=self.con,
            username="wilee9",
            email="wilee.coyote9@canyon.com",
            givenName="Wile E.9",
            familyName="Coyote9",
            password="BeepBeep9",
            lang=Languages.EN,
            status=True,
            sysadmin=True,
            in_projects={iri_project_0001: True},
            in_groups={iri_group_thing_searcher},
        ).create()
        user.unmakeProjectAdmin(iri_project_0001)
        updated_user = user.update()
        self.assertEqual(updated_user.in_projects, {iri_project_0001: False})

    def test_user_add_as_project_admin(self) -> None:
        user = User(
            con=self.con,
            username="wileeA",
            email="wilee.coyoteA@canyon.com",
            givenName="Wile E.A",
            familyName="CoyoteA",
            password="BeepBeepA",
            lang=Languages.EN,
            status=True,
            sysadmin=True,
            in_projects={iri_project_0001: False},
            in_groups={iri_group_thing_searcher},
        ).create()
        user.makeProjectAdmin(iri_project_0001)
        updated_user = user.update()
        self.assertEqual(updated_user.in_projects, {iri_project_0001: True})

    def test_user_get_all_users(self) -> None:
        all_users = User.getAllUsers(self.con)
        for user in all_users:
            self.assertIsNotNone(user.iri)


if __name__ == "__main__":
    pytest.main([__file__])
