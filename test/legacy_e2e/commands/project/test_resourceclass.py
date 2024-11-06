"""end to end tests for resourceClass class"""

import unittest

import pytest

from dsp_tools.commands.project.models.ontology import Ontology
from dsp_tools.commands.project.models.resourceclass import ResourceClass
from dsp_tools.models.langstring import LangString
from dsp_tools.models.langstring import Languages
from dsp_tools.utils.authentication_client_live import AuthenticationClientLive
from dsp_tools.utils.connection import Connection
from dsp_tools.utils.connection_live import ConnectionLive

# ruff: noqa: PT009 (pytest-unittest-assertion) (remove this line when pytest is used instead of unittest)


class TestResourceClass(unittest.TestCase):
    test_project = "http://rdfh.ch/projects/0001"
    res_name = "res_class_name"
    res_label = LangString({Languages.EN: "Resource Class Label"})
    res_comment = LangString({Languages.EN: "This is a resource class for testing"})
    con: Connection

    def setUp(self) -> None:
        """
        Creates a connection to DSP-API.
        For each test method, a new TestCase instance is created, so setUp() is executed before each test method.
        """
        auth = AuthenticationClientLive("http://0.0.0.0:3333", "root@example.com", "test")
        self.con = ConnectionLive("http://0.0.0.0:3333", auth)

    def tearDown(self) -> None:
        """
        Logs out from DSP-API.
        For each test method, a new TestCase instance is created, so tearDown() is executed after each test method.
        """
        self.con.logout()

    def test_ResourceClass_create(self) -> None:
        onto = Ontology(
            con=self.con,
            project=self.test_project,
            name="test_onto",
            label="Test Ontology",
        ).create()

        last_modification_date_onto = onto.lastModificationDate

        # create test resource class
        _, res_class = ResourceClass(
            con=self.con,
            context=onto.context,
            name=self.res_name,
            ontology_id=onto.iri,
            label=self.res_label,
            comment=self.res_comment,
        ).create(last_modification_date_onto)

        self.assertIsNotNone(res_class.iri)
        self.assertEqual(res_class.name, self.res_name)
        self.assertEqual(res_class.label["en"], self.res_label["en"])
        self.assertEqual(res_class.comment["en"], self.res_comment["en"])

    def test_ResourceClass_update(self) -> None:
        onto = Ontology(
            con=self.con,
            project=self.test_project,
            name="test_onto_2",
            label="Test Ontology 2",
        ).create()

        last_modification_date = onto.lastModificationDate

        # create test resource class
        last_modification_date, res_class = ResourceClass(
            con=self.con,
            context=onto.context,
            name=self.res_name,
            ontology_id=onto.iri,
            label=self.res_label,
            comment=self.res_comment,
        ).create(last_modification_date)

        onto.lastModificationDate = last_modification_date

        self.assertIsNotNone(res_class.iri)


if __name__ == "__main__":
    pytest.main([__file__])
