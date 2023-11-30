"""unit tests for Excel to JSON list"""

# pylint: disable=missing-class-docstring,missing-function-docstring

import json
import re
import unittest

import jsonpath_ng
import jsonpath_ng.ext
import pandas as pd
import pytest
import regex
from pytest_unordered import unordered

from dsp_tools.commands.excel2json import lists as e2l
from dsp_tools.models.exceptions import BaseError

with open("testdata/excel2json/lists-multilingual-output-expected.json", encoding="utf-8") as f:
    lists_section_valid = json.load(f)


def test_expand_lists_from_excel() -> None:
    # take the "lists" section of the systematic test project, expand it, and check if it is equal to the expanded
    # version stored in the testdata folder
    list_name = "expanded lists section of json-project/test-project-systematic.json"
    with open("testdata/json-project/test-project-systematic.json", encoding="utf-8") as f:
        lists_with_excel_reference = json.load(f)["project"]["lists"]
    lists_with_excel_reference_output = e2l.expand_lists_from_excel(lists_with_excel_reference)
    with open("testdata/excel2json/lists-section-expanded.json", encoding="utf-8") as f:
        lists_with_excel_reference_output_expected = json.load(f)[list_name]

    assert unordered(lists_with_excel_reference_output) == lists_with_excel_reference_output_expected

    # take the expanded version, and make sure that it is returned unchanged
    lists_without_excel_reference = lists_with_excel_reference_output_expected
    lists_without_excel_reference_output = e2l.expand_lists_from_excel(lists_without_excel_reference)
    assert unordered(lists_without_excel_reference_output) == lists_without_excel_reference


def test_excel2lists_invalid_excel1() -> None:
    # make sure that the invalid lists raise an Error
    expected_msg = r"Found duplicate in column 2, row 9"
    with pytest.raises(BaseError, match=expected_msg):
        e2l.excel2lists(excelfolder="testdata/invalid-testdata/excel2json/lists-invalid-1")


def test_excel2lists_invalid_excel2() -> None:
    expected_msg = r"The Excel file with the language code 'de' should have a value in row 10, column 2"
    with pytest.raises(BaseError, match=expected_msg):
        e2l.excel2lists(excelfolder="testdata/invalid-testdata/excel2json/lists-invalid-2")


class TestValidateListSection:
    def test_correct(self) -> None:
        """validate the valid "lists" section: should not raise an error"""
        assert e2l.validate_lists_section_with_schema(lists_section=lists_section_valid) is True

    def test_without_comments(self) -> None:
        """remove mandatory "comments" section from root node: should raise an error"""
        with open("testdata/excel2json/lists-multilingual-output-expected.json", encoding="utf-8") as f:
            lists_section_valid_invalid = json.load(f)
        del lists_section_valid_invalid[0]["comments"]
        expected_msg = re.escape(
            "'lists' section did not pass validation. The error message is: 'comments' is a required property"
        )
        with pytest.raises(BaseError, match=expected_msg):
            e2l.validate_lists_section_with_schema(lists_section=lists_section_valid_invalid)

    def test_invalid_lang(self) -> None:
        """insert invalid language code in "comments" section: should raise an error"""
        lists_section_valid[0]["comments"]["eng"] = "wrong English label"

        expected_msg = re.escape(
            "'lists' section did not pass validation. The error message is: 'eng' does not match any of the regexes"
        )
        with pytest.raises(BaseError, match=expected_msg):
            e2l.validate_lists_section_with_schema(lists_section=lists_section_valid)

    def test_wrong_signature_wrong_data(self) -> None:
        """wrong usage of the function: should raise an error"""
        expected_msg = re.escape("works only if exactly one of the two arguments is given")
        with pytest.raises(BaseError, match=expected_msg):
            e2l.validate_lists_section_with_schema()

    def test_wrong_signature_no_data(self) -> None:
        """wrong usage of the function: should raise an error"""
        expected_msg = r"works only if exactly one of the two arguments is given"
        with pytest.raises(BaseError, match=expected_msg):
            e2l.validate_lists_section_with_schema(
                path_to_json_project_file="testdata/json-project/test-project-systematic.json",
                lists_section=lists_section_valid,
            )

    def test_file_without_list(self) -> None:
        """pass a file that doesn't have a "lists" section"""
        tp_minimal = "testdata/json-project/test-project-minimal.json"
        expected_msg = r"there is no 'lists' section"
        with pytest.raises(BaseError, match=expected_msg):
            e2l.validate_lists_section_with_schema(path_to_json_project_file=tp_minimal)


class TestExcelToJSONList(unittest.TestCase):
    def test_excel2lists_multilingual(self) -> None:
        # create output files
        input_df = pd.read_excel("testdata/excel2json/lists-multilingual/de.xlsx", header=None, dtype="str")
        input_df = input_df.map(
            lambda x: x if pd.notna(x) and regex.search(r"\p{L}", str(x), flags=regex.UNICODE) else pd.NA
        )
        input_df = input_df.dropna(axis="index", how="all")
        excelfolder = "testdata/excel2json/lists-multilingual"
        output_from_method, _ = e2l.excel2lists(excelfolder=excelfolder, path_to_output_file="")

        # check that the output file has the same number of nodes than the Excel file has rows
        output_nodes_matches = jsonpath_ng.parse("$..name").find(output_from_method)
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
            index = int(str(index))  # index is a label/index/hashable, but we need an int
            jsonpath_elems = [cell.strip() for cell in row]
            parser_string = "$"
            for elem in jsonpath_elems:
                parser_string = parser_string + f'.nodes[?(@.labels.en == "{elem}")]'
            node_match = jsonpath_ng.ext.parse(parser_string).find(output_from_method)
            self.assertTrue(
                len(node_match) == 1,
                f'The node "{jsonpath_elems[-1]}" from Excel row {index+1} was not correctly translated to the '
                f"output JSON file.",
            )

    def test_excel2lists_monolingual(self) -> None:
        # create output files
        input_df = pd.read_excel("testdata/excel2json/lists-monolingual/de.xlsx", header=None, dtype="str")
        input_df = input_df.map(
            lambda x: x if pd.notna(x) and regex.search(r"\p{L}", str(x), flags=regex.UNICODE) else pd.NA
        )
        input_df = input_df.dropna(axis="index", how="all")
        excelfolder = "testdata/excel2json/lists-monolingual"
        output_from_method, _ = e2l.excel2lists(excelfolder=excelfolder, path_to_output_file="")

        # check that the output file has the same number of nodes than the Excel file has rows
        output_nodes_matches = jsonpath_ng.parse("$..name").find(output_from_method)
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
            index = int(str(index))  # index is a label/index/hashable, but we need an int
            jsonpath_elems = [cell.strip() for cell in row]
            parser_string = "$"
            for elem in jsonpath_elems:
                parser_string = parser_string + f'.nodes[?(@.labels.en == "{elem}")]'
            node_match = jsonpath_ng.ext.parse(parser_string).find(output_from_method)
            self.assertTrue(
                len(node_match) == 1,
                f'The node "{jsonpath_elems[-1]}" from Excel row {index+1} was not correctly translated to the '
                f"output JSON file.",
            )


if __name__ == "__main__":
    pytest.main([__file__])
