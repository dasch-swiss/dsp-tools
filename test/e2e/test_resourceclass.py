"""end to end tests for resourceClass class"""
import unittest

from knora.dsplib.models.connection import Connection
from knora.dsplib.models.langstring import Languages, LangString
from knora.dsplib.models.ontology import Ontology
from knora.dsplib.models.resourceclass import ResourceClass


class TestResourceClass(unittest.TestCase):
    test_project = "http://rdfh.ch/projects/Lw3FC39BSzCwvmdOaTyLqQ"

    res_name = 'res_class_name'
    res_label = LangString({Languages.EN: 'Resource Class Label'})
    res_comment = LangString({Languages.EN: 'This is a resource class for testing'})

    def setUp(self) -> None:
        """
        is executed before all tests; sets up a connection and logs in as user root
        """
        self.con = Connection('http://0.0.0.0:3333')
        self.con.login('root@example.com', 'test')

    def test_ResourceClass_create(self) -> None:
        onto = Ontology(
            con=self.con,
            project=self.test_project,
            name='test_onto',
            label='Test Ontology',
        ).create()

        last_modification_date_onto = onto.lastModificationDate

        # create test resource class
        last_modification_date_res, res_class = ResourceClass(
            con=self.con,
            context=onto.context,
            name=self.res_name,
            ontology_id=onto.id,
            label=self.res_label,
            comment=self.res_comment
        ).create(last_modification_date_onto)

        self.assertIsNotNone(res_class.id)
        self.assertEqual(res_class.name, self.res_name)
        self.assertEqual(res_class.label['en'], self.res_label['en'])
        self.assertEqual(res_class.comment['en'], self.res_comment['en'])

    def test_ResourceClass_update(self) -> None:
        onto = Ontology(
            con=self.con,
            project=self.test_project,
            name='test_onto_2',
            label='Test Ontology 2',
        ).create()

        last_modification_date = onto.lastModificationDate

        # create test resource class
        last_modification_date, res_class = ResourceClass(
            con=self.con,
            context=onto.context,
            name=self.res_name,
            ontology_id=onto.id,
            label=self.res_label,
            comment=self.res_comment
        ).create(last_modification_date)

        onto.lastModificationDate = last_modification_date

        self.assertIsNotNone(res_class.id)

        # modify the resource class
        res_class.addLabel('de', "Dies ist ein Kommentar")
        res_class.rmLabel('en')
        res_class.addComment('it', "Commentario italiano")

        last_modification_date, res_class = res_class.update(last_modification_date)
        self.assertEqual(res_class.label['de'], "Dies ist ein Kommentar")
        self.assertEqual(res_class.comment['it'], "Commentario italiano")

    def tearDown(self) -> None:
        """
        is executed after all tests are run through; performs a log out
        """
        self.con.logout()


if __name__ == '__main__':
    unittest.main()
