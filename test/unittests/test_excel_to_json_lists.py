"""unit tests for excel to JSON list"""
import os
import unittest
import json
import re
import jsonpath_ng
import pandas

from knora.dsplib.utils import excel_to_json_lists as e2l


# path: list[str] = list()
# def nested_dict_values_iterator(dicts: list):
#     global path
#     for dictionary in dicts:
#         if 'name' in dictionary:
#             path.append(dictionary['name'])
#             yield dictionary['name'], path
#             path.pop()
#         if 'nodes' in dict:
#             for value, _ in nested_dict_values_iterator(dictionary['nodes']):
#                 yield value


class TestExcelToJSONList(unittest.TestCase):

    def test_excel2jsonlist(self) -> None:
        # test if the output file was created
        excelfolder = "testdata/lists"
        outfile = "testdata/tmp/lists_output.json"
        e2l.list_excel2json(excelfolder, outfile)
        self.assertTrue(os.path.exists(outfile), f'The outfile {outfile} was not created')

        # check that the output file has the same number of nodes than the Excel file has rows
        with open(outfile) as f:
            output_as_dict = json.load(f)
        output_nodes_matches = jsonpath_ng.parse('name').find(output_as_dict)
        # TODO: hier noch anpassen, es findet nur das oberste statt allen verschachtelten

        output_as_string = json.dumps(output_as_dict)
        output_nodes_count = len(list(re.finditer(r'\"name\":', output_as_string))) - 1
        input_df = pandas.read_excel("testdata/lists/description_en.xlsx", header=None, dtype='str')
        self.assertTrue(
            len(input_df.index) == output_nodes_count,
            f"The output JSON file doesn't have the same number of nodes than the Excel file has rows"
        )

        # check that the longest Excel row(s) were correctly translated to the deepest-nested node(s)

        # take the last value
        # search that json path,
        # check if value is similar
        # to excel cell value with self.assertAlmostEqual


        # iterate through the rows with the deepest-nested nodes, i.e. the longest rows
        # TODO: wahrscheinlich so etwas: parse("$.movies[?(@.cast[:] =~ 'De Niro')].title")
        for index, row in input_df.loc[input_df[input_df.count().index[-1]].notna()].iterrows():
            jsonpath_raw = [e2l.simplify_name(cell.strip()) for cell in row]
            jsonpath = jsonpath_raw.copy()
            for i in range(len(jsonpath_raw)-1, -1, -1):
                jsonpath.insert(i, 'node')

            raw_counters = range(len(jsonpath_raw))         # [0, 1, 2, 3]
            counters = range(1, len(jsonpath)+1, 2)         # [1, 3, 5, 7]
            for raw_counter, counter in zip(raw_counters, counters):

                for pos, node in enumerate(output_as_dict['node']):
                    if node['name'] == jsonpath_raw[0]:
                        jsonpath[1] = pos

                for pos, node in enumerate(output_as_dict['node'][jsonpath[1]]['node']):
                    if node['name'] == jsonpath_raw[1]:
                        jsonpath[3] = pos

                for pos, node in enumerate(output_as_dict['node'][jsonpath[1]]['node'][jsonpath[3]]['node']):
                    if node['name'] == jsonpath_raw[2]:
                        jsonpath[5] = pos




        # df.dropna(how='all')
        # ws = openpyxl.load_workbook("testdata/lists/description_en.xlsx").worksheets[0]
        # for i in range(1, nodes_count+1):
        #     self.assertTrue(
        #         ws.cell(row=i, column=1).value is not None,
        #         f'The output JSON file has more nodes than the Excel file has rows'
        #     )
        #
        # for i in range(nodes_count+1, nodes_count+10):
        #     self.assertTrue(
        #         ws.cell(row=i, column=1).value is None,
        #         f'The output JSON file has less nodes than the Excel file has rows'
        #     )


if __name__ == '__main__':
    unittest.main()
