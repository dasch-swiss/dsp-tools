import unittest

from lxml import etree

import dsp_tools.utils.validate_xml_against_schema
from dsp_tools.models.exceptions import UserError

# ruff: noqa: PT009 (pytest-unittest-assertion) (remove this line when pytest is used instead of unittest)
# ruff: noqa: PT027 (pytest-unittest-raises-assertion) (remove this line when pytest is used instead of unittest)


class TestShared(unittest.TestCase):
    def test_validate_xml_against_schema(self) -> None:
        self.assertTrue(
            dsp_tools.utils.validate_xml_against_schema.validate_xml(
                input_file="testdata/xml-data/test-data-systematic.xml"
            )
        )
        self.assertTrue(
            dsp_tools.utils.validate_xml_against_schema.validate_xml(
                input_file=etree.parse(source="testdata/xml-data/test-data-minimal.xml")
            )
        )

        with self.assertRaisesRegex(
            UserError,
            "Line 12: Element 'resource', attribute 'invalidtag': The attribute 'invalidtag' is not allowed",
        ):
            dsp_tools.utils.validate_xml_against_schema.validate_xml(
                input_file="testdata/invalid-testdata/xml-data/invalid-resource-tag.xml"
            )

        with self.assertRaisesRegex(
            UserError,
            r"XML-tags are not allowed in text properties with encoding=utf8\. "
            r"The following resources of your XML file violate this rule:"
            r"\n.+line 13.+"
            r"\n.+line 14.+"
            r"\n.+line 15.+"
            r"\n.+line 16.+",
        ):
            dsp_tools.utils.validate_xml_against_schema.validate_xml(
                input_file="testdata/invalid-testdata/xml-data/utf8-text-with-xml-tags.xml"
            )

        with self.assertRaisesRegex(
            UserError,
            "Line 19: Element 'resource': Duplicate key-sequence .+ "
            "in unique identity-constraint 'IRI_attribute_of_resource_must_be_unique'",
        ):
            dsp_tools.utils.validate_xml_against_schema.validate_xml(
                input_file="testdata/invalid-testdata/xml-data/duplicate-iri.xml"
            )

        with self.assertRaisesRegex(
            UserError,
            "Line 19: Element 'resource': Duplicate key-sequence .+ "
            "in unique identity-constraint 'ARK_attribute_of_resource_must_be_unique'",
        ):
            dsp_tools.utils.validate_xml_against_schema.validate_xml(
                input_file="testdata/invalid-testdata/xml-data/duplicate-ark.xml"
            )

        with self.assertRaisesRegex(
            UserError,
            "Line 11: Element 'resource', attribute 'label': .+ "
            "The value '' has a length of '0'; this underruns the allowed minimum length of '1'",
        ):
            dsp_tools.utils.validate_xml_against_schema.validate_xml(
                input_file="testdata/invalid-testdata/xml-data/empty-label.xml"
            )

    def test_find_xml_tags_in_simple_text_elements_all_good(self) -> None:
        utf8_texts_with_allowed_html_escapes = [
            "(&lt;2cm) (&gt;10cm)",
            "text &lt; text/&gt;",
            "text &lt; text&gt; &amp; text",
            "text &lt;text text &gt; text",
            'text &lt; text text="text"&gt; text',
            'text &lt;text text="text" &gt; text',
        ]
        utf8_texts_with_allowed_html_escapes = [
            f"""
            <knora shortcode="4123" default-ontology="testonto">
                <resource label="label" restype=":restype" id="id">
                    <text-prop name=":name">
                        <text encoding="utf8">{txt}</text>
                    </text-prop>
                </resource>
            </knora>
            """
            for txt in utf8_texts_with_allowed_html_escapes
        ]
        for xml in utf8_texts_with_allowed_html_escapes:
            self.assertTrue(
                dsp_tools.utils.validate_xml_against_schema._find_xml_tags_in_simple_text_elements(
                    etree.fromstring(xml)
                )
            )

    def test_find_xml_tags_in_simple_text_elements_problems(self):
        utf8_texts_with_forbidden_html_escapes = ['&lt;tag s="t"&gt;', "&lt;em&gt;text&lt;/em&gt;"]
        utf8_texts_with_forbidden_html_escapes = [
            f"""
            <knora shortcode="4123" default-ontology="testonto">
                <resource label="label" restype=":restype" id="id">
                    <text-prop name=":name">
                        <text encoding="utf8">{txt}</text>
                    </text-prop>
                </resource>
            </knora>
            """
            for txt in utf8_texts_with_forbidden_html_escapes
        ]
        for xml in utf8_texts_with_forbidden_html_escapes:
            with self.assertRaisesRegex(UserError, "XML-tags are not allowed in text properties with encoding=utf8"):
                dsp_tools.utils.validate_xml_against_schema._find_xml_tags_in_simple_text_elements(
                    etree.fromstring(xml)
                )
