from lxml import etree
from pytest_unordered import unordered

from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import IIIFUriInfo
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLBitstream
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLProperty
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLValue
from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import XMLResource
from dsp_tools.commands.xmlupload.models.formatted_text_value import FormattedTextValue


class Test_XMLResource:
    def test_from_node(self) -> None:
        pass

    def test_get_restype_knora_base(self) -> None:
        pass

    def test_get_restype_abbreviated(self) -> None:
        pass

    def test_get_restype_full(self) -> None:
        pass

    def test_get_properties_bitstream_only(self) -> None:
        string = "<resource><bitstream>testdata/bitstreams/test.tif</bitstream></resource>"
        bitstream_expected = XMLBitstream("testdata/bitstreams/test.tif")
        bitstream, iiif, props = XMLResource._get_properties(etree.fromstring(string), "rosetta")
        assert bitstream == bitstream_expected
        assert not iiif
        assert not props

    def test_get_properties_iiif_only(self) -> None:
        iiif_uri = "https://iiif.dasch.swiss/0811/1Oi7mdiLsG7-FmFgp0xz2xU.jp2/full/837,530/0/default.jp2"
        string = f"<resource><iiif-uri>{iiif_uri}</iiif-uri></resource>"
        iiif_expected = IIIFUriInfo(iiif_uri)
        bitstream, iiif, props = XMLResource._get_properties(etree.fromstring(string), "rosetta")
        assert not bitstream
        assert iiif == iiif_expected
        assert not props

    def test_get_properties_of_normal_resource(self) -> None:
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

    def test_get_properties_of_audio_segment(self) -> None:
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

    def test_group_props(self) -> None:
        pass

    def test_get_props_with_links(self) -> None:
        pass
