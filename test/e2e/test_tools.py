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
from typing import cast

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
        """
        Retrieve the systematic JSON project file with the "get" command, 
        and check if the result is identical to the original file.
        """
        # open original project and project that was returned from the server
        get_project(
            project_identifier="tp",
            outfile_path="testdata/tmp/_test-project-systematic.json",
            server=self.server,
            user=self.user,
            password="test",
            verbose=True
        )
        with open("testdata/tmp/_test-project-systematic.json", encoding="utf-8") as f:
            project_returned = json.load(f)
        with open(self.test_project_systematic_file, encoding="utf-8") as f:
            project_original_str = f.read()
            project_original = json.loads(project_original_str)

        project_shortname = project_original["project"]["shortname"]

        # expand prefixes in original, then delete both "prefixes" sections, because
        #  - the "get" command returns full IRIs instead of prefixed IRIs, so the original prefixes won't be found in the returned file
        #  - the "get" command lists the ontos of the current file under "prefixes", which is optional in the original file
        for prefix, iri in project_original["prefixes"].items():
            project_original_str = re.sub(fr'"{prefix}:(\w+?)"', fr'"{iri}\1"', project_original_str)
        project_original = json.loads(project_original_str)
        del project_original["prefixes"]
        del project_returned["prefixes"]

        # delete both "$schema" sections (original might be relative path inside repo, returned is full URL)
        del project_original["$schema"]
        del project_returned["$schema"]

        # write default values into original, in case they were omitted (the "get" command writes all default values)
        for group in project_original["project"].get("groups"):
            if group.get("status") is None:
                group["status"] = True
            if group.get("selfjoin") is None:
                group["selfjoin"] = False

        # remove users that are not in current project (they won't be returned by the "get" command)
        if project_original["project"].get("users"):
            current_project_membership_strings = [":admin", ":member", f"{project_shortname}:admin", f"{project_shortname}:member"]
            project_original["project"]["users"] = [u for u in project_original["project"]["users"] 
                                                    if any(p in u.get("projects", []) for p in current_project_membership_strings)]

        # bring the "users" section of original into the form that is returned by the "get" command
        for user in project_original["project"].get("users"):
            index = project_original["project"]["users"].index(user)
            # remove password
            project_original["project"]["users"][index]["password"] = ""
            # write default values, in case they were omitted
            if user.get("groups") is None:
                project_original["project"]["users"][index]["groups"] = []
            if user.get("status") is None:
                project_original["project"]["users"][index]["status"] = True
            # expand ":xyz" to "project_shortname:xyz"
            if user.get("groups"):
                project_original["project"]["users"][index]["groups"] = [re.sub("^:", f"{project_shortname}:", g) for g in user["groups"]]
            if user.get("projects"):
                project_original["project"]["users"][index]["projects"] = [re.sub("^:", f"{project_shortname}:", p) for p in user["projects"]]

        # List nodes can be defined in Excel files. Such lists must be removed from both the original and the returned file, 
        # because they cannot be compared
        for list_original in project_original["project"].get("lists"):
            if isinstance(list_original["nodes"], dict) and len(list_original["nodes"]) == 1 and "folder" in list_original["nodes"]:
                project_original["project"]["lists"].remove(list_original)
                project_returned["project"]["lists"] = [x for x in project_returned["project"]["lists"] if x["name"] != list_original["name"]]
        
        # The original might have propnames of cardinalities in the form "testonto:hasSimpleText".
        # The returned file will have ":hasSimpleText", so we need to remove the onto name.
        for onto in project_original["project"]["ontologies"]:
            onto_name = onto["name"]
            for res in onto["resources"]:
                for card in res.get("cardinalities", []):
                    if card["propname"].startswith(onto_name):
                        card["propname"] = re.sub(fr"^{onto_name}:", ":", card["propname"])

        # If a subclass doesn't explicitly define all cardinalities of its superclass 
        # (or a subproperty of a cardinality of its superclass),
        # these cardinalities are implicitly added, so the "get" command will return them. 
        # It would be too complicated to test this behaviour, 
        # so we need to remove the cardinalities of all subclasses from both original file and returned file.
        for onto in project_original["project"]["ontologies"]:
            onto_name = onto["name"]
            for res in onto["resources"]:
                supers_as_list = [res["super"], ] if isinstance(res["super"], str) else res["super"]
                for sup in supers_as_list:
                    if re.search(fr"^({onto_name})?:\w+$", sup) and res.get("cardinalities"):
                        del res["cardinalities"]
                        # remove from returned file as well
                        onto_returned = [x for x in project_returned["project"]["ontologies"] if x["name"] == onto["name"]][0]
                        res_returned = [x for x in onto_returned["resources"] if x["name"] == res["name"]][0]
                        del res_returned["cardinalities"]

        # sort everything in both files
        for file in [project_original, project_returned]:
            file["project"]["groups"] = sorted(file["project"]["groups"], key=lambda x: cast(str, x["name"]))
            file["project"]["users"] = sorted(file["project"]["users"], key=lambda x: cast(str, x["username"]))
            file["project"]["lists"] = sorted(file["project"]["lists"], key=lambda x: cast(str, x["name"]))
            file["project"]["ontologies"] = sorted(file["project"]["ontologies"], key=lambda x: cast(str, x["name"]))
            for onto in file["project"]["ontologies"]:
                onto["resources"] = sorted(onto["resources"], key=lambda x: cast(str, x["name"]))
                onto["properties"] = sorted(onto["properties"], key=lambda x: cast(str, x["name"]))
                for res in onto["resources"]:
                    if res.get("cardinalities"):
                        res["cardinalities"] = sorted(res["cardinalities"], key=lambda x: cast(str, x["propname"]))
                    if isinstance(res["super"], list):
                        res["super"] = sorted(res["super"])
                for prop in onto["properties"]:
                    if isinstance(prop["super"], list):
                        prop["super"] = sorted(prop["super"])

        # Compare the original and the returned file
        project_original_str = json.dumps(project_original, sort_keys=True)
        project_returned_str = json.dumps(project_returned, sort_keys=True)
        self.assertEqual(project_original_str, project_returned_str)


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
    unittest.main()
