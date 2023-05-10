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
from typing import Any, Optional, cast

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


    def test_get_project(self) -> None:
        """
        Retrieve the systematic JSON project file with the "get" command, 
        and check if the result is identical to the original file.
        """
        # open original project and project that was returned from the server
        project_original = self._get_original_project()
        project_shortname = project_original["project"]["shortname"]

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

        self._compare_project(project_original, project_returned)
        self._compare_groups(
            groups_original=project_original["project"].get("groups"), 
            groups_returned=project_returned["project"].get("groups")
        )
        self._compare_users(
            users_original=project_original["project"].get("users"), 
            users_returned=project_returned["project"].get("users"),
            project_shortname=project_shortname
        )
        self._compare_lists(
            lists_original=project_original["project"].get("lists"), 
            lists_returned=project_returned["project"].get("lists")
        )

        for file in [project_original, project_returned]:
            file["project"]["ontologies"] = sorted(file["project"]["ontologies"], key=lambda x: cast(str, x["name"]))
        for onto_original, onto_returned in zip(project_original["project"]["ontologies"], project_returned["project"]["ontologies"]):
            self._compare_properties(
                properties_original=onto_original["properties"],
                properties_returned=onto_returned["properties"],
                onto_name=onto_original["name"]
            )
            self._compare_resources(
                resources_original=onto_original["resources"],
                resources_returned=onto_returned["resources"],
                onto_name=onto_original["name"]
            )


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

        
    def _get_original_project(self) -> dict[str, Any]:
        """
        Open the systematic JSON project file, expand all prefixes, and return the resulting Python object.
        The prefixes must be expanded because the "get" command returns full IRIs instead of prefixed IRIs, 
        so the original prefixes won't be found in the returned file.

        Returns:
            the original project as a Python dictionary
        """
        with open(self.test_project_systematic_file, encoding="utf-8") as f:
            project_original_str = f.read()
            project_original = json.loads(project_original_str)

        for prefix, iri in project_original["prefixes"].items():
            project_original_str = re.sub(fr'"{prefix}:(\w+?)"', fr'"{iri}\1"', project_original_str)
        project_original = json.loads(project_original_str)
        return project_original
    

    def _compare_project(
        self,
        project_original: dict[str, Any],
        project_returned: dict[str, Any]
    ) -> None:
        """
        Compare the basic metadata of 2 JSON project definitions.
        Fails with a message if the metadata are not identical.

        Args:
            project_original: original file
            project_returned: returned file
        """
        for field in ["shortcode", "shortname", "longname", "descriptions"]:
            orig = project_original["project"].get(field)
            ret = project_returned["project"].get(field)
            self.assertEqual(orig, ret, msg=f"Field '{field}' is not identical: original='{orig}', returned='{ret}'")
        
        orig_keywords = sorted(project_original["project"]["keywords"])
        ret_keywords = sorted(project_returned["project"]["keywords"])
        self.assertEqual(orig_keywords, ret_keywords, msg=f"Field keywords is not identical: original={orig_keywords}, returned={ret_keywords}")


    def _compare_groups(
        self, 
        groups_original: Optional[list[dict[str, Any]]], 
        groups_returned: Optional[list[dict[str, Any]]]
    ) -> None:
        """
        Compare the "groups" section of the original JSON project definition 
        with the "groups" section of the JSON returned by the "get" command.
        Fails with a message if the sections are not identical.

        Args:
            groups_original: "groups" section of the original file.
            groups_returned: "groups" section of the returned file.
        """
        # avoid mutable default argument
        groups_original = groups_original or []
        groups_returned = groups_returned or []

        # write default values into original, in case they were omitted (the "get" command writes all default values)
        for group in groups_original or []:
            if group.get("status") is None:
                group["status"] = True
            if group.get("selfjoin") is None:
                group["selfjoin"] = False
        
        # sort both lists
        groups_original = sorted(groups_original, key=lambda x: cast(str, x.get("name", "")))
        groups_returned = sorted(groups_returned, key=lambda x: cast(str, x.get("name", "")))
        if len(groups_original) != len(groups_returned):
            self.assertEqual(groups_original, groups_returned)
        else:
            for orig, ret in zip(groups_original, groups_returned):
                self.assertEqual(orig, ret, msg=f"Group with original name '{orig['name']}' and returned name '{ret['name']}' failed.")
    

    def _compare_users(
        self, 
        users_original: Optional[list[dict[str, Any]]], 
        users_returned: Optional[list[dict[str, Any]]],
        project_shortname: str
    ) -> None:
        """
        Compare the "users" section of the original JSON project definition
        with the "users" section of the JSON returned by the "get" command.
        Fails with a message if the sections are not identical.

        In order to do so, this method modifies the original as follows:
         - remove the users that are not in the current project
         - set all passwords to ""
         - add default values, in case they were omitted,
         - expand ":xyz" to "project_shortname:xyz"

        Args:
            users_original: "users" section of the original file.
            users_returned: "users" section of the returned file.
            project_shortname: shortname of the project
        """
        # avoid mutable default argument
        users_original = users_original or []
        users_returned = users_returned or []

        # remove users that are not in current project (they won't be returned by the "get" command)
        if users_original:
            current_project_membership_strings = [":admin", ":member", f"{project_shortname}:admin", f"{project_shortname}:member"]
            users_original = [u for u in users_original if any(p in u.get("projects", []) for p in current_project_membership_strings)]

        # bring the "users" section of original into the form that is returned by the "get" command
        for user in users_original:
            index = users_original.index(user)
            # remove password
            users_original[index]["password"] = ""
            # write default values, in case they were omitted
            if user.get("groups") is None:
                users_original[index]["groups"] = []
            if user.get("status") is None:
                users_original[index]["status"] = True
            # expand ":xyz" to "project_shortname:xyz"
            if user.get("groups"):
                users_original[index]["groups"] = [re.sub("^:", f"{project_shortname}:", g) for g in user["groups"]]
            if user.get("projects"):
                users_original[index]["projects"] = [re.sub("^:", f"{project_shortname}:", p) for p in user["projects"]]
        
        # sort both lists
        users_original = sorted(users_original or [], key=lambda x: cast(str, x["username"]))
        users_returned = sorted(users_returned or [], key=lambda x: cast(str, x["username"]))
        if len(users_original) != len(users_returned):
            self.assertEqual(users_original, users_returned)
        else:
            for orig, ret in zip(users_original, users_returned):
                self.assertEqual(orig, ret, msg=f"User with original name '{orig['username']}' and returned name '{ret['username']}' failed.")
    

    def _compare_lists(
        self, 
        lists_original: Optional[list[dict[str, Any]]], 
        lists_returned: Optional[list[dict[str, Any]]]
    ) -> None:
        """
        Compare the "lists" section of the original JSON project definition 
        with the "lists" section of the JSON returned by the "get" command.
        Fails with a message if the sections are not identical.

        In order to do so, 
        this method removes all lists of which the nodes are defined in an Excel file, 
        because they cannot be compared.

        Args:
            lists_original: "lists" section of the original file.
            lists_returned: "lists" section of the returned file.
        """
        # avoid mutable default argument
        lists_original = lists_original or []
        lists_returned = lists_returned or []

        # remove lists of which the nodes were defined in an Excel file
        for list_original in lists_original:
            if isinstance(list_original["nodes"], dict) and len(list_original["nodes"]) == 1 and "folder" in list_original["nodes"]:
                lists_original.remove(list_original)
                lists_returned = [x for x in lists_returned if x["name"] != list_original["name"]]
        
        # sort both lists
        lists_original = sorted(lists_original, key=lambda x: cast(str, x.get("name", "")))
        lists_returned = sorted(lists_returned, key=lambda x: cast(str, x.get("name", "")))
        if len(lists_original) != len(lists_returned):
            self.assertEqual(lists_original, lists_returned)
        else:
            for orig, ret in zip(lists_original, lists_returned):
                self.assertEqual(orig, ret, msg=f"List with original name '{orig['name']}' and returned name '{ret['name']}' failed.")
    

    def _compare_properties(
        self, 
        properties_original: Optional[list[dict[str, Any]]], 
        properties_returned: Optional[list[dict[str, Any]]],
        onto_name: str
    ) -> None:
        """
        Compare the "properties" section of an onto of the original JSON project definition 
        with the "properties" section of the respective onto of the JSON returned by the "get" command.
        Fails with a message if the sections are not identical.

        Args:
            properties_original: "properties" section of the original file.
            properties_returned: "properties" section of the returned file.
            onto_name: name of the ontology
        """
        # avoid mutable default argument
        properties_original = properties_original or []
        properties_returned = properties_returned or []

        # The original might have names in the form "currentonto:hasSimpleText".
        # The returned file will have ":hasSimpleText", so we have to remove the onto name.
        for prop in properties_original:
            if any(sup.startswith(onto_name) for sup in prop["super"]):
                prop["super"] = [re.sub(fr"^{onto_name}:", ":", sup) for sup in prop["super"]]
        
        # sort both lists
        properties_original = sorted(properties_original, key=lambda x: cast(str, x.get("name", "")))
        properties_returned = sorted(properties_returned, key=lambda x: cast(str, x.get("name", "")))
        for proplist in [properties_original, properties_returned]:
            for prop in proplist:
                if isinstance(prop["super"], list):
                    prop["super"] = sorted(prop["super"])
        
        if len(properties_original) != len(properties_returned):
            self.assertEqual(properties_original, properties_returned, msg=f"Onto {}")
        else:
            for orig, ret in zip(properties_original, properties_returned):
                self.assertEqual(
                    orig, 
                    ret, 
                    msg=f"Onto '{onto_name}': Property with original name '{orig['name']}' and returned name '{ret['name']}' failed."
                )
    

    def _compare_resources(
        self, 
        resources_original: Optional[list[dict[str, Any]]], 
        resources_returned: Optional[list[dict[str, Any]]],
        onto_name: str
    ) -> None:
        """
        Compare the "resources" section of an onto of the original JSON project definition 
        with the "resources" section of the respective onto of the JSON returned by the "get" command.
        Fails with a message if the sections are not identical.

        Args:
            resources_original: "resources" section of the original file.
            resources_returned: "resources" section of the returned file.
            onto_name: name of the ontology
        """
        # avoid mutable default argument
        resources_original = resources_original or []
        resources_returned = resources_returned or []

        # The original might have names in the form "currentonto:hasSimpleText".
        # The returned file will have ":hasSimpleText", so we have to remove the onto name.
        for res in resources_original:
            for card in res.get("cardinalities", []):
                if card["propname"].startswith(onto_name):
                    card["propname"] = re.sub(fr"^{onto_name}:", ":", card["propname"])
            supers_as_list = [res["super"], ] if isinstance(res["super"], str) else res["super"]
            if any(sup.startswith(onto_name) for sup in supers_as_list):
                res["super"] = [re.sub(fr"^{onto_name}:", ":", sup) for sup in supers_as_list]
        
        # If a subclass doesn't explicitly define all cardinalities of its superclass 
        # (or a subproperty of a cardinality of its superclass),
        # these cardinalities are implicitly added, so the "get" command will return them. 
        # It would be too complicated to test this behaviour, 
        # so we need to remove the cardinalities of all subclasses from both original file and returned file.
        for res in resources_original:
            supers_as_list = [res["super"], ] if isinstance(res["super"], str) else res["super"]
            for sup in supers_as_list:
                if re.search(fr"^({onto_name})?:\w+$", sup):
                    if res.get("cardinalities"):
                        del res["cardinalities"]
                    # remove from returned file, too
                    res_returned = [x for x in resources_returned if x["name"] == res["name"]][0]
                    if res_returned.get("cardinalities"):
                        del res_returned["cardinalities"]

        # sort both lists
        resources_original = sorted(resources_original, key=lambda x: cast(str, x.get("name", "")))
        resources_returned = sorted(resources_returned, key=lambda x: cast(str, x.get("name", "")))
        for reslist in [resources_original, resources_returned]:
            for res in reslist:
                if isinstance(res["super"], list):
                    res["super"] = sorted(res["super"])
                if res.get("cardinalities"):
                    res["cardinalities"] = sorted(res["cardinalities"], key=lambda x: cast(str, x["propname"]))

        if len(resources_original) != len(resources_returned):
            self.assertEqual(resources_original, resources_returned)
        else:
            for orig, ret in zip(resources_original, resources_returned):
                if orig.get("cardinalities") != ret.get("cardinalities"):
                    self.assertEqual(
                        orig.get("cardinalities"), 
                        ret.get("cardinalities"), 
                        msg=f"Onto '{onto_name}': The cardinalities of resource with original name '{orig['name']}' and returned name '{ret['name']}' failed.")
                else:
                    self.assertEqual(orig, ret, msg=f"Onto '{onto_name}': Resource with original name '{orig['name']}' and returned name '{ret['name']}' failed. "
                                     "The reason of the error lies OUTSIDE of the 'cardinalities' section.")


if __name__ == "__main__":
    unittest.main()
