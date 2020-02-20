import unittest
import pprint
import requests
from urllib.parse import quote_plus

from connection import Connection
from group import Group
from helpers import BaseError, Languages, Actions, LangString


def erase_group(iri = None):
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


class TestGroup(unittest.TestCase):

    iri = None

    def tearDown(self):
        res = erase_group(self.iri)

    def test_Group(self):
        con = Connection('http://0.0.0.0:3333')
        con.login('root@example.com', 'test')

        group = Group(con=con,
                           name="KNORA-PY-TEST",
                           description="Test project for knora-py",
                           project="http://rdfh.ch/projects/0001",
                           status=True,
                           selfjoin=False)
        self.assertEqual(group.name, 'KNORA-PY-TEST')
        self.assertEqual(group.description, 'Test project for knora-py')
        self.assertEqual(group.project, 'http://rdfh.ch/projects/0001')
        self.assertTrue(group.status)
        self.assertFalse(group.selfjoin)

    def test_Group_read(self):
        con = Connection('http://0.0.0.0:3333')
        con.login('root@example.com', 'test')

        group = Group(con=con,
                           id='http://rdfh.ch/groups/0001/thing-searcher').read()
        self.assertEqual(group.name, 'Thing searcher')
        self.assertEqual(group.description, 'A group for thing searchers.')
        self.assertEqual(group.project, 'http://rdfh.ch/projects/0001')
        self.assertTrue(group.status)
        self.assertTrue(group.selfjoin)

    def test_Group_create(self):
        global __iri
        con = Connection('http://0.0.0.0:3333')
        con.login('root@example.com', 'test')

        group = Group(con=con,
                           name="KNORA-PY TEST",
                           description="Test project for knora-py",
                           project="http://rdfh.ch/projects/0001",
                           status=True,
                           selfjoin=False).create()
        self.iri = group.id

        self.assertEqual(group.name, 'KNORA-PY TEST')
        self.assertEqual(group.description, 'Test project for knora-py')
        self.assertEqual(group.project, 'http://rdfh.ch/projects/0001')
        self.assertTrue(group.status)
        self.assertFalse(group.selfjoin)

    def test_Group_update(self):
        con = Connection('http://0.0.0.0:3333')
        con.login('root@example.com', 'test')

        group = Group(con=con,
                           name="KNORA-PY TEST",
                           description="Test project for knora-py",
                           project="http://rdfh.ch/projects/0001",
                           status=True,
                           selfjoin=False).create()
        self.iri = group.id
        group.name="KNORA-PY TEST - modified"
        group.description = "gaga gaga gaga gaga gaga gaga gaga"
        group.selfjoin = True
        group.status = False
        ngroup = group.update()
        self.assertEqual(group.name, 'KNORA-PY TEST - modified')
        self.assertEqual(group.description, 'gaga gaga gaga gaga gaga gaga gaga')
        self.assertEqual(group.project, 'http://rdfh.ch/projects/0001')
        self.assertFalse(group.status)
        self.assertTrue(group.selfjoin)

    def test_Group_delete(self):
        con = Connection('http://0.0.0.0:3333')
        con.login('root@example.com', 'test')

        group = Group(con=con,
                           name="KNORA-PY TEST",
                           description="Test project for knora-py",
                           project="http://rdfh.ch/projects/0001",
                           status=True,
                           selfjoin=False).create()
        self.iri = group.id
        ngroup = group.delete()
        self.assertEqual(ngroup.name, 'KNORA-PY TEST')
        self.assertEqual(ngroup.description, 'Test project for knora-py')
        self.assertEqual(ngroup.project, 'http://rdfh.ch/projects/0001')
        self.assertFalse(ngroup.status)
        self.assertFalse(ngroup.selfjoin)

    def test_getAllGroups(self):
        con = Connection('http://0.0.0.0:3333')
        con.login('root@example.com', 'test')
        groups = Group.getAllGroups(con)
        self.assertIsNotNone(groups)
        self.assertEqual(len(groups), 2)


if __name__ == '__main__':
    unittest.main()
