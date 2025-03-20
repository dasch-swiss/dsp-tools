import pytest
from lxml import etree

from dsp_tools.commands.validate_data.constants import KNORA_API_STR
from dsp_tools.utils.xml_parsing.get_data_deserialised import _deserialise_all_resources
from dsp_tools.utils.xml_parsing.get_data_deserialised import _deserialise_one_property
from dsp_tools.utils.xml_parsing.get_data_deserialised import _deserialise_one_resource
from dsp_tools.utils.xml_parsing.get_data_deserialised import _extract_metadata
from dsp_tools.utils.xml_parsing.get_data_deserialised import _get_text_as_string
from dsp_tools.utils.xml_parsing.models.data_deserialised import KnoraValueType
from dsp_tools.utils.xml_parsing.models.data_deserialised import PropertyObject
from dsp_tools.utils.xml_parsing.models.data_deserialised import ResourceDeserialised
from dsp_tools.utils.xml_parsing.models.data_deserialised import TripleObjectType
from dsp_tools.utils.xml_parsing.models.data_deserialised import TriplePropertyType
from dsp_tools.utils.xml_parsing.models.data_deserialised import ValueInformation


def _get_label_and_type(resource: ResourceDeserialised) -> tuple[PropertyObject, PropertyObject, list[PropertyObject]]:
    lbl = next(x for x in resource.property_objects if x.property_type == TriplePropertyType.RDFS_LABEL)
    rdf_type = next(x for x in resource.property_objects if x.property_type == TriplePropertyType.RDF_TYPE)
    permissions = list(x for x in resource.property_objects if x.property_type == TriplePropertyType.KNORA_PERMISSIONS)
    return lbl, rdf_type, permissions


