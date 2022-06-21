"""unit tests for excel to properties"""
import os
import unittest
import pandas as pd
import re
import json
import jsonpath_ng

from knora.dsplib.utils import excel_to_json_properties as e2j


class TestExcelToProperties(unittest.TestCase):

    def setUp(self) -> None:
        """Is executed before each test"""
        os.makedirs("testdata/tmp", exist_ok=True)

    def test_excel2json(self) -> None:
        excelfile = "testdata/Properties.xlsx"
        outfile = "testdata/tmp/_out_properties.json"
        languages = ["en", "de", "fr", "it", "rm"]
        any_char_regex = r"[\wäàëéèêöôòü]"
        e2j.properties_excel2json(excelfile, outfile)

        # read excel: skip all rows that lack one of the required values
        excel_df = pd.read_excel(excelfile, dtype=str)
        for required_column in ["name", "super", "object", "gui_element"]:
            excel_df = excel_df[pd.notna(excel_df[required_column])]
            excel_df = excel_df[[bool(re.search(any_char_regex, x)) for x in excel_df[required_column]]]

        # extract infos from excel file
        excel_names = [s.strip() for s in excel_df["name"]]
        excel_supers = [[x.strip() for x in s.split(",")] for s in excel_df["super"]]
        excel_objects = [s.strip() for s in excel_df["object"]]

        excel_labels: dict[str, list[str]] = dict()
        for _id in languages:
            excel_labels[_id] = [s.strip() if isinstance(s, str) and re.search(any_char_regex, s) else ""
                                 for s in list(excel_df[_id])]

        excel_comments: dict[str, list[str]] = dict()
        for _id in [f"comment_{lang}" for lang in languages]:
            excel_comments[_id] = [s.strip() if isinstance(s, str) and re.search(any_char_regex, s) else ""
                                   for s in list(excel_df[_id])]

        excel_gui_elements = [s.strip() for s in list(excel_df["gui_element"])]

        # read json file
        with open(outfile) as f:
            json_string = f.read()
            json_string = "{" + json_string + "}"
            json_file = json.loads(json_string)

        # extract infos from json file
        json_names = [match.value for match in jsonpath_ng.parse("$.properties[*].name").find(json_file)]
        json_supers = [match.value for match in jsonpath_ng.parse("$.properties[*].super").find(json_file)]
        json_objects = [match.value for match in jsonpath_ng.parse("$.properties[*].object").find(json_file)]

        json_labels_all = [match.value for match in jsonpath_ng.parse("$.properties[*].labels").find(json_file)]
        json_labels: dict[str, list[str]] = dict()
        for _id in languages:
            json_labels[_id] = [label.get(_id, "").strip() for label in json_labels_all]

        json_comments: dict[str, list[str]] = dict()
        for _id in languages:
            json_comments[f"comment_{_id}"] = [resource.get("comments", {}).get(_id, "").strip()
                                               for resource in json_file["properties"]]

        json_gui_elements = [match.value for match in jsonpath_ng.parse("$.properties[*].gui_element").find(json_file)]

        # make checks
        self.assertListEqual(excel_names, json_names)
        self.assertListEqual(excel_supers, json_supers)
        self.assertListEqual(excel_objects, json_objects)
        self.assertDictEqual(excel_labels, json_labels)
        self.assertDictEqual(excel_comments, json_comments)
        self.assertListEqual(excel_gui_elements, json_gui_elements)


if __name__ == "__main__":
    unittest.main()
