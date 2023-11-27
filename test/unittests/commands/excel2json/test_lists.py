"""unit tests for Excel to JSON list"""

# ruff: noqa: D101 (undocumented-public-class)
# ruff: noqa: D102 (undocumented-public-method)

import json
import os
import shutil
import unittest
from typing import Any

import jsonpath_ng
import jsonpath_ng.ext
import pandas as pd
import pytest
import regex

from dsp_tools.commands.excel2json import lists as e2l
from dsp_tools.models.exceptions import BaseError


class TestExcelToJSONList(unittest.TestCase):
    lists_section_valid: list[dict[str, Any]]

    @classmethod
    def setUpClass(cls) -> None:
        """Is executed once before the methods of this class are run"""
        os.makedirs("testdata/tmp", exist_ok=True)

    @classmethod
    def tearDownClass(cls) -> None:
        """Is executed after the methods of this class have all run through"""
        shutil.rmtree("testdata/tmp", ignore_errors=True)

    def setUp(self) -> None:
        """Is executed before each test method"""
        with open("testdata/excel2json/lists-multilingual-output-expected.json", encoding="utf-8") as f:
            self.lists_section_valid = json.load(f)

    def test_expand_lists_from_excel(self) -> None:
        # take the "lists" section of the systematic test project, expand it, and check if it is equal to the expanded
        # version stored in the testdata folder
        list_name = "expanded lists section of json-project/test-project-systematic.json"
        with open("testdata/json-project/test-project-systematic.json", encoding="utf-8") as f:
            lists_with_excel_reference = json.load(f)["project"]["lists"]
        lists_with_excel_reference_output = e2l.expand_lists_from_excel(lists_with_excel_reference)
        with open("testdata/excel2json/lists-section-expanded.json", encoding="utf-8") as f:
            lists_with_excel_reference_output_expected = json.load(f)[list_name]
        self.assertListEqual(lists_with_excel_reference_output, lists_with_excel_reference_output_expected)

        # take the expanded version, and make sure that it is returned unchanged
        lists_without_excel_reference = lists_with_excel_reference_output_expected
        lists_without_excel_reference_output = e2l.expand_lists_from_excel(lists_without_excel_reference)
        self.assertListEqual(lists_without_excel_reference, lists_without_excel_reference_output)

    def test_validate_lists_section(self) -> None:
        """validate the valid "lists" section: should not raise an error"""
        self.assertTrue(e2l.validate_lists_section_with_schema(lists_section=self.lists_section_valid))

    def test_validate_lists_section_without_comments(self) -> None:
        """remove mandatory "comments" section from root node: should raise an error"""
        del self.lists_section_valid[0]["comments"]
        with self.assertRaisesRegex(
            BaseError,
            "'lists' section did not pass validation. The error message is: 'comments' is a required property",
        ):
            e2l.validate_lists_section_with_schema(lists_section=self.lists_section_valid)

    def test_validate_lists_section_with_invalid_lang(self) -> None:
        """insert invalid language code in "comments" section: should raise an error"""
        self.lists_section_valid[0]["comments"]["eng"] = "wrong English label"
        with self.assertRaisesRegex(
            BaseError,
            "'lists' section did not pass validation. The error message is: 'eng' does not match any of the regexes",
        ):
            e2l.validate_lists_section_with_schema(lists_section=self.lists_section_valid)

    def test_validate_lists_section_wrong_signature(self) -> None:
        """wrong usage of the function: should raise an error"""
        with self.assertRaisesRegex(BaseError, "works only if exactly one of the two arguments is given"):
            e2l.validate_lists_section_with_schema(
                path_to_json_project_file="testdata/json-project/test-project-systematic.json",
                lists_section=self.lists_section_valid,
            )
        with self.assertRaisesRegex(BaseError, "works only if exactly one of the two arguments is given"):
            e2l.validate_lists_section_with_schema()

    def test_validate_lists_section_file_without_list(self) -> None:
        """pass a file that doesn't have a "lists" section"""
        tp_minimal = "testdata/json-project/test-project-minimal.json"
        with self.assertRaisesRegex(BaseError, "there is no 'lists' section"):
            e2l.validate_lists_section_with_schema(path_to_json_project_file=tp_minimal)

    def test_excel2lists_monolingual_multilingual(self) -> None:
        for mode in ["monolingual", "multilingual"]:
            # create output files
            input_df = pd.read_excel(f"testdata/excel2json/lists-{mode}/de.xlsx", header=None, dtype="str")
            input_df = input_df.map(
                lambda x: x if pd.notna(x) and regex.search(r"\p{L}", str(x), flags=regex.UNICODE) else pd.NA
            )
            input_df = input_df.dropna(axis="index", how="all")
            excelfolder = f"testdata/excel2json/lists-{mode}"
            outfile = f"testdata/tmp/lists_output_{mode}.json"
            output_from_method, _ = e2l.excel2lists(excelfolder=excelfolder, path_to_output_file=outfile)

            # check that output from file and from method are equal
            with open(outfile, encoding="utf-8") as f:
                output_from_file: list[dict[str, Any]] = json.load(f)
            self.assertListEqual(output_from_file, output_from_method)

            # check that the output file has the same number of nodes than the Excel file has rows
            output_nodes_matches = jsonpath_ng.parse("$..name").find(output_from_file)
            self.assertTrue(
                len(input_df.index) == len(output_nodes_matches),
                "The output JSON file doesn't have the same number of nodes than the Excel file has rows",
            )

            # check that the longest Excel row(s) were correctly translated to the deepest-nested node(s)
            last_non_empty_column_index = input_df.count().index[-1]
            longest_rows_selector = input_df[last_non_empty_column_index].notna()
            # count() returns a Series that maps each column number to the number of entries it contains
            # index[-1] returns the number of the last non-empty column (in this test case: 3)
            # input_df[3].notna() returns a boolean Series with 'true' for every non-empty cell in column 3
            for index, row in input_df.loc[longest_rows_selector].iterrows():
                index_int = int(str(index))  # index is a label/index/hashable, but we need an int
                jsonpath_elems = [cell.strip() for cell in row]
                parser_string = "$"
                for elem in jsonpath_elems:
                    parser_string = parser_string + f'.nodes[?(@.labels.en == "{elem}")]'
                node_match = jsonpath_ng.ext.parse(parser_string).find(output_from_file)
                self.assertTrue(
                    len(node_match) == 1,
                    f'The node "{jsonpath_elems[-1]}" from Excel row {index_int+1} was not correctly translated to the '
                    f"output JSON file.",
                )

    def test_excel2lists_invalid1(self) -> None:
        # make sure that the invalid lists raise an Error
        with self.assertRaisesRegex(BaseError, r"Found duplicate in column 2, row 9"):
            e2l.excel2lists(excelfolder="testdata/invalid-testdata/excel2json/lists-invalid-1")

    def test_excel2lists_invalid2(self) -> None:
        with self.assertRaisesRegex(
            BaseError, r"The Excel file with the language code 'de' should have a value in row 10, column 2"
        ):
            e2l.excel2lists(excelfolder="testdata/invalid-testdata/excel2json/lists-invalid-2")


if __name__ == "__main__":
    pytest.main([__file__])
