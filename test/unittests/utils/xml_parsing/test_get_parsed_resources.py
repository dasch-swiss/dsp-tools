# mypy: disable-error-code="method-assign,no-untyped-def"
from copy import deepcopy

import pytest
from lxml import etree

from dsp_tools.utils.rdflib_constants import KNORA_API_STR
from dsp_tools.utils.xml_parsing.get_parsed_resources import _convert_api_url_for_correct_iri_namespace
from dsp_tools.utils.xml_parsing.get_parsed_resources import _create_from_local_name_to_absolute_iri_lookup
from dsp_tools.utils.xml_parsing.get_parsed_resources import _get_file_value_type
from dsp_tools.utils.xml_parsing.get_parsed_resources import _get_one_absolute_iri
from dsp_tools.utils.xml_parsing.get_parsed_resources import _parse_file_values
from dsp_tools.utils.xml_parsing.get_parsed_resources import _parse_iiif_uri
from dsp_tools.utils.xml_parsing.get_parsed_resources import _parse_one_value
from dsp_tools.utils.xml_parsing.get_parsed_resources import _parse_segment_values
from dsp_tools.utils.xml_parsing.get_parsed_resources import get_parsed_resources
from dsp_tools.utils.xml_parsing.models.parsed_resource import KnoraValueType
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedFileValue
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedMigrationMetadata

API_URL = "http://url.ch"
DEFAULT_ONTO_NAMESPACE = f"{API_URL}/ontology/0000/default/v2#"

HAS_PROP = f"{DEFAULT_ONTO_NAMESPACE}hasProp"
RES_CLASS = f"{DEFAULT_ONTO_NAMESPACE}Class"

IRI_LOOKUP = {
    ":Class": RES_CLASS,
    ":hasProp": HAS_PROP,
    "hasColor": f"{KNORA_API_STR}hasColor",
    "isRegionOf": f"{KNORA_API_STR}isRegionOf",
    "hasGeometry": f"{KNORA_API_STR}hasGeometry",
    "hasComment": f"{KNORA_API_STR}hasComment",
    "hasLinkTo": f"{KNORA_API_STR}hasLinkTo",
}


@pytest.mark.parametrize(
    ("input_str", "expected"),
    [
        ("https://app.dasch.swiss", "http://app.dasch.swiss"),
        ("http://0.0.0.0:3333", "http://0.0.0.0:3333"),
    ],
)
def test_convert_api_url_for_correct_iri_namespace(input_str, expected):
    assert _convert_api_url_for_correct_iri_namespace(input_str) == expected


