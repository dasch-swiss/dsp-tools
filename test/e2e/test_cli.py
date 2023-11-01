# pylint: disable=missing-class-docstring

import json
import shutil
import subprocess
import unittest
from pathlib import Path

import jsonpath_ng
import jsonpath_ng.ext
import pytest

from dsp_tools.utils.project_create import create_project
from dsp_tools.utils.project_create_lists import create_lists


class TestCLI(unittest.TestCase):
    server = "http://0.0.0.0:3333"
    user = "root@example.com"
    password = "test"
    test_project_systematic_file = Path("testdata/json-project/test-project-systematic.json")
    test_project_minimal_file = Path("testdata/json-project/test-project-minimal.json")
    test_data_minimal_file = Path("testdata/xml-data/test-data-minimal.xml")
    cwd = Path("cwd")

    @classmethod
    def setUpClass(cls) -> None:
        """Is executed once before the methods of this class are run"""
        cls.cwd.mkdir(exist_ok=True)

    @classmethod
    def tearDownClass(cls) -> None:
        """Is executed after the methods of this class have all run through"""
        shutil.rmtree(cls.cwd)
        for f in Path().glob("*id2iri_*.json"):
            f.unlink()

    def _make_cli_call(
        self,
        cli_call: str,
        working_directory: Path = cwd,
    ) -> None:
        """
        Execute a CLI call, capture its stdout and stderr,
        and raise an AssertionError with stdout and stderr if it fails.
        Before every call, preprend "poetry run",
        so that the correct virtual environment is used.

        Args:
            cli_call: a command that can be executed by the system shell
            working_directory: working directory where to execute the call. Defaults to the class' default_cwd.

        Raises:
            AssertionError: detailed diagnostic message with stdout and stderr if the call fails
        """
        try:
            subprocess.run(
                f"poetry run {cli_call}",
                check=True,
                shell=True,
                capture_output=True,
                cwd=working_directory,
            )
        except subprocess.CalledProcessError as e:
            msg = (
                f"Failed CLI call:\n'{cli_call}'\n\n"
                f"Stdout:\n{e.output.decode('utf-8')}\n\n"
                f"Stderr:\n{e.stderr.decode('utf-8')}"
            )
            raise AssertionError(msg) from None

    def test_validate_lists_section_with_schema(self) -> None:
        """
        Test if the resource file 'src/dsp_tools/resources/schema/lists-only.json' can be accessed.
        For this, a real CLI call from another working directory is necessary.
        """
        cmd = f"dsp-tools create --lists-only --validate-only {self.test_project_systematic_file.absolute()}"
        self._make_cli_call(cmd)

    def test_create_lists(self) -> None:
        """
        Test that the 'lists' section of a JSON file is correctly created,
        and that the returned {node name: iri} mapping contains the same node names than the original list.
        """
        # create a project without lists
        create_project(
            project_file_as_path_or_parsed=self.test_project_minimal_file.absolute(),
            server=self.server,
            user_mail=self.user,
            password=self.password,
            verbose=True,
        )

        # insert a "lists" section into the project that was created
        with open("testdata/excel2json/lists-multilingual-output-expected.json", encoding="utf-8") as f:
            lists_section = json.load(f)
        with open(self.test_project_minimal_file, encoding="utf-8") as f:
            test_project_minimal = json.load(f)
        test_project_minimal["project"]["lists"] = [lists_section[0]]

        # The method to be tested can now be called with the project with the added list
        name2iri_mapping, success = create_lists(
            server=self.server,
            user=self.user,
            password=self.password,
            project_file_as_path_or_parsed=test_project_minimal,
        )

        # test if the returned mapping contains the same node names than the original list
        self.assertTrue(success)
        names_returned = [str(m.path) for m in jsonpath_ng.ext.parse("$..* where id").find(name2iri_mapping)]
        node_names = [m.value for m in jsonpath_ng.ext.parse("$.project.lists[*]..name").find(test_project_minimal)]
        self.assertListEqual(names_returned, node_names)

    def test_validate_project(self) -> None:
        """
        Test if the resource file 'src/dsp_tools/resources/schema/project.json' can be accessed.
        For this, a real CLI call from another working directory is necessary.
        """
        self._make_cli_call(cli_call=f"dsp-tools create --validate-only {self.test_project_minimal_file.absolute()}")

    def test_xml_upload(self) -> None:
        """
        Test if the resource file 'src/dsp_tools/resources/schema/data.xsd' can be accessed.
        For this, a real CLI call from another working directory is necessary.
        """
        self._make_cli_call(f"dsp-tools xmlupload -v {self.test_data_minimal_file.absolute()}")


if __name__ == "__main__":
    pytest.main([__file__])
