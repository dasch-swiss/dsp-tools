import json
import unittest
from pathlib import Path


class TestExcel2JsonCli(unittest.TestCase):
    testdata_tmp = Path("testdata/tmp")

    def test_excel_to_json_list(self) -> None:
        excel_folder = Path("testdata/excel2json/lists-multilingual")
        out_file = self.testdata_tmp / "_lists-out.json"
        self._make_cli_call(f"dsp-tools excel2lists {excel_folder.absolute()} {out_file.absolute()}")
        with open(out_file, encoding="utf-8") as f:
            output_actual = json.load(f)
        with open("testdata/excel2json/lists-multilingual-output-expected.json", encoding="utf-8") as f:
            output_expected = json.load(f)
        self.assertListEqual(output_actual, output_expected)
        out_file.unlink()

    def test_excel_to_json_resources(self) -> None:
        excel_file = Path("testdata/excel2json/excel2json_files/test-name (test_label)/resources.xlsx")
        out_file = self.testdata_tmp / "_out_resources.json"
        self._make_cli_call(f"dsp-tools excel2resources '{excel_file.absolute()}' {out_file.absolute()}")
        with open(out_file, encoding="utf-8") as f:
            output_actual = json.load(f)
        with open("testdata/excel2json/resources-output-expected.json", encoding="utf-8") as f:
            output_expected = json.load(f)
        self.assertListEqual(output_actual, output_expected)
        out_file.unlink()

    def test_excel_to_json_properties(self) -> None:
        excel_file = Path("testdata/excel2json/excel2json_files/test-name (test_label)/properties.xlsx")
        out_file = self.testdata_tmp / "_out_properties.json"
        self._make_cli_call(f"dsp-tools excel2properties '{excel_file.absolute()}' {out_file.absolute()}")
        with open(out_file, encoding="utf-8") as f:
            output_actual = json.load(f)
        with open("testdata/excel2json/properties-output-expected.json", encoding="utf-8") as f:
            output_expected = json.load(f)
        self.assertListEqual(output_actual, output_expected)
        out_file.unlink()
