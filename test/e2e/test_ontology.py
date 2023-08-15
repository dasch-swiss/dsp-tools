"""end to end tests for ontology class"""

# pylint: disable=missing-class-docstring,missing-function-docstring

import unittest

import pytest

from dsp_tools.models.connection import Connection
from dsp_tools.models.helpers import DateTimeStamp
from dsp_tools.models.ontology import Ontology


class TestOntology(unittest.TestCase):
    con = Connection(server="http://0.0.0.0:3333", user_email="root@example.com", password="test")
    test_project = "http://rdfh.ch/projects/0001"
    test_onto = "http://0.0.0.0:3333/ontology/0001/anything/v2"

    def test_Ontology(self) -> None:
        last_mod_date_str = "2017-12-19T15:23:42.166Z"
        onto = Ontology(
            con=self.con,
            project=self.test_project,
            name="test_onto_name",
            label="Test ontology label",
            lastModificationDate=last_mod_date_str,
        )
        self.assertEqual(onto.project, self.test_project)
        self.assertEqual(onto.name, "test_onto_name")
        self.assertEqual(onto.label, "Test ontology label")
        self.assertEqual(onto.lastModificationDate, DateTimeStamp(last_mod_date_str))

    def test_ontology_read(self) -> None:
        onto = Ontology(con=self.con, iri=self.test_onto).read()

        self.assertEqual(onto.iri, self.test_onto)
        self.assertEqual(onto.project, self.test_project)
        self.assertEqual(onto.name, "anything")
        self.assertEqual(onto.label, "The anything ontology")
        self.assertIsNotNone(onto.lastModificationDate)

    def test_ontology_create(self) -> None:
        onto = Ontology(
            con=self.con,
            project=self.test_project,
            name="test_onto_create",
            label="Test ontology create label",
        ).create()

        self.assertIsNotNone(onto.iri)
        self.assertEqual(onto.iri, "http://0.0.0.0:3333/ontology/0001/" + "test_onto_create" + "/v2")
        self.assertEqual(onto.project, self.test_project)
        self.assertEqual(onto.name, "test_onto_create")
        self.assertEqual(onto.label, "Test ontology create label")
        self.assertIsNotNone(onto.lastModificationDate)

    def test_ontology_update_label(self) -> None:
        onto = Ontology(
            con=self.con,
            project=self.test_project,
            name="test_onto_update",
            label="Test ontology update label",
        ).create()

        onto.label = "Test ontology update label - modified"
        onto = onto.update()
        self.assertEqual(onto.label, "Test ontology update label - modified")

    def test_ontology_delete(self) -> None:
        onto = Ontology(
            con=self.con,
            project=self.test_project,
            name="test_onto_delete",
            label="Test ontology delete label",
        ).create()

        res = onto.delete()
        self.assertEqual(res, "Ontology http://0.0.0.0:3333/ontology/0001/test_onto_delete/v2 has been deleted")

    def test_ontology_getProjectOntologies(self) -> None:
        onto_list = Ontology.getProjectOntologies(self.con, self.test_project)
        onto_list_ids = [l.iri for l in onto_list]
        self.assertIn("http://0.0.0.0:3333/ontology/0001/anything/v2", onto_list_ids)
        self.assertIn("http://0.0.0.0:3333/ontology/0001/test_onto_create/v2", onto_list_ids)


if __name__ == "__main__":
    pytest.main([__file__])