class TestParseResource:
    def test_empty(self, root_no_resources, resource_no_values):
        root = deepcopy(root_no_resources)
        root.append(resource_no_values)
        parsed_res, iris = get_parsed_resources(root, API_URL)
        assert iris == {RES_CLASS}
        assert len(parsed_res) == 1
        resource = parsed_res.pop(0)
        assert resource.res_id == "resource_no_values"
        assert resource.res_type == RES_CLASS
        assert resource.label == "lbl"
        assert not resource.permissions_id
        assert len(resource.values) == 0
        assert not resource.file_value
        assert not resource.migration_metadata

    def test_resource_with_migration_data(self, root_no_resources, resource_with_migration_data):
        root = deepcopy(root_no_resources)
        root.append(resource_with_migration_data)
        parsed_res, _ = get_parsed_resources(root, API_URL)
        assert len(parsed_res) == 1
        resource = parsed_res.pop(0)
        assert resource.res_id == "resource_with_migration_data"
        assert resource.res_type == RES_CLASS
        assert resource.label == "lbl"
        assert not resource.permissions_id
        assert len(resource.values) == 0
        assert not resource.file_value
        metadata = resource.migration_metadata
        assert isinstance(metadata, ParsedMigrationMetadata)
        assert metadata.iri == "iri"
        assert metadata.ark == "ark"
        assert metadata.creation_date == "2019-01-09T15:45:54.502951Z"

    def test_with_value(self, root_no_resources, resource_with_value):
        root = deepcopy(root_no_resources)
        root.append(resource_with_value)
        parsed_res, _ = get_parsed_resources(root, API_URL)
        assert len(parsed_res) == 1
        resource = parsed_res.pop(0)
        assert resource.res_id == "resource_with_value"
        assert resource.res_type == RES_CLASS
        assert resource.label == "lbl"
        assert not resource.permissions_id
        assert len(resource.values) == 1
        val = resource.values.pop(0)
        assert val.prop_name == HAS_PROP
        assert val.value == "true"
        assert val.value_type == KnoraValueType.BOOLEAN_VALUE
        assert not val.permissions_id
        assert not val.comment
        assert not resource.file_value
        assert not resource.migration_metadata

    def test_file_value(self, root_no_resources, resource_with_file_value):
        root = deepcopy(root_no_resources)
        root.append(resource_with_file_value)
        parsed_res, _ = get_parsed_resources(root, API_URL)
        assert len(parsed_res) == 1
        resource = parsed_res.pop(0)
        assert resource.res_id == "resource_with_file_value"
        assert resource.res_type == RES_CLASS
        assert resource.label == "lbl"
        assert not resource.permissions_id
        assert len(resource.values) == 0
        assert not resource.migration_metadata
        file_val = resource.file_value
        assert isinstance(file_val, ParsedFileValue)
        assert file_val.value_type == KnoraValueType.AUDIO_FILE
        assert file_val.value == "testdata/bitstreams/test.wav"

    def test_iiif_value(self, root_no_resources, resource_with_iiif):
        root = deepcopy(root_no_resources)
        root.append(resource_with_iiif)
        parsed_res, _ = get_parsed_resources(root, API_URL)
        assert len(parsed_res) == 1
        resource = parsed_res.pop(0)
        assert resource.res_id == "resource_with_iiif"
        assert resource.res_type == RES_CLASS
        assert resource.label == "lbl"
        assert not resource.permissions_id
        assert len(resource.values) == 0
        assert not resource.migration_metadata
        file_val = resource.file_value
        assert isinstance(file_val, ParsedFileValue)
        assert file_val.value_type == KnoraValueType.STILL_IMAGE_IIIF

    def test_region(self, root_no_resources, resource_region):
        root = deepcopy(root_no_resources)
        root.append(resource_region)
        parsed_res, _ = get_parsed_resources(root, API_URL)
        assert len(parsed_res) == 1
        resource = parsed_res.pop(0)
        assert resource.res_id == "resource_region"
        assert resource.res_type == f"{KNORA_API_STR}Region"
        assert resource.label == "lbl"
        assert not resource.permissions_id
        assert len(resource.values) == 4
        assert not resource.file_value
        assert not resource.migration_metadata

    def test_link(self, root_no_resources, resource_link):
        root = deepcopy(root_no_resources)
        root.append(resource_link)
        parsed_res, _ = get_parsed_resources(root, API_URL)
        assert len(parsed_res) == 1
        resource = parsed_res.pop(0)
        assert resource.res_id == "resource_link"
        assert resource.res_type == f"{KNORA_API_STR}LinkObj"
        assert resource.label == "lbl"
        assert not resource.permissions_id
        assert len(resource.values) == 1
        assert not resource.file_value
        assert not resource.migration_metadata


