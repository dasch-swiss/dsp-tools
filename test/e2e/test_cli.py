# pylint: disable=missing-class-docstring

import copy
import json
import shutil
import subprocess
import unittest
from pathlib import Path
from typing import Any, Optional, cast

import jsonpath_ng
import jsonpath_ng.ext
import pytest
import regex

from dsp_tools.utils.project_create_lists import create_lists
from dsp_tools.utils.shared import get_most_recent_glob_match


class TestCLI(unittest.TestCase):
    server = "http://0.0.0.0:3333"
    user = "root@example.com"
    password = "test"
    imgdir = "."
    sipi = "http://0.0.0.0:1024"
    test_project_systematic_file = Path("testdata/json-project/test-project-systematic.json")
    test_project_minimal_file = Path("testdata/json-project/test-project-minimal.json")
    test_project_hlist_file = Path("testdata/json-project/test-project-hlist-refers-label.json")
    test_data_systematic_file = Path("testdata/xml-data/test-data-systematic.xml")
    test_data_minimal_file = Path("testdata/xml-data/test-data-minimal.xml")
    cwd = Path("cwd")
    testdata_tmp = Path("testdata/tmp")

    @classmethod
    def setUpClass(cls) -> None:
        """Is executed once before the methods of this class are run"""
        cls.testdata_tmp.mkdir(exist_ok=True)
        cls.cwd.mkdir(exist_ok=True)

    @classmethod
    def tearDownClass(cls) -> None:
        """Is executed after the methods of this class have all run through"""
        shutil.rmtree(cls.testdata_tmp)
        shutil.rmtree(cls.cwd)
        for f in Path().glob("*id2iri_*.json"):
            f.unlink()

    def _make_cli_call(
        self,
        cli_call: str,
        working_directory: Path = cwd,
    ) -> None:
        """
        Execute a CLI call, capture its stdout and stderr,
        and raise an AssertionError with stdout and stderr if it fails.
        Before every call, preprend "poetry run",
        so that the correct virtual environment is used.

        Args:
            cli_call: a command that can be executed by the system shell
            working_directory: working directory where to execute the call. Defaults to the class' default_cwd.

        Raises:
            AssertionError: detailed diagnostic message with stdout and stderr if the call fails
        """
        try:
            subprocess.run(
                f"poetry run {cli_call}",
                check=True,
                shell=True,
                capture_output=True,
                cwd=working_directory,
            )
        except subprocess.CalledProcessError as e:
            msg = (
                f"Failed CLI call:\n'{cli_call}'\n\n"
                f"Stdout:\n{e.output.decode('utf-8')}\n\n"
                f"Stderr:\n{e.stderr.decode('utf-8')}"
            )
            raise AssertionError(msg) from None

    def test_validate_lists_section_with_schema(self) -> None:
        """
        Test if the resource file 'src/dsp_tools/resources/schema/lists-only.json' can be accessed.
        For this, a real CLI call from another working directory is necessary.
        """
        cmd = f"dsp-tools create --lists-only --validate-only {self.test_project_systematic_file.absolute()}"
        self._make_cli_call(cmd)

    def test_create_lists(self) -> None:
        """
        Test that the 'lists' section of a JSON file is correctly created,
        and that the returned {node name: iri} mapping contains the same node names than the original list.
        """
        # the project must already exist, so let's create a project without lists
        self._make_cli_call(f"dsp-tools create {self.test_project_minimal_file.absolute()}")

        # open a "lists" section and the project that was created
        with open("testdata/excel2json/lists-multilingual-output-expected.json", encoding="utf-8") as f:
            lists_section = json.load(f)
        with open(self.test_project_minimal_file, encoding="utf-8") as f:
            test_project_minimal = json.load(f)

        # create a copy of the project that was created, and insert the list into it
        tp_minimal_with_list = copy.deepcopy(test_project_minimal)
        tp_minimal_with_list["project"]["lists"] = [lists_section[0]]

        # The method to be tested can now be called with the project with the added list
        name2iri_mapping, success = create_lists(
            server=self.server,
            user=self.user,
            password=self.password,
            project_file_as_path_or_parsed=tp_minimal_with_list,
        )

        # test if the returned mapping contains the same node names than the original list
        self.assertTrue(success)
        names_returned = [str(m.path) for m in jsonpath_ng.ext.parse("$..* where id").find(name2iri_mapping)]
        node_names = [m.value for m in jsonpath_ng.ext.parse("$.project.lists[*]..name").find(tp_minimal_with_list)]
        self.assertListEqual(names_returned, node_names)

    def test_validate_project(self) -> None:
        """
        Test if the resource file 'src/dsp_tools/resources/schema/project.json' can be accessed.
        For this, a real CLI call from another working directory is necessary.
        """
        self._make_cli_call(
            cli_call=f"dsp-tools create --validate-only {self.test_project_minimal_file.absolute()}",
        )

    def test_create_project(self) -> None:
        # the working directory must be ".", because the JSON file contains a reference to an Excel file,
        # which is relative to the root of the repo
        self._make_cli_call(
            cli_call=f"dsp-tools create {self.test_project_systematic_file.absolute()} --verbose",
            working_directory=Path("."),
        )

    def test_create_project_hlist_refers_label(self) -> None:
        self._make_cli_call(f"dsp-tools create {self.test_project_hlist_file.absolute()} -v")

    def test_get_project(self) -> None:
        """
        Retrieve the systematic JSON project file with the "get" command,
        and check if the result is identical to the original file.
        """
        out_file = self.testdata_tmp / "_test-project-systematic.json"
        self._make_cli_call(f"dsp-tools get --project systematic-tp {out_file.absolute()}")

        project_original = self._get_original_project()
        with open(self.testdata_tmp / "_test-project-systematic.json", encoding="utf-8") as f:
            project_returned = json.load(f)

        self._compare_project(project_original, project_returned)
        self._compare_groups(
            groups_original=project_original["project"].get("groups"),
            groups_returned=project_returned["project"].get("groups"),
        )
        self._compare_users(
            users_original=project_original["project"].get("users"),
            users_returned=project_returned["project"].get("users"),
            project_shortname=project_original["project"]["shortname"],
        )
        self._compare_lists(
            lists_original=project_original["project"].get("lists"),
            lists_returned=project_returned["project"].get("lists"),
        )

        for file in [project_original, project_returned]:
            file["project"]["ontologies"] = sorted(file["project"]["ontologies"], key=lambda x: cast(str, x["name"]))
        for onto_original, onto_returned in zip(
            project_original["project"]["ontologies"],
            project_returned["project"]["ontologies"],
        ):
            self._compare_properties(
                properties_original=onto_original["properties"],
                properties_returned=onto_returned["properties"],
                onto_name=onto_original["name"],
            )
            self._compare_resources(
                resources_original=onto_original["resources"],
                resources_returned=onto_returned["resources"],
                onto_name=onto_original["name"],
            )

    def test_validate_xml_against_schema(self) -> None:
        cmd = f"dsp-tools xmlupload --validate-only --verbose {self.test_data_systematic_file.absolute()}"
        self._make_cli_call(cmd)

    def test_xml_upload(self) -> None:
        self._make_cli_call(f"dsp-tools xmlupload -v {self.test_data_minimal_file.absolute()}")

    def test_xml_upload_incremental(self) -> None:
        # the working directory must be ".", because the JSON file contains a reference to an Excel file,
        # which is relative to the root of the repo
        self._make_cli_call(
            cli_call=f"dsp-tools xmlupload {self.test_data_systematic_file.absolute()}",
            working_directory=Path("."),
        )

        mapping_file = get_most_recent_glob_match("test-data-systematic_id2iri_mapping_*.json")
        second_xml_file_orig = Path("testdata/id2iri/test-id2iri-data.xml")
        self._make_cli_call(f"dsp-tools id2iri {second_xml_file_orig.absolute()} {mapping_file.absolute()}")
        mapping_file.unlink()

        second_xml_file_replaced = get_most_recent_glob_match(self.cwd / f"{second_xml_file_orig.stem}_replaced_*.xml")
        self._make_cli_call(f"dsp-tools xmlupload -v {second_xml_file_replaced.absolute()}")
        second_xml_file_replaced.unlink()
        self.assertListEqual(list(Path(self.cwd).glob("stashed_*_properties_*.txt")), [])

    def test_excel_to_json_project(self) -> None:
        excel_folder = Path("testdata/excel2json/excel2json_files")
        out_file = self.testdata_tmp / "_out_project.json"
        self._make_cli_call(f"dsp-tools excel2json {excel_folder.absolute()} {out_file.absolute()}")
        with open("testdata/excel2json/excel2json-expected-output.json", encoding="utf-8") as f:
            output_expected = json.load(f)
        with open(out_file, encoding="utf-8") as f:
            output = json.load(f)
        self.assertDictEqual(output, output_expected)
        out_file.unlink()

    def test_excel_to_json_list(self) -> None:
        excel_folder = Path("testdata/excel2json/lists-multilingual")
        out_file = self.testdata_tmp / "_lists-out.json"
        self._make_cli_call(f"dsp-tools excel2lists {excel_folder.absolute()} {out_file.absolute()}")
        with open(out_file, encoding="utf-8") as f:
            output_actual = json.load(f)
        with open("testdata/excel2json/lists-multilingual-output-expected.json", encoding="utf-8") as f:
            output_expected = json.load(f)
        self.assertListEqual(output_actual, output_expected)
        out_file.unlink()

    def test_excel_to_json_resources(self) -> None:
        excel_file = Path("testdata/excel2json/excel2json_files/test-name (test_label)/resources.xlsx")
        out_file = self.testdata_tmp / "_out_resources.json"
        self._make_cli_call(f"dsp-tools excel2resources '{excel_file.absolute()}' {out_file.absolute()}")
        with open(out_file, encoding="utf-8") as f:
            output_actual = json.load(f)
        with open("testdata/excel2json/resources-output-expected.json", encoding="utf-8") as f:
            output_expected = json.load(f)
        self.assertListEqual(output_actual, output_expected)
        out_file.unlink()

    def test_excel_to_json_properties(self) -> None:
        excel_file = Path("testdata/excel2json/excel2json_files/test-name (test_label)/properties.xlsx")
        out_file = self.testdata_tmp / "_out_properties.json"
        self._make_cli_call(f"dsp-tools excel2properties '{excel_file.absolute()}' {out_file.absolute()}")
        with open(out_file, encoding="utf-8") as f:
            output_actual = json.load(f)
        with open("testdata/excel2json/properties-output-expected.json", encoding="utf-8") as f:
            output_expected = json.load(f)
        self.assertListEqual(output_actual, output_expected)
        out_file.unlink()

    def test_id2iri(self) -> None:
        xml_file = Path("testdata/id2iri/test-id2iri-data.xml")
        mapping_file = Path("testdata/id2iri/test-id2iri-mapping.json")
        self._make_cli_call(f"dsp-tools id2iri {xml_file.absolute()} {mapping_file.absolute()}")
        out_file = get_most_recent_glob_match(self.cwd / "test-id2iri-data_replaced_*.xml")
        with open(out_file, encoding="utf-8") as f:
            output_actual = f.read()
        out_file.unlink()
        with open("testdata/id2iri/test-id2iri-output-expected.xml", encoding="utf-8") as f:
            output_expected = f.read()
        self.assertEqual(output_actual, output_expected)

    def test_id2iri_remove_resources(self) -> None:
        xml_file = Path("testdata/id2iri/remove-resources/data.xml")
        mapping_file = Path("testdata/id2iri/remove-resources/mapping.json")
        self._make_cli_call(f"dsp-tools id2iri --remove-resources {xml_file.absolute()} {mapping_file.absolute()}")
        out_file = get_most_recent_glob_match(self.cwd / "data_replaced_*.xml")
        with open(out_file, encoding="utf-8") as f:
            output_actual = f.read()
        out_file.unlink()
        with open("testdata/id2iri/remove-resources/output-expected.xml", encoding="utf-8") as f:
            output_expected = f.read()
        self.assertEqual(output_actual, output_expected)

    @pytest.mark.filterwarnings("ignore::UserWarning")
    def test_excel2xml(self) -> None:
        datafile = Path("testdata/excel2xml/excel2xml-testdata.xlsx")
        shortcode = "1234"
        onto_name = "excel2xml-output"
        out_file = self.cwd / f"{onto_name}-data.xml"
        self._make_cli_call(f"dsp-tools excel2xml {datafile.absolute()} {shortcode} {onto_name}")
        with open(out_file, encoding="utf-8") as f:
            output_actual = f.read()
        with open("testdata/excel2xml/excel2xml-expected-output.xml", encoding="utf-8") as f:
            output_expected = f.read()
        self.assertEqual(output_actual, output_expected)
        out_file.unlink()

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
            project_original_str = regex.sub(rf'"{prefix}:(\w+?)"', rf'"{iri}\1"', project_original_str)
        project_original = json.loads(project_original_str)
        return cast(dict[str, Any], project_original)

    def _compare_project(
        self,
        project_original: dict[str, Any],
        project_returned: dict[str, Any],
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
        self.assertEqual(
            orig_keywords,
            ret_keywords,
            msg=f"Field keywords is not identical: original={orig_keywords}, returned={ret_keywords}",
        )

    def _compare_groups(
        self,
        groups_original: Optional[list[dict[str, Any]]],
        groups_returned: Optional[list[dict[str, Any]]],
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
            self.assertEqual(
                groups_original,
                groups_returned,
                msg="Returned number of groups is different from original number of groups.",
            )
        else:
            for orig, ret in zip(groups_original, groups_returned):
                self.assertEqual(
                    orig,
                    ret,
                    msg=f"Group with original name '{orig['name']}' and returned name '{ret['name']}' failed.",
                )

    def _compare_users(
        self,
        users_original: Optional[list[dict[str, Any]]],
        users_returned: Optional[list[dict[str, Any]]],
        project_shortname: str,
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
            current_project_membership_strings = [
                ":admin",
                ":member",
                f"{project_shortname}:admin",
                f"{project_shortname}:member",
            ]
            users_original = [
                u for u in users_original if any(p in u.get("projects", []) for p in current_project_membership_strings)
            ]

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
                users_original[index]["groups"] = [regex.sub("^:", f"{project_shortname}:", g) for g in user["groups"]]
            if user.get("projects"):
                users_original[index]["projects"] = [
                    regex.sub("^:", f"{project_shortname}:", p) for p in user["projects"]
                ]

        # sort both lists
        users_original = sorted(users_original or [], key=lambda x: cast(str, x["username"]))
        users_returned = sorted(users_returned or [], key=lambda x: cast(str, x["username"]))
        if len(users_original) != len(users_returned):
            self.assertEqual(
                users_original,
                users_returned,
                msg="Returned number of users is different from original number of users.",
            )
        else:
            for orig, ret in zip(users_original, users_returned):
                self.assertEqual(
                    orig,
                    ret,
                    msg=f"User with original name '{orig['username']}' and returned name '{ret['username']}' failed.",
                )

    def _compare_lists(
        self,
        lists_original: Optional[list[dict[str, Any]]],
        lists_returned: Optional[list[dict[str, Any]]],
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
            if (
                isinstance(list_original["nodes"], dict)
                and len(list_original["nodes"]) == 1
                and "folder" in list_original["nodes"]
            ):
                lists_original.remove(list_original)
                lists_returned = [x for x in lists_returned if x["name"] != list_original["name"]]

        # sort both lists
        lists_original = sorted(lists_original, key=lambda x: cast(str, x.get("name", "")))
        lists_returned = sorted(lists_returned, key=lambda x: cast(str, x.get("name", "")))
        if len(lists_original) != len(lists_returned):
            self.assertEqual(
                lists_original,
                lists_returned,
                msg="Returned number of lists is different from original number of lists.",
            )
        else:
            for orig, ret in zip(lists_original, lists_returned):
                self.assertEqual(
                    orig,
                    ret,
                    msg=f"List with original name '{orig['name']}' and returned name '{ret['name']}' failed.",
                )

    def _compare_properties(
        self,
        properties_original: Optional[list[dict[str, Any]]],
        properties_returned: Optional[list[dict[str, Any]]],
        onto_name: str,
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
                prop["super"] = [regex.sub(rf"^{onto_name}:", ":", sup) for sup in prop["super"]]

        # sort both lists
        properties_original = sorted(properties_original, key=lambda x: cast(str, x.get("name", "")))
        properties_returned = sorted(properties_returned, key=lambda x: cast(str, x.get("name", "")))
        for proplist in [properties_original, properties_returned]:
            for prop in proplist:
                if isinstance(prop["super"], list):
                    prop["super"] = sorted(prop["super"])

        if len(properties_original) != len(properties_returned):
            self.assertEqual(
                properties_original,
                properties_returned,
                msg=f"Onto {onto_name}: Returned number of properties is different from original number of properties.",
            )
        else:
            for orig, ret in zip(properties_original, properties_returned):
                self.assertEqual(
                    orig,
                    ret,
                    msg=f"Onto '{onto_name}': Property with original name '{orig['name']}' "
                    f"and returned name '{ret['name']}' failed.",
                )

    def _compare_resources(
        self,
        resources_original: Optional[list[dict[str, Any]]],
        resources_returned: Optional[list[dict[str, Any]]],
        onto_name: str,
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
                    card["propname"] = regex.sub(rf"^{onto_name}:", ":", card["propname"])
            supers_as_list = [res["super"]] if isinstance(res["super"], str) else res["super"]
            if any(sup.startswith(onto_name) for sup in supers_as_list):
                res["super"] = [regex.sub(rf"^{onto_name}:", ":", sup) for sup in supers_as_list]

        # If a subclass doesn't explicitly define all cardinalities of its superclass
        # (or a subproperty of a cardinality of its superclass),
        # these cardinalities are implicitly added, so the "get" command will return them.
        # It would be too complicated to test this behaviour,
        # so we need to remove the cardinalities of all subclasses from both original file and returned file.
        for res in resources_original:
            supers_as_list = [res["super"]] if isinstance(res["super"], str) else res["super"]
            for sup in supers_as_list:
                if regex.search(rf"^({onto_name})?:\w+$", sup):
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
            self.assertEqual(
                resources_original,
                resources_returned,
                msg=f"Onto {onto_name}: Returned number of resources is different from original number of resources.",
            )
        else:
            for orig, ret in zip(resources_original, resources_returned):
                if orig.get("cardinalities") != ret.get("cardinalities"):
                    self.assertEqual(
                        orig.get("cardinalities"),
                        ret.get("cardinalities"),
                        msg=f"Onto '{onto_name}': The cardinalities of resource with original name '{orig['name']}' "
                        f"and returned name '{ret['name']}' failed.",
                    )
                else:
                    self.assertEqual(
                        orig,
                        ret,
                        msg=f"Onto '{onto_name}': Resource with original name '{orig['name']}' and returned name "
                        "'{ret['name']}' failed. The reason of the error lies OUTSIDE of the 'cardinalities' section.",
                    )


if __name__ == "__main__":
    pytest.main([__file__])
