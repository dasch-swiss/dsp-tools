import json
import unittest

import pytest

from dsp_tools.commands.excel2json.project import _old_create_project_json
from dsp_tools.commands.excel2json.project import _old_validate_folder_structure_get_filenames

# ruff: noqa: PT009 (pytest-unittest-assertion) (remove this line when pytest is used instead of unittest)


class TestCreateProject(unittest.TestCase):
    def test_excel_to_json_project(self) -> None:
        excel_folder = "testdata/excel2json/excel2json_files"
        listfolder, onto_folders = _old_validate_folder_structure_get_filenames(excel_folder)
        _, project = _old_create_project_json(excel_folder, listfolder, onto_folders)
        with open("testdata/excel2json/excel2json-expected-output.json", encoding="utf-8") as f:
            output_expected = json.load(f)
        self.assertDictEqual(project, output_expected)


if __name__ == "__main__":
    pytest.main([__file__])
