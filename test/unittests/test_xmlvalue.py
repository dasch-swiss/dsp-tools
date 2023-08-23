import unittest

import pytest
from lxml import etree

from dsp_tools.models.xmlvalue import XMLValue


class TestXmlValue(unittest.TestCase):
    """Test the XMLValue class"""

    def test_cleanup_unformatted_text(self) -> None:
        """Test the removal of whitespaces and line breaks in utf8-encoded text values"""
        unformatted_text_orig = """<text permissions="prop-default">

                Poem
                with 1 line break:
                and 2 line breaks:

                and 3 line breaks:


                and     multiple     spaces	and		tabstops ...
                
                and spaces on empty lines.


            </text>"""
        unformatted_text_expected = (
            "Poem"
            "\n"
            "with 1 line break:\n"
            "and 2 line breaks:\n\n"
            "and 3 line breaks:\n\n"  # max. 1 empty line. 2+ are replaced by 1.
            "and multiple spaces and tabstops ...\n\n"
            "and spaces on empty lines."
        )
        unformatted_node = etree.fromstring(unformatted_text_orig)
        unformatted_xml_value = XMLValue(node=unformatted_node, val_type="unformatted-text")
        self.assertEqual(unformatted_xml_value.value, unformatted_text_expected)

    def test_cleanup_formatted_text(self) -> None:
        """Test the removal of whitespaces and line breaks in xml-formatted text values"""
        formatted_text_orig = """<text permissions="prop-default">

                This is <em>italicized and <strong>bold</strong></em> text!
                It contains <code>monospace text  that   preserves whitespaces and &amp; HTML-escapes</code>.

                It    contains    multiple    whitespaces	and		tabstops.<br/><br/>
                Line breaks must be done with <code><br/></code> tags.<br/>
                Otherwise they will be removed.<br/><br/>
                
                It contains links to a resource:
                <a class="salsah-link" href="IRI:test_thing_0:IRI">test_thing_0</a>

            </text>"""
        formatted_text_expected = (
            "This is <em>italicized and <strong>bold</strong></em> text! "
            "It contains <code>monospace text  that   preserves whitespaces and &amp; HTML-escapes</code>. "
            "It contains multiple whitespaces and tabstops.<br/><br/>"
            "Line breaks must be done with <code><br/></code> tags.<br/>"
            "Otherwise they will be removed.<br/><br/>"
            "It contains links to a resource: "
            '<a class="salsah-link" href="IRI:test_thing_0:IRI">test_thing_0</a>'
        )
        formatted_node = etree.fromstring(formatted_text_orig)
        formatted_xml_value = XMLValue(node=formatted_node, val_type="formatted-text")
        self.assertEqual(str(formatted_xml_value.value), formatted_text_expected)


if __name__ == "__main__":
    pytest.main([__file__])
