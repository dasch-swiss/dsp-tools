import unittest

import numpy as np
import pandas as pd

from knora.dsplib.models.helpers import BaseError
from knora.dsplib.models.propertyelement import PropertyElement
from knora.dsplib.utils import shared


class TestShared(unittest.TestCase):

    def test_validate_xml_against_schema(self) -> None:
        self.assertTrue(shared.validate_xml_against_schema("testdata/test-data-systematic.xml"))
        self.assertTrue(shared.validate_xml_against_schema("testdata/test-data-minimal.xml"))
        with self.assertRaisesRegex(
            BaseError,
            "Line 12: Element '{https://dasch.swiss/schema}resource', attribute 'invalidtag': "
            "The attribute 'invalidtag' is not allowed"
        ):
            shared.validate_xml_against_schema("testdata/invalid_testdata/test-data-invalid-resource-tag.xml")


    def test_prepare_dataframe(self) -> None:
        original_df = pd.DataFrame({
             "  TitLE of Column 1 ": ["1",  " 0-1 ", "1-n ", pd.NA,  "    ", " ",    "",     " 0-n ", np.nan],
             " Title of Column 2 ":  [None, "1",     1,      "text", "text", "text", "text", "text",  "text"],
             "Title of Column 3":    ["",   pd.NA,   None,   "text", "text", "text", "text", np.nan,  "text"]
        })
        expected_df = pd.DataFrame({
            "title of column 1":     [      "0-1", "1-n",                                  "0-n"],
            "title of column 2":     [      "1",   "1",                                    "text"],
            "title of column 3":     [      "",    "",                                     ""]
        })
        returned_df = shared.prepare_dataframe(
            df=original_df,
            required_columns=["  TitLE of Column 1 ", " Title of Column 2 "],
            location_of_sheet=''
        )
        for expected, returned in zip(expected_df.iterrows(), returned_df.iterrows()):
            i, expected_row = expected
            _, returned_row = returned
            self.assertListEqual(list(expected_row), list(returned_row), msg=f"Failed in row {i}")


    def test_check_notna(self) -> None:
        na_values = [None, pd.NA, np.nan, "", "  ", "-", ",", ".", "*", " ⳰", " ῀ ", " ῾ ", " \n\t ", "N/A", "n/a",
                     "<NA>", "None", ["a", "b"], pd.array(["a", "b"]), np.array([0, 1])]
        for na_value in na_values:
            self.assertFalse(shared.check_notna(na_value), msg=f"Failed na_value: {na_value}")

        notna_values = [1, 0.1, True, False, "True", "False", r" \n\t ", "0", "_", "Ὅμηρος", "!", "?"]
        notna_values.extend([PropertyElement(x) for x in notna_values])
        for notna_value in notna_values:
            self.assertTrue(shared.check_notna(notna_value), msg=f"Failed notna_value: {notna_value}")


if __name__ == '__main__':
    unittest.main()
