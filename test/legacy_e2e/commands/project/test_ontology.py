"""end to end tests for ontology class"""

import unittest

import pytest

from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.clients.connection import Connection
from dsp_tools.clients.connection_live import ConnectionLive
from dsp_tools.commands.project.legacy_models.ontology import Ontology
from dsp_tools.legacy_models.datetimestamp import DateTimeStamp

# ruff: noqa: PT009 (pytest-unittest-assertion) (remove this line when pytest is used instead of unittest)


class TestOntology(unittest.TestCase):
    con: Connection
    test_project = "http://rdfh.ch/projects/0001"
    test_onto = "http://0.0.0.0:3333/ontology/0001/anything/v2"

    def setUp(self) -> None:
        """
        Creates a connection to DSP-API.
        For each test method, a new TestCase instance is created, so setUp() is executed before each test method.
        """
        auth = AuthenticationClientLive("http://0.0.0.0:3333", "root@example.com", "test")
        self.con = ConnectionLive("http://0.0.0.0:3333", auth)

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

    def test_ontology_getProjectOntologies(self) -> None:
        onto_list = Ontology.getProjectOntologies(self.con, self.test_project)
        onto_list_ids = [lst.iri for lst in onto_list]
        self.assertIn("http://0.0.0.0:3333/ontology/0001/anything/v2", onto_list_ids)
        self.assertIn("http://0.0.0.0:3333/ontology/0001/test_onto_create/v2", onto_list_ids)


if __name__ == "__main__":
    pytest.main([__file__])
