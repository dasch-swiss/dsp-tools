"""
This test class tests the basic functionalities of dsp-tools, i.e. all commands that can be called from the command
line. The methods are tested in the order in which teh appear in dsp_tools.py. This class only tests that the methods
can be called with the basic configuration that is available via CLI. More thorough testing of each method is done in
separate unit tests/e2e tests.
"""
import copy
import datetime
import json
import os
import re
import unittest

import jsonpath_ng
import jsonpath_ng.ext
import pytest

from dsp_tools.excel2xml import excel2xml
from dsp_tools.utils.excel_to_json_lists import (
    excel2lists,
    validate_lists_section_with_schema
)
from dsp_tools.utils.excel_to_json_project import excel2json
from dsp_tools.utils.excel_to_json_properties import excel2properties
from dsp_tools.utils.excel_to_json_resources import excel2resources
from dsp_tools.utils.id_to_iri import id_to_iri
from dsp_tools.utils.project_create import create_project
from dsp_tools.utils.project_create_lists import create_lists
from dsp_tools.utils.project_get import get_project
from dsp_tools.utils.project_validate import validate_project
from dsp_tools.utils.shared import validate_xml_against_schema
from dsp_tools.utils.xml_upload import xml_upload


class TestTools(unittest.TestCase):
    server = "http://0.0.0.0:3333"
    user = "root@example.com"
    password = "test"
    imgdir = "."
    sipi = "http://0.0.0.0:1024"
    test_project_systematic_file = "testdata/json-project/test-project-systematic.json"
    test_project_minimal_file = "testdata/json-project/test-project-minimal.json"
    test_data_systematic_file = "testdata/xml-data/test-data-systematic.xml"
    test_data_minimal_file = "testdata/xml-data/test-data-minimal.xml"

    @classmethod
    def setUpClass(cls) -> None:
        """Is executed before the methods of this class are run"""
        os.makedirs("testdata/tmp", exist_ok=True)

    @classmethod
    def tearDownClass(cls) -> None:
        """Is executed after the methods of this class have all run through"""
        for file in os.listdir("testdata/tmp"):
            os.remove("testdata/tmp/" + file)
        os.rmdir("testdata/tmp")
        for file in [f for f in os.listdir(".") if re.search(r"id2iri_.+\.json", f)]:
            os.remove(file)


    def test_validate_lists_section_with_schema(self) -> None:
        self.assertTrue(validate_lists_section_with_schema(self.test_project_systematic_file))


    def test_create_lists(self) -> None:
        # the project must already exist, so let's create a project without lists
        create_project(
            project_file_as_path_or_parsed=self.test_project_minimal_file,
            server=self.server,
            user_mail=self.user,
            password="test",
            verbose=True,
            dump=False
        )

        # open a "lists" section and the project that was created
        with open("testdata/excel2json/lists-multilingual-output-expected.json") as f:
            lists_section = json.load(f)
        with open(self.test_project_minimal_file) as f:
            test_project_minimal = json.load(f)

        # create a copy of the project that was created, and insert the first list into it
        test_project_minimal_with_list_1 = copy.deepcopy(test_project_minimal)
        test_project_minimal_with_list_1["project"]["lists"] = [lists_section[0], ]

        # create another copy of the project that was created, insert the second list into it, and save it as file
        test_project_minimal_with_list_2 = copy.deepcopy(test_project_minimal)
        test_project_minimal_with_list_2["project"]["lists"] = [lists_section[1], ]
        with open("testdata/tmp/test_project_minimal_with_list_2.json", "x") as f:
            json.dump(test_project_minimal_with_list_2, f)

        # The method to be tested can now be called with both versions of the same project. One is loaded from disk,
        # the other is a Python object. The two projects each contain another list.
        name2iri_mapping1, success1 = create_lists(server=self.server,
                                                   user=self.user,
                                                   password=self.password,
                                                   project_file_as_path_or_parsed=test_project_minimal_with_list_1)
        name2iri_mapping2, success2 = create_lists(server=self.server,
                                                   user=self.user,
                                                   password=self.password,
                                                   project_file_as_path_or_parsed="testdata/tmp/test_project_minimal_with_list_2.json")
        
        # test that both lists have been correctly created
        self.assertTrue(success1)
        self.assertTrue(success2)
        name2iri_names_1 = [str(m.path) for m in jsonpath_ng.ext.parse("$..* where id").find(name2iri_mapping1)]
        name2iri_names_2 = [str(m.path) for m in jsonpath_ng.ext.parse("$..* where id").find(name2iri_mapping2)]
        node_names_1 = [m.value for m in jsonpath_ng.ext.parse("$.project.lists[*]..name").find(test_project_minimal_with_list_1)]
        node_names_2 = [m.value for m in jsonpath_ng.ext.parse("$.project.lists[*]..name").find(test_project_minimal_with_list_2)]
        self.assertListEqual(name2iri_names_1, node_names_1)
        self.assertListEqual(name2iri_names_2, node_names_2)


    def test_validate_project(self) -> None:
        self.assertTrue(validate_project(self.test_project_systematic_file))


    def test_create_project(self) -> None:
        result = create_project(
            project_file_as_path_or_parsed=self.test_project_systematic_file,
            server=self.server,
            user_mail=self.user,
            password="test",
            verbose=True,
            dump=False
        )
        self.assertTrue(result)


    def test_get_ontology(self) -> None:
        with open(self.test_project_systematic_file) as f:
            project_expected = json.load(f)

        get_project(project_identifier="tp",
                    outfile_path="testdata/tmp/_test-project-systematic.json",
                    server=self.server,
                    user=self.user,
                    password="test",
                    verbose=True)

        with open("testdata/tmp/_test-project-systematic.json") as f:
            project_received = json.load(f)

        self.assertEqual(project_expected["project"]["shortcode"], project_received["project"]["shortcode"])
        self.assertEqual(project_expected["project"]["shortname"], project_received["project"]["shortname"])
        self.assertEqual(project_expected["project"]["longname"], project_received["project"]["longname"])
        self.assertEqual(project_expected["project"]["descriptions"], project_received["project"]["descriptions"])
        self.assertEqual(sorted(project_expected["project"]["keywords"]), sorted(project_received["project"]["keywords"]))

        groups_expected = project_expected["project"]["groups"]
        groups_received = project_received["project"]["groups"]
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

        users_expected = project_expected["project"]["users"]
        users_received = project_received["project"]["users"]
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

        ontos_expected = project_expected["project"]["ontologies"]
        ontos_received = project_received["project"]["ontologies"]
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

        lists = project_expected["project"]["lists"]
        test_list: dict[str, str] = next((l for l in lists if l["name"] == "testlist"), {})
        not_used_list: dict[str, str] = next((l for l in lists if l["name"] == "notUsedList"), {})
        excel_list: dict[str, str] = next((l for l in lists if l["name"] == "my-list-from-excel"), {})

        lists_out = project_received["project"]["lists"]
        test_list_out: dict[str, str] = next((l for l in lists_out if l["name"] == "testlist"), {})
        not_used_list_out: dict[str, str] = next((l for l in lists_out if l["name"] == "notUsedList"), {})
        excel_list_out: dict[str, str] = next((l for l in lists_out if l["name"] == "my-list-from-excel"), {})

        self.assertEqual(test_list.get("labels"), test_list_out.get("labels"))
        self.assertEqual(test_list.get("comments"), test_list_out.get("comments"))
        self.assertEqual(test_list.get("nodes"), test_list_out.get("nodes"))

        self.assertEqual(not_used_list.get("labels"), not_used_list_out.get("labels"))
        self.assertEqual(not_used_list.get("comments"), not_used_list_out.get("comments"))
        self.assertEqual(not_used_list.get("nodes"), not_used_list_out.get("nodes"))

        self.assertEqual(excel_list.get("comments"), excel_list_out.get("comments"))


    def test_validate_xml_against_schema(self) -> None:
        self.assertTrue(validate_xml_against_schema(input_file=self.test_data_systematic_file))


    def test_xml_upload(self) -> None:
        result_minimal = xml_upload(
            input_file=self.test_data_minimal_file,
            server=self.server,
            user=self.user,
            password=self.password,
            imgdir=self.imgdir,
            sipi=self.sipi,
            verbose=False,
            incremental=False,
            save_metrics=False)
        self.assertTrue(result_minimal)

        result_systematic = xml_upload(
            input_file=self.test_data_systematic_file,
            server=self.server,
            user=self.user,
            password=self.password,
            imgdir=self.imgdir,
            sipi=self.sipi,
            verbose=False,
            incremental=False,
            save_metrics=False)
        self.assertTrue(result_systematic)

        mapping_file = ""
        for mapping in [x for x in os.scandir(".") if x.name.startswith("test-data-systematic_id2iri_mapping_")]:
            delta = datetime.datetime.now() - datetime.datetime.fromtimestamp(mapping.stat().st_mtime_ns / 1000000000)
            if delta.seconds < 15:
                mapping_file = mapping.name
        self.assertNotEqual(mapping_file, "")

        id2iri_replaced_xml_filename = "testdata/tmp/_test-id2iri-replaced.xml"
        id_to_iri(xml_file="testdata/id2iri/test-id2iri-data.xml",
                  json_file=mapping_file,
                  out_file=id2iri_replaced_xml_filename,
                  verbose=True)
        self.assertTrue(os.path.isfile(id2iri_replaced_xml_filename))

        result_replaced = xml_upload(
            input_file=id2iri_replaced_xml_filename,
            server=self.server,
            user=self.user,
            password=self.password,
            imgdir=self.imgdir,
            sipi=self.sipi,
            verbose=True,
            incremental=True,
            save_metrics=False
        )
        self.assertTrue(result_replaced)
        self.assertTrue(all([not f.name.startswith("stashed_text_properties_") for f in os.scandir(".")]))
        self.assertTrue(all([not f.name.startswith("stashed_resptr_properties_") for f in os.scandir(".")]))

        os.remove(mapping_file)
        os.remove(id2iri_replaced_xml_filename)


    def test_excel_to_json_project(self) -> None:
        excel2json(data_model_files="testdata/excel2json/excel2json_files",
                   path_to_output_file="testdata/tmp/_out_project.json")
        with open("testdata/excel2json/excel2json-expected-output.json") as f:
            output_expected = json.load(f)
        with open("testdata/tmp/_out_project.json") as f:
            output = json.load(f)
        self.assertDictEqual(output, output_expected)
        os.remove("testdata/tmp/_out_project.json")


    def test_excel_to_json_list(self) -> None:
        excel2lists(excelfolder="testdata/excel2json/lists-multilingual",
                    path_to_output_file="testdata/tmp/_lists-out.json")
        self.assertTrue(os.path.isfile("testdata/tmp/_lists-out.json"))
        os.remove("testdata/tmp/_lists-out.json")


    def test_excel_to_json_resources(self) -> None:
        excel2resources(excelfile="testdata/excel2json/excel2json_files/test-name (test_label)/resources.xlsx",
                        path_to_output_file="testdata/tmp/_out_resources.json")
        self.assertTrue(os.path.isfile("testdata/tmp/_out_resources.json"))
        os.remove("testdata/tmp/_out_resources.json")


    def test_excel_to_json_properties(self) -> None:
        excel2properties(excelfile="testdata/excel2json/excel2json_files/test-name (test_label)/properties.xlsx",
                         path_to_output_file="testdata/tmp/_out_properties.json")
        self.assertTrue(os.path.isfile("testdata/tmp/_out_properties.json"))
        os.remove("testdata/tmp/_out_properties.json")


    def test_id_to_iri(self) -> None:
        id_to_iri(xml_file="testdata/id2iri/test-id2iri-data.xml",
                  json_file="testdata/id2iri/test-id2iri-mapping.json",
                  out_file="testdata/tmp/test-id2iri-out.xml",
                  verbose=True)
        self.assertTrue(os.path.isfile("testdata/tmp/test-id2iri-out.xml"))
        os.remove("testdata/tmp/test-id2iri-out.xml")

    @pytest.mark.filterwarnings("ignore")
    def test_excel2xml(self) -> None:
        excel2xml("testdata/excel2xml/excel2xml-testdata.xlsx", "1234", "excel2xml-output")
        self.assertTrue(os.path.isfile("excel2xml-output-data.xml"))
        os.remove("excel2xml-output-data.xml")


if __name__ == "__main__":
    pytest.main([__file__])
