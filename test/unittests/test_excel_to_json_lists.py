"""unit tests for Excel to JSON list"""
import os
import unittest
import json
import jsonpath_ng
import jsonpath_ng.ext
import pandas as pd
import regex

from knora.dsplib.utils import excel_to_json_lists as e2l


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

    def test_excel2jsonlist(self) -> None:
        for mode in ["monolingual", "multilingual"]:
            # create output files
            input_df = pd.read_excel(f"testdata/{mode} lists/Listen_de.xlsx", header=None, dtype='str')
            input_df = input_df.applymap(lambda x: x if pd.notna(x) and regex.search(r"\p{L}", str(x), flags=regex.UNICODE) else pd.NA)
            input_df.dropna(axis="index", how="all", inplace=True)
            excelfolder = f"testdata/{mode} lists"
            outfile = f"testdata/tmp/lists_output_{mode}.json"
            e2l.list_excel2json(excelfolder=excelfolder, outfile=outfile)

            # check that the output file has the same number of nodes than the Excel file has rows
            with open(outfile) as f:
                output_as_dict = json.load(f)
            output_nodes_matches = jsonpath_ng.parse('$..name').find(output_as_dict)
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
                node_match = jsonpath_ng.ext.parse(parser_string).find(output_as_dict)
                self.assertTrue(
                    len(node_match) == 1,
                    f'The node "{jsonpath_elems[-1]}" from Excel row {index+1} was not correctly translated to the '
                    f'output JSON file.'
                )


if __name__ == '__main__':
    unittest.main()
