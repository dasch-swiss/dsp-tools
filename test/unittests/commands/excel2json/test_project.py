import json
import unittest

from dsp_tools.commands.excel2json.project import _create_project_json, _validate_folder_structure_get_filenames

# pylint: disable=missing-function-docstring


class TestCreateProject(unittest.TestCase):
    """Test the create project command"""

    def test_excel_to_json_project(self) -> None:
        excel_folder = "testdata/excel2json/excel2json_files"
        listfolder, onto_folders = _validate_folder_structure_get_filenames(excel_folder)
        _, project = _create_project_json(excel_folder, listfolder, onto_folders)
        with open("testdata/excel2json/excel2json-expected-output.json", encoding="utf-8") as f:
            output_expected = json.load(f)
        self.assertDictEqual(project, output_expected)
