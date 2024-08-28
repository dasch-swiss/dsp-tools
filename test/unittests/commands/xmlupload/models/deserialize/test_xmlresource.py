from lxml import etree
from pytest_unordered import unordered

from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import IIIFUriInfo
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLBitstream
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLProperty
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLValue
from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import XMLResource
from dsp_tools.commands.xmlupload.models.formatted_text_value import FormattedTextValue


def test_get_restype_knora_api() -> None:
    res = XMLResource._get_restype(etree.fromstring("""<resource restype="Region"/>"""), "rosetta")
    assert res == "knora-api:Region"


def test_get_restype_abbreviated() -> None:
    res = XMLResource._get_restype(etree.fromstring("""<resource restype=":TestThing"/>"""), "rosetta")
    assert res == "rosetta:TestThing"


def test_get_restype_full() -> None:
    res = XMLResource._get_restype(etree.fromstring("""<resource restype="rosetta:TestThing"/>"""), "rosetta")
    assert res == "rosetta:TestThing"


def test_get_properties_bitstream_only() -> None:
    string = "<resource><bitstream>testdata/bitstreams/test.tif</bitstream></resource>"
    bitstream_expected = XMLBitstream("testdata/bitstreams/test.tif")
    bitstream, iiif, props = XMLResource._get_properties(etree.fromstring(string), "rosetta")
    assert bitstream == bitstream_expected
    assert not iiif
    assert not props


def test_get_properties_iiif_only() -> None:
    iiif_uri = "https://iiif.dasch.swiss/0811/1Oi7mdiLsG7-FmFgp0xz2xU.jp2/full/837,530/0/default.jp2"
    string = f"<resource><iiif-uri>{iiif_uri}</iiif-uri></resource>"
    iiif_expected = IIIFUriInfo(iiif_uri)
    bitstream, iiif, props = XMLResource._get_properties(etree.fromstring(string), "rosetta")
    assert not bitstream
    assert iiif == iiif_expected
    assert not props


def test_get_properties_of_normal_resource() -> None:
    string = """
        <resource>
            <boolean-prop name=":hasBoolean"><boolean>true</boolean></boolean-prop>
            <color-prop name=":hasColor"><color>#00ff00</color></color-prop>
            <date-prop name=":hasDate"><date>JULIAN:BCE:70:CE:1</date></date-prop>
            <decimal-prop name=":hasDecimal"><decimal>2.718</decimal></decimal-prop>
            <geometry-prop name="hasGeometry"><geometry>{...}</geometry></geometry-prop>
            <geoname-prop name=":hasGeoname"><geoname>5416656</geoname></geoname-prop>
            <integer-prop name=":hasInteger"><integer>4711</integer></integer-prop>
            <list-prop list="testlist" name=":hasListItem"><list>subnode</list></list-prop>
            <resptr-prop name=":hasLink"><resptr>test_thing_0</resptr></resptr-prop>
            <text-prop name=":hasSimpleText"><text encoding="utf8">foo</text></text-prop>
            <time-prop name=":hasTime"><time>2019-10-23T13:45:12.01-14:00</time></time-prop>
            <uri-prop name=":hasUri"><uri>https://dasch.swiss</uri></uri-prop>
        </resource>
    """
    props_expected = [
        XMLProperty("rosetta:hasBoolean", "boolean", [XMLValue("true")]),
        XMLProperty("rosetta:hasColor", "color", [XMLValue("#00ff00")]),
        XMLProperty("rosetta:hasDate", "date", [XMLValue("JULIAN:BCE:70:CE:1")]),
        XMLProperty("rosetta:hasDecimal", "decimal", [XMLValue("2.718")]),
        XMLProperty("knora-api:hasGeometry", "geometry", [XMLValue("{...}")]),
        XMLProperty("rosetta:hasGeoname", "geoname", [XMLValue("5416656")]),
        XMLProperty("rosetta:hasInteger", "integer", [XMLValue("4711")]),
        XMLProperty("rosetta:hasListItem", "list", [XMLValue("testlist:subnode")]),
        XMLProperty("rosetta:hasLink", "resptr", [XMLValue("test_thing_0")]),
        XMLProperty("rosetta:hasSimpleText", "text", [XMLValue("foo")]),
        XMLProperty("rosetta:hasTime", "time", [XMLValue("2019-10-23T13:45:12.01-14:00")]),
        XMLProperty("rosetta:hasUri", "uri", [XMLValue("https://dasch.swiss")]),
    ]
    bitstream, iiif, props = XMLResource._get_properties(etree.fromstring(string), "rosetta")
    assert not bitstream
    assert not iiif
    assert props == unordered(props_expected)


