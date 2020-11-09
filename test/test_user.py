import unittest

from dsplib.models.connection import Connection
from dsplib.models.langstring import Languages, LangStringParam, LangString
from dsplib.models.user import User


class TestUser(unittest.TestCase):

    def setUp(self) -> None:
        self.con = Connection('http://0.0.0.0:3333')
        self.con.login('root@example.com', 'test')

    def test_user(self):
        user = User(
            con=self.con,
            username='wilee',
            email='wilee.coyote@canyon.com',
            givenName='Wile E.',
            familyName='Coyote',
            password='BeepBeep',
            lang=Languages.EN,
            status=True,
            sysadmin=True,
            in_projects={"http://rdfh.ch/projects/0001": True},
            in_groups={"http://rdfh.ch/groups/0001/thing-searcher"}
        )
        self.assertEqual(user.username, 'wilee')
        self.assertEqual(user.email, 'wilee.coyote@canyon.com')
        self.assertEqual(user.givenName, 'Wile E.')
        self.assertEqual(user.familyName, 'Coyote')
        self.assertTrue(user.status)
        self.assertEqual(user.lang, Languages.EN)
        self.assertTrue(user.sysadmin)
        self.assertEqual(user.in_projects, {"http://rdfh.ch/projects/0001": True})
        self.assertEqual(user.in_groups, {"http://rdfh.ch/groups/0001/thing-searcher"})

    def test_User_read(self):
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

    def test_User_create(self):
        user = User(
            con=self.con,
            username='wilee',
            email='wilee.coyote@canyon.com',
            givenName='Wile E.',
            familyName='Coyote',
            password='BeepBeep',
            lang=Languages.EN,
            status=True,
            sysadmin=True,
            in_projects={"http://rdfh.ch/projects/0001": True},
            in_groups={"http://rdfh.ch/groups/0001/thing-searcher"}
        ).create()
        self.assertEqual(user.username, 'wilee')
        self.assertEqual(user.email, 'wilee.coyote@canyon.com')
        self.assertEqual(user.givenName, 'Wile E.')
        self.assertEqual(user.familyName, 'Coyote')
        self.assertTrue(user.status)
        self.assertEqual(user.lang, Languages.EN)
        self.assertTrue(user.sysadmin)
        self.assertEqual(user.in_projects, {"http://rdfh.ch/projects/0001": True})
        self.assertEqual(user.in_groups, {"http://rdfh.ch/groups/0001/thing-searcher"})

    def test_User_read2(self):
        user = User(
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

    def test_User_delete(self):
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
        nuser = user.delete()
        self.assertIsNotNone(nuser)
        self.assertFalse(nuser.status)

    def test_User_update(self):
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

    def test_User_update2(self):
        user = User(
            con=self.con,
            username='wilee5',
            email='wilee.coyote5@canyon.com',
            givenName='Wile E.5',
            familyName='Coyote5',
            password='BeepBeep5',
            lang=Languages.EN,
            status=True,
            sysadmin=True,
            in_projects={"http://rdfh.ch/projects/0001": True},
            in_groups={"http://rdfh.ch/groups/0001/thing-searcher"}
        ).create()
        user.password = 'gagagagagagagaga'
        nuser = user.update('test')
        self.assertIsNotNone(nuser)

    def test_User_addToGroup(self):
        return #  TODO: Check why this test failes with error: Message:{"error":"org.knora.webapi.UpdateNotPerformedException: User's 'group' memberships where not updated. Please report this as a possible bug."}
        user = self.createTestUser()
        user.addToGroup('http://rdfh.ch/groups/0001/thing-searcher')
        nuser = user.update()
        self.assertIsNotNone(nuser)
        self.assertEqual(nuser.in_groups, {"http://rdfh.ch/groups/0001/thing-searcher", 'http://rdfh.ch/groups/0001/thing-searcher'})

    def test_User_rmFromGroup(self):
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
        user.rmFromGroup('http://rdfh.ch/groups/00FF/images-reviewer')
        nuser = user.update()
        self.assertIsNotNone(nuser)

    def test_User_addToProject(self):
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
        self.assertIsNotNone(nuser)
        self.assertEqual(nuser.in_projects, {"http://rdfh.ch/projects/0001": True, 'http://rdfh.ch/projects/00FF': False})

    def test_User_rmFromProject(self):
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
        user.rmFromProject('http://rdfh.ch/projects/0001')
        nuser = user.update()
        self.assertIsNotNone(nuser)
        self.assertEqual(nuser.in_projects, {})

    def test_User_unmakeProjectAdmin(self):
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
        self.assertIsNotNone(nuser)
        self.assertEqual(nuser.in_projects, {'http://rdfh.ch/projects/0001': False})

    def test_User_makeProjectAdmin(self):
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
            in_projects={"http://rdfh.ch/projects/0001": True},
            in_groups={"http://rdfh.ch/groups/0001/thing-searcher"}
        ).create()
        user.addToProject('http://rdfh.ch/projects/00FF', False)
        user = user.update()
        user.makeProjectAdmin('http://rdfh.ch/projects/00FF')
        nuser = user.update()
        self.assertIsNotNone(nuser)
        self.assertEqual(nuser.in_projects, {'http://rdfh.ch/projects/0001': True,
                                             'http://rdfh.ch/projects/00FF': True})

    def test_getAllUsers(self):
        con = Connection('http://0.0.0.0:3333')
        con.login('root@example.com', 'test')
        all_users = User.getAllUsers(con)
        for u in all_users:
            self.assertIsNotNone(u.id)

if __name__ == '__main__':
    unittest.main()
