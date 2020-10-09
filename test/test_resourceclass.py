import unittest

from dsplib.models.connection import Connection
from dsplib.models.helpers import BaseError, Actions, LastModificationDate
from dsplib.models.langstring import Languages, LangStringParam, LangString
from dsplib.models.ontology import Ontology
from dsplib.models.resourceclass import ResourceClass, HasProperty


class TestResourceClass(unittest.TestCase):
    project = "http://rdfh.ch/projects/0001"

    label = LangString({Languages.DE: 'MyResClassLabel'})
    comment = LangString({Languages.DE: 'This is a resource class for testing'})
    name = 'MyResClassName'


    def test_ResourceClass_create(self):
        #
        # Connect to Knora
        #
        con = Connection('http://0.0.0.0:3333')
        con.login('root@example.com', 'test')

        #
        # Create a test ontology
        #
        onto = Ontology(
            con=con,
            project=self.project,
            name='resclass-test-onto-1',
            label='resclass test ontology 1',
        ).create()
        last_modification_date = onto.lastModificationDate
        self.assertIsNotNone(onto.id)
        #
        # Create new resource class
        #
        last_modification_date, resclass = ResourceClass(
            con=con,
            context=onto.context,
            name=self.name,
            ontology_id=onto.id,
            label=self.label,
            comment=self.comment
        ).create(last_modification_date)
        onto.lastModificationDate = last_modification_date
        self.assertIsNotNone(resclass.id)

        self.assertEqual(resclass.name, self.name)
        self.assertEqual(resclass.label['de'], self.label['de'])
        self.assertEqual(resclass.comment['de'], self.comment['de'])

        #
        # Delete the new resource class
        #
        last_modification_date = resclass.delete(last_modification_date)
        onto.lastModificationDate = last_modification_date


    def test_ResourceClass_update(self):
        #
        # Connect to Knora
        #
        con = Connection('http://0.0.0.0:3333')
        con.login('root@example.com', 'test')

        #
        # Create a test ontology
        #
        onto = Ontology(
            con=con,
            project=self.project,
            name='resclass-test-onto-2',
            label='resclass test ontology 2',
        ).create()
        last_modification_date = onto.lastModificationDate
        self.assertIsNotNone(onto.id)
        #
        # create test resource class
        #
        last_modification_date, resclass = ResourceClass(
            con=con,
            context=onto.context,
            name=self.name,
            ontology_id=onto.id,
            label=self.label,
            comment=self.comment
        ).create(last_modification_date)
        onto.lastModificationDate = last_modification_date
        self.assertIsNotNone(resclass.id)

        #
        # Modify the resource class
        #
        resclass.addLabel('en', "This is english gaga")
        resclass.rmLabel('de')
        resclass.addComment('it', "Commentario italiano")
        last_modification_date, resclass = resclass.update(last_modification_date)
        onto.lastModificationDate = last_modification_date
        self.assertEqual(resclass.label['en'], "This is english gaga")
        self.assertEqual(resclass.comment['it'], "Commentario italiano")

        #
        # Now delete the resource class to clean up
        #
        last_modification_date = resclass.delete(last_modification_date)
        onto.lastModificationDate = last_modification_date


if __name__ == '__main__':
    unittest.main()