def test_get_properties_of_audio_segment() -> None:
    string = """
        <audio-segment>
            <isSegmentOf>audio_thing_1</isSegmentOf>
            <hasSegmentBounds segment_start="10" segment_end="30"/>
            <hasTitle>Title</hasTitle>
            <hasComment>Comment</hasComment>
            <hasDescription>Description</hasDescription>
            <hasKeyword>Keyword</hasKeyword>
            <relatesTo>video_segment_0</relatesTo>
        </audio-segment>
    """
    props_expected = [
        XMLProperty("knora-api:isSegmentOf", "resptr", [XMLValue("audio_thing_1")]),
        XMLProperty("knora-api:hasSegmentBounds", "interval", [XMLValue("10:30")]),
        XMLProperty("knora-api:hasTitle", "text", [XMLValue("Title")]),
        XMLProperty("knora-api:hasComment", "text", [XMLValue(FormattedTextValue("Comment"))]),
        XMLProperty("knora-api:hasDescription", "text", [XMLValue(FormattedTextValue("Description"))]),
        XMLProperty("knora-api:hasKeyword", "text", [XMLValue("Keyword")]),
        XMLProperty("knora-api:relatesTo", "resptr", [XMLValue("video_segment_0")]),
    ]
    bitstream, iiif, props = XMLResource._get_properties(etree.fromstring(string), "rosetta")
    assert not bitstream
    assert not iiif
    assert props == unordered(props_expected)


def test_group_props() -> None:
    comment_1 = XMLValue(FormattedTextValue("Comment 1"))
    comment_2 = XMLValue(FormattedTextValue("Comment 2"))
    desc_1 = XMLValue(FormattedTextValue("Description 1"))
    desc_2 = XMLValue(FormattedTextValue("Description 2"))
    kw_1 = XMLValue("Keyword 1")
    kw_2 = XMLValue("Keyword 2")
    link_1 = XMLValue("other_res_1")
    link_2 = XMLValue("other_res_2")
    ungrouped = [
        XMLProperty("knora-api:isSegmentOf", "resptr", [XMLValue("audio_thing_1")]),
        XMLProperty("knora-api:hasSegmentBounds", "interval", [XMLValue("10:30")]),
        XMLProperty("knora-api:hasTitle", "text", [XMLValue("Title")]),
        XMLProperty("knora-api:hasComment", "text", [comment_1]),
        XMLProperty("knora-api:hasDescription", "text", [desc_1]),
        XMLProperty("knora-api:hasKeyword", "text", [kw_1]),
        XMLProperty("knora-api:relatesTo", "resptr", [link_1]),
        XMLProperty("knora-api:hasComment", "text", [comment_2]),
        XMLProperty("knora-api:hasDescription", "text", [desc_2]),
        XMLProperty("knora-api:hasKeyword", "text", [kw_2]),
        XMLProperty("knora-api:relatesTo", "resptr", [link_2]),
    ]
    expected = [
        XMLProperty("knora-api:isSegmentOf", "resptr", [XMLValue("audio_thing_1")]),
        XMLProperty("knora-api:hasSegmentBounds", "interval", [XMLValue("10:30")]),
        XMLProperty("knora-api:hasTitle", "text", [XMLValue("Title")]),
        XMLProperty("knora-api:hasComment", "text", [comment_1, comment_2]),
        XMLProperty("knora-api:hasDescription", "text", [desc_1, desc_2]),
        XMLProperty("knora-api:hasKeyword", "text", [kw_1, kw_2]),
        XMLProperty("knora-api:relatesTo", "resptr", [link_1, link_2]),
    ]
    grouped = XMLResource._group_props(ungrouped)
    assert grouped == unordered(expected)


def test_get_props_with_links() -> None:
    link_1 = """<a class="salsah-link" href="IRI:test_thing_3:IRI">link</a>"""
    link_2 = """<a class="salsah-link" href="IRI:test_thing_4:IRI">link</a>"""
    string = f"""
        <resource label="label" id="id" restype=":foo">
            <boolean-prop name=":hasBoolean"><boolean>true</boolean></boolean-prop>
            <resptr-prop name=":hasLink">
                <resptr>test_thing_1</resptr>
            </resptr-prop>
            <resptr-prop name=":hasOtherLink">
                <resptr>test_thing_2</resptr>
            </resptr-prop>
            <text-prop name=":hasText1">
                <text encoding="xml">{link_1}</text>
            </text-prop>
            <text-prop name=":hasText2">
                <text encoding="xml">{link_2}</text>
            </text-prop>
            <uri-prop name=":hasUri"><uri>https://dasch.swiss</uri></uri-prop>
        </resource>
    """
    xml_resource = XMLResource.from_node(etree.fromstring(string), "rosetta")
    expected = [
        XMLProperty("rosetta:hasLink", "resptr", [XMLValue("test_thing_1")]),
        XMLProperty("rosetta:hasOtherLink", "resptr", [XMLValue("test_thing_2")]),
        XMLProperty("rosetta:hasText1", "text", [XMLValue(FormattedTextValue(link_1), resrefs={"test_thing_3"})]),
        XMLProperty("rosetta:hasText2", "text", [XMLValue(FormattedTextValue(link_2), resrefs={"test_thing_4"})]),
    ]
    res = xml_resource.get_props_with_links()
    assert res == unordered(expected)
