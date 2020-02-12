import unittest
import pprint
import requests
from urllib.parse import quote_plus

from context import BaseError, Languages, Actions, LangString
from context import KnoraUser, KnoraConnection


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


class TestKnoraUser(unittest.TestCase):

    iri = None
    username = 'wiley'
    email = 'wiley.coyote@canyon.com'
    givenName = 'Wiley'
    familyName = 'Coyote'
    password = 'BeepBeep'
    lang = Languages.EN
    status = True
    sysadmin = True
    in_projects = {"http://rdfh.ch/projects/0001": True}
    in_groups = {"http://rdfh.ch/groups/00FF/images-reviewer"}

    def createTestUser(self):
        con = KnoraConnection('http://0.0.0.0:3333')
        con.login('root@example.com', 'test')
        user = KnoraUser(
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
        self.assertIsNotNone(user)
        self.iri = user.id
        return user

    def tearDown(self):
        res = erase_user(self.iri)

    def test_KnoraUser(self):
        con = KnoraConnection('http://0.0.0.0:3333')
        con.login('root@example.com', 'test')

        user = KnoraUser(
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

    def test_KnoraUser_read(self):
        con = KnoraConnection('http://0.0.0.0:3333')
        con.login('root@example.com', 'test')
        user = KnoraUser(
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

    def test_KnoraUser_create(self):
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

    def test_KnoraUser_delete(self):
        user = self.createTestUser()
        nuser = user.delete()
        self.assertIsNotNone(nuser)
        self.assertFalse(nuser.status)

    def test_KnoraUser_addToGroup(self):
        user = self.createTestUser()
        user.addToGroup('http://rdfh.ch/groups/0001/thing-searcher')
        nuser = user.update()
        self.assertIsNotNone(nuser)
        self.assertEqual(nuser.in_groups, {"http://rdfh.ch/groups/00FF/images-reviewer", 'http://rdfh.ch/groups/0001/thing-searcher'})


if __name__ == '__main__':
    unittest.main()