class TestSegment:
    def test_video_segment(self, root_no_resources, resource_video_segment):
        root = deepcopy(root_no_resources)
        root.append(resource_video_segment)
        parsed_res, _ = get_parsed_resources(root, API_URL)
        assert len(parsed_res) == 1
        resource = parsed_res.pop(0)
        assert resource.res_id == "resource_video_segment"
        assert resource.res_type == f"{KNORA_API_STR}VideoSegment"
        assert resource.label == "lbl"
        assert not resource.permissions_id
        assert len(resource.values) == 8
        assert not resource.file_value
        assert not resource.migration_metadata

    def test_audio_segment(self, root_no_resources, resource_audio_segment):
        root = deepcopy(root_no_resources)
        root.append(resource_audio_segment)
        parsed_res, _ = get_parsed_resources(root, API_URL)
        assert len(parsed_res) == 1
        resource = parsed_res.pop(0)
        assert resource.res_id == "resource_audio_segment"
        assert resource.res_type == f"{KNORA_API_STR}AudioSegment"
        assert resource.label == "lbl"
        assert not resource.permissions_id
        assert len(resource.values) == 8
        assert not resource.file_value
        assert not resource.migration_metadata

    def test_parse_segment_values(self, resource_audio_segment):
        values = _parse_segment_values(resource_audio_segment, "Audio")
        expected = [
            (f"{KNORA_API_STR}isAudioSegmentOf", KnoraValueType.LINK_VALUE, "target", None, None),
            (f"{KNORA_API_STR}hasSegmentBounds", KnoraValueType.INTERVAL_VALUE, ("0.1", "0.234"), "open", None),
            (f"{KNORA_API_STR}hasTitle", KnoraValueType.SIMPLETEXT_VALUE, "Title", None, "Cmt"),
            (f"{KNORA_API_STR}hasComment", KnoraValueType.RICHTEXT_VALUE, "<p>Comment</p>", None, None),
            (f"{KNORA_API_STR}hasDescription", KnoraValueType.RICHTEXT_VALUE, "<p>Description 1</p>", None, None),
            (f"{KNORA_API_STR}hasDescription", KnoraValueType.RICHTEXT_VALUE, "Description 2", None, None),
            (f"{KNORA_API_STR}hasKeyword", KnoraValueType.SIMPLETEXT_VALUE, "Keyword", None, None),
            (f"{KNORA_API_STR}relatesTo", KnoraValueType.LINK_VALUE, "relates_to_id", None, None),
        ]
        for result, (prop, value_type, content, perm, cmt) in zip(values, expected):
            assert result.prop_name == prop
            assert result.value == content
            assert result.value_type == value_type
            assert result.permissions_id == perm
            assert result.comment == cmt


