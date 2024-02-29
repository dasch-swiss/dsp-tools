import unittest
from pathlib import Path

import pandas as pd
import pytest
import regex

from dsp_tools import excel2xml
from dsp_tools.models.exceptions import BaseError

# ruff: noqa: PT009 (pytest-unittest-assertion) (remove this line when pytest is used instead of unittest)
# ruff: noqa: PT027 (pytest-unittest-raises-assertion) (remove this line when pytest is used instead of unittest)


class TestExcel2xmlLib(unittest.TestCase):
    def tearDown(self) -> None:
        Path("excel2xml-invalid-data.xml").unlink(missing_ok=True)

    def test_make_xsd_id_compatible(self) -> None:
        teststring = "0aüZ/_-äöü1234567890?`^':.;+*ç%&/()=±“#Ç[]|{}≠₂₃āṇśṣr̥ṁñἄ𝝺𝝲𝛆’الشعرُאדםПопрыгуньяşğ"  # noqa: RUF001
        expected_ = "_0a_Z__-___1234567890_____.__________________________r______________________________"

        # test that the results are distinct from each other
        results = {excel2xml.make_xsd_id_compatible(teststring) for _ in range(10)}
        self.assertTrue(len(results) == 10)
        for res in results:
            self.assertTrue(res.startswith(expected_))

        # test that the results are valid xsd:ids
        for result in results:
            self.assertTrue(regex.search(r"^[a-zA-Z_][\w.-]*$", result))

        # test that invalid inputs lead to an error
        self.assertRaises(BaseError, excel2xml.make_xsd_id_compatible, 0)
        self.assertRaises(BaseError, excel2xml.make_xsd_id_compatible, "n/a")
        self.assertRaises(BaseError, excel2xml.make_xsd_id_compatible, None)
        self.assertRaises(BaseError, excel2xml.make_xsd_id_compatible, "")
        self.assertRaises(BaseError, excel2xml.make_xsd_id_compatible, " ")
        self.assertRaises(BaseError, excel2xml.make_xsd_id_compatible, ".")

        # test that the special characters in the "Label" row of excel2xml-testdata-special-characters.xlsx are replaced
        special_characters_df = pd.read_excel("testdata/excel2xml/excel2xml-testdata-special-characters.xlsx")
        root = excel2xml.make_root("00A1", "test")
        root = excel2xml.append_permissions(root)
        for _, row in special_characters_df.iterrows():
            root.append(
                excel2xml.make_resource(
                    label=row["Label"], restype=":xyz", id=excel2xml.make_xsd_id_compatible(row["Label"])
                )
            )
        # schema validation inside the write_xml() checks if the ids of the resources are valid as xsd:ID
        excel2xml.write_xml(root, "special-characters.xml")
        Path("special-characters.xml").unlink()


if __name__ == "__main__":
    pytest.main([__file__])
