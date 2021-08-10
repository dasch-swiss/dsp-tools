"""This test class tests the basic functionalities of dsp-tools"""
import json
import unittest

from knora.dsplib.utils import excel_to_json_lists
from knora.dsplib.utils.excel_to_json_lists import list_excel2json
from knora.dsplib.utils.onto_create_ontology import create_ontology
from knora.dsplib.utils.onto_get import get_ontology
from knora.dsplib.utils.onto_validate import validate_ontology
from knora.dsplib.utils.xml_upload import xml_upload


class TestTools(unittest.TestCase):
    def setUp(self) -> None:
        """Is executed before each test"""
        excel_to_json_lists.list_of_lists = []
        excel_to_json_lists.cell_names = []

    def tearDown(self) -> None:
        """Is executed after each test"""
        excel_to_json_lists.list_of_lists = []
        excel_to_json_lists.cell_names = []

    def test_get(self):
        with open('testdata/anything-onto.json') as f:
            onto_json_str = f.read()
        anything_onto = json.loads(onto_json_str)

        get_ontology(projident='anything',
                     outfile='_anything-onto.json',
                     server='http://0.0.0.0:3333',
                     user='root@example.com',
                     password='test',
                     verbose=True)

        with open('_anything-onto.json') as f:
            onto_json_str = f.read()
        anything_onto_out = json.loads(onto_json_str)

        self.assertEqual(anything_onto['project']['shortcode'], anything_onto_out['project']['shortcode'])
        self.assertEqual(anything_onto['project']['shortname'], anything_onto_out['project']['shortname'])
        self.assertEqual(anything_onto['project']['longname'], anything_onto_out['project']['longname'])

        for list in anything_onto['project']['lists']:
            list_name = list.get('name')
            if list_name == 'otherTreeList':
                other_tree_list = list
            elif list_name == 'notUsedList':
                not_used_list = list
            elif list_name == 'treelistroot':
                tree_list_root = list

        for list in anything_onto_out['project']['lists']:
            list_name = list.get('name')
            print(list.get('name'))
            if list_name == 'otherTreeList':
                other_tree_list_out = list
            elif list_name == 'notUsedList':
                not_used_list_out = list
            elif list_name == 'treelistroot':
                tree_list_root_out = list

        self.assertEqual(other_tree_list.get('labels'), other_tree_list_out.get('labels'))
        self.assertEqual(other_tree_list.get('comments'), other_tree_list_out.get('comments'))
        self.assertEqual(other_tree_list.get('nodes'), other_tree_list_out.get('nodes'))

        self.assertEqual(not_used_list.get('labels'), not_used_list_out.get('labels'))
        self.assertEqual(not_used_list.get('comments'), not_used_list_out.get('comments'))
        self.assertEqual(not_used_list.get('nodes'), not_used_list_out.get('nodes'))

        self.assertEqual(tree_list_root.get('labels'), tree_list_root_out.get('labels'))
        self.assertEqual(tree_list_root.get('comments'), tree_list_root_out.get('comments'))
        self.assertEqual(tree_list_root.get('nodes'), tree_list_root_out.get('nodes'))

        # TODO fix this test
        # self.assertEqual(anything_onto['project']['ontologies'], anything_onto_out['project']['ontologies'])

    def test_excel(self):
        list_excel2json(listname='my_test_list',
                        excelfolder='testdata/lists',
                        outfile='_lists-out.json')

    def test_validate_ontology(self):
        validate_ontology('testdata/test-onto.json')

    def test_create_ontology(self):
        create_ontology(input_file='testdata/test-onto.json',
                        lists_file='lists-out.json',
                        server='http://0.0.0.0:3333',
                        user='root@example.com',
                        password='test',
                        verbose=True,
                        dump=True)

    def test_xml_upload(self):
        xml_upload(input_file='testdata/test-data.xml',
                   server='http://0.0.0.0:3333',
                   user='root@example.com',
                   password='test',
                   imgdir='testdata/bitstreams',
                   sipi='http://0.0.0.0:1024',
                   verbose=True,
                   validate_only=False)


if __name__ == '__main__':
    unittest.main()