class TestParseValues:
    def test_boolean_value_with_metadata(self):
        xml_val = etree.fromstring("""
        <boolean-prop name=":hasProp">
            <boolean permissions="open" comment="Comment on Value">true</boolean>
        </boolean-prop>
        """)
        result = _parse_one_value(xml_val, IRI_LOOKUP)
        assert len(result) == 1
        val = result.pop(0)
        assert val.prop_name == HAS_PROP
        assert val.value == "true"
        assert val.value_type == KnoraValueType.BOOLEAN_VALUE
        assert val.permissions_id == "open"
        assert val.comment == "Comment on Value"

    def test_color_value(self):
        xml_val = etree.fromstring("""
        <color-prop name=":hasProp">
            <color>#00ff00</color>
        </color-prop>
        """)
        result = _parse_one_value(xml_val, IRI_LOOKUP)
        assert len(result) == 1
        val = result.pop(0)
        assert val.prop_name == HAS_PROP
        assert val.value == "#00ff00"
        assert val.value_type == KnoraValueType.COLOR_VALUE
        assert not val.permissions_id
        assert not val.comment

    def test_color_value_several(self):
        xml_val = etree.fromstring("""
        <color-prop name=":hasProp">
            <color>#00ff00</color>
            <color>#00ff11</color>
        </color-prop>
        """)
        result = _parse_one_value(xml_val, IRI_LOOKUP)
        assert len(result) == 2
        val1 = result[0]
        assert val1.prop_name == HAS_PROP
        assert val1.value == "#00ff00"
        assert val1.value_type == KnoraValueType.COLOR_VALUE
        assert not val1.permissions_id
        assert not val1.comment
        val2 = result[1]
        assert val2.prop_name == HAS_PROP
        assert val2.value == "#00ff11"
        assert val2.value_type == KnoraValueType.COLOR_VALUE
        assert not val2.permissions_id
        assert not val2.comment

    def test_date_value(self):
        xml_val = etree.fromstring("""
        <date-prop name=":hasProp">
            <date>JULIAN:BCE:0700:BCE:0600</date>
        </date-prop>
        """)
        result = _parse_one_value(xml_val, IRI_LOOKUP)
        assert len(result) == 1
        val = result.pop(0)
        assert val.prop_name == HAS_PROP
        assert val.value == "JULIAN:BCE:0700:BCE:0600"
        assert val.value_type == KnoraValueType.DATE_VALUE
        assert not val.permissions_id
        assert not val.comment

    def test_decimal_value(self):
        xml_val = etree.fromstring("""
        <decimal-prop name=":hasProp">
            <decimal>2.71</decimal>
        </decimal-prop>
        """)
        result = _parse_one_value(xml_val, IRI_LOOKUP)
        assert len(result) == 1
        val = result.pop(0)
        assert val.prop_name == HAS_PROP
        assert val.value == "2.71"
        assert val.value_type == KnoraValueType.DECIMAL_VALUE
        assert not val.permissions_id
        assert not val.comment

    def test_geometry_value(self):
        xml_val = etree.fromstring("""
        <geometry-prop name="hasGeometry">
            <geometry>{}</geometry>
        </geometry-prop>
        """)
        result = _parse_one_value(xml_val, IRI_LOOKUP)
        assert len(result) == 1
        val = result.pop(0)
        assert val.prop_name == f"{KNORA_API_STR}hasGeometry"
        assert val.value == "{}"
        assert val.value_type == KnoraValueType.GEOM_VALUE
        assert not val.permissions_id
        assert not val.comment

    def test_geoname_value(self):
        xml_val = etree.fromstring("""
        <geoname-prop name=":hasProp">
            <geoname>1111111 </geoname>
        </geoname-prop>
        """)
        result = _parse_one_value(xml_val, IRI_LOOKUP)
        assert len(result) == 1
        val = result.pop(0)
        assert val.prop_name == HAS_PROP
        assert val.value == "1111111"
        assert val.value_type == KnoraValueType.GEONAME_VALUE
        assert not val.permissions_id
        assert not val.comment

    def test_integer_value(self):
        xml_val = etree.fromstring("""
        <integer-prop name=":hasProp">
            <integer>1</integer>
        </integer-prop>
        """)
        result = _parse_one_value(xml_val, IRI_LOOKUP)
        assert len(result) == 1
        val = result.pop(0)
        assert val.prop_name == HAS_PROP
        assert val.value == "1"
        assert val.value_type == KnoraValueType.INT_VALUE
        assert not val.permissions_id
        assert not val.comment

    def test_list_value(self):
        xml_val = etree.fromstring("""
        <list-prop list="firstList" name=":hasProp">
            <list>n1 </list>
        </list-prop>
        """)
        result = _parse_one_value(xml_val, IRI_LOOKUP)
        assert len(result) == 1
        val = result.pop(0)
        assert val.prop_name == HAS_PROP
        assert val.value == ("firstList", "n1")
        assert val.value_type == KnoraValueType.LIST_VALUE
        assert not val.permissions_id
        assert not val.comment

    def test_list_value_none(self):
        xml_val = etree.fromstring("""
        <list-prop list="firstList" name=":hasProp">
            <list></list>
        </list-prop>
        """)
        result = _parse_one_value(xml_val, IRI_LOOKUP)
        assert len(result) == 1
        val = result.pop(0)
        assert val.prop_name == HAS_PROP
        assert val.value == ("firstList", None)
        assert val.value_type == KnoraValueType.LIST_VALUE
        assert not val.permissions_id
        assert not val.comment

    def test_list_value_several(self):
        xml_val = etree.fromstring("""
        <list-prop list="firstList" name=":hasProp">
            <list>n1</list>
            <list>n2</list>
        </list-prop>
        """)
        result = _parse_one_value(xml_val, IRI_LOOKUP)
        assert len(result) == 2
        val1 = result[0]
        assert val1.prop_name == HAS_PROP
        assert val1.value == ("firstList", "n1")
        assert val1.value_type == KnoraValueType.LIST_VALUE
        assert not val1.permissions_id
        assert not val1.comment
        val2 = result[1]
        assert val2.prop_name == HAS_PROP
        assert val2.value == ("firstList", "n2")
        assert val2.value_type == KnoraValueType.LIST_VALUE
        assert not val2.permissions_id
        assert not val2.comment

    def test_resptr_value(self):
        xml_val = etree.fromstring("""
        <resptr-prop name=":hasProp">
            <resptr>id_1</resptr>
        </resptr-prop>
        """)
        result = _parse_one_value(xml_val, IRI_LOOKUP)
        assert len(result) == 1
        val = result.pop(0)
        assert val.prop_name == HAS_PROP
        assert val.value == "id_1"
        assert val.value_type == KnoraValueType.LINK_VALUE
        assert not val.permissions_id
        assert not val.comment

    def test_resptr_value_none(self):
        xml_val = etree.fromstring("""
        <resptr-prop name=":hasProp">
            <resptr></resptr>
        </resptr-prop>
        """)
        result = _parse_one_value(xml_val, IRI_LOOKUP)
        assert len(result) == 1
        val = result.pop(0)
        assert val.prop_name == HAS_PROP
        assert val.value == None  # noqa: E711 Comparison to `None`
        assert val.value_type == KnoraValueType.LINK_VALUE
        assert not val.permissions_id
        assert not val.comment

    def test_text_richtext_value(self):
        xml_val = etree.fromstring("""
        <text-prop name=":hasProp">
            <text encoding="xml"><p>Text</p></text>
        </text-prop>
        """)
        result = _parse_one_value(xml_val, IRI_LOOKUP)
        assert len(result) == 1
        val = result.pop(0)
        assert val.prop_name == HAS_PROP
        assert val.value == "<p>Text</p>"
        assert val.value_type == KnoraValueType.RICHTEXT_VALUE
        assert not val.permissions_id
        assert not val.comment

    def test_text_richtext_value_none(self):
        xml_val = etree.fromstring("""
        <text-prop name=":hasProp">
            <text encoding="xml"></text>
        </text-prop>
        """)
        result = _parse_one_value(xml_val, IRI_LOOKUP)
        assert len(result) == 1
        val = result.pop(0)
        assert val.prop_name == HAS_PROP
        assert val.value == None  # noqa: E711 Comparison to `None`
        assert val.value_type == KnoraValueType.RICHTEXT_VALUE
        assert not val.permissions_id
        assert not val.comment

    def test_text_richtext_escaped_characters(self):
        xml_val = etree.fromstring("""
        <text-prop name=":hasProp">
            <text encoding="xml">&amp;</text>
        </text-prop>
        """)
        result = _parse_one_value(xml_val, IRI_LOOKUP)
        assert len(result) == 1
        val = result.pop(0)
        assert val.prop_name == HAS_PROP
        assert val.value == "&amp;"
        assert val.value_type == KnoraValueType.RICHTEXT_VALUE
        assert not val.permissions_id
        assert not val.comment

    def test_text_simpletext_value(self):
        xml_val = etree.fromstring("""
        <text-prop name=":hasProp">
            <text encoding="utf8"> Text</text>
        </text-prop>
        """)
        result = _parse_one_value(xml_val, IRI_LOOKUP)
        assert len(result) == 1
        val = result.pop(0)
        assert val.prop_name == HAS_PROP
        assert val.value == "Text"
        assert val.value_type == KnoraValueType.SIMPLETEXT_VALUE
        assert not val.permissions_id
        assert not val.comment

    def test_text_simpletext_not_tags_but_angular_brackets(self):
        # It is permissible for simpletext to contain angular brackets,
        # even though they will not be displayed as XML on the app.
        # lxml will see them as XMl and we must ensure that they are parsed correctly.
        xml_val = etree.fromstring("""
        <text-prop name=":hasProp">
            <text encoding="utf8"><notARecognisedTag>Text</notARecognisedTag></text>
        </text-prop>
        """)
        result = _parse_one_value(xml_val, IRI_LOOKUP)
        assert len(result) == 1
        val = result.pop(0)
        assert val.prop_name == HAS_PROP
        assert val.value == "<notARecognisedTag>Text</notARecognisedTag>"
        assert val.value_type == KnoraValueType.SIMPLETEXT_VALUE
        assert not val.permissions_id
        assert not val.comment

    def test_text_simpletext_value_no_text(self):
        xml_val = etree.fromstring("""
        <text-prop name=":hasProp">
            <text encoding="utf8"></text>
        </text-prop>
        """)
        result = _parse_one_value(xml_val, IRI_LOOKUP)
        assert len(result) == 1
        val = result.pop(0)
        assert val.prop_name == HAS_PROP
        assert not val.value
        assert val.value_type == KnoraValueType.SIMPLETEXT_VALUE
        assert not val.permissions_id
        assert not val.comment

    def test_time_value(self):
        xml_val = etree.fromstring("""
        <time-prop name=":hasProp">
            <time>2019-10-23T13:45:12.01-14:00</time>
        </time-prop>
        """)
        result = _parse_one_value(xml_val, IRI_LOOKUP)
        assert len(result) == 1
        val = result.pop(0)
        assert val.prop_name == HAS_PROP
        assert val.value == "2019-10-23T13:45:12.01-14:00"
        assert val.value_type == KnoraValueType.TIME_VALUE
        assert not val.permissions_id
        assert not val.comment

    def test_uri_value(self):
        xml_val = etree.fromstring("""
        <uri-prop name=":hasProp">
            <uri>https://dasch.swiss</uri>
        </uri-prop>
        """)
        result = _parse_one_value(xml_val, IRI_LOOKUP)
        assert len(result) == 1
        val = result.pop(0)
        assert val.prop_name == HAS_PROP
        assert val.value == "https://dasch.swiss"
        assert val.value_type == KnoraValueType.URI_VALUE
        assert not val.permissions_id
        assert not val.comment


