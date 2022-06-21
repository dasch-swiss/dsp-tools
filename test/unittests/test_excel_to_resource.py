"""unit tests for excel to resource"""
import os
import unittest
import pandas as pd
import json
import jsonpath_ng
import re

from knora.dsplib.utils import excel_to_json_resources as e2j


class TestExcelToResource(unittest.TestCase):

    def setUp(self) -> None:
        """Is executed before each test"""
        os.makedirs("testdata/tmp", exist_ok=True)

    def test_excel2json(self) -> None:
        excelfile = "testdata/Resources.xlsx"
        outfile = "testdata/tmp/_out_res.json"
        languages = ["en", "de", "fr", "it", "rm"]
        any_char_regex = r"[\wäàëéèêöôòü]"
        e2j.resources_excel2json(excelfile, outfile)

        # read excel: skip all rows that lack one of the required values
        excel_df = pd.read_excel(excelfile, dtype=str)
        for required_column in ["name", "super"]:
            excel_df = excel_df[pd.notna(excel_df[required_column])]
            excel_df = excel_df[[bool(re.search(any_char_regex, x)) for x in excel_df[required_column]]]

        excel_first_class_df = pd.read_excel(excelfile, sheet_name=1, dtype=str)
        for required_column in ["Property", "Cardinality"]:
            excel_first_class_df = excel_first_class_df[pd.notna(excel_first_class_df[required_column])]
            excel_first_class_df = excel_first_class_df[[bool(re.search(any_char_regex, x)) for x in excel_first_class_df[required_column]]]

        # extract infos from excel file
        excel_names = [s.strip() for s in excel_df["name"]]
        excel_supers = [[x.strip() for x in s.split(",")] for s in excel_df["super"]]

        excel_labels: dict[str, list[str]] = dict()
        for _id in languages:
            excel_labels[_id] = [s.strip() if isinstance(s, str) and re.search(any_char_regex, s) else "" for s in list(excel_df[_id])]

        excel_comments: dict[str, list[str]] = dict()
        for _id in [f"comment_{lang}" for lang in languages]:
            excel_comments[_id] = [s.strip() if isinstance(s, str) and re.search(any_char_regex, s) else "" for s in list(excel_df[_id])]

        excel_first_class_properties = [f":{s.strip()}" for s in excel_first_class_df["Property"]]
        excel_first_class_cardinalities = [str(s).strip().lower() for s in excel_first_class_df["Cardinality"]]

        # read json file
        with open(outfile) as f:
            json_string = f.read()
            json_string = "{" + json_string + "}"
            json_file = json.loads(json_string)

        # extract infos from json file
        json_names = [match.value for match in jsonpath_ng.parse("$.resources[*].name").find(json_file)]
        json_supers = [match.value for match in jsonpath_ng.parse("$.resources[*].super").find(json_file)]

        json_labels_all = [match.value for match in jsonpath_ng.parse("$.resources[*].labels").find(json_file)]
        json_labels: dict[str, list[str]] = dict()
        for _id in languages:
            json_labels[_id] = [label.get(_id, "").strip() for label in json_labels_all]

        json_comments: dict[str, list[str]] = dict()
        for _id in languages:
            # make sure the lists of the json comments contain a blank string even if there is no "comments" section at all in this resource
            json_comments[f"comment_{_id}"] = [resource.get("comments", {}).get(_id, "").strip() for resource in json_file["resources"]]

        json_first_class_properties = [match.value for match in jsonpath_ng.parse("$.resources[0].cardinalities[*].propname").find(json_file)]
        json_first_class_cardinalities = [match.value for match in jsonpath_ng.parse("$.resources[0].cardinalities[*].cardinality").find(json_file)]

        # make checks
        self.assertListEqual(excel_names, json_names)
        self.assertListEqual(excel_supers, json_supers)
        self.assertDictEqual(excel_labels, json_labels)
        self.assertDictEqual(excel_comments, json_comments)
        self.assertListEqual(excel_first_class_properties, json_first_class_properties)
        self.assertListEqual(excel_first_class_cardinalities, json_first_class_cardinalities)


if __name__ == "__main__":
    unittest.main()
