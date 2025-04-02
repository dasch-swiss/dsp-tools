# mypy: disable-error-code="method-assign,no-untyped-def"
from copy import deepcopy

import pytest

from dsp_tools.utils.rdflib_constants import KNORA_API_STR
from dsp_tools.utils.xml_parsing.get_parsed_resources import _create_from_local_name_to_absolute_iri_lookup
from dsp_tools.utils.xml_parsing.get_parsed_resources import _get_one_absolute_iri
from dsp_tools.utils.xml_parsing.get_parsed_resources import _parse_file_values
from dsp_tools.utils.xml_parsing.get_parsed_resources import _parse_one_value
from dsp_tools.utils.xml_parsing.models.parsed_resource import KnoraValueType

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


class TestParseResource:
    def test_empty(self, root_no_resources, resource_no_values):
        root = deepcopy(root_no_resources)
        root.append(resource_no_values)

    def test_with_values(self, root_no_resources, resource_with_values):
        root = deepcopy(root_no_resources)
        root.append(resource_with_values)

    def test_file_value(self, root_no_resources, resource_with_file_values):
        root = deepcopy(root_no_resources)
        root.append(resource_with_file_values)

    def test_region(self, root_no_resources, resource_region):
        root = deepcopy(root_no_resources)
        root.append(resource_region)

    def test_link(self, root_no_resources, resource_link):
        root = deepcopy(root_no_resources)
        root.append(resource_link)

    def test_video_segment(self, root_no_resources, resource_video_segment):
        root = deepcopy(root_no_resources)
        root.append(resource_video_segment)

    def test_audio_segment(self, root_no_resources, resource_audio_segment):
        root = deepcopy(root_no_resources)
        root.append(resource_audio_segment)


class TestParseValues:
    def test_boolean_value_with_metadata(self, boolean_value_with_metadata):
        result = _parse_one_value(boolean_value_with_metadata, IRI_LOOKUP)
        assert len(result) == 1
        val = result.pop(0)
        assert val.prop_name == HAS_PROP
        assert val.value == "true"
        assert val.value_type == KnoraValueType.BOOLEAN_VALUE
        assert val.permissions_id == "open"
        assert val.comment == "Comment on Value"

    def test_color_value(self, color_value):
        result = _parse_one_value(color_value, IRI_LOOKUP)
        assert len(result) == 1
        val = result.pop(0)
        assert val.prop_name == HAS_PROP
        assert val.value == "#00ff00"
        assert val.value_type == KnoraValueType.COLOR_VALUE
        assert not val.permissions_id
        assert not val.comment

    def test_color_value_several(self, color_value_several):
        result = _parse_one_value(color_value_several, IRI_LOOKUP)
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

    def test_date_value(self, date_value):
        result = _parse_one_value(date_value, IRI_LOOKUP)
        assert len(result) == 1
        val = result.pop(0)
        assert val.prop_name == HAS_PROP
        assert val.value == "JULIAN:BCE:0700:BCE:0600"
        assert val.value_type == KnoraValueType.DATE_VALUE
        assert not val.permissions_id
        assert not val.comment

    def test_decimal_value(self, decimal_value):
        result = _parse_one_value(decimal_value, IRI_LOOKUP)
        assert len(result) == 1
        val = result.pop(0)
        assert val.prop_name == HAS_PROP
        assert val.value == "2.71"
        assert val.value_type == KnoraValueType.DECIMAL_VALUE
        assert not val.permissions_id
        assert not val.comment

    def test_geometry_value(self, geometry_value):
        result = _parse_one_value(geometry_value, IRI_LOOKUP)
        assert len(result) == 1
        val = result.pop(0)
        assert val.prop_name == HAS_PROP
        assert val.value == "{}"
        assert val.value_type == KnoraValueType.GEOM_VALUE
        assert not val.permissions_id
        assert not val.comment

    def test_geoname_value(self, geoname_value):
        result = _parse_one_value(geoname_value, IRI_LOOKUP)
        assert len(result) == 1
        val = result.pop(0)
        assert val.prop_name == HAS_PROP
        assert val.value == "1111111"
        assert val.value_type == KnoraValueType.GEONAME_VALUE
        assert not val.permissions_id
        assert not val.comment

    def test_integer_value(self, integer_value):
        result = _parse_one_value(integer_value, IRI_LOOKUP)
        assert len(result) == 1
        val = result.pop(0)
        assert val.prop_name == HAS_PROP
        assert val.value == "1"
        assert val.value_type == KnoraValueType.INT_VALUE
        assert not val.permissions_id
        assert not val.comment

    def test_list_value(self, list_value):
        result = _parse_one_value(list_value, IRI_LOOKUP)
        assert len(result) == 1
        val = result.pop(0)
        assert val.prop_name == HAS_PROP
        assert val.value == ("firstList", "n1")
        assert val.value_type == KnoraValueType.LIST_VALUE
        assert not val.permissions_id
        assert not val.comment

    def test_list_value_several(self, list_value_several):
        result = _parse_one_value(list_value_several, IRI_LOOKUP)
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

    def test_resptr_value(self, resptr_value):
        result = _parse_one_value(resptr_value, IRI_LOOKUP)
        assert len(result) == 1
        val = result.pop(0)
        assert val.prop_name == HAS_PROP
        assert val.value == "id_1"
        assert val.value_type == KnoraValueType.LINK_VALUE
        assert not val.permissions_id
        assert not val.comment

    def test_text_richtext_value(self, text_richtext_value):
        result = _parse_one_value(text_richtext_value, IRI_LOOKUP)
        assert len(result) == 1
        val = result.pop(0)
        assert val.prop_name == HAS_PROP
        assert val.value == "<p>Text</p>"
        assert val.value_type == KnoraValueType.RICHTEXT_VALUE
        assert not val.permissions_id
        assert not val.comment

    def test_text_simpletext_value(self, text_simpletext_value):
        result = _parse_one_value(text_simpletext_value, IRI_LOOKUP)
        assert len(result) == 1
        val = result.pop(0)
        assert val.prop_name == HAS_PROP
        assert val.value == "Text"
        assert val.value_type == KnoraValueType.SIMPLETEXT_VALUE
        assert not val.permissions_id
        assert not val.comment

    def test_text_simpletext_value_no_text(self, text_simpletext_value_no_text):
        result = _parse_one_value(text_simpletext_value_no_text, IRI_LOOKUP)
        assert len(result) == 1
        val = result.pop(0)
        assert val.prop_name == HAS_PROP
        assert not val.value
        assert val.value_type == KnoraValueType.SIMPLETEXT_VALUE
        assert not val.permissions_id
        assert not val.comment

    def test_time_value(self, time_value):
        result = _parse_one_value(time_value, IRI_LOOKUP)
        assert len(result) == 1
        val = result.pop(0)
        assert val.prop_name == HAS_PROP
        assert val.value == "2019-10-23T13:45:12.01-14:00"
        assert val.value_type == KnoraValueType.TIME_VALUE
        assert not val.permissions_id
        assert not val.comment

    def test_uri_value(self, uri_value):
        result = _parse_one_value(uri_value, IRI_LOOKUP)
        assert len(result) == 1
        val = result.pop(0)
        assert val.prop_name == HAS_PROP
        assert val.value == "https://dasch.swiss"
        assert val.value_type == KnoraValueType.URI_VALUE
        assert not val.permissions_id
        assert not val.comment


