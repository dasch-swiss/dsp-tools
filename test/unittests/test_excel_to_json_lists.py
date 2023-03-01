"""unit tests for Excel to JSON list"""
import copy
import json
import os
import unittest
from typing import Any

import jsonpath_ng
import jsonpath_ng.ext
import pandas as pd
import regex

from dsp_tools.models.helpers import BaseError
from dsp_tools.utils import excel_to_json_lists as e2l


class TestExcelToJSONList(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        """Is executed before the methods of this class are run"""
        os.makedirs('testdata/tmp', exist_ok=True)

    @classmethod
    def tearDownClass(cls) -> None:
        """Is executed after the methods of this class have all run through"""
        for file in os.listdir('testdata/tmp'):
            os.remove('testdata/tmp/' + file)
        os.rmdir('testdata/tmp')


    def test_expand_lists_from_excel(self) -> None:
        # take the "lists" section of the systematic test project, expand it, and check if it is equal to the expanded
        # version stored in the testdata folder
        with open("testdata/test-project-systematic.json") as f:
            lists_with_excel_reference = json.load(f)["project"]["lists"]
        lists_with_excel_reference_output = e2l.expand_lists_from_excel(lists_with_excel_reference)
        with open("testdata/lists_section_expanded.json") as f:
            lists_with_excel_reference_output_expected = json.load(f)["expanded lists section of test-project-systematic.json"]
        self.assertListEqual(lists_with_excel_reference_output, lists_with_excel_reference_output_expected)

        # take the expanded version, and make sure that it is returned unchanged
        lists_without_excel_reference = lists_with_excel_reference_output_expected
        lists_without_excel_reference_output = e2l.expand_lists_from_excel(lists_without_excel_reference)
        self.assertListEqual(lists_without_excel_reference, lists_without_excel_reference_output)


    def test_make_json_lists_from_excel(self) -> None:
        lists_multilingual = [f"testdata/lists_multilingual/{lang}.xlsx" for lang in ["de", "en", "fr"]]
        lists_multilingual_output = e2l._make_json_lists_from_excel(lists_multilingual)
        with open("testdata/lists_multilingual_output_expected.json") as f:
            lists_multilingual_output_expected = json.load(f)
        self.assertListEqual(lists_multilingual_output, lists_multilingual_output_expected)


    def test_validate_lists_section_with_schema(self) -> None:
        with open("testdata/lists_multilingual_output_expected.json") as f:
            lists_section_valid = json.load(f)

        # validate the valid "lists" section in a correct way
        self.assertTrue(e2l.validate_lists_section_with_schema(lists_section=lists_section_valid))

        # remove mandatory "comments" section from root node
        lists_section_without_comment_at_rootnode = copy.deepcopy(lists_section_valid)
        del lists_section_without_comment_at_rootnode[0]["comments"]
        with self.assertRaisesRegex(
            BaseError,
            "\"lists\" section did not pass validation. The error message is: 'comments' is a required property"
        ):
            e2l.validate_lists_section_with_schema(lists_section=lists_section_without_comment_at_rootnode)

        # remove mandatory "comments" section from root node
        lists_section_with_invalid_lang = copy.deepcopy(lists_section_valid)
        lists_section_with_invalid_lang[0]["comments"]["eng"] = "wrong English label"
        with self.assertRaisesRegex(
            BaseError,
            "\"lists\" section did not pass validation. The error message is: 'eng' does not match any of the regexes"
        ):
            e2l.validate_lists_section_with_schema(lists_section=lists_section_with_invalid_lang)

        # wrong usage of the method
        with self.assertRaisesRegex(
            BaseError,
            "Validation of the 'lists' section works only if exactly one of the two arguments is given."
        ):
            e2l.validate_lists_section_with_schema(
                path_to_json_project_file="testdata/test-project-systematic.json",
                lists_section=lists_section_valid
            )
        with self.assertRaisesRegex(
            BaseError,
            "Validation of the 'lists' section works only if exactly one of the two arguments is given."
        ):
            e2l.validate_lists_section_with_schema()

        # pass a file that doesn't have a "lists" section
        with self.assertRaisesRegex(BaseError, "there is no \"lists\" section"):
            e2l.validate_lists_section_with_schema(path_to_json_project_file="testdata/test-project-minimal.json")


    def test_excel2lists(self) -> None:
        for mode in ["monolingual", "multilingual"]:
            # create output files
            input_df = pd.read_excel(f"testdata/lists_{mode}/de.xlsx", header=None, dtype='str')
            input_df = input_df.applymap(lambda x: x if pd.notna(x) and regex.search(r"\p{L}", str(x), flags=regex.UNICODE) else pd.NA)
            input_df.dropna(axis="index", how="all", inplace=True)
            excelfolder = f"testdata/lists_{mode}"
            outfile = f"testdata/tmp/lists_output_{mode}.json"
            output_from_method, _ = e2l.excel2lists(excelfolder=excelfolder, path_to_output_file=outfile)

            # check that output from file and from method are equal
            with open(outfile) as f:
                output_from_file: list[dict[str, Any]] = json.load(f)
            self.assertListEqual(output_from_file, output_from_method)

            # check that the output file has the same number of nodes than the Excel file has rows
            output_nodes_matches = jsonpath_ng.parse('$..name').find(output_from_file)
            self.assertTrue(
                len(input_df.index) == len(output_nodes_matches),
                f"The output JSON file doesn't have the same number of nodes than the Excel file has rows"
            )

            # check that the longest Excel row(s) were correctly translated to the deepest-nested node(s)
            last_non_empty_column_index = input_df.count().index[-1]
            longest_rows_selector = input_df[last_non_empty_column_index].notna()
                # count() returns a Series that maps each column number to the number of entries it contains
                # index[-1] returns the number of the last non-empty column (in this test case: 3)
                # input_df[3].notna() returns a boolean Series with 'true' for every non-empty cell in column 3
            for index, row in input_df.loc[longest_rows_selector].iterrows():
                jsonpath_elems = [cell.strip() for cell in row]
                parser_string = '$'
                for elem in jsonpath_elems:
                    parser_string = parser_string + f'.nodes[?(@.labels.en == "{elem}")]'
                node_match = jsonpath_ng.ext.parse(parser_string).find(output_from_file)
                self.assertTrue(
                    len(node_match) == 1,
                    f'The node "{jsonpath_elems[-1]}" from Excel row {index+1} was not correctly translated to the '
                    f'output JSON file.'
                )

        # make sure that the invalid lists raise an Error
        with self.assertRaisesRegex(BaseError, r"Found duplicate in column 2, row 9"):
            e2l.excel2lists(excelfolder="testdata/invalid_testdata/lists_invalid_1", path_to_output_file=outfile)
        with self.assertRaisesRegex(BaseError, r"The Excel file with the language code 'de' should have a value in row 10, column 2"):
            e2l.excel2lists(excelfolder="testdata/invalid_testdata/lists_invalid_2", path_to_output_file=outfile)


if __name__ == '__main__':
    unittest.main()
