import pytest
from lxml import etree
from pytest_unordered import unordered

from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLValue
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import _cleanup_formatted_text
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import _cleanup_unformatted_text
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import _extract_formatted_text_from_node
from dsp_tools.commands.xmlupload.models.formatted_text_value import FormattedTextValue


class Test_XMLProperty:
    def test_from_node_normal_prop(self) -> None:
        pass

    def test_from_node_knora_base_prop(self) -> None:
        pass

    def test_get_name_special_tag(self) -> None:
        pass

    def test_get_name_knora_base_prop_with_normal_tag(self) -> None:
        pass

    def test_get_name_normal_tag(self) -> None:
        pass

    def test_get_values_from_normal_props_list(self) -> None:
        pass

    def test_get_values_from_normal_props_geoname(self) -> None:
        pass

    def test_get_values_from_normal_props_invalid(self) -> None:
        pass

    def test_get_value_from_knora_base_prop_with_all_attributes(self) -> None:
        pass

    def test_get_value_from_knora_base_prop_hasSegmentBounds(self) -> None:
        pass

    def test_get_value_from_knora_base_prop_hasDescription_hasComment(self) -> None:
        pass

    def test_get_value_from_knora_base_prop_hasTitle(self) -> None:
        pass


class Test_XMLValue:
    def test_from_node_integer_value(self) -> None:
        # test content, and these attributes: comments, permissions, and linkUUID (if existing)
        node = etree.fromstring("""<integer permissions="prop-default" comment="cmt" linkUUID="foo">99</integer>""")
        value = XMLValue.from_node(node, "integer")
        assert value.value == "99"
        assert value.resrefs is None
        assert value.comment == "cmt"
        assert value.permissions == "prop-default"
        assert value.link_uuid == "foo"

    def test_from_node_formatted_text(self) -> None:
        # test that resrefs are extracted, and that the formatted text is tidied up
        string = """
            <text encoding="xml">
                <a class="salsah-link" href="IRI:test_thing_0:IRI">first link</a>
                This is <em>italicized and <strong>bold</strong></em> text!
                <a class="salsah-link" href="IRI:test_thing_1:IRI">second link</a>
            </text>
        """
        expected = " ".join(
            [
                '<a class="salsah-link" href="IRI:test_thing_0:IRI">first link</a>',
                "This is <em>italicized and <strong>bold</strong></em> text!",
                '<a class="salsah-link" href="IRI:test_thing_1:IRI">second link</a>',
            ]
        )
        node = etree.fromstring(string)
        value = XMLValue.from_node(node, "text")
        assert isinstance(value.value, FormattedTextValue)
        assert value.value.xmlstr == expected
        assert value.resrefs == unordered(["test_thing_0", "test_thing_1"])
        assert value.comment is None
        assert value.permissions is None
        assert value.link_uuid is None

    def test_from_node_unformatted_text(self) -> None:
        # assure that unformatted text is tidied up
        node = etree.fromstring("""<text encoding="utf8"> Poem </text>""")
        value = XMLValue.from_node(node, "text")
        assert value.value == "Poem"
        assert value.resrefs is None
        assert value.comment is None
        assert value.permissions is None
        assert value.link_uuid is None

    def test_from_node_list_value(self) -> None:
        # assure that list node is constructed correctly
        node = etree.fromstring("""<list>second subnode</list>""")
        value = XMLValue.from_node(node, "list", "testlist")
        assert value.value == "testlist:second subnode"
        assert value.resrefs is None
        assert value.comment is None
        assert value.permissions is None
        assert value.link_uuid is None


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
    orig = """<text permissions="prop-default" encoding="xml" linkUUID="foo">
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
