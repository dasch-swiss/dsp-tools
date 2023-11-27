"""end to end tests for resourceClass class"""

# ruff: noqa: D101 (undocumented-public-class)
# ruff: noqa: D102 (undocumented-public-method)

import unittest

import pytest

from dsp_tools.commands.project.models.ontology import Ontology
from dsp_tools.commands.project.models.resourceclass import ResourceClass
from dsp_tools.models.langstring import LangString, Languages
from dsp_tools.utils.connection import Connection
from dsp_tools.utils.connection_live import ConnectionLive


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
        self.con = ConnectionLive(server="http://0.0.0.0:3333")
        self.con.login(email="root@example.com", password="test")

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

        # modify the resource class
        res_class.addLabel("de", "Dies ist ein Kommentar")
        res_class.rmLabel("en")
        res_class.addComment("it", "Commentario italiano")

        last_modification_date, res_class = res_class.update(last_modification_date)
        self.assertEqual(res_class.label["de"], "Dies ist ein Kommentar")
        self.assertEqual(res_class.comment["it"], "Commentario italiano")


if __name__ == "__main__":
    pytest.main([__file__])
