import unittest
import pprint
import requests
from urllib.parse import quote_plus

from connection import Connection
from helpers import BaseError, Actions
from langstring import Languages, LangStringParam, LangString

from user import User


def erase_user(iri = None):
    if iri is None:
        return
    sparql = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX knora-base: <http://www.knora.org/ontology/knora-base#>
        DELETE {
            GRAPH <http://www.knora.org/data/admin> {
                <%s> ?property ?value
            }
        } WHERE {
            GRAPH <http://www.knora.org/data/admin> {
                <%s> ?property ?value
            }
        }

    """ % (iri,iri)
    req = requests.post('http://localhost:7200/repositories/knora-test/statements',
                        headers={'Content-Type': 'application/sparql-update',
                                 'Accept': 'application/json, text/plain, */*'},
                        data=sparql)
    if 'error' in req:
        print('ERROR: ' + req.error)
    if req.status_code != 204:
        print('STATUS-CODE: ' + str(req.status_code))
        print('TEXT: ' + req.text)
    return req.status_code


class TestUser(unittest.TestCase):

    iri = None
    username = 'wilee'
    email = 'wilee.coyote@canyon.com'
    givenName = 'Wile E.'
    familyName = 'Coyote'
    password = 'BeepBeep'
    lang = Languages.EN
    status = True
    sysadmin = True
    in_projects = {"http://rdfh.ch/projects/0001": True}
    in_groups = {"http://rdfh.ch/groups/00FF/images-reviewer"}

    def createTestUser(self):
        con = Connection('http://0.0.0.0:3333')
        con.login('root@example.com', 'test')
        user = User(
            con=con,
            username=self.username,
            email=self.email,
            givenName=self.givenName,
            familyName=self.familyName,
            password=self.password,
            status=self.status,
            lang=self.lang,
            sysadmin=self.sysadmin,
            in_projects=self.in_projects,
            in_groups=self.in_groups
        ).create()
        self.assertIsNotNone(user.id)
        self.iri = user.id
        return user

    def tearDown(self):
        res = erase_user(self.iri)

    def test_User(self):
        con = Connection('http://0.0.0.0:3333')
        con.login('root@example.com', 'test')

        user = User(
            con=con,
            username=self.username,
            email=self.email,
            givenName=self.givenName,
            familyName=self.familyName,
            password=self.password,
            status=self.status,
            lang=self.lang,
            sysadmin=self.sysadmin,
            in_projects=self.in_projects,
            in_groups=self.in_groups
        )
        self.assertEqual(user.username, self.username)
        self.assertEqual(user.email, self.email)
        self.assertEqual(user.givenName, self.givenName)
        self.assertEqual(user.familyName, self.familyName)
        self.assertTrue(user.status)
        self.assertEqual(user.lang, self.lang)
        self.assertTrue(user.sysadmin)
        self.assertEqual(user.in_projects, self.in_projects)
        self.assertEqual(user.in_groups, self.in_groups)

    def test_User_read(self):
        con = Connection('http://0.0.0.0:3333')
        con.login('root@example.com', 'test')
        user = User(
            con=con,
            id='http://rdfh.ch/users/91e19f1e01'
        ).read()
        self.assertEqual(user.id, 'http://rdfh.ch/users/91e19f1e01')
        self.assertEqual(user.username, 'root-alt')
        self.assertEqual(user.familyName, 'Admin-alt')
        self.assertEqual(user.givenName, 'Administrator-alt')
        self.assertEqual(user.lang, Languages.DE)
        self.assertFalse(user.status)
        self.assertFalse(user.sysadmin)
        self.assertEqual(user.in_projects, {"http://rdfh.ch/projects/0803": False})

    def test_User_read2(self):
        user = self.createTestUser()
        con = Connection('http://0.0.0.0:3333')
        con.login('root@example.com', 'test')
        user = User(
            con=con,
            email=self.email
        ).read()
        self.assertEqual(user.username, self.username)
        self.assertEqual(user.familyName, self.familyName)
        self.assertEqual(user.givenName, self.givenName)
        self.assertEqual(user.lang, self.lang)
        self.assertTrue(user.status)
        self.assertTrue(user.sysadmin)
        self.assertEqual(user.in_projects, self.in_projects)
        self.assertEqual(user.in_groups, self.in_groups)

    def test_User_create(self):
        user = self.createTestUser()
        self.assertEqual(user.username, self.username)
        self.assertEqual(user.email, self.email)
        self.assertEqual(user.givenName, self.givenName)
        self.assertEqual(user.familyName, self.familyName)
        self.assertTrue(user.status)
        self.assertEqual(user.lang, self.lang)
        self.assertTrue(user.sysadmin)
        self.assertEqual(user.in_projects, self.in_projects)
        self.assertEqual(user.in_groups, self.in_groups)

    def test_User_delete(self):
        user = self.createTestUser()
        nuser = user.delete()
        self.assertIsNotNone(nuser)
        self.assertFalse(nuser.status)

    def test_User_update(self):
        user = self.createTestUser()
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
        user = self.createTestUser()
        user.password = 'gagagagagagagaga'
        nuser = user.update('test')
        self.assertIsNotNone(nuser)

    def test_User_addToGroup(self):
        user = self.createTestUser()
        user.addToGroup('http://rdfh.ch/groups/0001/thing-searcher')
        nuser = user.update()
        self.assertIsNotNone(nuser)
        self.assertEqual(nuser.in_groups, {"http://rdfh.ch/groups/00FF/images-reviewer", 'http://rdfh.ch/groups/0001/thing-searcher'})

    def test_User_rmFromGroup(self):
        user = self.createTestUser()
        user.rmFromGroup('http://rdfh.ch/groups/00FF/images-reviewer')
        nuser = user.update()
        self.assertIsNotNone(nuser)

    def test_User_addToProject(self):
        user = self.createTestUser()
        user.addToProject('http://rdfh.ch/projects/00FF', False)
        nuser = user.update()
        self.assertIsNotNone(nuser)
        self.assertEqual(nuser.in_projects, {"http://rdfh.ch/projects/0001": True, 'http://rdfh.ch/projects/00FF': False})

    def test_User_rmFromProject(self):
        user = self.createTestUser()
        user.rmFromProject('http://rdfh.ch/projects/0001')
        nuser = user.update()
        self.assertIsNotNone(nuser)
        self.assertEqual(nuser.in_projects, {})

    def test_User_unmakeProjectAdmin(self):
        user = self.createTestUser()
        user.unmakeProjectAdmin('http://rdfh.ch/projects/0001')
        nuser = user.update()
        self.assertIsNotNone(nuser)
        self.assertEqual(nuser.in_projects, {'http://rdfh.ch/projects/0001': False})

    def test_User_makeProjectAdmin(self):
        user = self.createTestUser()
        user.addToProject('http://rdfh.ch/projects/00FF', False)
        user = user.update()
        user.makeProjectAdmin('http://rdfh.ch/projects/00FF')
        nuser = user.update()
        self.assertIsNotNone(nuser)
        self.assertEqual(nuser.in_projects, {'http://rdfh.ch/projects/0001': True, 'http://rdfh.ch/projects/00FF': True})

    def test_getAllUsers(self):
        con = Connection('http://0.0.0.0:3333')
        con.login('root@example.com', 'test')
        all_users = User.getAllUsers(con)
        for u in all_users:
            self.assertIsNotNone(u.id)

if __name__ == '__main__':
    unittest.main()