class TestParseFileValues:
    def test_iiif_no_legal_info(self):
        xml_val = etree.fromstring("""
        <iiif-uri>
            https://iiif.uri/full.jpg
        </iiif-uri>
        """)
        val = _parse_iiif_uri(xml_val)
        assert val.value == "https://iiif.uri/full.jpg"
        assert val.value_type == KnoraValueType.STILL_IMAGE_IIIF
        assert not val.metadata.license_iri
        assert not val.metadata.copyright_holder
        assert not val.metadata.authorship_id
        assert not val.metadata.permissions_id

    def test_iiif_with_legal_info_and_whitespaces(self):
        xml_val = etree.fromstring("""
        <iiif-uri license="license_iri"
                  copyright-holder="copy"
                  authorship-id="auth"
        >
        https://iiif.uri/full.jpg
        </iiif-uri>
        """)
        val = _parse_iiif_uri(xml_val)
        assert val.value == "https://iiif.uri/full.jpg"
        assert val.value_type == KnoraValueType.STILL_IMAGE_IIIF
        assert val.metadata.license_iri == "license_iri"
        assert val.metadata.copyright_holder == "copy"
        assert val.metadata.authorship_id == "auth"
        assert not val.metadata.permissions_id

    def test_bitstream_with_permissions_and_whitespaces(self):
        xml_val = etree.fromstring("""
        <bitstream permissions="open">
            this/is/filepath/file.z
        </bitstream>
        """)
        val = _parse_file_values(xml_val)
        assert val.value == "this/is/filepath/file.z"
        assert val.value_type == KnoraValueType.ARCHIVE_FILE
        assert not val.metadata.license_iri
        assert not val.metadata.copyright_holder
        assert not val.metadata.authorship_id
        assert val.metadata.permissions_id == "open"

    def test_bitstream_with_legal_info_and_whitespaces(self):
        xml_val = etree.fromstring("""
        <bitstream license="http://rdfh.ch/licenses/unknown"
                   copyright-holder="DaSCH"
                   authorship-id="authorship_1"
        >
            this/is/filepath/file.z
        </bitstream>
        """)
        val = _parse_file_values(xml_val)
        assert val.value == "this/is/filepath/file.z"
        assert val.value_type == KnoraValueType.ARCHIVE_FILE
        assert val.metadata.license_iri == "http://rdfh.ch/licenses/unknown"
        assert val.metadata.copyright_holder == "DaSCH"
        assert val.metadata.authorship_id == "authorship_1"
        assert not val.metadata.permissions_id


