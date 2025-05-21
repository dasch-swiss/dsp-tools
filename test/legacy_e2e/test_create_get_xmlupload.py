import contextlib
import glob
import json
import shutil
import unittest
from pathlib import Path
from typing import Any
from typing import Optional
from typing import Union
from typing import cast

import regex

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.id2iri import id2iri
from dsp_tools.commands.project.create.project_create_all import create_project
from dsp_tools.commands.project.get import get_project
from dsp_tools.commands.xmlupload.xmlupload import xmlupload

# ruff: noqa: PT009 (pytest-unittest-assertion) (remove this line when pytest is used instead of unittest)


class TestCreateGetXMLUpload(unittest.TestCase):
    """Test if the commands "create", "get", and "xmlupload" work together as expected."""

    creds = ServerCredentials(
        user="root@example.com", password="test", server="http://0.0.0.0:3333", dsp_ingest_url="http://0.0.0.0:3340"
    )
    imgdir = "."
    test_project_systematic_file = Path("testdata/json-project/test-project-systematic.json")
    test_data_systematic_file = Path("testdata/xml-data/test-data-systematic.xml")
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
        for f in Path().glob("id2iri_*.json"):
            f.unlink()

    def test_create_project(self) -> None:
        """Test if the systematic JSON project file can be uploaded without producing an error on its way"""
        success = create_project(
            project_file_as_path_or_parsed=self.test_project_systematic_file.absolute(),
            creds=self.creds,
            verbose=True,
        )
        self.assertTrue(success)

    def test_xml_upload_incremental(self) -> None:
        """
        Test if the systematic XML data file can be uploaded without producing an error on its way,
        and if the 'id2iri' replacement works, so that the 2nd upload works.
        """
        success = xmlupload(
            input_file=self.test_data_systematic_file,
            creds=self.creds,
            imgdir=self.imgdir,
        )
        self.assertTrue(success)

        mapping_file = self._get_most_recent_glob_match("id2iri_*.json")
        second_xml_file_orig = Path("testdata/id2iri/test-id2iri-data.xml")
        success = id2iri(
            xml_file=str(second_xml_file_orig),
            json_file=str(mapping_file),
        )
        mapping_file.unlink()
        self.assertTrue(success)

        second_xml_file_replaced = self._get_most_recent_glob_match(f"{second_xml_file_orig.stem}_replaced_*.xml")
        success = xmlupload(
            input_file=second_xml_file_replaced,
            creds=self.creds,
            imgdir=self.imgdir,
        )
        second_xml_file_replaced.unlink()
        self.assertListEqual(list(Path(self.cwd).glob("stashed_*_properties_*.txt")), [])
        self.assertTrue(success)

    def test_get_project(self) -> None:
        """
        Retrieve the systematic JSON project file with the "get" command,
        and check if the result is identical to the original file.
        """
        out_file = self.testdata_tmp / "_test-project-systematic.json"
        success = get_project(
            project_identifier="systematic-tp",
            outfile_path=str(out_file),
            creds=self.creds,
            verbose=True,
        )
        self.assertTrue(success)

        project_original = self._get_original_project()
        with open(out_file, encoding="utf-8") as f:
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

        orig_licenses = set(project_original["project"]["enabled_licenses"])
        ret_licenses = set(project_returned["project"]["enabled_licenses"])
        self.assertSetEqual(
            orig_licenses,
            ret_licenses,
            msg=f"Field enabled_licenses is not identical: original={orig_licenses}, returned={ret_licenses}",
        )

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
            if proj_memberships := user.get("projects"):
                proj_memberships_expanded = [regex.sub("^:", f"{project_shortname}:", p) for p in proj_memberships]
                if f"{project_shortname}:admin" in proj_memberships_expanded:
                    with contextlib.suppress(ValueError):
                        proj_memberships_expanded.remove(f"{project_shortname}:member")
                users_original[index]["projects"] = proj_memberships_expanded

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
        # The returned file will have ":hasSimpleText" --> remove the onto name.
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

        resources_original = self._remove_onto_names_in_original_resources(onto_name, resources_original)

        resources_original, resources_returned = self._remove_cardinalities_in_original_resources(
            onto_name, resources_original, resources_returned
        )

        resources_original, resources_returned = self._sort_resources(resources_original, resources_returned)

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

    @staticmethod
    def _sort_resources(
        resources_original: list[dict[str, Any]], resources_returned: list[dict[str, Any]]
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        resources_original = sorted(resources_original, key=lambda x: cast(str, x.get("name", "")))
        resources_returned = sorted(resources_returned, key=lambda x: cast(str, x.get("name", "")))
        for reslist in [resources_original, resources_returned]:
            for res in reslist:
                if isinstance(res["super"], list):
                    res["super"] = sorted(res["super"])
                if res.get("cardinalities"):
                    res["cardinalities"] = sorted(res["cardinalities"], key=lambda x: cast(str, x["propname"]))
        return resources_original, resources_returned

    @staticmethod
    def _remove_cardinalities_in_original_resources(
        onto_name: str, resources_original: list[dict[str, Any]], resources_returned: list[dict[str, Any]]
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        # If a subclass doesn't explicitly define all cardinalities of its superclass
        # (or a subproperty of a cardinality of its superclass),
        # these cardinalities are implicitly added, so the "get" command will return them.
        # It would be too complicated to test this behaviour,
        # --> remove the cardinalities of all subclasses from both original file and returned file.
        for res in resources_original:
            supers_as_list = [res["super"]] if isinstance(res["super"], str) else res["super"]
            for sup in supers_as_list:
                if regex.search(rf"^({onto_name})?:\w+$", sup):
                    if res.get("cardinalities"):
                        del res["cardinalities"]
                    # remove from returned file, too
                    res_returned = next(x for x in resources_returned if x["name"] == res["name"])
                    if res_returned.get("cardinalities"):
                        del res_returned["cardinalities"]
        return resources_original, resources_returned

    @staticmethod
    def _remove_onto_names_in_original_resources(
        onto_name: str, resources_original: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        # The original might have names in the form "currentonto:hasSimpleText".
        # The returned file will have ":hasSimpleText" --> remove the onto name.
        for res in resources_original:
            for card in res.get("cardinalities", []):
                if card["propname"].startswith(onto_name):
                    card["propname"] = regex.sub(rf"^{onto_name}:", ":", card["propname"])
            supers_as_list = [res["super"]] if isinstance(res["super"], str) else res["super"]
            if any(sup.startswith(onto_name) for sup in supers_as_list):
                res["super"] = [regex.sub(rf"^{onto_name}:", ":", sup) for sup in supers_as_list]
        return resources_original

    @staticmethod
    def _get_most_recent_glob_match(glob_pattern: Union[str, Path]) -> Path:
        """
        Find the most recently created file that matches a glob pattern.

        Args:
            glob_pattern: glob pattern, either absolute or relative to the cwd of the caller

        Returns:
            the most recently created file that matches the glob pattern
        """
        candidates = [Path(x) for x in glob.glob(str(glob_pattern))]
        return max(candidates, key=lambda item: item.stat().st_ctime)
