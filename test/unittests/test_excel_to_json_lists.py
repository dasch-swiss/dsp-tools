"""unit tests for Excel to JSON list"""
import os
import unittest
import json
import jsonpath_ng
import jsonpath_ng.ext
import pandas

from knora.dsplib.utils import excel_to_json_lists as e2l


class TestExcelToJSONList(unittest.TestCase):

    def setUp(self) -> None:
        """Is executed before each test"""
        os.makedirs('testdata/tmp', exist_ok=True)

    def test_excel2jsonlist(self) -> None:
        # check that the output file was created
        excelfolder = "testdata/lists"
        outfile = "testdata/tmp/_lists_output.json"
        e2l.list_excel2json(listname=None, excelfolder=excelfolder, outfile=outfile)
        self.assertTrue(os.path.exists(outfile), f'The outfile {outfile} was not created')

        # check that the output file has the same number of nodes than the Excel file has rows
        with open(outfile) as f:
            output_as_dict = json.load(f)
        output_nodes_matches = jsonpath_ng.parse('$..name').find(output_as_dict)
        input_df = pandas.read_excel("testdata/lists/description_en.xlsx", header=None, dtype='str')
        self.assertTrue(
            len(input_df.index) == len(output_nodes_matches) - 1,
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
                f'The node "{jsonpath_elems[-1]}" from Excel row {index+1} was not correctly translated to the output '
                f'JSON file.'
            )


if __name__ == '__main__':
    unittest.main()
