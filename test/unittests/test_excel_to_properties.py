"""unit tests for excel to properties"""
import os
import unittest

from openpyxl import Workbook

from knora.dsplib.utils import excel_to_json_properties as e2j


class TestExcelToProperties(unittest.TestCase):

    def setUp(self) -> None:
        """Is executed before each test"""
        os.makedirs('testdata/tmp', exist_ok=True)

    def test_excel2json(self) -> None:
        excelfile = "testdata/Properties.xlsx"
        outfile = "testdata/tmp/_out_properties.json"
        e2j.properties_excel2json(excelfile, outfile)
        self.assertTrue(os.path.exists(outfile))

    def test_row_to_prop(self) -> None:
        wb = Workbook()
        ws = wb.create_sheet("Tabelle1")
        row = (
            "hasAnthroponym  ",
            " hasValue, dcterms:creator   ",
            " TextValue ",
            "anthroponym",
            "",
            "Anthroponyme",
            "",
            " A strange chance put me in possession of this journal.  ",
            "",
            "",
            "",
            " Richtext ",
            ""
        )
        for i, c in enumerate(row):
            ws.cell(row=2, column=i+1, value=c)
        properties_dict = e2j.row_to_prop(row)
        expected_dict = {
            "name": "hasAnthroponym",
            "super": [
                "hasValue",
                "dcterms:creator"
            ],
            "object": "TextValue",
            "labels": {
                "en": "anthroponym",
                "fr": "Anthroponyme",
            },
            "comments": {
                "en": "A strange chance put me in possession of this journal."
            },
            "gui_element": "Richtext"
        }
        self.assertDictEqual(properties_dict, expected_dict)


if __name__ == '__main__':
    unittest.main()
