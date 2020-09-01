import unittest

from dsplib.models.connection import Connection
from dsplib.models.helpers import BaseError, Actions, Cardinality, LastModificationDate
from dsplib.models.langstring import Languages, LangStringParam, LangString
from dsplib.models.ontology import Ontology
from dsplib.models.resourceclass import ResourceClass, HasProperty
from dsplib.models.propertyclass import PropertyClass


class TestAllClass(unittest.TestCase):
    project = "http://rdfh.ch/projects/0001"
    onto_name = 'all-test'
    onto_label = 'all_test_ontology'

    resclass_name = 'MyResClassName'
    resclass_label = LangString({Languages.DE: 'MyResClassLabel'})
    resclass_comment = LangString({Languages.DE: 'This is a resource class for testing'})

    propclass_name = 'MyPropClassName'
    propclass_object = 'TextValue'
    propclass_label = LangString({Languages.DE: 'MyPropClassLabel'})
    propclass_comment = LangString({Languages.DE: 'This is a property class for testing'})

    con: Connection
    onto: Ontology
    last_modification_date: LastModificationDate

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

    def test_AllThings_create(self):
        #
        # Create new resource class
        #
        self.last_modification_date, resclass = ResourceClass(
            con=self.con,
            context=self.onto.context,
            name=self.resclass_name,
            ontology_id=self.onto.id,
            label=self.resclass_label,
            comment=self.resclass_comment
        ).create(self.last_modification_date)
        self.assertIsNotNone(resclass.id)

        self.assertEqual(resclass.name, self.resclass_name)
        self.assertEqual(resclass.label['de'], self.resclass_label['de'])
        self.assertEqual(resclass.comment['de'], self.resclass_comment['de'])

        #
        # Create new property class
        #
        self.last_modification_date, propclass = PropertyClass(
            con=self.con,
            context=self.onto.context,
            name=self.propclass_name,
            ontology_id=self.onto.id,
            object=self.propclass_object,
            label=self.propclass_label,
            comment=self.propclass_comment
        ).create(self.last_modification_date)
        self.assertIsNotNone(propclass.id)

        self.assertEqual(propclass.name, self.propclass_name)
        self.assertEqual(propclass.label['de'], self.propclass_label['de'])
        self.assertEqual(propclass.comment['de'], self.propclass_comment['de'])

        #
        # Create HasProperty (cardinality)
        #
        self.last_modification_date = resclass.addProperty(propclass.id, Cardinality.C_1, self.last_modification_date)
        self.assertEqual(resclass.getProperty(propclass.id).cardinality, Cardinality.C_1)
        self.assertIsNotNone(self.last_modification_date)

        #
        # Modify HasProperty (cardinality)
        #
        self.last_modification_date = resclass.updateProperty(propclass.id, Cardinality.C_1_n, self.last_modification_date)
        self.assertEqual(resclass.getProperty(propclass.id).cardinality, Cardinality.C_1_n)
        self.assertIsNotNone(self.last_modification_date)


if __name__ == '__main__':
    unittest.main()
