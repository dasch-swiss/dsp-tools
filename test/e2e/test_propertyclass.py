"""end to end tests for property class"""
import unittest

from knora.dsplib.models.connection import Connection
from knora.dsplib.models.helpers import DateTimeStamp
from knora.dsplib.models.langstring import Languages, LangString
from knora.dsplib.models.ontology import Ontology
from knora.dsplib.models.propertyclass import PropertyClass


class TestPropertyClass(unittest.TestCase):
    project = "http://rdfh.ch/projects/0001"
    onto_name = 'propclass-test-a'
    onto_label = 'propclass_test_ontology'

    onto: Ontology
    last_modification_date: DateTimeStamp
    con: Connection

    name = 'MyPropClassName'
    object = 'TextValue'
    label = LangString({Languages.DE: 'MyPropClassLabel'})
    comment = LangString({Languages.DE: 'This is a property class for testing'})

    def setUp(self) -> None:
        """
        is executed before all tests; sets up a connection and logs in as user root; creates a new ontology
        """
        self.con = Connection('http://0.0.0.0:3333')
        self.con.login('root@example.com', 'test')

        # Create a test ontology
        self.onto = Ontology(
            con=self.con,
            project=self.project,
            name=self.onto_name,
            label=self.onto_label,
        ).create()

        self.assertIsNotNone(self.onto.id)
        self.last_modification_date = self.onto.lastModificationDate

    def tearDown(self) -> None:
        """
        is executed after all tests are run through; removes test ontology
        """
        result = self.onto.delete()
        self.assertIsNotNone(result)

    def test_PropertyClass_create(self) -> None:
        """
        create new property class
        """
        self.last_modification_date, property_class = PropertyClass(
            con=self.con,
            context=self.onto.context,
            name=self.name,
            ontology_id=self.onto.id,
            object=self.object,
            label=self.label,
            comment=self.comment
        ).create(self.last_modification_date)

        self.onto.lastModificationDate = self.last_modification_date

        self.assertIsNotNone(property_class.id)
        self.assertEqual(property_class.name, self.name)
        self.assertEqual(property_class.label['de'], self.label['de'])
        self.assertEqual(property_class.comment['de'], self.comment['de'])

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
            name=self.name,
            ontology_id=self.onto.id,
            object=self.object,
            label=self.label,
            comment=self.comment
        ).create(self.last_modification_date)
        self.onto.lastModificationDate = self.last_modification_date
        self.assertIsNotNone(property_class.id)

        # modify the property class
        property_class.addLabel('en', "This is english comment")
        property_class.rmLabel('de')
        property_class.addComment('it', "Commentario italiano")
        self.last_modification_date, property_class_updated = property_class.update(self.last_modification_date)
        self.onto.lastModificationDate = self.last_modification_date
        self.assertEqual(property_class_updated.label['en'], "This is english comment")
        self.assertEqual(property_class_updated.comment['it'], "Commentario italiano")

        # delete the resource class to clean up
        self.last_modification_date = property_class_updated.delete(self.last_modification_date)
        self.onto.lastModificationDate = self.last_modification_date


if __name__ == '__main__':
    unittest.main()
