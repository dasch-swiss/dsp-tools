import pytest
from lxml import etree

from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import _cleanup_unformatted_text
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import _extract_formatted_text_from_node


def test_cleanup_unformatted_text() -> None:
    """Test the removal of whitespaces and line breaks in utf8-encoded text values"""
    orig = """<text permissions="prop-default" encoding="utf8" linkUUID="foo">

            Poem
            with 1 line break:
            and 2 line breaks:

            and 3 line breaks:


            and     multiple     spaces	and		tabstops ...
            
            and spaces on empty lines.


        </text>"""
    expected = (
        "Poem"
        "\n"
        "with 1 line break:\n"
        "and 2 line breaks:\n\n"
        "and 3 line breaks:\n\n\n"
        "and multiple spaces and tabstops ...\n\n"
        "and spaces on empty lines."
    )
    res = _cleanup_unformatted_text(orig)
    assert res == expected


def test_extract_formatted_text_from_node() -> None:
    """Test the removal of whitespaces and line breaks in xml-formatted text values"""
    formatted_text_orig = """<text permissions="prop-default" encoding="xml" linkUUID="foo">

            This is <em>italicized and <strong>bold</strong></em> text!
            It contains <code>monospace text  that   preserves whitespaces and &amp; HTML-escapes</code>.
            The same <pre>is   true   for   preformatted   text</pre>.

            It    contains    multiple    whitespaces	and		tabstops.<br/><br/>
            Line breaks must be done with <code><br/></code> tags.<br/>
            Otherwise they will be removed.<br/><br/>
            
            It contains links to a resource:
            <a class="salsah-link" href="IRI:test_thing_0:IRI">test_thing_0</a>

        </text>"""
    formatted_text_expected = (
        "This is <em>italicized and <strong>bold</strong></em> text! "
        "It contains <code>monospace text  that   preserves whitespaces and &amp; HTML-escapes</code>. "
        "The same <pre>is   true   for   preformatted   text</pre>. "
        "It contains multiple whitespaces and tabstops.<br/><br/>"
        "Line breaks must be done with <code><br/></code> tags.<br/>"
        "Otherwise they will be removed.<br/><br/>"
        "It contains links to a resource: "
        '<a class="salsah-link" href="IRI:test_thing_0:IRI">test_thing_0</a>'
    )
    formatted_node = etree.fromstring(formatted_text_orig)
    xml_value = _extract_formatted_text_from_node(node=formatted_node)
    assert xml_value.xmlstr == formatted_text_expected


if __name__ == "__main__":
    pytest.main([__file__])
