"""This test class tests the basic functionalities of dsp-tools"""
import json
import unittest

from knora.dsplib.utils import excel_to_json_lists
from knora.dsplib.utils.excel_to_json_lists import list_excel2json
from knora.dsplib.utils.excel_to_json_properties import properties_excel2json
from knora.dsplib.utils.excel_to_json_resources import resources_excel2json
from knora.dsplib.utils.id_to_iri import id_to_iri
from knora.dsplib.utils.onto_create_ontology import create_ontology
from knora.dsplib.utils.onto_get import get_ontology
from knora.dsplib.utils.onto_validate import validate_ontology
from knora.dsplib.utils.xml_upload import xml_upload


class TestTools(unittest.TestCase):
    server = 'http://0.0.0.0:3333'
    user = 'root@example.com'
    test_onto_file = 'testdata/test-onto.json'
    test_list_file = 'testdata/test-list.json'
    test_data_file = 'testdata/test-data.xml'

    def setUp(self) -> None:
        """Is executed before each test"""
        excel_to_json_lists.list_of_lists = []
        excel_to_json_lists.cell_names = []

    def tearDown(self) -> None:
        """Is executed after each test"""
        excel_to_json_lists.list_of_lists = []
        excel_to_json_lists.cell_names = []

    def test_get(self) -> None:
        with open(self.test_onto_file) as f:
            onto_json_str = f.read()
        test_onto = json.loads(onto_json_str)

        get_ontology(project_identifier='tp',
                     outfile='testdata/tmp/_test-onto.json',
                     server=self.server,
                     user=self.user,
                     password='test',
                     verbose=False)

        with open('testdata/tmp/_test-onto.json') as f:
            onto_json_str = f.read()
        test_onto_out = json.loads(onto_json_str)

        self.assertEqual(test_onto['project']['shortcode'], test_onto_out['project']['shortcode'])
        self.assertEqual(test_onto['project']['shortname'], test_onto_out['project']['shortname'])
        self.assertEqual(test_onto['project']['longname'], test_onto_out['project']['longname'])
        self.assertEqual(test_onto['project']['descriptions'], test_onto_out['project']['descriptions'])
        self.assertEqual(sorted(test_onto['project']['keywords']), sorted(test_onto_out['project']['keywords']))

        groups_expected = test_onto['project']['groups']
        groups_received = test_onto_out['project']['groups']
        group_names_expected = []
        group_descriptions_expected = []
        group_selfjoin_expected = []
        group_status_expected = []
        groups_names_received = []
        group_descriptions_received = []
        group_selfjoin_received = []
        group_status_received = []
        for group in groups_expected:
            group_names_expected.append(group["name"])
            group_descriptions_expected.append(group["descriptions"]["en"])
            group_selfjoin_expected.append(group["selfjoin"])
            group_status_expected.append(group["status"])
        for group in groups_received:
            groups_names_received.append(group["name"])
            group_descriptions_received.append(group["descriptions"]["en"])
            group_selfjoin_received.append(group["selfjoin"])
            group_status_received.append(group["status"])
        self.assertEqual(sorted(group_names_expected), sorted(groups_names_received))
        self.assertEqual(sorted(group_descriptions_expected), sorted(group_descriptions_received))
        self.assertEqual(group_selfjoin_expected, group_selfjoin_received)
        self.assertEqual(group_status_expected, group_status_received)

        users_expected = test_onto['project']['users']
        users_received = test_onto_out['project']['users']
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
            if user["username"] == "testerKnownUser":  # ignore testerKnownUser as he is not part of the project
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

        ontos_expected = test_onto['project']['ontologies']
        ontos_received = test_onto_out['project']['ontologies']
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

        lists = test_onto['project']['lists']
        test_list: dict[str, str] = next((l for l in lists if l['name'] == 'testlist'), {})
        not_used_list: dict[str, str] = next((l for l in lists if l['name'] == 'notUsedList'), {})
        excel_list: dict[str, str] = next((l for l in lists if l['name'] == 'my-list-from-excel'), {})

        lists_out = test_onto_out['project']['lists']
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
        list_excel2json(listname='my_test_list',
                        excelfolder='testdata/lists',
                        outfile='testdata/tmp/_lists-out.json')

    def test_excel_to_json_resources(self) -> None:
        resources_excel2json(excelfile='testdata/Resources.xlsx',
                             outfile='testdata/tmp/_resources-out.json')

    def test_excel_to_json_properties(self) -> None:
        properties_excel2json(excelfile='testdata/Properties.xlsx',
                              outfile='testdata/tmp/_properties-out.json')

    def test_validate_ontology(self) -> None:
        validate_ontology(self.test_onto_file)

    def test_create_ontology(self) -> None:
        create_ontology(input_file=self.test_onto_file,
                        lists_file=self.test_list_file,
                        server=self.server,
                        user_mail=self.user,
                        password='test',
                        verbose=False,
                        dump=False)

    def test_xml_upload(self) -> None:
        xml_upload(input_file=self.test_data_file,
                   server=self.server,
                   user=self.user,
                   password='test',
                   imgdir='.',
                   sipi='http://0.0.0.0:1024',
                   verbose=False,
                   validate_only=False,
                   incremental=False)

    def test_id_to_iri(self) -> None:
        id_to_iri(xml_file='testdata/test-id2iri-data.xml',
                  json_file='testdata/test-id2iri-mapping.json',
                  out_file='testdata/tmp/_test-id2iri-replaced.xml',
                  verbose=False)


if __name__ == '__main__':
    unittest.main()
