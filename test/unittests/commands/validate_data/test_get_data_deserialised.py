# mypy: disable-error-code="method-assign,no-untyped-def"

import pytest

from dsp_tools.commands.validate_data.get_data_deserialised import _get_file_metadata
from dsp_tools.commands.validate_data.get_data_deserialised import _get_file_value
from dsp_tools.commands.validate_data.get_data_deserialised import _get_generic_value
from dsp_tools.commands.validate_data.get_data_deserialised import _get_one_resource
from dsp_tools.commands.validate_data.get_data_deserialised import get_data_deserialised
from dsp_tools.utils.rdflib_constants import KNORA_API_STR
from dsp_tools.utils.xml_parsing.models.data_deserialised import PropertyObject
from dsp_tools.utils.xml_parsing.models.data_deserialised import ResourceDeserialised
from dsp_tools.utils.xml_parsing.models.data_deserialised import TripleObjectType
from dsp_tools.utils.xml_parsing.models.data_deserialised import TriplePropertyType
from dsp_tools.utils.xml_parsing.models.data_deserialised import ValueInformation
from dsp_tools.utils.xml_parsing.models.parsed_resource import KnoraValueType
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedFileValue
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedFileValueMetadata
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedValue

from dsp_tools.utils.xml_parsing.models.parsed_resource import KnoraValueType
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedFileValue
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedFileValueMetadata
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedMigrationMetadata
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedResource
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedValue
ONTO = "http://0.0.0.0:3333/ontology/9999/onto/v2#"
HAS_PROP = f"{ONTO}hasProp"
RES_TYPE = f"{ONTO}ResourceType"


@pytest.fixture
def file_with_permission() -> ParsedFileValue:
    metadata = ParsedFileValueMetadata("http://rdfh.ch/licenses/cc-by-nc-4.0", "copy", "auth_id", "open")
    return ParsedFileValue("file.jpg", KnoraValueType.STILL_IMAGE_FILE, metadata)


@pytest.fixture
def bool_value() -> ParsedValue:
    return ParsedValue(HAS_PROP, "true", KnoraValueType.BOOLEAN_VALUE, None, None)


@pytest.fixture
def iiif_file_value():
    metadata = ParsedFileValueMetadata("http://rdfh.ch/licenses/cc-by-nc-4.0", "copy", "auth_id", None)
    return ParsedFileValue("https://this/is/a/uri.jpg", KnoraValueType.STILL_IMAGE_IIIF, metadata)


def _get_label_and_type(resource: ResourceDeserialised) -> tuple[PropertyObject, PropertyObject, list[PropertyObject]]:
    lbl = next(x for x in resource.property_objects if x.property_type == TriplePropertyType.RDFS_LABEL)
    rdf_type = next(x for x in resource.property_objects if x.property_type == TriplePropertyType.RDF_TYPE)
    permissions = list(x for x in resource.property_objects if x.property_type == TriplePropertyType.KNORA_PERMISSIONS)
    return lbl, rdf_type, permissions


