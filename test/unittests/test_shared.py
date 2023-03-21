import unittest

import numpy as np
import pandas as pd
from lxml import etree

from dsp_tools.models.exceptions import UserError
from dsp_tools.models.propertyelement import PropertyElement
from dsp_tools.utils import shared


class TestShared(unittest.TestCase):

    def test_validate_xml_against_schema(self) -> None:
        self.assertTrue(shared.validate_xml_against_schema(input_file="testdata/xml-data/test-data-systematic.xml"))
        self.assertTrue(shared.validate_xml_against_schema(input_file=etree.parse(source="testdata/xml-data/test-data-minimal.xml")))
        
        with self.assertRaisesRegex(
            UserError,
            "Line 12: Element 'resource', attribute 'invalidtag': "
            "The attribute 'invalidtag' is not allowed"
        ):
            shared.validate_xml_against_schema(input_file="testdata/invalid-testdata/xml-data/invalid-resource-tag.xml")
        
        with self.assertRaisesRegex(
            UserError, 
            r"XML-tags are not allowed in text properties with encoding=utf8\. The following resources of your XML file violate this rule:"
            r"\n.+line 13.+" 
            r"\n.+line 14.+" 
            r"\n.+line 15.+" 
            r"\n.+line 16.+" 
        ):
            shared.validate_xml_against_schema(input_file="testdata/invalid-testdata/xml-data/utf8-text-with-xml-tags.xml")

        utf8_texts_with_allowed_html_escapes = [
            "(&lt;2cm) (&gt;10cm)",
            "text &lt; text/&gt;",
            "text &lt; text&gt; &amp; text",
            "text &lt;text text &gt; text",
            'text &lt; text text="text"&gt; text',
            'text &lt;text text="text" &gt; text'
        ]
        utf8_texts_with_allowed_html_escapes = [
            f'<knora shortcode="4123" default-ontology="testonto" xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">' +
            f'<resource label="label" restype=":restype" id="id">' + 
            f'<text-prop name=":name">' + 
            f'<text encoding="utf8">{txt}' + 
            f'</text></text-prop></resource></knora>' 
            for txt in utf8_texts_with_allowed_html_escapes
        ]
        for xml in utf8_texts_with_allowed_html_escapes:
            self.assertTrue(shared.validate_xml_against_schema(input_file=etree.fromstring(xml)))

        utf8_texts_with_forbidden_html_escapes = [
            f"&lt;tag s=\"t\"&gt;", 
            "&lt;em&gt;text&lt;/em&gt;"
        ]
        utf8_texts_with_forbidden_html_escapes = [
            f'<knora shortcode="4123" default-ontology="testonto" xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">' +
            f'<resource label="label" restype=":restype" id="id">' + 
            f'<text-prop name=":name">' + 
            f'<text encoding="utf8">{txt}' + 
            f'</text></text-prop></resource></knora>' 
            for txt in utf8_texts_with_forbidden_html_escapes
        ]
        for xml in utf8_texts_with_forbidden_html_escapes:
            with self.assertRaisesRegex(UserError, "XML-tags are not allowed in text properties with encoding=utf8"):
                shared.validate_xml_against_schema(input_file=etree.fromstring(xml))



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
