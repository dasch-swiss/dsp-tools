import pytest
from lxml import etree

from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLProperty
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLValue
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import _cleanup_formatted_text
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import _cleanup_unformatted_text
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import _extract_formatted_text_from_node
from dsp_tools.commands.xmlupload.models.formatted_text_value import FormattedTextValue
from dsp_tools.models.exceptions import XmlUploadError


class Test_XMLProperty:
    def test_from_node_normal_prop(self) -> None:
        string = """
            <time-prop name=":hasTime">
                <time>2019-10-23T13:45:12.01-14:00</time>
                <time>2019-10-23T13:45:12-14:00</time>
            </time-prop>
        """
        res = XMLProperty.from_node(etree.fromstring(string), "time", "rosetta")
        expected_vals = [XMLValue("2019-10-23T13:45:12.01-14:00"), XMLValue("2019-10-23T13:45:12-14:00")]
        expected = XMLProperty("rosetta:hasTime", "time", expected_vals)
        assert res == expected

    def test_from_node_knora_base_prop(self) -> None:
        string = """<hasKeyword>Keyword 2 of video segment</hasKeyword>"""
        res = XMLProperty.from_node(etree.fromstring(string), "hasKeyword", "rosetta")
        expected = XMLProperty("knora-api:hasKeyword", "hasKeyword", [XMLValue("Keyword 2 of video segment")])
        assert res == expected

    def test_get_name_special_tag(self) -> None:
        res = XMLProperty._get_name(etree.fromstring("<isSegmentOf>foo</isSegmentOf>"), "rosetta")
        assert res == "knora-api:isSegmentOf"

    def test_get_name_knora_base_prop_with_normal_tag(self) -> None:
        string = """<text-prop name="hasComment"><text encoding="xml">comment</text></text-prop>"""
        res = XMLProperty._get_name(etree.fromstring(string), "rosetta")
        assert res == "knora-api:hasComment"

    def test_get_name_normal_tag_abbreviated(self) -> None:
        string = """<text-prop name=":hasText"><text encoding="utf8">foobar</text></text-prop>"""
        res = XMLProperty._get_name(etree.fromstring(string), "rosetta")
        assert res == "rosetta:hasText"

    def test_get_name_normal_tag_full(self) -> None:
        string = """<text-prop name="rosetta:hasText"><text encoding="utf8">foobar</text></text-prop>"""
        res = XMLProperty._get_name(etree.fromstring(string), "rosetta")
        assert res == "rosetta:hasText"

    def test_get_values_from_normal_props_list(self) -> None:
        string = """<list-prop list="testlist" name=":hasListItem"><list>first subnode</list></list-prop>"""
        expected = [XMLValue("testlist:first subnode")]
        res = XMLProperty._get_values_from_normal_props(etree.fromstring(string), "list")
        assert res == expected

    def test_get_values_from_normal_props_uri(self) -> None:
        string = """
            <uri-prop name=":hasUri">
                <uri>https://dasch.swiss/</uri>
                <uri>https://www.test-case.ch/</uri>
            </uri-prop>
        """
        expected = [XMLValue("https://dasch.swiss/"), XMLValue("https://www.test-case.ch/")]
        res = XMLProperty._get_values_from_normal_props(etree.fromstring(string), "uri")
        assert res == expected

    def test_get_values_from_normal_props_invalid(self) -> None:
        string = """
            <uri-prop name=":hasUri">
                <uri>https://dasch.swiss/</uri>
                <integer>https://www.test-case.ch/</integer>
            </uri-prop>
        """
        with pytest.raises(XmlUploadError):
            XMLProperty._get_values_from_normal_props(etree.fromstring(string), "uri")

    def test_get_value_from_knora_base_prop_with_all_attributes(self) -> None:
        string = """<isSegmentOf permissions="open" comment="cmt">video_thing_1</isSegmentOf>"""
        expected = XMLValue("video_thing_1", permissions="open", comment="cmt")
        res = XMLProperty._get_value_from_knora_base_prop(etree.fromstring(string))
        assert res == expected

    def test_get_value_from_knora_base_prop_hasSegmentBounds(self) -> None:
        string = """<hasSegmentBounds segment_start="0.1" segment_end="0.234"/>"""
        expected = XMLValue("0.1:0.234")
        res = XMLProperty._get_value_from_knora_base_prop(etree.fromstring(string))
        assert res == expected

    def test_get_value_from_knora_base_prop_hasDescription(self) -> None:
        string = """
            <hasDescription linkUUID="123456789">
                text <a class="salsah-link" href="IRI:test_thing_2:IRI">link</a>
            </hasDescription>
        """
        xmltext = FormattedTextValue("""text <a class="salsah-link" href="IRI:test_thing_2:IRI">link</a>""")
        expected = XMLValue(xmltext, resrefs={"test_thing_2"}, link_uuid="123456789")
        res = XMLProperty._get_value_from_knora_base_prop(etree.fromstring(string))
        assert res == expected

    def test_get_value_from_knora_base_prop_hasComment(self) -> None:
        string = "<hasComment>text <strong>bold</strong></hasComment>"
        expected = XMLValue(FormattedTextValue("text <strong>bold</strong>"))
        res = XMLProperty._get_value_from_knora_base_prop(etree.fromstring(string))
        assert res == expected

    def test_get_value_from_knora_base_prop_hasTitle(self) -> None:
        string = "<hasTitle> Title  of   video  segment </hasTitle>"
        expected = XMLValue("Title of video segment")
        res = XMLProperty._get_value_from_knora_base_prop(etree.fromstring(string))
        assert res == expected


