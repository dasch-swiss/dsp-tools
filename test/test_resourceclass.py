import unittest
import pprint
import requests
from urllib.parse import quote_plus

from knora.models.connection import Connection
from knora.models.helpers import BaseError, Actions, LastModificationDate
from knora.models.langstring import Languages, LangStringParam, LangString
from knora.models.ontology import Ontology
from knora.models.resourceclass import ResourceClass, HasProperty


class TestResourceClass(unittest.TestCase):
    con: Connection

    project = "http://rdfh.ch/projects/0001"
    onto_name = 'resclass-test'
    onto_label = 'resclass_test_ontology'

    onto: Ontology
    last_modification_date: LastModificationDate

    label = LangString({Languages.DE: 'MyResClassLabel'})
    comment = LangString({Languages.DE: 'This is a resource class for testing'})
    name = 'MyResClassName'

    def setUp(self) -> None:
        #
        # Connect to Knora
        #
        self.con = Connection('http://0.0.0.0:3333')
        self.con.login('root@example.com', 'test')

        #
        # Create a test ontology
        #
        self.last_modification_date, self.onto = Ontology(
            con=self.con,
            project=self.project,
            name=self.onto_name,
            label=self.onto_label,
        ).create()
        self.assertIsNotNone(self.onto.id)

    def tearDown(self):
        #
        # remove test ontology
        #
        result = self.onto.delete(self.last_modification_date)
        self.assertIsNotNone(result)


    def test_ResourceClass_create(self):
        #
        # Create new resource class
        #
        self.last_modification_date, resclass = ResourceClass(
            con=self.con,
            context=self.onto.context,
            name=self.name,
            ontology_id=self.onto.id,
            label=self.label,
            comment=self.comment
        ).create(self.last_modification_date)
        self.assertIsNotNone(resclass.id)

        self.assertEqual(resclass.name, self.name)
        self.assertEqual(resclass.label['de'], self.label['de'])
        self.assertEqual(resclass.comment['de'], self.comment['de'])

        #
        # Again get ontology data
        #
        self.last_modification_date = resclass.delete(self.last_modification_date)


    def test_ResourceClass_update(self):
        #
        # create test resource class
        #
        self.last_modification_date, resclass = ResourceClass(
            con=self.con,
            context=self.onto.context,
            name=self.name,
            ontology_id=self.onto.id,
            label=self.label,
            comment=self.comment
        ).create(self.last_modification_date)
        self.assertIsNotNone(resclass.id)

        #
        # Modify the resource class
        #
        resclass.addLabel('en', "This is english gaga")
        resclass.rmLabel('de')
        resclass.addComment('it', "Commentario italiano")
        self.last_modification_date, resclass = resclass.update(self.last_modification_date)
        self.assertEqual(resclass.label['en'], "This is english gaga")
        self.assertEqual(resclass.comment['it'], "Commentario italiano")

        #
        # Now delete the resource class to clean up
        #
        self.last_modification_date = resclass.delete(self.last_modification_date)


if __name__ == '__main__':
    unittest.main()