class TestResource:
    def test_empty(self, resource_empty: etree._Element) -> None:
        res = _deserialise_one_resource(resource_empty)
        assert res.res_id == "one"
        assert len(res.property_objects) == 2
        assert not res.asset_value
        lbl, rdf_type, _ = _get_label_and_type(res)
        assert lbl.object_value == "lbl"
        assert lbl.object_type == TripleObjectType.STRING
        assert rdf_type.object_value == "http://0.0.0.0:3333/ontology/9999/onto/v2#ClassWithEverything"
        assert rdf_type.object_type == TripleObjectType.IRI
        assert len(res.values) == 0

    def test_migration_metadata(self, resource_with_migration_metadata: etree._Element) -> None:
        res = _deserialise_one_resource(resource_with_migration_metadata)
        assert res.res_id == "one"
        assert len(res.property_objects) == 2
        assert not res.asset_value
        lbl, rdf_type, _ = _get_label_and_type(res)
        assert lbl.object_value == "lbl"
        assert lbl.object_type == TripleObjectType.STRING
        assert rdf_type.object_value == "http://0.0.0.0:3333/ontology/9999/onto/v2#ClassWithEverything"
        assert rdf_type.object_type == TripleObjectType.IRI
        assert len(res.values) == 0
        assert res.migration_metadata.any()
        assert res.migration_metadata.ark == "ark"
        assert res.migration_metadata.iri == "iri"
        assert str(res.migration_metadata.creation_date) == "2019-01-09T15:45:54.502951Z"

    def test_empty_permissions(self, resource_empty_permissions: etree._Element) -> None:
        res = _deserialise_one_resource(resource_empty_permissions)
        assert res.res_id == "one"
        assert len(res.property_objects) == 3
        assert not res.asset_value
        lbl, rdf_type, perm = _get_label_and_type(res)
        assert len(perm) == 1
        permission = perm.pop(0)
        assert permission.object_value == "open"
        assert permission.object_type == TripleObjectType.STRING
        assert permission.property_type == TriplePropertyType.KNORA_PERMISSIONS
        assert lbl.object_value == "lbl"
        assert lbl.object_type == TripleObjectType.STRING
        assert rdf_type.object_value == "http://0.0.0.0:3333/ontology/9999/onto/v2#ClassWithEverything"
        assert rdf_type.object_type == TripleObjectType.IRI
        assert len(res.values) == 0
        assert not res.migration_metadata.any()

    def test_with_props(self, root_resource_with_props: etree._Element) -> None:
        res_list = _deserialise_all_resources(root_resource_with_props).resources
        assert len(res_list) == 1
        res = res_list[0]
        assert res.res_id == "one"
        assert len(res.property_objects) == 2
        assert not res.asset_value
        lbl, rdf_type, _ = _get_label_and_type(res)
        assert lbl.object_value == "lbl"
        assert lbl.object_type == TripleObjectType.STRING
        assert rdf_type.object_value == "http://0.0.0.0:3333/ontology/9999/onto/v2#ClassWithEverything"
        assert rdf_type.object_type == TripleObjectType.IRI
        assert len(res.values) == 3
        assert not res.migration_metadata.any()

    def test_with_bitstream(self, resource_with_bitstream: etree._Element) -> None:
        result = _deserialise_one_resource(resource_with_bitstream)
        assert len(result.values) == 0
        bitstream = result.asset_value
        assert isinstance(bitstream, ValueInformation)
        assert bitstream.user_facing_prop == f"{KNORA_API_STR}hasAudioFileValue"
        assert bitstream.user_facing_value == "testdata/bitstreams/test.wav"
        assert bitstream.knora_type == KnoraValueType.AUDIO_FILE
        assert not bitstream.value_metadata
        assert not result.migration_metadata.any()

    def test_region(self, root_resource_region: etree._Element) -> None:
        res_list = _deserialise_all_resources(root_resource_region).resources
        res = res_list[0]
        assert res.res_id == "region_1"
        assert len(res.property_objects) == 2
        assert not res.asset_value
        lbl, rdf_type, _ = _get_label_and_type(res)
        assert lbl.object_value == "Region"
        assert lbl.object_type == TripleObjectType.STRING
        assert rdf_type.object_value == "http://api.knora.org/ontology/knora-api/v2#Region"
        assert rdf_type.object_type == TripleObjectType.IRI
        assert len(res.values) == 4
        expected_props = {
            f"{KNORA_API_STR}hasColor",
            f"{KNORA_API_STR}isRegionOf",
            f"{KNORA_API_STR}hasGeometry",
            f"{KNORA_API_STR}hasComment",
        }
        actual_props = {x.user_facing_prop for x in res.values}
        assert actual_props == expected_props
        assert not res.migration_metadata.any()

    def test_audio_segment(self, audio_segment: etree._Element) -> None:
        res = _deserialise_one_resource(audio_segment)
        assert res.res_id == "audio_id"
        assert len(res.property_objects) == 2
        assert not res.asset_value
        lbl, rdf_type, _ = _get_label_and_type(res)
        assert lbl.object_value == "lbl"
        assert lbl.object_type == TripleObjectType.STRING
        assert rdf_type.object_value == "http://api.knora.org/ontology/knora-api/v2#AudioSegment"
        assert rdf_type.object_type == TripleObjectType.IRI
        assert len(res.values) == 2
        propname_to_info = {x.user_facing_prop: x for x in res.values}
        segment_of = propname_to_info.pop(f"{KNORA_API_STR}isAudioSegmentOf")
        assert segment_of.user_facing_value == "is_segment_of_id"
        assert segment_of.knora_type == KnoraValueType.LINK_VALUE
        assert len(segment_of.value_metadata) == 1
        assert segment_of.value_metadata[0].property_type == TriplePropertyType.KNORA_COMMENT_ON_VALUE
        assert segment_of.value_metadata[0].object_value == "Comment"
        assert segment_of.value_metadata[0].object_type == TripleObjectType.STRING
        segment_bounds = propname_to_info.pop(f"{KNORA_API_STR}hasSegmentBounds")
        assert not segment_bounds.user_facing_value
        assert segment_bounds.knora_type == KnoraValueType.INTERVAL_VALUE
        assert len(segment_bounds.value_metadata) == 3
        seg_bounds_prop_objects = {x.property_type: x for x in segment_bounds.value_metadata}
        permission = seg_bounds_prop_objects.pop(TriplePropertyType.KNORA_PERMISSIONS)
        assert permission.object_value == "open"
        assert permission.object_type == TripleObjectType.STRING
        start_bound = seg_bounds_prop_objects.pop(TriplePropertyType.KNORA_INTERVAL_START)
        assert start_bound.object_value == "0.5"
        assert start_bound.object_type == TripleObjectType.DECIMAL
        end_bound = seg_bounds_prop_objects.pop(TriplePropertyType.KNORA_INTERVAL_END)
        assert end_bound.object_value == "7"
        assert end_bound.object_type == TripleObjectType.DECIMAL
        assert not res.migration_metadata.any()

    def test_video_segment(self, video_segment: etree._Element) -> None:
        res = _deserialise_one_resource(video_segment)
        assert res.res_id == "video_id"
        assert len(res.property_objects) == 2
        assert not res.asset_value
        lbl, rdf_type, _ = _get_label_and_type(res)
        assert lbl.object_value == "lbl"
        assert lbl.object_type == TripleObjectType.STRING
        assert rdf_type.object_value == "http://api.knora.org/ontology/knora-api/v2#VideoSegment"
        assert rdf_type.object_type == TripleObjectType.IRI
        assert len(res.values) == 7
        propname_to_info = {x.user_facing_prop: x for x in res.values}
        segment_bounds = propname_to_info.pop(f"{KNORA_API_STR}hasSegmentBounds")
        assert not segment_bounds.user_facing_value
        assert segment_bounds.knora_type == KnoraValueType.INTERVAL_VALUE
        assert len(segment_bounds.value_metadata) == 2
        seg_bounds_prop_objects = {x.property_type: x for x in segment_bounds.value_metadata}
        start_bound = seg_bounds_prop_objects.pop(TriplePropertyType.KNORA_INTERVAL_START)
        assert start_bound.object_value == "0.1"
        assert start_bound.object_type == TripleObjectType.DECIMAL
        end_bound = seg_bounds_prop_objects.pop(TriplePropertyType.KNORA_INTERVAL_END)
        assert end_bound.object_value == "0.234"
        assert end_bound.object_type == TripleObjectType.DECIMAL

        other_props = {
            f"{KNORA_API_STR}isVideoSegmentOf": ("is_segment_of_id", KnoraValueType.LINK_VALUE),
            f"{KNORA_API_STR}hasTitle": ("Title", KnoraValueType.SIMPLETEXT_VALUE),
            f"{KNORA_API_STR}hasComment": ("Comment", KnoraValueType.RICHTEXT_VALUE),
            f"{KNORA_API_STR}hasKeyword": ("Keyword", KnoraValueType.SIMPLETEXT_VALUE),
            f"{KNORA_API_STR}relatesTo": ("relates_to_id", KnoraValueType.LINK_VALUE),
            f"{KNORA_API_STR}hasDescription": ("Description", KnoraValueType.RICHTEXT_VALUE),
        }
        for prop_name, value_info in propname_to_info.items():
            expected = other_props[prop_name]
            assert value_info.user_facing_value == expected[0]
            assert value_info.knora_type == expected[1]
            assert len(value_info.value_metadata) == 0
        assert not res.migration_metadata.any()