class TestResource:
    def test_empty(self):
        res = ParsedResource(
            res_id="one",
            res_type=RES_TYPE,
            label="lbl",
            permissions_id=None,
            values=[],
            file_value=None,
            migration_metadata=None,
        )
        result = _get_one_resource(res)
        assert result.res_id == "one"
        assert len(result.property_objects) == 2
        assert not result.asset_value
        lbl, rdf_type, _ = _get_label_and_type(result)
        assert lbl.object_value == "lbl"
        assert lbl.object_type == TripleObjectType.STRING
        assert rdf_type.object_value == RES_TYPE
        assert rdf_type.object_type == TripleObjectType.IRI
        assert len(result.values) == 0

    def test_empty_permissions(self, resource_empty_permissions):
        result = _get_one_resource(resource_empty_permissions)
        assert result.res_id == "one"
        assert len(result.property_objects) == 3
        assert not result.asset_value
        lbl, rdf_type, perm = _get_label_and_type(result)
        assert len(perm) == 1
        permission = perm.pop(0)
        assert permission.object_value == "open"
        assert permission.object_type == TripleObjectType.STRING
        assert permission.property_type == TriplePropertyType.KNORA_PERMISSIONS
        assert lbl.object_value == "lbl"
        assert lbl.object_type == TripleObjectType.STRING
        assert rdf_type.object_value == RES_TYPE
        assert rdf_type.object_type == TripleObjectType.IRI
        assert len(result.values) == 0
        assert not result.migration_metadata.any()

    def test_with_props(self, root_resource_with_props):
        result = get_data_deserialised(root_resource_with_props).resources
        assert result.res_id == "one"
        assert len(result.property_objects) == 2
        assert not result.asset_value
        lbl, rdf_type, _ = _get_label_and_type(result)
        assert lbl.object_value == "lbl"
        assert lbl.object_type == TripleObjectType.STRING
        assert rdf_type.object_value == RES_TYPE
        assert rdf_type.object_type == TripleObjectType.IRI
        assert len(result.values) == 3
        assert not result.migration_metadata.any()

    def test_with_file_value(self, resource_with_bitstream):
        result = _get_one_resource(resource_with_bitstream)
        assert len(result.values) == 0
        bitstream = result.asset_value
        assert isinstance(bitstream, ValueInformation)
        assert bitstream.user_facing_prop == f"{KNORA_API_STR}hasAudioFileValue"
        assert bitstream.user_facing_value == "testdata/bitstreams/test.wav"
        assert bitstream.knora_type == KnoraValueType.AUDIO_FILE
        assert not bitstream.value_metadata
        assert not result.migration_metadata.any()

    def test_audio_segment(self, audio_segment):
        result = _get_one_resource(audio_segment)
        assert result.res_id == "audio_id"
        assert len(result.property_objects) == 2
        assert not result.asset_value
        lbl, rdf_type, _ = _get_label_and_type(result)
        assert lbl.object_value == "lbl"
        assert lbl.object_type == TripleObjectType.STRING
        assert rdf_type.object_value == "http://api.knora.org/ontology/knora-api/v2#AudioSegment"
        assert rdf_type.object_type == TripleObjectType.IRI
        assert len(result.values) == 2
        propname_to_info = {x.user_facing_prop: x for x in result.values}
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
        assert not result.migration_metadata.any()


