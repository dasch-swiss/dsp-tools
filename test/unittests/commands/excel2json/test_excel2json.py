import json
import shutil
import unittest
from pathlib import Path

from dsp_tools.commands.excel2json.project import excel2json


class TestExcel2Json(unittest.TestCase):
    """Test the excel2json command"""

    testdata_tmp = Path("testdata/tmp")

    @classmethod
    def setUpClass(cls) -> None:
        """Is executed once before the methods of this class are run"""
        cls.testdata_tmp.mkdir(exist_ok=True)

    @classmethod
    def tearDownClass(cls) -> None:
        """Is executed after the methods of this class have all run through"""
        shutil.rmtree(cls.testdata_tmp)

    def test_excel_to_json_project(self) -> None:
        """
        Test if the excel2json command handles the expected folder structure correctly,
        and that every file in the nested folder structure is correctly translated into JSON.
        """
        excel_folder = Path("testdata/excel2json/excel2json_files")
        out_file = self.testdata_tmp / "_out_project.json"
        excel2json(str(excel_folder), str(out_file))
        with open("testdata/excel2json/excel2json-expected-output.json", encoding="utf-8") as f:
            output_expected = json.load(f)
        with open(out_file, encoding="utf-8") as f:
            output = json.load(f)
        self.assertDictEqual(output, output_expected)
        out_file.unlink()