class TestBooleanValue:
    def test_corr(self, boolean_value_corr: etree._Element) -> None:
        res_list = _deserialise_one_property(boolean_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert res.user_facing_prop == "http://0.0.0.0:3333/ontology/9999/onto/v2#testBoolean"
        assert res.user_facing_value == "true"
        assert res.knora_type == KnoraValueType.BOOLEAN_VALUE
        assert not res.value_metadata


class TestColorValue:
    def test_corr(self, color_value_corr: etree._Element) -> None:
        res_list = _deserialise_one_property(color_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert res.user_facing_prop == "http://0.0.0.0:3333/ontology/9999/onto/v2#testColor"
        assert res.user_facing_value == "#00ff00"
        assert res.knora_type == KnoraValueType.COLOR_VALUE
        assert not res.value_metadata

    def test_several(self, color_value_corr_several: etree._Element) -> None:
        res = _deserialise_one_property(color_value_corr_several)
        assert len(res) == 2
        assert res[0].user_facing_prop == "http://0.0.0.0:3333/ontology/9999/onto/v2#testColor"
        assert res[0].user_facing_value == "#00ff00"
        assert res[1].user_facing_value == "#00ff11"
        assert res[0].knora_type == KnoraValueType.COLOR_VALUE
        assert res[1].knora_type == KnoraValueType.COLOR_VALUE


class TestDateValue:
    def test_corr(self, date_value_corr: etree._Element) -> None:
        res_list = _deserialise_one_property(date_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert res.user_facing_prop == "http://0.0.0.0:3333/ontology/9999/onto/v2#testSubDate1"
        assert res.user_facing_value == "JULIAN:BCE:0700:BCE:0600"
        assert res.knora_type == KnoraValueType.DATE_VALUE
        assert not res.value_metadata

    def test_several(self, date_value_corr_several: etree._Element) -> None:
        res = _deserialise_one_property(date_value_corr_several)
        assert len(res) == 2
        assert res[0].user_facing_prop == "http://0.0.0.0:3333/ontology/9999/onto/v2#testSubDate1"
        assert res[0].user_facing_value == "JULIAN:BCE:0700:BCE:0600"
        assert res[1].user_facing_value == "ISLAMIC:0600:0700"
        assert res[0].knora_type == KnoraValueType.DATE_VALUE
        assert res[1].knora_type == KnoraValueType.DATE_VALUE


class TestDecimalValue:
    def test_corr(self, decimal_value_corr: etree._Element) -> None:
        res_list = _deserialise_one_property(decimal_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert res.user_facing_prop == "http://0.0.0.0:3333/ontology/9999/onto/v2#testDecimalSimpleText"
        assert res.user_facing_value == "2.71"
        assert res.knora_type == KnoraValueType.DECIMAL_VALUE
        assert not res.value_metadata

    def test_several(self, decimal_value_corr_several: etree._Element) -> None:
        res = _deserialise_one_property(decimal_value_corr_several)
        assert len(res) == 2
        assert res[0].user_facing_prop == "http://0.0.0.0:3333/ontology/9999/onto/v2#testDecimalSimpleText"
        assert res[0].user_facing_value == "1.0"
        assert res[1].user_facing_value == "2.0"
        assert res[0].knora_type == KnoraValueType.DECIMAL_VALUE
        assert res[1].knora_type == KnoraValueType.DECIMAL_VALUE


class TestGeonameValue:
    def test_corr(self, geoname_value_corr: etree._Element) -> None:
        res_list = _deserialise_one_property(geoname_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert res.user_facing_prop == "http://0.0.0.0:3333/ontology/9999/onto/v2#testGeoname"
        assert res.user_facing_value == "1111111"
        assert res.knora_type == KnoraValueType.GEONAME_VALUE
        assert not res.value_metadata

    def test_several(self, geoname_value_corr_several: etree._Element) -> None:
        res = _deserialise_one_property(geoname_value_corr_several)
        assert len(res) == 2
        assert res[0].user_facing_prop == "http://0.0.0.0:3333/ontology/9999/onto/v2#testGeoname"
        assert res[0].user_facing_value == "1111111"
        assert res[1].user_facing_value == "2222222"
        assert res[0].knora_type == KnoraValueType.GEONAME_VALUE
        assert res[1].knora_type == KnoraValueType.GEONAME_VALUE


class TestGeomValue:
    def test_corr(self, geometry_value_corr: etree._Element) -> None:
        res_list = _deserialise_one_property(geometry_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert res.user_facing_prop == f"{KNORA_API_STR}hasGeometry"
        assert res.user_facing_value is not None
        assert res.knora_type == KnoraValueType.GEOM_VALUE
        assert not res.value_metadata

    def test_wrong(self, geometry_value_wrong: etree._Element) -> None:
        res_list = _deserialise_one_property(geometry_value_wrong)
        assert len(res_list) == 1
        res = res_list[0]
        assert res.user_facing_prop == f"{KNORA_API_STR}hasGeometry"
        assert not res.user_facing_value
        assert res.knora_type == KnoraValueType.GEOM_VALUE
        assert not res.value_metadata


class TestIntValue:
    def test_corr(self, integer_value_corr: etree._Element) -> None:
        res_list = _deserialise_one_property(integer_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert res.user_facing_prop == "http://0.0.0.0:3333/ontology/9999/onto/v2#testIntegerSimpleText"
        assert res.user_facing_value == "1"
        assert res.knora_type == KnoraValueType.INT_VALUE
        assert not res.value_metadata

    def test_several(self, integer_value_corr_several: etree._Element) -> None:
        res = _deserialise_one_property(integer_value_corr_several)
        assert len(res) == 2
        assert res[0].user_facing_prop == "http://0.0.0.0:3333/ontology/9999/onto/v2#testIntegerSimpleText"
        assert res[0].user_facing_value == "1"
        assert res[1].user_facing_value == "2"
        assert res[0].knora_type == KnoraValueType.INT_VALUE
        assert res[1].knora_type == KnoraValueType.INT_VALUE


class TestListValue:
    def test_corr(self, list_value_corr: etree._Element) -> None:
        res_list = _deserialise_one_property(list_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert res.user_facing_prop == "http://0.0.0.0:3333/ontology/9999/onto/v2#testListProp"
        assert res.user_facing_value == "firstList / n1"
        assert res.knora_type == KnoraValueType.LIST_VALUE
        assert not res.value_metadata

    def test_several(self, list_value_corr_several: etree._Element) -> None:
        res = _deserialise_one_property(list_value_corr_several)
        assert len(res) == 2
        one = res[0]
        assert one.user_facing_prop == "http://0.0.0.0:3333/ontology/9999/onto/v2#testListProp"
        assert res[0].user_facing_value == "firstList / n1"
        assert res[1].user_facing_value == "firstList / n2"
        assert res[0].knora_type == KnoraValueType.LIST_VALUE
        assert res[1].knora_type == KnoraValueType.LIST_VALUE


class TestSimpleTextValue:
    def test_corr(self, text_simpletext_value_corr: etree._Element) -> None:
        res_list = _deserialise_one_property(text_simpletext_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert res.user_facing_prop == "http://0.0.0.0:3333/ontology/9999/onto/v2#testTextarea"
        assert res.user_facing_value == "Text"
        assert res.knora_type == KnoraValueType.SIMPLETEXT_VALUE
        assert not res.value_metadata

    def test_several(self, text_simpletext_value_corr_several: etree._Element) -> None:
        res = _deserialise_one_property(text_simpletext_value_corr_several)
        assert len(res) == 2
        assert res[0].user_facing_prop == "http://0.0.0.0:3333/ontology/9999/onto/v2#testSimpleText"
        assert res[0].user_facing_value == "Text 1"
        assert res[1].user_facing_value == "Text 2"
        assert res[0].knora_type == KnoraValueType.SIMPLETEXT_VALUE
        assert res[1].knora_type == KnoraValueType.SIMPLETEXT_VALUE

    def test_wrong(self, text_simpletext_value_wrong: etree._Element) -> None:
        res_list = _deserialise_one_property(text_simpletext_value_wrong)
        assert len(res_list) == 1
        res = res_list[0]
        assert res.user_facing_prop == "http://0.0.0.0:3333/ontology/9999/onto/v2#testSimpleText"
        assert not res.user_facing_value
        assert res.knora_type == KnoraValueType.SIMPLETEXT_VALUE
        assert not res.value_metadata


class TestRichtextValue:
    def test_corr(self, text_richtext_value_corr: etree._Element) -> None:
        res_list = _deserialise_one_property(text_richtext_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert res.user_facing_prop == "http://0.0.0.0:3333/ontology/9999/onto/v2#testRichtext"
        assert res.user_facing_value == "<p>Text</p>"
        assert res.knora_type == KnoraValueType.RICHTEXT_VALUE
        assert not res.value_metadata

    def test_several(self, text_richtext_value_corr_several: etree._Element) -> None:
        res = _deserialise_one_property(text_richtext_value_corr_several)
        assert len(res) == 2
        assert res[0].user_facing_prop == "http://0.0.0.0:3333/ontology/9999/onto/v2#testRichtext"
        assert res[0].user_facing_value == "Text 1"
        assert res[1].user_facing_value == "Text 2"
        assert res[0].knora_type == KnoraValueType.RICHTEXT_VALUE
        assert res[1].knora_type == KnoraValueType.RICHTEXT_VALUE


class TestTimeValue:
    def test_corr(self, time_value_corr: etree._Element) -> None:
        res_list = _deserialise_one_property(time_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert res.user_facing_prop == "http://0.0.0.0:3333/ontology/9999/onto/v2#testTimeValue"
        assert res.user_facing_value == "2019-10-23T13:45:12.01-14:00"
        assert res.knora_type == KnoraValueType.TIME_VALUE
        assert not res.value_metadata

    def test_several(self, time_value_corr_several: etree._Element) -> None:
        res = _deserialise_one_property(time_value_corr_several)
        assert len(res) == 2
        assert res[0].user_facing_prop == "http://0.0.0.0:3333/ontology/9999/onto/v2#testTimeValue"
        assert res[0].user_facing_value == "2019-10-23T13:45:12.01-14:00"
        assert res[1].user_facing_value == "2019-10-23T13:45:12.01-08:00"
        assert res[0].knora_type == KnoraValueType.TIME_VALUE
        assert res[1].knora_type == KnoraValueType.TIME_VALUE


class TestUriValue:
    def test_corr(self, uri_value_corr: etree._Element) -> None:
        res_list = _deserialise_one_property(uri_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert res.user_facing_prop == "http://0.0.0.0:3333/ontology/9999/onto/v2#testUriValue"
        assert res.user_facing_value == "https://dasch.swiss"
        assert res.knora_type == KnoraValueType.URI_VALUE
        assert not res.value_metadata

    def test_several(self, uri_value_corr_several: etree._Element) -> None:
        res = _deserialise_one_property(uri_value_corr_several)
        assert len(res) == 2
        assert res[0].user_facing_prop == "http://0.0.0.0:3333/ontology/9999/onto/v2#testUriValue"
        assert res[0].user_facing_value == "https://dasch.swiss"
        assert res[1].user_facing_value == "https://app.dasch.swiss"
        assert res[0].knora_type == KnoraValueType.URI_VALUE
        assert res[1].knora_type == KnoraValueType.URI_VALUE


class TestLinkValue:
    def test_corr(self, resptr_value_corr: etree._Element) -> None:
        res_list = _deserialise_one_property(resptr_value_corr)
        assert len(res_list) == 1
        res = res_list[0]
        assert res.user_facing_prop == "http://0.0.0.0:3333/ontology/9999/onto/v2#testHasLinkTo"
        assert res.user_facing_value == "id_1"
        assert res.knora_type == KnoraValueType.LINK_VALUE
        assert not res.value_metadata

    def test_several(self, resptr_value_corr_several: etree._Element) -> None:
        res = _deserialise_one_property(resptr_value_corr_several)
        assert len(res) == 2
        assert res[0].user_facing_prop == "http://0.0.0.0:3333/ontology/9999/onto/v2#testHasLinkTo"
        assert res[0].user_facing_value == "id_1"
        assert res[1].user_facing_value == "id_2"
        assert res[0].knora_type == KnoraValueType.LINK_VALUE
        assert res[1].knora_type == KnoraValueType.LINK_VALUE


class TestFileValue:
    def test_iiif(self, iiif_with_spaces: etree._Element) -> None:
        result = _deserialise_one_property(iiif_with_spaces)
        assert len(result) == 1
        res = result.pop()
        assert res.user_facing_prop == f"{KNORA_API_STR}hasStillImageFileValue"
        assert res.user_facing_value == "https://iiif.uri/full.jpg"
        assert res.knora_type == KnoraValueType.STILL_IMAGE_IIIF
        assert not res.value_metadata


class TestExtractMetadata:
    def test_none(self, boolean_value_no_attrib: etree._Element) -> None:
        res = _extract_metadata(boolean_value_no_attrib)
        assert not res

    def test_comment(self, boolean_value_comment: etree._Element) -> None:
        res = _extract_metadata(boolean_value_comment)
        assert len(res) == 1
        val = res.pop(0)
        assert val.property_type == TriplePropertyType.KNORA_COMMENT_ON_VALUE
        assert val.object_value == "Comment on Value"
        assert val.object_type == TripleObjectType.STRING

    def test_permissions(self, boolean_value_permissions: etree._Element) -> None:
        res = _extract_metadata(boolean_value_permissions)
        assert len(res) == 1
        permission = res.pop(0)
        assert permission.property_type == TriplePropertyType.KNORA_PERMISSIONS
        assert permission.object_value == "open"
        assert permission.object_type == TripleObjectType.STRING

    def test_iiif_with_legal_info(self, iiif_with_legal_info: etree._Element) -> None:
        result = _extract_metadata(iiif_with_legal_info)
        assert len(result) == 3
        license_res = next(x for x in result if x.property_type == TriplePropertyType.KNORA_LICENSE)
        assert license_res.object_value == "license_iri"
        assert license_res.object_type == TripleObjectType.IRI
        author_res = next(x for x in result if x.property_type == TriplePropertyType.KNORA_AUTHORSHIP)
        assert author_res.object_value == "auth"
        assert author_res.object_type == TripleObjectType.STRING
        copyright_res = next(x for x in result if x.property_type == TriplePropertyType.KNORA_COPYRIGHT_HOLDER)
        assert copyright_res.object_value == "copy"
        assert copyright_res.object_type == TripleObjectType.STRING


@pytest.mark.parametrize(
    ("input_str", "expected"),
    [
        ('<text encoding="xml"><p>Text</p></text>', "<p>Text</p>"),
        ('<text encoding="xml"><text>Text</text></text>', "<text>Text</text>"),
        ('<text encoding="xml"><p><p>Text second word</p>Tail</p></text>', "<p><p>Text second word</p>Tail</p>"),
        ('<text encoding="xml"> </text>', " "),
        ('<text encoding="xml"></text>', None),
        ('<text encoding="xml"><br/>Text</text>', "<br/>Text"),
        ('<text encoding="xml">Text<br/>  </text>', "Text<br/>"),
        ('<text encoding="xml">  Text<br/>Text<br/>Text</text>', "Text<br/>Text<br/>Text"),
    ],
)
def test_get_text_as_string(input_str: str, expected: str) -> None:
    val = etree.fromstring(input_str)
    result = _get_text_as_string(val)
    assert result == expected


if __name__ == "__main__":
    pytest.main([__file__])
