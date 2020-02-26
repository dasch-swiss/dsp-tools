import unittest
import pprint
import requests
from urllib.parse import quote_plus

from connection import Connection
from helpers import BaseError, Languages, Actions, LangString
from ontology import Ontology


def erase_ontology(iri=None):
    if iri is None:
        return None

    print(quote_plus(iri.replace('0.0.0.0:3333', 'www.knora.org')))
    req = requests.delete('http://localhost:7200/repositories/knora-test/rdf-graphs/service?graph=' + quote_plus(iri.replace('0.0.0.0:3333', 'www.knora.org')),
                          headers={'Content-Type': 'text/plain',
                                   'Accept': 'application/json, application/x-turtle, */*'})
    pprint.pprint(req)
    if 'error' in req:
        print('ERROR: ' + req.error)
    if req.status_code != 204:
        print('STATUS-CODE: ' + str(req.status_code))
        print('TEXT: ' + req.text)
    return req.status_code


class TestOntology(unittest.TestCase):
    iri = None
    project = "http://rdfh.ch/projects/0001"
    name = 'pythontest'
    label = 'test_ontology'

    def tearDown(self):
        res = erase_ontology(self.iri)

    def createTestOntology(self):
        con = Connection('http://0.0.0.0:3333')
        con.login('root@example.com', 'test')
        onto = Ontology(
            con=con,
            project=self.project,
            name=self.name,
            label=self.label,
        ).create()
        self.assertIsNotNone(onto.id)
        self.iri = onto.id[:-3]
        return onto

    def test_Ontology(self):
        con = Connection('http://0.0.0.0:3333')
        onto = Ontology(
            con=con,
            project=self.project,
            name=self.name,
            label=self.label,
            lastModificationDate="2017-12-19T15:23:42.166Z"
        )
        self.assertEqual(onto.project, self.project)
        self.assertEqual(onto.label, self.label)
        self.assertEqual(onto.lastModificationDate, "2017-12-19T15:23:42.166Z")

    def test_read(self):
        con = Connection('http://0.0.0.0:3333')
        onto = Ontology(
            con=con,
            id='http://0.0.0.0:3333/ontology/0001/anything/v2'
        ).read()
        self.assertEqual(onto.id, "http://0.0.0.0:3333/ontology/0001/anything/v2")
        self.assertEqual(onto.project, "http://rdfh.ch/projects/0001")
        self.assertEqual(onto.label, "The anything ontology")
        self.assertIsNotNone(onto.lastModificationDate)

    def test_create(self):
        onto = self.createTestOntology()
        self.assertEqual(onto.id, 'http://0.0.0.0:3333/ontology/0001/' + self.name + '/v2')
        self.assertEqual(onto.label, self.label)
        self.assertEqual(onto.project, self.project)

    def test_update(self):
        onto = self.createTestOntology()
        onto.label = 'This is a modified label!'
        onto = onto.update()
        self.assertEqual(onto.label, 'This is a modified label!')

    def test_delete(self):
        onto = self.createTestOntology()
        res = onto.delete()
        self.assertIsNotNone(res)

    def test_get_ontologies_of_project(self):
        con = Connection('http://0.0.0.0:3333')
        ontos = Ontology.getProjectOntologies(con, self.project)
        self.assertEqual(len(ontos), 2)
        self.assertEqual(ontos[0].id, 'http://0.0.0.0:3333/ontology/0001/anything/v2')
        self.assertEqual(ontos[1].id, 'http://0.0.0.0:3333/ontology/0001/pythontest/v2')


if __name__ == '__main__':
    unittest.main()
