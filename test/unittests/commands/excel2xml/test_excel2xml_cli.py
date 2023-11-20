# pylint: disable=missing-class-docstring,missing-function-docstring

import unittest
from pathlib import Path

import regex

from dsp_tools.commands.excel2xml import excel2xml_cli
from dsp_tools.models.exceptions import BaseError


class TestExcel2xmlCli(unittest.TestCase):
    def test_excel2xml_cli(self) -> None:
        # test the valid files, 3 times identical, but in the three formats XLSX, XLS, and CSV
        with open("testdata/excel2xml/excel2xml-expected-output.xml", encoding="utf-8") as f:
            expected = f.read()
        for ext in ["xlsx", "xls", "csv"]:
            excel2xml_cli.excel2xml(f"testdata/excel2xml/excel2xml-testdata.{ext}", "1234", "excel2xml-output")
            with open("excel2xml-output-data.xml", encoding="utf-8") as f:
                returned = f.read()
                self.assertEqual(returned, expected, msg=f"Failed with extension {ext}")
            Path("excel2xml-output-data.xml").unlink(missing_ok=True)

        # test the invalid files
        invalid_prefix = "testdata/invalid-testdata/excel2xml"
        warning_cases = [
            (
                f"{invalid_prefix}/boolean-prop-two-values.xlsx",
                "A <boolean-prop> can only have a single value",
            ),
            (
                f"{invalid_prefix}/empty-property.xlsx",
                "At least one value per property is required",
            ),
            (
                f"{invalid_prefix}/missing-prop-permissions.xlsx",
                "Missing permissions in column '2_permissions' of property ':hasName'",
            ),
            (
                f"{invalid_prefix}/missing-resource-label.xlsx",
                "Missing label for resource",
            ),
            (
                f"{invalid_prefix}/missing-resource-permissions.xlsx",
                "Missing permissions for resource",
            ),
            (
                f"{invalid_prefix}/missing-restype.xlsx",
                "Missing restype",
            ),
            (
                f"{invalid_prefix}/no-bitstream-permissions.xlsx",
                "Missing file permissions",
            ),
            (
                f"{invalid_prefix}/single-invalid-value-for-property.xlsx",
                "row 3 has an entry in column.+ '1_encoding', '1_permissions', but not",
            ),
        ]
        for file, _regex in warning_cases:
            _, catched_warnings = excel2xml_cli.excel2xml(file, "1234", "excel2xml-invalid")
            self.assertTrue(len(catched_warnings) > 0)
            messages = [str(w.message) for w in catched_warnings]
            self.assertTrue(any(regex.search(_regex, msg) for msg in messages), msg=f"Failed with file '{file}'")

        error_cases = [
            (
                f"{invalid_prefix}/id-propname-both.xlsx",
                "Exactly 1 of the 2 columns 'id' and 'prop name' must be filled",
            ),
            (
                f"{invalid_prefix}/id-propname-none.xlsx",
                "Exactly 1 of the 2 columns 'id' and 'prop name' must be filled",
            ),
            (
                f"{invalid_prefix}/nonexisting-proptype.xlsx",
                "Invalid prop type",
            ),
            (
                f"{invalid_prefix}/start-with-property-row.xlsx",
                "The first row must define a resource, not a property",
            ),
        ]
        for file, _regex in error_cases:
            with self.assertRaisesRegex(BaseError, _regex, msg=f"Failed with file '{file}'"):
                excel2xml_cli.excel2xml(file, "1234", "excel2xml-invalid")
