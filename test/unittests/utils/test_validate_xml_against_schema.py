import unittest

import pytest
from lxml import etree

import dsp_tools.utils.validate_xml_against_schema
from dsp_tools.models.exceptions import InputError

# ruff: noqa: PT009 (pytest-unittest-assertion) (remove this line when pytest is used instead of unittest)
# ruff: noqa: PT027 (pytest-unittest-raises-assertion) (remove this line when pytest is used instead of unittest)


class TestValidateXMLAgainstSchema(unittest.TestCase):
    def test_data_systematic(self) -> None:
        self.assertTrue(
            dsp_tools.utils.validate_xml_against_schema.validate_xml(
                input_file="testdata/xml-data/test-data-systematic.xml"
            )
        )

    def test_data_minimal(self) -> None:
        self.assertTrue(
            dsp_tools.utils.validate_xml_against_schema.validate_xml(
                input_file=etree.parse(source="testdata/xml-data/test-data-minimal.xml")
            )
        )

    def test_invalid_resource_tag_line_twelve(self) -> None:
        with self.assertRaisesRegex(
            InputError,
            "Line 12: Element 'resource', attribute 'invalidtag': The attribute 'invalidtag' is not allowed",
        ):
            dsp_tools.utils.validate_xml_against_schema.validate_xml(
                input_file="testdata/invalid-testdata/xml-data/invalid-resource-tag.xml"
            )

    def test_invalid_resource_tag_problem(self) -> None:
        with self.assertRaisesRegex(
            InputError,
            r"XML-tags are not allowed in text properties with encoding=utf8\.\n"
            r"The following resources of your XML file violate this rule:\n"
            r"    - line 13: resource 'the_only_resource', property ':test'\n"
            r"    - line 14: resource 'the_only_resource', property ':test'\n"
            r"    - line 15: resource 'the_only_resource', property ':test'\n"
            r"    - line 16: resource 'the_only_resource', property ':test'",
        ):
            dsp_tools.utils.validate_xml_against_schema.validate_xml(
                input_file="testdata/invalid-testdata/xml-data/utf8-text-with-xml-tags.xml"
            )

    def test_data_duplicate_iri(self) -> None:
        with self.assertRaisesRegex(
            InputError,
            "Line 19: Element 'resource': Duplicate key-sequence .+ "
            "in unique identity-constraint 'IRI_attribute_of_resource_must_be_unique'",
        ):
            dsp_tools.utils.validate_xml_against_schema.validate_xml(
                input_file="testdata/invalid-testdata/xml-data/duplicate-iri.xml"
            )

    def test_duplicate_ark(self) -> None:
        with self.assertRaisesRegex(
            InputError,
            "Line 19: Element 'resource': Duplicate key-sequence .+ "
            "in unique identity-constraint 'ARK_attribute_of_resource_must_be_unique'",
        ):
            dsp_tools.utils.validate_xml_against_schema.validate_xml(
                input_file="testdata/invalid-testdata/xml-data/duplicate-ark.xml"
            )

    def test_empty_label(self) -> None:
        with self.assertRaisesRegex(
            InputError,
            "Line 11: Element 'resource', attribute 'label': .+ "
            "The value '' has a length of '0'; this underruns the allowed minimum length of '1'",
        ):
            dsp_tools.utils.validate_xml_against_schema.validate_xml(
                input_file="testdata/invalid-testdata/xml-data/empty-label.xml"
            )


class TestFindXMLTagsInUTF8(unittest.TestCase):
    def test_find_xml_tags_in_simple_text_elements_all_good(self) -> None:
        allowed_html_escapes = [
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
            for txt in allowed_html_escapes
        ]
        for xml in utf8_texts_with_allowed_html_escapes:
            self.assertTrue(
                dsp_tools.utils.validate_xml_against_schema._find_xml_tags_in_simple_text_elements(
                    etree.fromstring(xml)
                )
            )

    def test_find_xml_tags_in_simple_text_elements_forbidden_escapes(self) -> None:
        test_ele = etree.fromstring(
            """
            <knora shortcode="4123" default-ontology="testonto">
                <resource label="label" restype=":restype" id="id">
                    <text-prop name=":name">
                        <text encoding="utf8">&lt;tag s="t"&gt;</text>
                    </text-prop>
                </resource>
            </knora>
            """
        )
        expected_msg = (
            "XML-tags are not allowed in text properties with encoding=utf8.\n"
            "The following resources of your XML file violate this rule:\n"
            "    - line 5: resource 'id', property ':name'"
        )
        all_good, res_msg = dsp_tools.utils.validate_xml_against_schema._find_xml_tags_in_simple_text_elements(test_ele)
        assert all_good is False
        assert res_msg == expected_msg

    def test_find_xml_tags_in_simple_text_elements_forbidden_escapes_two(self) -> None:
        test_ele = etree.fromstring(
            """
            <knora shortcode="4123" default-ontology="testonto">
                <resource label="label" restype=":restype" id="id">
                    <text-prop name=":propName">
                        <text encoding="utf8">&lt;em&gt;text&lt;/em&gt;</text>
                    </text-prop>
                </resource>
            </knora>
            """
        )
        expected_msg = (
            "XML-tags are not allowed in text properties with encoding=utf8.\n"
            "The following resources of your XML file violate this rule:\n"
            "    - line 5: resource 'id', property ':propName'"
        )
        all_good, res_msg = dsp_tools.utils.validate_xml_against_schema._find_xml_tags_in_simple_text_elements(test_ele)
        assert all_good is False
        assert res_msg == expected_msg


if __name__ == "__main__":
    pytest.main([__file__])