class TestFileTypeInfo:
    @pytest.mark.parametrize(
        "file_name", ["test.zip", "test.tar", "test.gz", "test.z", "test.tgz", "test.gzip", "test.7z"]
    )
    def test_archive(self, file_name: str):
        assert _get_file_value_type(file_name) == KnoraValueType.ARCHIVE_FILE

    @pytest.mark.parametrize("file_name", ["test.mp3", "test.wav"])
    def test_audio(self, file_name: str):
        assert _get_file_value_type(file_name) == KnoraValueType.AUDIO_FILE

    @pytest.mark.parametrize(
        "file_name", ["test.pdf", "test.DOC", "test.docx", "test.xls", "test.xlsx", "test.ppt", "test.pptx"]
    )
    def test_document(self, file_name: str):
        assert _get_file_value_type(file_name) == KnoraValueType.DOCUMENT_FILE

    def test_moving_image(self):
        assert _get_file_value_type("test.mp4") == KnoraValueType.MOVING_IMAGE_FILE

    @pytest.mark.parametrize(
        "file_name", ["test.jpg", "test.jpeg", "path/test.jp2", "test.png", "test.tif", "test.tiff", "test.jpx"]
    )
    def test_still_image(self, file_name: str):
        assert _get_file_value_type(file_name) == KnoraValueType.STILL_IMAGE_FILE

    @pytest.mark.parametrize(
        "file_name",
        ["path/test.odd", "test.rng", "test.txt", "test.xml", "test.xsd", "test.xsl", "test.csv", "test.json"],
    )
    def test_text(self, file_name: str):
        assert _get_file_value_type(file_name) == KnoraValueType.TEXT_FILE

    def test_unknown(self):
        assert not _get_file_value_type("file.unknown")

    def test_none(self):
        assert not _get_file_value_type(None)


def test_create_from_local_name_to_absolute_iri_lookup(root_with_2_resources):
    result = _create_from_local_name_to_absolute_iri_lookup(root_with_2_resources, API_URL)
    expected = {
        ":minimalResource": f"{DEFAULT_ONTO_NAMESPACE}minimalResource",
        "hasLinkTo": f"{KNORA_API_STR}hasLinkTo",
    }
    assert result == expected


@pytest.mark.parametrize(
    ("local_name", "expected"),
    [
        (":defaultOnto", f"{DEFAULT_ONTO_NAMESPACE}defaultOnto"),
        ("knora-api:localName", f"{KNORA_API_STR}localName"),
        ("knoraApiNoPrefix", f"{KNORA_API_STR}knoraApiNoPrefix"),
        ("other-onto:localName", f"{API_URL}/ontology/0000/other-onto/v2#localName"),
        ("default:withDefaultOnto", f"{DEFAULT_ONTO_NAMESPACE}withDefaultOnto"),
    ],
)
def test_get_one_absolute_iri(local_name, expected):
    result = _get_one_absolute_iri(local_name, "0000", "default", API_URL)
    assert result == expected
