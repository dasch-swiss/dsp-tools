"""end to end tests for user class"""
import unittest

from knora.dsplib.models.connection import Connection
from knora.dsplib.models.langstring import Languages
from knora.dsplib.models.user import User


class TestUser(unittest.TestCase):

    def setUp(self) -> None:
        """
        is executed before all tests; sets up a connection and logs in as user root
        """
        self.con = Connection('http://0.0.0.0:3333')
        self.con.login('root@example.com', 'test')

    def test_user_create(self) -> None:
        user = User(
            con=self.con,
            username='wilee1',
            email='wilee.coyote1@canyon.com',
            givenName='Wile E.1',
            familyName='Coyote1',
            password='BeepBeep1',
            lang=Languages.EN,
            status=True,
            sysadmin=True,
            in_projects={"http://rdfh.ch/projects/0001": True},
            in_groups={"http://rdfh.ch/groups/0001/thing-searcher"}
        ).create()
        self.assertEqual(user.username, 'wilee1')
        self.assertEqual(user.email, 'wilee.coyote1@canyon.com')
        self.assertEqual(user.givenName, 'Wile E.1')
        self.assertEqual(user.familyName, 'Coyote1')
        self.assertTrue(user.status)
        self.assertEqual(user.lang, Languages.EN)
        self.assertTrue(user.sysadmin)
        self.assertEqual(user.in_projects, {"http://rdfh.ch/projects/0001": True})
        self.assertEqual(user.in_groups, {"http://rdfh.ch/groups/0001/thing-searcher"})

    def test_user_read_by_iri(self) -> None:
        user = User(
            con=self.con,
            id='http://rdfh.ch/users/91e19f1e01'
        ).read()
        self.assertEqual(user.id, 'http://rdfh.ch/users/91e19f1e01')
        self.assertEqual(user.username, 'root-alt')
        self.assertEqual(user.familyName, 'Admin-alt')
        self.assertEqual(user.givenName, 'Administrator-alt')
        self.assertEqual(user.lang, Languages.DE)
        self.assertTrue(user.status)
        self.assertFalse(user.sysadmin)
        self.assertEqual(user.in_projects, {"http://rdfh.ch/projects/0803": False})

    def test_user_create_and_read_by_email(self) -> None:
        User(
            con=self.con,
            username='wilee2',
            email='wilee.coyote2@canyon.com',
            givenName='Wile E.2',
            familyName='Coyote2',
            password='BeepBeep2',
            lang=Languages.EN,
            status=True,
            sysadmin=True,
            in_projects={"http://rdfh.ch/projects/0001": True},
            in_groups={"http://rdfh.ch/groups/0001/thing-searcher"}
        ).create()
        user = User(
            con=self.con,
            email='wilee.coyote2@canyon.com'
        ).read()
        self.assertEqual(user.username, 'wilee2')
        self.assertEqual(user.familyName, 'Coyote2')
        self.assertEqual(user.givenName, 'Wile E.2')
        self.assertEqual(user.lang, Languages.EN)
        self.assertTrue(user.status)
        self.assertTrue(user.sysadmin)
        self.assertEqual(user.in_projects, {"http://rdfh.ch/projects/0001": True})
        self.assertEqual(user.in_groups, {"http://rdfh.ch/groups/0001/thing-searcher"})

    def tesu_User_delete(self) -> None:
        user = User(
            con=self.con,
            username='wilee3',
            email='wilee.coyote3@canyon.com',
            givenName='Wile E.3',
            familyName='Coyote3',
            password='BeepBeep3',
            lang=Languages.EN,
            status=True,
            sysadmin=True,
            in_projects={"http://rdfh.ch/projects/0001": True},
            in_groups={"http://rdfh.ch/groups/0001/thing-searcher"}
        ).create()
        self.assertTrue(user.status)
        nuser = user.delete()
        # user still exists only status is set to false
        self.assertFalse(nuser.status)

    def test_user_update_basic_information(self) -> None:
        user = User(
            con=self.con,
            username='wilee4',
            email='wilee.coyote4@canyon.com',
            givenName='Wile E.4',
            familyName='Coyote4',
            password='BeepBeep4',
            lang=Languages.EN,
            status=True,
            sysadmin=True,
            in_projects={"http://rdfh.ch/projects/0001": True},
            in_groups={"http://rdfh.ch/groups/0001/thing-searcher"}
        ).create()
        user.email = 'roadrunner.geococcyx@canyon.com'
        user.username = 'roadrunner'
        user.givenName = 'roadrunner'
        user.familyName = 'Geococcyx'
        user.lang = 'fr'
        user.status = False
        user.sysadmin = False
        nuser = user.update()
        self.assertEqual(nuser.email, 'roadrunner.geococcyx@canyon.com')
        self.assertEqual(nuser.username, 'roadrunner')
        self.assertEqual(nuser.givenName, 'roadrunner')
        self.assertEqual(nuser.familyName, 'Geococcyx')
        self.assertEqual(nuser.lang, Languages.FR)
        self.assertFalse(nuser.status)
        self.assertFalse(nuser.sysadmin)

    def test_user_update_password(self) -> None:
        user = User(
            con=self.con,
            username='wilee5',
            email='wilee.coyote5@canyon.com',
            givenName='Wile E.5',
            familyName='Coyote5',
            password='BeepBeep5.1',
            lang=Languages.EN,
            status=True,
            sysadmin=True,
            in_projects={"http://rdfh.ch/projects/0001": True},
            in_groups={"http://rdfh.ch/groups/0001/thing-searcher"}
        ).create()

        # change user's password as user root
        user.password = 'BeepBeep5.2'
        user.update('test')

        # login as user wilee5 with new password (this would fail if password update wasn't successful)
        con = Connection('http://0.0.0.0:3333')
        con.login('wilee.coyote5@canyon.com', 'BeepBeep5.2')

        updated_user = User(
            con=con,
            email='wilee.coyote5@canyon.com'
        ).read()

        # update password as user wilee5 (this would fail if password update wasn't successful)
        updated_user.password = 'BeepBeep5.3'
        nuser = updated_user.update('BeepBeep5.2')
        self.assertIsNotNone(nuser)

    def test_user_add_to_group(self) -> None:
        user = User(
            con=self.con,
            username='wilee10',
            email='wilee.coyote10@canyon.com',
            givenName='Wile E.10',
            familyName='Coyote10',
            password='BeepBeep10',
            lang=Languages.EN,
            status=True,
            sysadmin=True,
            in_projects={"http://rdfh.ch/projects/0001": True},
            in_groups={"http://rdfh.ch/groups/00FF/images-reviewer"}
        ).create()

        self.assertEqual(user.in_groups, {"http://rdfh.ch/groups/00FF/images-reviewer"})

        user.addToGroup('http://rdfh.ch/groups/0001/thing-searcher')
        nuser = user.update()
        self.assertEqual(nuser.in_groups,
                         {"http://rdfh.ch/groups/0001/thing-searcher", 'http://rdfh.ch/groups/00FF/images-reviewer'})

    def test_user_remove_from_group(self) -> None:
        user = User(
            con=self.con,
            username='wilee6',
            email='wilee.coyote6@canyon.com',
            givenName='Wile E.6',
            familyName='Coyote6',
            password='BeepBeep6',
            lang=Languages.EN,
            status=True,
            sysadmin=True,
            in_projects={"http://rdfh.ch/projects/0001": True},
            in_groups={"http://rdfh.ch/groups/00FF/images-reviewer"}
        ).create()
        self.assertEqual(user.in_groups, {"http://rdfh.ch/groups/00FF/images-reviewer"})
        user.rmFromGroup('http://rdfh.ch/groups/00FF/images-reviewer')
        nuser = user.update()
        self.assertEqual(nuser.in_groups, set())

    def test_user_add_to_project(self) -> None:
        user = User(
            con=self.con,
            username='wilee7',
            email='wilee.coyote7@canyon.com',
            givenName='Wile E.7',
            familyName='Coyote7',
            password='BeepBeep7',
            lang=Languages.EN,
            status=True,
            sysadmin=True,
            in_projects={"http://rdfh.ch/projects/0001": True},
            in_groups={"http://rdfh.ch/groups/0001/thing-searcher"}
        ).create()
        user.addToProject('http://rdfh.ch/projects/00FF', False)
        nuser = user.update()
        self.assertEqual(nuser.in_projects,
                         {"http://rdfh.ch/projects/0001": True, 'http://rdfh.ch/projects/00FF': False})

    def test_user_remove_from_project(self) -> None:
        user = User(
            con=self.con,
            username='wilee8',
            email='wilee.coyote8@canyon.com',
            givenName='Wile E.8',
            familyName='Coyote8',
            password='BeepBeep8',
            lang=Languages.EN,
            status=True,
            sysadmin=True,
            in_projects={"http://rdfh.ch/projects/0001": True},
            in_groups={"http://rdfh.ch/groups/0001/thing-searcher"}
        ).create()
        self.assertEqual(user.in_projects,
                         {"http://rdfh.ch/projects/0001": True})
        user.rmFromProject('http://rdfh.ch/projects/0001')
        nuser = user.update()
        self.assertEqual(nuser.in_projects, {})

    def test_user_remove_as_project_admin(self) -> None:
        user = User(
            con=self.con,
            username='wilee9',
            email='wilee.coyote9@canyon.com',
            givenName='Wile E.9',
            familyName='Coyote9',
            password='BeepBeep9',
            lang=Languages.EN,
            status=True,
            sysadmin=True,
            in_projects={"http://rdfh.ch/projects/0001": True},
            in_groups={"http://rdfh.ch/groups/0001/thing-searcher"}
        ).create()
        user.unmakeProjectAdmin('http://rdfh.ch/projects/0001')
        nuser = user.update()
        self.assertEqual(nuser.in_projects, {'http://rdfh.ch/projects/0001': False})

    def test_user_add_as_project_admin(self) -> None:
        user = User(
            con=self.con,
            username='wileeA',
            email='wilee.coyoteA@canyon.com',
            givenName='Wile E.A',
            familyName='CoyoteA',
            password='BeepBeepA',
            lang=Languages.EN,
            status=True,
            sysadmin=True,
            in_projects={"http://rdfh.ch/projects/0001": False},
            in_groups={"http://rdfh.ch/groups/0001/thing-searcher"}
        ).create()
        user.makeProjectAdmin('http://rdfh.ch/projects/0001')
        nuser = user.update()
        self.assertEqual(nuser.in_projects, {'http://rdfh.ch/projects/0001': True})

    def test_user_get_all_users(self) -> None:
        all_users = User.getAllUsers(self.con)
        for user in all_users:
            self.assertIsNotNone(user.id)

    def tearDown(self) -> None:
        """
        is executed after all tests are run through; performs a log out
        """
        self.con.logout()


if __name__ == '__main__':
    unittest.main()