class TestValues:
    def test_boolean_corr(self, boolean_value_corr):
        res = _get_generic_value(boolean_value_corr)
        assert res.user_facing_prop == "http://0.0.0.0:3333/ontology/9999/onto/v2#testBoolean"
        assert res.user_facing_value == "true"
        assert res.knora_type == KnoraValueType.BOOLEAN_VALUE
        assert not res.value_metadata

    def test_color_corr(self, color_value_corr):
        res = _get_generic_value(color_value_corr)
        assert res.user_facing_prop == "http://0.0.0.0:3333/ontology/9999/onto/v2#testColor"
        assert res.user_facing_value == "#00ff00"
        assert res.knora_type == KnoraValueType.COLOR_VALUE
        assert not res.value_metadata

    def test_date_corr(self, date_value_corr):
        res = _get_generic_value(date_value_corr)
        assert res.user_facing_prop == "http://0.0.0.0:3333/ontology/9999/onto/v2#testSubDate1"
        assert res.user_facing_value == "JULIAN:BCE:0700:BCE:0600"
        assert res.knora_type == KnoraValueType.DATE_VALUE
        assert not res.value_metadata

    def test_decimal_corr(self, decimal_value_corr):
        res = _get_generic_value(decimal_value_corr)
        assert res.user_facing_prop == "http://0.0.0.0:3333/ontology/9999/onto/v2#testDecimalSimpleText"
        assert res.user_facing_value == "2.71"
        assert res.knora_type == KnoraValueType.DECIMAL_VALUE
        assert not res.value_metadata

    def test_geoname_corr(self, geoname_value_corr):
        res = _get_generic_value(geoname_value_corr)
        assert res.user_facing_prop == "http://0.0.0.0:3333/ontology/9999/onto/v2#testGeoname"
        assert res.user_facing_value == "1111111"
        assert res.knora_type == KnoraValueType.GEONAME_VALUE
        assert not res.value_metadata

    def test_geom_corr(self, geometry_value_corr):
        res = _get_generic_value(geometry_value_corr)
        assert res.user_facing_prop == f"{KNORA_API_STR}hasGeometry"
        assert res.user_facing_value is not None
        assert res.knora_type == KnoraValueType.GEOM_VALUE
        assert not res.value_metadata

    def test_geom_wrong(self, geometry_value_wrong):
        res = _get_generic_value(geometry_value_wrong)
        assert res.user_facing_prop == f"{KNORA_API_STR}hasGeometry"
        assert not res.user_facing_value
        assert res.knora_type == KnoraValueType.GEOM_VALUE
        assert not res.value_metadata

    def test_int_corr(self, integer_value_corr):
        res = _get_generic_value(integer_value_corr)
        assert res.user_facing_prop == "http://0.0.0.0:3333/ontology/9999/onto/v2#testIntegerSimpleText"
        assert res.user_facing_value == "1"
        assert res.knora_type == KnoraValueType.INT_VALUE
        assert not res.value_metadata

    def test_list_corr(self, list_value_corr):
        res = _get_generic_value(list_value_corr)
        assert res.user_facing_prop == "http://0.0.0.0:3333/ontology/9999/onto/v2#testListProp"
        assert res.user_facing_value == "firstList / n1"
        assert res.knora_type == KnoraValueType.LIST_VALUE
        assert not res.value_metadata

    def test_simple_text_corr(self, text_simpletext_value_corr):
        res = _get_generic_value(text_simpletext_value_corr)
        assert res.user_facing_prop == "http://0.0.0.0:3333/ontology/9999/onto/v2#testTextarea"
        assert res.user_facing_value == "Text"
        assert res.knora_type == KnoraValueType.SIMPLETEXT_VALUE
        assert not res.value_metadata

    def test_simple_text_wrong(self, text_simpletext_value_wrong):
        res = _get_generic_value(text_simpletext_value_wrong)
        assert res.user_facing_prop == "http://0.0.0.0:3333/ontology/9999/onto/v2#testSimpleText"
        assert not res.user_facing_value
        assert res.knora_type == KnoraValueType.SIMPLETEXT_VALUE
        assert not res.value_metadata

    def test_richtext_corr(self, text_richtext_value_corr):
        res = _get_generic_value(text_richtext_value_corr)
        assert res.user_facing_prop == "http://0.0.0.0:3333/ontology/9999/onto/v2#testRichtext"
        assert res.user_facing_value == "<p>Text</p>"
        assert res.knora_type == KnoraValueType.RICHTEXT_VALUE
        assert not res.value_metadata

    def test_time_corr(self, time_value_corr):
        res = _get_generic_value(time_value_corr)
        assert res.user_facing_prop == "http://0.0.0.0:3333/ontology/9999/onto/v2#testTimeValue"
        assert res.user_facing_value == "2019-10-23T13:45:12.01-14:00"
        assert res.knora_type == KnoraValueType.TIME_VALUE
        assert not res.value_metadata

    def test_uri_corr(self, uri_value_corr):
        res = _get_generic_value(uri_value_corr)
        assert res.user_facing_prop == "http://0.0.0.0:3333/ontology/9999/onto/v2#testUriValue"
        assert res.user_facing_value == "https://dasch.swiss"
        assert res.knora_type == KnoraValueType.URI_VALUE
        assert not res.value_metadata

    def test_link_corr(self, resptr_value_corr):
        res = _get_generic_value(resptr_value_corr)
        assert res.user_facing_prop == "http://0.0.0.0:3333/ontology/9999/onto/v2#testHasLinkTo"
        assert res.user_facing_value == "id_1"
        assert res.knora_type == KnoraValueType.LINK_VALUE
        assert not res.value_metadata


class TestFileValue:
    def test_iiif(self, iiif_with_spaces):
        res = _get_file_value(iiif_with_spaces)
        assert res.user_facing_prop == f"{KNORA_API_STR}hasStillImageFileValue"
        assert res.user_facing_value == "https://iiif.uri/full.jpg"
        assert res.knora_type == KnoraValueType.STILL_IMAGE_IIIF
        assert not res.value_metadata

    def test_iiif_with_legal_info(self, iiif_with_legal_info):
        result = _get_file_metadata(iiif_with_legal_info)
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


if __name__ == "__main__":
    pytest.main([__file__])