class TestParseFileValues:
    def test_iiif_no_legal_info(self, iiif_no_legal_info):
        val = _parse_file_values(iiif_no_legal_info)
        assert val.value == "https://iiif.uri/full.jpg"
        assert val.value_type == KnoraValueType.STILL_IMAGE_IIIF
        assert not val.metadata.license_iri
        assert not val.metadata.copyright_holder
        assert not val.metadata.authorship_id
        assert not val.metadata.permissions_id

    def test_iiif_with_legal_info(self, iiif_with_legal_info):
        val = _parse_file_values(iiif_with_legal_info)
        assert val.value == "https://iiif.uri/full.jpg"
        assert val.value_type == KnoraValueType.STILL_IMAGE_IIIF
        assert val.metadata.license_iri == "license_iri"
        assert val.metadata.copyright_holder == "copy"
        assert val.metadata.authorship_id == "auth"
        assert not val.metadata.permissions_id

    def test_bitstream_with_permissions(self, bitstream_with_permissions):
        val = _parse_file_values(bitstream_with_permissions)
        assert val.value == "this/is/filepath/file.z"
        assert val.value_type == KnoraValueType.ARCHIVE_FILE
        assert not val.metadata.license_iri
        assert not val.metadata.copyright_holder
        assert not val.metadata.authorship_id
        assert val.metadata.permissions_id == "open"

    def test_bitstream_with_legal_info(self, bitstream_with_legal_info):
        val = _parse_file_values(bitstream_with_legal_info)
        assert val.value == "this/is/filepath/file.z"
        assert val.value_type == KnoraValueType.ARCHIVE_FILE
        assert val.metadata.license_iri == "http://rdfh.ch/licenses/unknown"
        assert val.metadata.copyright_holder == "DaSCH"
        assert val.metadata.authorship_id == "authorship_1"
        assert not val.metadata.permissions_id


def test_create_from_local_name_to_absolute_iri_lookup(minimal_root):
    result = _create_from_local_name_to_absolute_iri_lookup(minimal_root, API_URL)
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
