import shutil
import subprocess
import unittest
from pathlib import Path

import pytest


class TestCLI(unittest.TestCase):
    """
    Test if the files in 'src/dsp_tools/resources/schema' are accessible
    when DSP-TOOLS is installed from wheel instead of from source,
    and when the call is made from another working directory.
    In addition, making a CLI call also tests if all dependencies are shipped correctly,
    (the entry point imports all modules, so a not-shipped dependency would cause an import error).
    """

    test_project_systematic_file = Path("testdata/json-project/test-project-systematic.json")
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
        cmd = f"dsp-tools create --lists-only --validate-only {self.test_project_systematic_file.absolute()}"
        self._make_cli_call(cmd)

    def test_excel_to_json_resources(self) -> None:
        """
        Test if the resource file 'src/dsp_tools/resources/schema/resources-only.json' can be accessed.
        The output is not tested here, this is done in the unit tests.
        """
        excel_file = Path("testdata/excel2json/excel2json_files/test-name (test_label)/resources.xlsx")
        out_file = self.testdata_tmp / "_out_resources.json"
        self._make_cli_call(f"dsp-tools excel2resources '{excel_file.absolute()}' {out_file.absolute()}")
        out_file.unlink()

    def test_excel_to_json_properties(self) -> None:
        """
        Test if the resource file 'src/dsp_tools/resources/schema/properties-only.json' can be accessed.
        The output is not tested here, this is done in the unit tests.
        """
        excel_file = Path("testdata/excel2json/excel2json_files/test-name (test_label)/properties.xlsx")
        out_file = self.testdata_tmp / "_out_properties.json"
        self._make_cli_call(f"dsp-tools excel2properties '{excel_file.absolute()}' {out_file.absolute()}")
        out_file.unlink()

    def test_validate_project(self) -> None:
        """Test if the resource file 'src/dsp_tools/resources/schema/project.json' can be accessed."""
        self._make_cli_call(cli_call=f"dsp-tools create --validate-only {self.test_project_systematic_file.absolute()}")

    def test_xml_upload(self) -> None:
        """Test if the resource file 'src/dsp_tools/resources/schema/data.xsd' can be accessed."""
        self._make_cli_call(f"dsp-tools xmlupload -v --validate-only {self.test_data_minimal_file.absolute()}")

    def _make_cli_call(self, cli_call: str) -> None:
        """
        Execute a CLI call, capture its stdout and stderr,
        and raise an AssertionError with stdout and stderr if it fails.

        Args:
            cli_call: a command that can be executed by the system shell

        Raises:
            AssertionError: detailed diagnostic message with stdout and stderr if the call fails
        """
        try:
            subprocess.run(
                cli_call,
                check=True,
                shell=True,
                capture_output=True,
                cwd=self.cwd,
            )
        except subprocess.CalledProcessError as e:
            msg = (
                f"Failed CLI call:\n'{cli_call}'\n\n"
                f"Stdout:\n{e.output.decode('utf-8')}\n\n"
                f"Stderr:\n{e.stderr.decode('utf-8')}"
            )
            raise AssertionError(msg) from None


if __name__ == "__main__":
    pytest.main([__file__])
