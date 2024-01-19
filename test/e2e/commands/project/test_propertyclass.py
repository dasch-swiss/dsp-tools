"""end to end tests for property class"""

import unittest

import pytest

from dsp_tools.commands.project.models.ontology import Ontology
from dsp_tools.commands.project.models.propertyclass import PropertyClass
from dsp_tools.models.langstring import LangString, Languages
from dsp_tools.utils.connection_live import ConnectionLive

# ruff: noqa: PT009 (pytest-unittest-assertion) (remove this line when pytest is used instead of unittest)


class TestPropertyClass(unittest.TestCase):
    name = "MyPropClassName"
    label = LangString({Languages.DE: "MyPropClassLabel"})
    comment = LangString({Languages.DE: "This is a property class for testing"})

    def test_PropertyClass_create(self) -> None:
        con = ConnectionLive(server="http://0.0.0.0:3333")
        con.login(email="root@example.com", password="test")

        # Create a test ontology
        onto = Ontology(
            con=con,
            project="http://rdfh.ch/projects/0001",
            name="onto-1",
            label="onto-label",
        ).create()
        self.assertIsNotNone(onto.iri)
        last_modification_date = onto.lastModificationDate

        # create new property class
        last_modification_date, property_class = PropertyClass(
            con=con,
            context=onto.context,
            name=self.name,
            ontology_id=onto.iri,
            rdf_object="TextValue",
            label=self.label,
            comment=self.comment,
        ).create(last_modification_date)

        self.assertIsNotNone(property_class.iri)
        self.assertEqual(property_class.name, self.name)
        self.assertEqual(property_class.label["de"], self.label["de"])
        self.assertEqual(property_class.comment["de"], self.comment["de"])

        # modify the property class
        property_class.addLabel("en", "This is english comment")
        property_class.rmLabel("de")
        property_class.addComment("it", "Commentario italiano")
        last_modification_date, property_class_updated = property_class.update(last_modification_date)
        self.assertEqual(property_class_updated.label["en"], "This is english comment")
        self.assertEqual(property_class_updated.comment["it"], "Commentario italiano")

        # delete the property class to clean up
        _ = property_class_updated.delete(last_modification_date)


if __name__ == "__main__":
    pytest.main([__file__])
