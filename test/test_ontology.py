import unittest

from dsplib.models.connection import Connection
from dsplib.models.helpers import BaseError, Actions, LastModificationDate
from dsplib.models.ontology import Ontology


class TestOntology(unittest.TestCase):
    project = "http://rdfh.ch/projects/0001"
    label = 'test_ontology'
    last_modification_date: LastModificationDate

    def setUp(self) -> None:
        self.con = Connection('http://0.0.0.0:3333')
        self.con.login('root@example.com', 'test')

    def test_ontology(self):
        onto = Ontology(
            con=self.con,
            project=self.project,
            name="test_ontology_0",
            label="test ontology 0",
            lastModificationDate="2017-12-19T15:23:42.166Z"
        )
        self.assertEqual(onto.project, self.project)
        self.assertEqual(onto.label, "test ontology 0")
        self.assertEqual(onto.lastModificationDate, LastModificationDate("2017-12-19T15:23:42.166Z"))

    def test_read(self):
        onto = Ontology(
            con=self.con,
            id='http://0.0.0.0:3333/ontology/0001/anything/v2'
        ).read()
        self.assertEqual(onto.id, "http://0.0.0.0:3333/ontology/0001/anything/v2")
        self.assertEqual(onto.project, "http://rdfh.ch/projects/0001")
        self.assertEqual(onto.label, "The anything ontology")
        self.assertIsNotNone(onto.lastModificationDate)

    def test_create(self):
        onto = Ontology(
            con=self.con,
            project=self.project,
            name="testonto_1",
            label="test ontology 1",
        ).create()
        self.assertIsNotNone(onto.id)
        self.assertEqual(onto.id, 'http://0.0.0.0:3333/ontology/0001/' + "testonto_1" + '/v2')
        self.assertEqual(onto.label, "test ontology 1")
        self.assertEqual(onto.project, self.project)

    def test_update(self):
        onto = Ontology(
            con=self.con,
            project=self.project,
            name="testonto_2",
            label="test ontology 2",
        ).create()
        self.assertIsNotNone(onto.id)
        onto.label = 'This is a modified label!'
        onto = onto.update()
        self.assertEqual(onto.label, 'This is a modified label!')

    def test_delete(self):
        onto = Ontology(
            con=self.con,
            project=self.project,
            name="testonto_3",
            label="test ontology 3",
        ).create()
        self.assertIsNotNone(onto.id)
        res = onto.delete()
        self.assertIsNotNone(res)

    def test_get_ontologies_of_project(self):
        ontolist = Ontology.getProjectOntologies(self.con, self.project)
        ontolist_ids = [x.id for x in ontolist]
        self.assertIn('http://0.0.0.0:3333/ontology/0001/anything/v2', ontolist_ids)
        self.assertIn('http://0.0.0.0:3333/ontology/0001/minimal/v2', ontolist_ids)
        self.assertIn('http://0.0.0.0:3333/ontology/0001/something/v2', ontolist_ids)


if __name__ == '__main__':
    unittest.main()
