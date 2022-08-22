import unittest
import re
import pandas as pd
import numpy as np
from knora import csv2xml as c2x
from knora.dsplib.models.helpers import BaseError


class TestCsv2xml(unittest.TestCase):

    def test_make_xsd_id_compatible(self) -> None:
        teststring = "0aüZ/_-äöü1234567890?`^':.;+*ç%&/()=±“#Ç[]|{}≠"

        # test that the results are distinct from each other
        results = {c2x.make_xsd_id_compatible(teststring) for _ in range(10)}
        self.assertTrue(len(results) == 10)

        # test that the results are valid xsd:ids
        for result in results:
            self.assertTrue(re.search(r"^[a-zA-Z_][\w.-]*$", result))

        # test that invalid inputs lead to an error
        self.assertRaises(BaseError, c2x.make_xsd_id_compatible, 0)
        self.assertRaises(BaseError, c2x.make_xsd_id_compatible, "n/a")
        self.assertRaises(BaseError, c2x.make_xsd_id_compatible, None)
        self.assertRaises(BaseError, c2x.make_xsd_id_compatible, "")
        self.assertRaises(BaseError, c2x.make_xsd_id_compatible, " ")
        self.assertRaises(BaseError, c2x.make_xsd_id_compatible, ".")


    def test_check_notna(self) -> None:
        na_values = [None, pd.NA, np.nan, "", "  ", "-", ",", ".", "*", "!", " \n\t ", "N/A", "n/a", "<NA>", ["a", "b"],
                     pd.array(["a", "b"]), np.array([0, 1])]
        for na_value in na_values:
            self.assertFalse(c2x.check_notna(na_value), msg=f"Failed na_value: {na_value}")

        notna_values = [1, 0.1, True, False, "True", "False", r" \n\t ", "0", "_"]
        for notna_value in notna_values:
            self.assertTrue(c2x.check_notna(notna_value), msg=f"Failed notna_value: {notna_value}")


    def test_find_date_in_string(self) -> None:

        # template as documented in docstring: 2021-01-01 | 2015_01_02
        self.assertEqual(c2x.find_date_in_string("text 1492-10-12, text"), "GREGORIAN:CE:1492-10-12:CE:1492-10-12")
        self.assertEqual(c2x.find_date_in_string("Text 0476-09-04. text"), "GREGORIAN:CE:0476-09-04:CE:0476-09-04")
        self.assertEqual(c2x.find_date_in_string("Text (0476-09-04) text"), "GREGORIAN:CE:0476-09-04:CE:0476-09-04")
        self.assertIsNone(c2x.find_date_in_string("Text [1492-10-32?] text"))

        # template as documented in docstring: 26.2.-24.3.1948
        self.assertEqual(c2x.find_date_in_string("Text ...2193_01_26... text"), "GREGORIAN:CE:2193-01-26:CE:2193-01-26")
        self.assertEqual(c2x.find_date_in_string("Text -2193_01_26- text"), "GREGORIAN:CE:2193-01-26:CE:2193-01-26")
        self.assertIsNone(c2x.find_date_in_string("Text 2193_02_30 text"))

        # template as documented in docstring: 27.-28.1.1900
        self.assertEqual(c2x.find_date_in_string("Text _1.3. - 25.4.2022_ text"), "GREGORIAN:CE:2022-03-01:CE:2022-04-25")
        self.assertEqual(c2x.find_date_in_string("Text (01.03. - 25.04.2022) text"), "GREGORIAN:CE:2022-03-01:CE:2022-04-25")
        self.assertEqual(c2x.find_date_in_string("Text 28.2.-1.12.1515 text"), "GREGORIAN:CE:1515-02-28:CE:1515-12-01")
        self.assertEqual(c2x.find_date_in_string("Text 28.2.-1.12.1515 text"), "GREGORIAN:CE:1515-02-28:CE:1515-12-01")
        self.assertIsNone(c2x.find_date_in_string("Text 28.2.-26.2.1515 text"))

        # template as documented in docstring: 1.12.1973 - 6.1.1974
        self.assertEqual(c2x.find_date_in_string("Text 25.-26.2.0800 text"), "GREGORIAN:CE:0800-02-25:CE:0800-02-26")
        self.assertEqual(c2x.find_date_in_string("Text 25. - 26.2.0800 text"), "GREGORIAN:CE:0800-02-25:CE:0800-02-26")
        self.assertEqual(c2x.find_date_in_string("Text 25. - 26.2.0800 text"), "GREGORIAN:CE:0800-02-25:CE:0800-02-26")
        self.assertIsNone(c2x.find_date_in_string("Text 25.-24.2.0800 text"))

        # template as documented in docstring: 31.4.2021 | 5/11/2021
        self.assertEqual(c2x.find_date_in_string("Text 25.12.2022-03.01.2024 text"), "GREGORIAN:CE:2022-12-25:CE:2024-01-03")
        self.assertEqual(c2x.find_date_in_string("Text 25.12.2022 - 3.1.2024 text"), "GREGORIAN:CE:2022-12-25:CE:2024-01-03")
        self.assertIsNone(c2x.find_date_in_string("Text 25.12.2022-03.01.2022 text"))
        self.assertEqual(c2x.find_date_in_string("Text 25/12/2022-03/01/2024 text"), "GREGORIAN:CE:2022-12-25:CE:2024-01-03")
        self.assertEqual(c2x.find_date_in_string("Text 25/12/2022 - 03/01/2024 text"), "GREGORIAN:CE:2022-12-25:CE:2024-01-03")
        self.assertEqual(c2x.find_date_in_string("Text 25/12/2022 - 03/01/2024 text"), "GREGORIAN:CE:2022-12-25:CE:2024-01-03")
        self.assertIsNone(c2x.find_date_in_string("Text 25/12/2022-03/01/2022 text"))

        # template as documented in docstring: February 9, 1908 | Dec 5,1908
        self.assertEqual(c2x.find_date_in_string("Text Jan 26, 1993 text"), "GREGORIAN:CE:1993-01-26:CE:1993-01-26")
        self.assertEqual(c2x.find_date_in_string("Text February 26,2051 text"), "GREGORIAN:CE:2051-02-26:CE:2051-02-26")
        self.assertEqual(c2x.find_date_in_string("Text Sept 1, 1000 text"), "GREGORIAN:CE:1000-09-01:CE:1000-09-01")
        self.assertEqual(c2x.find_date_in_string("Text October 01, 1000 text"), "GREGORIAN:CE:1000-10-01:CE:1000-10-01")
        self.assertEqual(c2x.find_date_in_string("Text Nov 6,1000 text"), "GREGORIAN:CE:1000-11-06:CE:1000-11-06")
        self.assertEqual(c2x.find_date_in_string("Text Nov 6,1000 text"), "GREGORIAN:CE:1000-11-06:CE:1000-11-06")

        # template as documented in docstring: 1907
        self.assertEqual(c2x.find_date_in_string("Text 1848 text"), "GREGORIAN:CE:1848:CE:1848")

        # template as documented in docstring: 1849/50 | 1845-50 | 1849/1850
        self.assertEqual(c2x.find_date_in_string("Text 1849/1850? text"), "GREGORIAN:CE:1849:CE:1850")
        self.assertEqual(c2x.find_date_in_string("Text 1845-1850, text"), "GREGORIAN:CE:1845:CE:1850")
        self.assertEqual(c2x.find_date_in_string("Text 1849/50. text"), "GREGORIAN:CE:1849:CE:1850")
        self.assertEqual(c2x.find_date_in_string("Text (1845-50) text"), "GREGORIAN:CE:1845:CE:1850")
        self.assertEqual(c2x.find_date_in_string("Text [1849/1850] text"), "GREGORIAN:CE:1849:CE:1850")

if __name__ == "__main__":
    unittest.main()
