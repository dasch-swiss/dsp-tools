# pylint: disable=f-string-without-interpolation,missing-class-docstring,missing-function-docstring

import unittest
from typing import Union

import numpy as np
import pandas as pd
import pytest
from lxml import etree

from dsp_tools.models.exceptions import UserError
from dsp_tools.models.propertyelement import PropertyElement
from dsp_tools.utils import shared


class TestShared(unittest.TestCase):
    def test_validate_xml_against_schema(self) -> None:
        self.assertTrue(shared.validate_xml_against_schema(input_file="testdata/xml-data/test-data-systematic.xml"))
        self.assertTrue(
            shared.validate_xml_against_schema(input_file=etree.parse(source="testdata/xml-data/test-data-minimal.xml"))
        )

        with self.assertRaisesRegex(
            UserError,
            "Line 12: Element 'resource', attribute 'invalidtag': The attribute 'invalidtag' is not allowed",
        ):
            shared.validate_xml_against_schema(input_file="testdata/invalid-testdata/xml-data/invalid-resource-tag.xml")

        with self.assertRaisesRegex(
            UserError,
            r"XML-tags are not allowed in text properties with encoding=utf8\. "
            r"The following resources of your XML file violate this rule:"
            r"\n.+line 13.+"
            r"\n.+line 14.+"
            r"\n.+line 15.+"
            r"\n.+line 16.+",
        ):
            shared.validate_xml_against_schema(
                input_file="testdata/invalid-testdata/xml-data/utf8-text-with-xml-tags.xml"
            )

        with self.assertRaisesRegex(
            UserError,
            "Line 19: Element 'resource': Duplicate key-sequence .+ "
            "in unique identity-constraint 'IRI_attribute_of_resource_must_be_unique'",
        ):
            shared.validate_xml_against_schema(input_file="testdata/invalid-testdata/xml-data/duplicate-iri.xml")

        with self.assertRaisesRegex(
            UserError,
            "Line 19: Element 'resource': Duplicate key-sequence .+ "
            "in unique identity-constraint 'ARK_attribute_of_resource_must_be_unique'",
        ):
            shared.validate_xml_against_schema(input_file="testdata/invalid-testdata/xml-data/duplicate-ark.xml")

        with self.assertRaisesRegex(
            UserError,
            "Line 11: Element 'resource', attribute 'label': .+ "
            "The value '' has a length of '0'; this underruns the allowed minimum length of '1'",
        ):
            shared.validate_xml_against_schema(input_file="testdata/invalid-testdata/xml-data/empty-label.xml")

    def test_validate_xml_tags_in_text_properties(self) -> None:
        utf8_texts_with_allowed_html_escapes = [
            "(&lt;2cm) (&gt;10cm)",
            "text &lt; text/&gt;",
            "text &lt; text&gt; &amp; text",
            "text &lt;text text &gt; text",
            'text &lt; text text="text"&gt; text',
            'text &lt;text text="text" &gt; text',
        ]
        utf8_texts_with_allowed_html_escapes = [
            f'<knora shortcode="4123" default-ontology="testonto" xmlns="https://dasch.swiss/schema" '
            + f'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
            + f'<resource label="label" restype=":restype" id="id">'
            + f'<text-prop name=":name">'
            + f'<text encoding="utf8">{txt}'
            + f"</text></text-prop></resource></knora>"
            for txt in utf8_texts_with_allowed_html_escapes
        ]
        for xml in utf8_texts_with_allowed_html_escapes:
            self.assertTrue(
                shared._validate_xml_tags_in_text_properties(etree.fromstring(xml))  # pylint: disable=protected-access
            )

        utf8_texts_with_forbidden_html_escapes = ['&lt;tag s="t"&gt;', "&lt;em&gt;text&lt;/em&gt;"]
        utf8_texts_with_forbidden_html_escapes = [
            f'<knora shortcode="4123" default-ontology="testonto" xmlns="https://dasch.swiss/schema" '
            f'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
            + f'<resource label="label" restype=":restype" id="id">'
            + f'<text-prop name=":name">'
            + f'<text encoding="utf8">{txt}'
            + f"</text></text-prop></resource></knora>"
            for txt in utf8_texts_with_forbidden_html_escapes
        ]
        for xml in utf8_texts_with_forbidden_html_escapes:
            with self.assertRaisesRegex(UserError, "XML-tags are not allowed in text properties with encoding=utf8"):
                shared._validate_xml_tags_in_text_properties(etree.fromstring(xml))  # pylint: disable=protected-access

    def test_check_notna(self) -> None:
        na_values = [
            None,
            pd.NA,
            pd.NA,
            "",
            "  ",
            "-",
            ",",
            ".",
            "*",
            " ⳰",
            " ῀ ",
            " ῾ ",
            " \n\t ",
            "N/A",
            "n/a",
            "<NA>",
            "None",
            ["a", "b"],
            pd.array(["a", "b"]),
            np.array([0, 1]),
        ]
        for na_value in na_values:
            self.assertFalse(shared.check_notna(na_value), msg=f"Failed na_value: {na_value}")

        notna_values_orig: list[Union[str, int, float, bool]] = [
            1,
            0.1,
            True,
            False,
            "True",
            "False",
            r" \n\t ",
            "0",
            "_",
            "Ὅμηρος",
            "!",
            "?",
        ]
        notna_values_as_propelem = [PropertyElement(x) for x in notna_values_orig]
        for notna_value in notna_values_orig + notna_values_as_propelem:
            self.assertTrue(shared.check_notna(notna_value), msg=f"Failed notna_value: {notna_value}")


if __name__ == "__main__":
    pytest.main([__file__])
