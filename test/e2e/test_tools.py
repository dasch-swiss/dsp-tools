"""This test class tests the basic functionalities of dsp-tools"""
import json
import unittest
import os
import datetime

from knora.dsplib.utils import excel_to_json_lists
from knora.dsplib.utils.excel_to_json_lists import list_excel2json
from knora.dsplib.utils.excel_to_json_properties import properties_excel2json
from knora.dsplib.utils.excel_to_json_resources import resources_excel2json
from knora.dsplib.utils.id_to_iri import id_to_iri
from knora.dsplib.utils.onto_create_ontology import create_project
from knora.dsplib.utils.onto_get import get_ontology
from knora.dsplib.utils.xml_upload import xml_upload


class TestTools(unittest.TestCase):
    server = 'http://0.0.0.0:3333'
    user = 'root@example.com'
    password = 'test'
    imgdir = '.'
    sipi = 'http://0.0.0.0:1024'
    test_project_file = 'testdata/test-project-systematic.json'
    test_project_minimal_file = 'testdata/test-project-minimal.json'
    test_data_file = 'testdata/test-data-systematic.xml'

    @classmethod
    def setUpClass(cls) -> None:
        """Is executed before the methods of this class are run"""
        os.makedirs('testdata/tmp', exist_ok=True)

    @classmethod
    def tearDownClass(cls) -> None:
        """Is executed after the methods of this class have all run through"""
        for file in os.listdir('testdata/tmp'):
            os.remove('testdata/tmp/' + file)
        os.rmdir('testdata/tmp')

    def test_get(self) -> None:
        with open(self.test_project_file) as f:
            project_json_str = f.read()
        test_project = json.loads(project_json_str)

        get_ontology(project_identifier='tp',
                     outfile='testdata/tmp/_test-project-systematic.json',
                     server=self.server,
                     user=self.user,
                     password='test',
                     verbose=True)

        with open('testdata/tmp/_test-project-systematic.json') as f:
            project_json_str = f.read()
        test_project_out = json.loads(project_json_str)

        self.assertEqual(test_project['project']['shortcode'], test_project_out['project']['shortcode'])
        self.assertEqual(test_project['project']['shortname'], test_project_out['project']['shortname'])
        self.assertEqual(test_project['project']['longname'], test_project_out['project']['longname'])
        self.assertEqual(test_project['project']['descriptions'], test_project_out['project']['descriptions'])
        self.assertEqual(sorted(test_project['project']['keywords']), sorted(test_project_out['project']['keywords']))

        groups_expected = test_project['project']['groups']
        groups_received = test_project_out['project']['groups']
        group_names_expected = []
        group_descriptions_expected = []
        group_selfjoin_expected = []
        group_status_expected = []
        groups_names_received = []
        group_descriptions_received = []
        group_selfjoin_received = []
        group_status_received = []
        for group in sorted(groups_expected, key=lambda x: x["name"]):
            group_names_expected.append(group["name"])
            group_descriptions_expected.append(group["descriptions"]["en"])
            group_selfjoin_expected.append(group.get("selfjoin", False))
            group_status_expected.append(group.get("status", True))
        for group in sorted(groups_received, key=lambda x: x["name"]):
            groups_names_received.append(group["name"])
            group_descriptions_received.append(group["descriptions"]["en"])
            group_selfjoin_received.append(group.get("selfjoin", False))
            group_status_received.append(group.get("status", True))
        self.assertEqual(sorted(group_names_expected), sorted(groups_names_received))
        self.assertEqual(sorted(group_descriptions_expected), sorted(group_descriptions_received))
        self.assertEqual(group_selfjoin_expected, group_selfjoin_received)
        self.assertEqual(group_status_expected, group_status_received)

        users_expected = test_project['project']['users']
        users_received = test_project_out['project']['users']
        user_username_expected = []
        user_email_expected = []
        user_given_name_expected = []
        user_family_name_expected = []
        user_lang_expected = []
        user_username_received = []
        user_email_received = []
        user_given_name_received = []
        user_family_name_received = []
        user_lang_received = []
        for user in users_expected:
            if user["username"] in ["testerKnownUser", "testerSystemAdmin"]:
                # ignore the ones who are not part of the project
                continue
            user_username_expected.append(user["username"])
            user_email_expected.append(user["email"])
            user_given_name_expected.append(user["givenName"])
            user_family_name_expected.append(user["familyName"])
            user_lang_expected.append(user["lang"])
        for user in users_received:
            user_username_received.append(user["username"])
            user_email_received.append(user["email"])
            user_given_name_received.append(user["givenName"])
            user_family_name_received.append(user["familyName"])
            user_lang_received.append(user["lang"])
        self.assertEqual(sorted(user_username_expected), sorted(user_username_received))
        self.assertEqual(sorted(user_email_expected), sorted(user_email_received))
        self.assertEqual(sorted(user_given_name_expected), sorted(user_given_name_received))
        self.assertEqual(sorted(user_family_name_expected), sorted(user_family_name_received))
        self.assertEqual(sorted(user_lang_expected), sorted(user_lang_received))

        ontos_expected = test_project['project']['ontologies']
        ontos_received = test_project_out['project']['ontologies']
        onto_names_expected = []
        onto_labels_expected = []
        onto_names_received = []
        onto_labels_received = []
        for onto in ontos_expected:
            onto_names_expected.append(onto["name"])
            onto_labels_expected.append(onto["label"])
        for onto in ontos_received:
            onto_names_received.append(onto["name"])
            onto_labels_received.append(onto["label"])
        self.assertEqual(sorted(onto_names_expected), sorted(onto_names_received))
        self.assertEqual(sorted(onto_labels_expected), sorted(onto_labels_received))

        lists = test_project['project']['lists']
        test_list: dict[str, str] = next((l for l in lists if l['name'] == 'testlist'), {})
        not_used_list: dict[str, str] = next((l for l in lists if l['name'] == 'notUsedList'), {})
        excel_list: dict[str, str] = next((l for l in lists if l['name'] == 'my-list-from-excel'), {})

        lists_out = test_project_out['project']['lists']
        test_list_out: dict[str, str] = next((l for l in lists_out if l['name'] == 'testlist'), {})
        not_used_list_out: dict[str, str] = next((l for l in lists_out if l['name'] == 'notUsedList'), {})
        excel_list_out: dict[str, str] = next((l for l in lists_out if l['name'] == 'my-list-from-excel'), {})

        self.assertEqual(test_list.get('labels'), test_list_out.get('labels'))
        self.assertEqual(test_list.get('comments'), test_list_out.get('comments'))
        self.assertEqual(test_list.get('nodes'), test_list_out.get('nodes'))

        self.assertEqual(not_used_list.get('labels'), not_used_list_out.get('labels'))
        self.assertEqual(not_used_list.get('comments'), not_used_list_out.get('comments'))
        self.assertEqual(not_used_list.get('nodes'), not_used_list_out.get('nodes'))

        self.assertEqual(excel_list.get('comments'), excel_list_out.get('comments'))

    def test_excel_to_json_list(self) -> None:
        excel_to_json_lists.list_of_lists = []
        excel_to_json_lists.cell_names = []
        list_excel2json(listname='my_test_list',
                        excelfolder='testdata/lists',
                        outfile='testdata/tmp/_lists-out.json')

    def test_excel_to_json_resources(self) -> None:
        resources_excel2json(excelfile='testdata/Resources.xlsx',
                             outfile='testdata/tmp/_out_resources.json')

    def test_excel_to_json_properties(self) -> None:
        properties_excel2json(excelfile='testdata/Properties.xlsx',
                              outfile='testdata/tmp/_out_properties.json')

    def test_create_project(self) -> None:
        result1 = create_project(
            input_file=self.test_project_file,
            server=self.server,
            user_mail=self.user,
            password='test',
            verbose=True,
            dump=False
        )
        result2 = create_project(
            input_file=self.test_project_minimal_file,
            server=self.server,
            user_mail=self.user,
            password='test',
            verbose=True,
            dump=False
        )
        self.assertTrue(result1)
        self.assertTrue(result2)

    def test_xml_upload(self) -> None:
        result = xml_upload(
            input_file=self.test_data_file,
            server=self.server,
            user=self.user,
            password=self.password,
            imgdir=self.imgdir,
            sipi=self.sipi,
            verbose=False,
            validate_only=False,
            incremental=False)
        self.assertTrue(result)

        mapping_file = ''
        for mapping in [x for x in os.scandir('.') if x.name.startswith('id2iri_test-data-systematic_mapping_')]:
            delta = datetime.datetime.now() - datetime.datetime.fromtimestamp(mapping.stat().st_mtime_ns / 1000000000)
            if delta.seconds < 15:
                mapping_file = mapping.name
        self.assertNotEqual(mapping_file, '')

        id2iri_replaced_xml_filename = 'testdata/tmp/_test-id2iri-replaced.xml'
        id_to_iri(xml_file='testdata/test-id2iri-data.xml',
                  json_file=mapping_file,
                  out_file=id2iri_replaced_xml_filename,
                  verbose=True)
        self.assertEqual(os.path.isfile(id2iri_replaced_xml_filename), True)

        result = xml_upload(
            input_file=id2iri_replaced_xml_filename,
            server=self.server,
            user=self.user,
            password=self.password,
            imgdir=self.imgdir,
            sipi=self.sipi,
            verbose=True,
            validate_only=False,
            incremental=True
        )
        self.assertTrue(result)
        self.assertTrue(all([not f.name.startswith('stashed_text_properties_') for f in os.scandir('.')]))
        self.assertTrue(all([not f.name.startswith('stashed_resptr_properties_') for f in os.scandir('.')]))


if __name__ == '__main__':
    unittest.main()
