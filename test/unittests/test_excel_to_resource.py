"""unit tests for excel to resource"""
import os
import unittest

from openpyxl import Workbook

from knora.dsplib.utils import excel_to_json_resources as e2j


class TestExcelToResource(unittest.TestCase):

    def test_excel2json(self) -> None:
        in_file = "testdata/Resources.xlsx"
        out_file = "out_res.json"
        e2j.resources_excel2json(in_file, out_file)
        self.assertTrue(os.path.exists(out_file))

    def test_extract_row(self) -> None:
        wb = Workbook()
        ws_classes = wb.create_sheet("classes")
        res_name = "ClassA"
        row = (
            res_name,
            "Class A",
            "",
            "",
            "",
            "A comment on Class A",
            "",
            "",
            "",
            "Resource",
        )
        for i, c in enumerate(row):
            ws_classes.cell(row=2, column=i+1, value=c)
        ws_class_a = wb.create_sheet(res_name)
        ws_class_a["A2"] = "property1"
        ws_class_a["B2"] = "1"
        resource_dict = e2j._extract_row(row, wb)
        expected_dict = {
            'name': 'ClassA',
            'labels': {
                'en': 'Class A'
            },
            'comments': {
                'en': 'A comment on Class A'
            },
            'super': 'Resource',
            'cardinalities': [{
                'propname': ':property1',
                'cardinality': '1',
                'gui_order': 1
            }]}
        self.assertDictEqual(resource_dict, expected_dict)