class Test_XMLValue:
    def test_from_node_integer_value(self) -> None:
        # test content, and these attributes: comments, permissions, and linkUUID (if existing)
        node = etree.fromstring("""<integer permissions="open" comment="cmt" linkUUID="foo">99</integer>""")
        expected = XMLValue(value="99", comment="cmt", permissions="open", link_uuid="foo")
        res = XMLValue.from_node(node, "integer")
        assert res == expected

    def test_from_node_formatted_text(self) -> None:
        # test that resrefs are extracted, and that the formatted text is tidied up
        string = """
            <text encoding="xml">
                <a class="salsah-link" href="IRI:test_thing_0:IRI">first link</a>
                This is <em>italicized and <strong>bold</strong></em> text!
                <a class="salsah-link" href="IRI:test_thing_1:IRI">second link</a>
            </text>
        """
        expected_text = " ".join(
            [
                '<a class="salsah-link" href="IRI:test_thing_0:IRI">first link</a>',
                "This is <em>italicized and <strong>bold</strong></em> text!",
                '<a class="salsah-link" href="IRI:test_thing_1:IRI">second link</a>',
            ]
        )
        node = etree.fromstring(string)
        expected = XMLValue(value=FormattedTextValue(expected_text), resrefs={"test_thing_0", "test_thing_1"})
        res = XMLValue.from_node(node, "text")
        assert res == expected

    def test_from_node_unformatted_text(self) -> None:
        # assure that unformatted text is tidied up
        node = etree.fromstring("""<text encoding="utf8"> Poem </text>""")
        expected = XMLValue("Poem")
        res = XMLValue.from_node(node, "text")
        assert res == expected

    def test_from_node_list_value(self) -> None:
        # assure that list node is constructed correctly
        node = etree.fromstring("""<list>second subnode</list>""")
        expected = XMLValue(value="testlist:second subnode")
        res = XMLValue.from_node(node, "list", "testlist")
        assert res == expected


def test_cleanup_unformatted_text() -> None:
    """Test the removal of whitespaces and line breaks in utf8-encoded text values"""
    orig = """<text permissions="open" encoding="utf8" linkUUID="foo">

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
    orig = """<text permissions="open" encoding="xml" linkUUID="foo">
            This is <em>italicized and <strong>bold</strong></em> text!
        </text>"""
    expected = "This is <em>italicized and <strong>bold</strong></em> text!"
    formatted_node = etree.fromstring(orig)
    xml_value = _extract_formatted_text_from_node(formatted_node)
    assert xml_value.xmlstr == expected


def test_cleanup_formatted_text() -> None:
    """Test the removal of whitespaces and line breaks in xml-formatted text values"""
    orig = """

        This is <em>italicized and <strong>bold</strong></em> text!
        It contains <code>monospace text  that   preserves whitespaces and &amp; HTML-escapes</code>.
        The same <pre>is   true   for   preformatted   text</pre>.

        It    contains    multiple    whitespaces	and		tabstops.<br/><br/>
        Line breaks must be done with <code><br/></code> tags.<br/>
        Otherwise they will be removed.<br/><br/>
        
        It contains links to a resource:
        <a class="salsah-link" href="IRI:test_thing_0:IRI">test_thing_0</a>

    """
    expected = (
        "This is <em>italicized and <strong>bold</strong></em> text! "
        "It contains <code>monospace text  that   preserves whitespaces and &amp; HTML-escapes</code>. "
        "The same <pre>is   true   for   preformatted   text</pre>. "
        "It contains multiple whitespaces and tabstops.<br/><br/>"
        "Line breaks must be done with <code><br/></code> tags.<br/>"
        "Otherwise they will be removed.<br/><br/>"
        "It contains links to a resource: "
        '<a class="salsah-link" href="IRI:test_thing_0:IRI">test_thing_0</a>'
    )
    res = _cleanup_formatted_text(orig)
    assert res == expected


if __name__ == "__main__":
    pytest.main([__file__])
