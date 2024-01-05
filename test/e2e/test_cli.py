import shutil
import subprocess
import unittest
from pathlib import Path

import pytest

from dsp_tools.commands.project.create.project_create import create_project


class TestCLI(unittest.TestCase):
    """
    Test if the files in 'src/dsp_tools/resources/schema' are accessible
    if the CLI is called from another working directory.
    """

    server = "http://0.0.0.0:3333"
    user = "root@example.com"
    password = "test"
    test_project_systematic_file = Path("testdata/json-project/test-project-systematic.json")
    test_project_minimal_file = Path("testdata/json-project/test-project-minimal.json")
    test_data_minimal_file = Path("testdata/xml-data/test-data-minimal.xml")
    cwd = Path("cwd")
    testdata_tmp = Path("testdata/tmp")

    @classmethod
    def setUpClass(cls) -> None:
        """Is executed once before the methods of this class are run"""
        cls.testdata_tmp.mkdir(exist_ok=True)
        cls.cwd.mkdir(exist_ok=True)

    @classmethod
    def tearDownClass(cls) -> None:
        """Is executed after the methods of this class have all run through"""
        shutil.rmtree(cls.testdata_tmp)
        shutil.rmtree(cls.cwd)
        for f in Path().glob("*id2iri_*.json"):
            f.unlink()

    def test_validate_lists_section_with_schema(self) -> None:
        """Test if the resource file 'src/dsp_tools/resources/schema/lists-only.json' can be accessed."""
        args = ["create", "--lists-only", "--validate-only", str(self.test_project_systematic_file.absolute())]
        self._make_cli_call(args)

    def test_excel_to_json_resources(self) -> None:
        """
        Test if the resource file 'src/dsp_tools/resources/schema/resources-only.json' can be accessed.
        The output is not tested here, this is done in the unit tests.
        """
        excel_file = Path("testdata/excel2json/excel2json_files/test-name (test_label)/resources.xlsx")
        out_file = self.testdata_tmp / "_out_resources.json"
        self._make_cli_call(["excel2resources", str(excel_file.absolute()), str(out_file.absolute())])
        out_file.unlink()

    def test_excel_to_json_properties(self) -> None:
        """
        Test if the resource file 'src/dsp_tools/resources/schema/properties-only.json' can be accessed.
        The output is not tested here, this is done in the unit tests.
        """
        excel_file = Path("testdata/excel2json/excel2json_files/test-name (test_label)/properties.xlsx")
        out_file = self.testdata_tmp / "_out_properties.json"
        self._make_cli_call(["excel2properties", str(excel_file.absolute()), str(out_file.absolute())])
        out_file.unlink()

    def test_validate_project(self) -> None:
        """Test if the resource file 'src/dsp_tools/resources/schema/project.json' can be accessed."""
        self._make_cli_call(["create", "--validate-only", str(self.test_project_minimal_file.absolute())])

    def test_xml_upload(self) -> None:
        """Test if the resource file 'src/dsp_tools/resources/schema/data.xsd' can be accessed."""
        # create the necessary project
        # (if it was already created in a previous test, the function returns False, which doesn't matter)
        create_project(
            project_file_as_path_or_parsed=self.test_project_minimal_file.absolute(),
            server=self.server,
            user_mail=self.user,
            password=self.password,
            verbose=True,
        )
        self._make_cli_call(["xmlupload", "-v", str(self.test_data_minimal_file.absolute())])

    def _make_cli_call(
        self,
        args: list[str],
        working_directory: Path = cwd,
    ) -> None:
        """
        Execute a CLI call to dsp-tools, capture its stdout and stderr,
        and raise an AssertionError with stdout and stderr if it fails.

        Args:
            args: list of arguments for the dsp-tools CLI call
            working_directory: working directory where to execute the call. Defaults to the class' default_cwd.

        Raises:
            AssertionError: detailed diagnostic message with stdout and stderr if the call fails
        """
        try:
            subprocess.run(
                ["poetry", "run", "dsp-tools", *args],  # noqa: S607 (Starting a process with a partial executable path)
                check=True,
                capture_output=True,
                cwd=working_directory,
            )
        except subprocess.CalledProcessError as e:
            msg = (
                f"Failed CLI call:\n'{args}'\n\n"
                f"Stdout:\n{e.output.decode('utf-8')}\n\n"
                f"Stderr:\n{e.stderr.decode('utf-8')}"
            )
            raise AssertionError(msg) from None


if __name__ == "__main__":
    pytest.main([__file__])
