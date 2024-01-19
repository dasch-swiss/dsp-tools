"""end to end tests for property class"""

import unittest

import pytest

from dsp_tools.commands.project.models.ontology import Ontology
from dsp_tools.commands.project.models.propertyclass import PropertyClass
from dsp_tools.models.helpers import DateTimeStamp
from dsp_tools.models.langstring import LangString, Languages
from dsp_tools.utils.connection import Connection
from dsp_tools.utils.connection_live import ConnectionLive

# ruff: noqa: PT009 (pytest-unittest-assertion) (remove this line when pytest is used instead of unittest)


class TestPropertyClass(unittest.TestCase):
    project = "http://rdfh.ch/projects/0001"
    onto_name = "propclass-test-a"
    onto_label = "propclass_test_ontology"

    onto: Ontology
    last_modification_date: DateTimeStamp
    con: Connection

    name = "MyPropClassName"
    rdf_object = "TextValue"
    label = LangString({Languages.DE: "MyPropClassLabel"})
    comment = LangString({Languages.DE: "This is a property class for testing"})

    def setUp(self) -> None:
        """
        Creates a connection and a new ontology.
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

    def test_PropertyClass_create(self) -> None:
        """
        create new property class
        """
        # Create a test ontology
        self.onto = Ontology(
            con=self.con,
            project=self.project,
            name=self.onto_name,
            label=self.onto_label,
        ).create()
        self.assertIsNotNone(self.onto.iri)
        self.last_modification_date = self.onto.lastModificationDate

        # create new property class
        self.last_modification_date, property_class = PropertyClass(
            con=self.con,
            context=self.onto.context,
            name=self.name,
            ontology_id=self.onto.iri,
            rdf_object=self.rdf_object,
            label=self.label,
            comment=self.comment,
        ).create(self.last_modification_date)

        self.onto.lastModificationDate = self.last_modification_date

        self.assertIsNotNone(property_class.iri)
        self.assertEqual(property_class.name, self.name)
        self.assertEqual(property_class.label["de"], self.label["de"])
        self.assertEqual(property_class.comment["de"], self.comment["de"])

        # get ontology data
        self.onto = self.onto.read()
        self.last_modification_date = self.onto.lastModificationDate
        self.last_modification_date = property_class.delete(self.last_modification_date)

        # get ontology data
        self.onto = self.onto.read()

    def test_PropertyClass_update(self) -> None:
        self.onto = self.onto.read()

        # create test resource class
        self.last_modification_date, property_class = PropertyClass(
            con=self.con,
            context=self.onto.context,
            name="foo",
            ontology_id=self.onto.iri,
            rdf_object=self.rdf_object,
            label=self.label,
            comment=self.comment,
        ).create(self.last_modification_date)
        self.onto.lastModificationDate = self.last_modification_date
        self.assertIsNotNone(property_class.iri)

        # modify the property class
        property_class.addLabel("en", "This is english comment")
        property_class.rmLabel("de")
        property_class.addComment("it", "Commentario italiano")
        self.last_modification_date, property_class_updated = property_class.update(self.last_modification_date)
        self.onto.lastModificationDate = self.last_modification_date
        self.assertEqual(property_class_updated.label["en"], "This is english comment")
        self.assertEqual(property_class_updated.comment["it"], "Commentario italiano")

        # delete the resource class to clean up
        self.last_modification_date = property_class_updated.delete(self.last_modification_date)
        self.onto.lastModificationDate = self.last_modification_date


if __name__ == "__main__":
    pytest.main([__file__])
