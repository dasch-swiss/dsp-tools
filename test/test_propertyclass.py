import unittest
import pprint

from dsplib.models.connection import Connection
from dsplib.models.helpers import BaseError, Actions, LastModificationDate
from dsplib.models.langstring import Languages, LangStringParam, LangString
from dsplib.models.ontology import Ontology
from dsplib.models.propertyclass import PropertyClass


class TestPropertyClass(unittest.TestCase):
    project = "http://rdfh.ch/projects/0001"
    onto_name = 'propclass-test'
    onto_label = 'propclass_test_ontology'

    onto: Ontology
    last_modification_date: LastModificationDate
    con: Connection

    name = 'MyPropClassName'
    object = 'TextValue'
    label = LangString({Languages.DE: 'MyPropClassLabel'})
    comment = LangString({Languages.DE: 'This is a property class for testing'})


    def setUp(self) -> None:
        #
        # Connect to Knora
        #
        self.con = Connection('http://0.0.0.0:3333')
        self.con.login('root@example.com', 'test')

        #
        # Create a test ontology
        #
        self.onto = Ontology(
            con=self.con,
            project=self.project,
            name=self.onto_name,
            label=self.onto_label,
        ).create()
        self.assertIsNotNone(self.onto.id)
        self.last_modification_date = self.onto.lastModificationDate

    def tearDown(self):
        #
        # remove test ontology
        #
        result = self.onto.delete()
        self.assertIsNotNone(result)


    def test_PropertyClass_create(self):
        #
        # Create new property class
        #
        self.last_modification_date, propclass = PropertyClass(
            con=self.con,
            context=self.onto.context,
            name=self.name,
            ontology_id=self.onto.id,
            object=self.object,
            label=self.label,
            comment=self.comment
        ).create(self.last_modification_date)
        self.onto.lastModificationDate = self.last_modification_date
        self.assertIsNotNone(propclass.id)

        self.assertEqual(propclass.name, self.name)
        self.assertEqual(propclass.label['de'], self.label['de'])
        self.assertEqual(propclass.comment['de'], self.comment['de'])

        #
        # Again get ontology data
        #
        self.onto = self.onto.read()
        self.last_modification_date = self.onto.lastModificationDate
        self.last_modification_date = propclass.delete(self.last_modification_date)

        #
        # Again get ontology data
        #
        self.onto = self.onto.read()

    def test_PropertyClass_update(self):
        self.onto = self.onto.read()

        #
        # create test resource class
        #
        self.last_modification_date, propclass = PropertyClass(
            con=self.con,
            context=self.onto.context,
            name=self.name,
            ontology_id=self.onto.id,
            object=self.object,
            label=self.label,
            comment=self.comment
        ).create(self.last_modification_date)
        self.onto.lastModificationDate = self.last_modification_date
        self.assertIsNotNone(propclass.id)

        #
        # Modify the property class
        #
        propclass.addLabel('en', "This is english gaga")
        propclass.rmLabel('de')
        propclass.addComment('it', "Commentario italiano")
        self.last_modification_date, propclass = propclass.update(self.last_modification_date)
        self.onto.lastModificationDate = self.last_modification_date
        self.assertEqual(propclass.label['en'], "This is english gaga")
        self.assertEqual(propclass.comment['it'], "Commentario italiano")

        #
        # Now delete the resource class to clean up
        #
        self.last_modification_date = propclass.delete(self.last_modification_date)
        self.onto.lastModificationDate = self.last_modification_date


if __name__ == '__main__':
    unittest.main()
