# mypy: disable-error-code="method-assign,no-untyped-def"

import pytest

from dsp_tools.commands.validate_data.models.api_responses import ListLookup
from dsp_tools.commands.validate_data.models.rdf_like_data import PropertyObject
from dsp_tools.commands.validate_data.models.rdf_like_data import RdfLikeResource
from dsp_tools.commands.validate_data.models.rdf_like_data import RdfLikeValue
from dsp_tools.commands.validate_data.models.rdf_like_data import TripleObjectType
from dsp_tools.commands.validate_data.models.rdf_like_data import TriplePropertyType
from dsp_tools.commands.validate_data.prepare_data.get_rdf_like_data import _get_all_stand_off_links
from dsp_tools.commands.validate_data.prepare_data.get_rdf_like_data import _get_date_str
from dsp_tools.commands.validate_data.prepare_data.get_rdf_like_data import _get_file_metadata
from dsp_tools.commands.validate_data.prepare_data.get_rdf_like_data import _get_file_value
from dsp_tools.commands.validate_data.prepare_data.get_rdf_like_data import _get_link_string_and_triple_object_type
from dsp_tools.commands.validate_data.prepare_data.get_rdf_like_data import _get_list_value_str
from dsp_tools.commands.validate_data.prepare_data.get_rdf_like_data import _get_one_resource
from dsp_tools.commands.validate_data.prepare_data.get_rdf_like_data import _get_one_value
from dsp_tools.commands.validate_data.prepare_data.get_rdf_like_data import _get_resource_ids_and_iri_strings
from dsp_tools.commands.validate_data.prepare_data.get_rdf_like_data import _get_xsd_like_dates
from dsp_tools.commands.validate_data.prepare_data.get_rdf_like_data import get_rdf_like_data
from dsp_tools.utils.data_formats.date_util import Era
from dsp_tools.utils.data_formats.date_util import SingleDate
from dsp_tools.utils.rdflib_constants import KNORA_API_STR
from dsp_tools.utils.xml_parsing.models.parsed_resource import KnoraValueType
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedFileValue
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedFileValueMetadata
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedResource
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedValue

ONTO = "http://0.0.0.0:3333/ontology/9999/onto/v2#"
HAS_PROP = f"{ONTO}hasProp"
RES_TYPE = f"{ONTO}ResourceType"


AUTHORSHIP_LOOKUP = {"auth_id": ["Author Resolved"]}
LIST_LOOKUP = ListLookup({("list", "node"): "http://rdfh.ch/lists/9999/n1"})


@pytest.fixture
def file_with_permission() -> ParsedFileValue:
    metadata = ParsedFileValueMetadata("http://rdfh.ch/licenses/cc-by-nc-4.0", "copy", "auth_id", "public")
    return ParsedFileValue("file.jpg", KnoraValueType.STILL_IMAGE_FILE, metadata)


@pytest.fixture
def bool_value() -> ParsedValue:
    return ParsedValue(HAS_PROP, "true", KnoraValueType.BOOLEAN_VALUE, None, None)


@pytest.fixture
def richtext_with_standoff() -> ParsedValue:
    text_str = 'With <a class="salsah-link" href="IRI:link:IRI">link text</a>.'
    return ParsedValue(HAS_PROP, text_str, KnoraValueType.RICHTEXT_VALUE, None, None)


def _get_label_and_type(resource: RdfLikeResource) -> tuple[PropertyObject, PropertyObject, list[PropertyObject]]:
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
        result = _get_one_resource(res, {}, LIST_LOOKUP)
        assert result.res_id == "one"
        assert len(result.property_objects) == 2
        lbl, rdf_type, _ = _get_label_and_type(result)
        assert lbl.object_value == "lbl"
        assert lbl.object_type == TripleObjectType.STRING
        assert rdf_type.object_value == RES_TYPE
        assert rdf_type.object_type == TripleObjectType.IRI
        assert len(result.values) == 0

    def test_empty_permissions(self):
        res = ParsedResource(
            res_id="one",
            res_type=RES_TYPE,
            label="lbl",
            permissions_id="public",
            values=[],
            file_value=None,
            migration_metadata=None,
        )
        result = _get_one_resource(res, {}, LIST_LOOKUP)
        assert result.res_id == "one"
        assert len(result.property_objects) == 3
        lbl, rdf_type, perm = _get_label_and_type(result)
        assert len(perm) == 1
        permission = perm.pop(0)
        assert permission.object_value == "public"
        assert permission.object_type == TripleObjectType.STRING
        assert permission.property_type == TriplePropertyType.KNORA_PERMISSIONS
        assert lbl.object_value == "lbl"
        assert lbl.object_type == TripleObjectType.STRING
        assert rdf_type.object_value == RES_TYPE
        assert rdf_type.object_type == TripleObjectType.IRI
        assert len(result.values) == 0

    def test_with_props(self, bool_value):
        res = ParsedResource(
            res_id="one",
            res_type=RES_TYPE,
            label="lbl",
            permissions_id=None,
            values=[bool_value],
            file_value=None,
            migration_metadata=None,
        )
        result_list = get_rdf_like_data([res], {}, LIST_LOOKUP)
        assert len(result_list.resources) == 1
        result = result_list.resources.pop(0)
        assert result.res_id == "one"
        assert len(result.property_objects) == 2
        lbl, rdf_type, _ = _get_label_and_type(result)
        assert lbl.object_value == "lbl"
        assert lbl.object_type == TripleObjectType.STRING
        assert rdf_type.object_value == RES_TYPE
        assert rdf_type.object_type == TripleObjectType.IRI
        assert len(result.values) == 1

    def test_with_file_value(self, file_with_permission):
        res = ParsedResource(
            res_id="one",
            res_type=RES_TYPE,
            label="lbl",
            permissions_id=None,
            values=[],
            file_value=file_with_permission,
            migration_metadata=None,
        )
        result = _get_one_resource(res, AUTHORSHIP_LOOKUP, LIST_LOOKUP)
        assert len(result.values) == 1
        file_value = result.values.pop(0)
        assert isinstance(file_value, RdfLikeValue)
        assert file_value.user_facing_prop == f"{KNORA_API_STR}hasStillImageFileValue"
        assert file_value.user_facing_value == "file.jpg"
        assert file_value.knora_type == KnoraValueType.STILL_IMAGE_FILE
        assert len(file_value.value_metadata) == 4

    def test_with_standoff(self, richtext_with_standoff):
        res = ParsedResource(
            res_id="one",
            res_type=RES_TYPE,
            label="lbl",
            permissions_id=None,
            values=[richtext_with_standoff],
            file_value=None,
            migration_metadata=None,
        )
        result = _get_one_resource(res, {}, LIST_LOOKUP)
        assert result.res_id == "one"
        assert len(result.property_objects) == 3
        lbl, rdf_type, _ = _get_label_and_type(result)
        assert lbl.object_value == "lbl"
        assert lbl.object_type == TripleObjectType.STRING
        assert rdf_type.object_value == RES_TYPE
        assert rdf_type.object_type == TripleObjectType.IRI
        standoff = next(x for x in result.property_objects if x.property_type == TriplePropertyType.KNORA_STANDOFF_LINK)
        assert standoff.object_value == "link"
        assert standoff.object_type == TripleObjectType.INTERNAL_ID
        assert len(result.values) == 1


class TestValues:
    def test_boolean_corr(self):
        val = ParsedValue(HAS_PROP, "true", KnoraValueType.BOOLEAN_VALUE, None, None)
        res = _get_one_value(val, LIST_LOOKUP)
        assert res.user_facing_prop == HAS_PROP
        assert res.user_facing_value == "true"
        assert res.knora_type == KnoraValueType.BOOLEAN_VALUE
        assert not res.value_metadata

    def test_boolean_with_comment_corr(self):
        val = ParsedValue(HAS_PROP, "true", KnoraValueType.BOOLEAN_VALUE, None, "comment")
        res = _get_one_value(val, LIST_LOOKUP)
        assert res.user_facing_prop == HAS_PROP
        assert res.user_facing_value == "true"
        assert res.knora_type == KnoraValueType.BOOLEAN_VALUE
        assert len(res.value_metadata) == 1
        metadata = res.value_metadata.pop(0)
        assert metadata.property_type == TriplePropertyType.KNORA_COMMENT_ON_VALUE
        assert metadata.object_value == "comment"
        assert metadata.object_type == TripleObjectType.STRING

    def test_boolean_with_comment_empty_string(self):
        val = ParsedValue(HAS_PROP, "true", KnoraValueType.BOOLEAN_VALUE, None, "")
        res = _get_one_value(val, LIST_LOOKUP)
        assert res.user_facing_prop == HAS_PROP
        assert res.user_facing_value == "true"
        assert res.knora_type == KnoraValueType.BOOLEAN_VALUE
        assert len(res.value_metadata) == 1
        metadata = res.value_metadata.pop(0)
        assert metadata.property_type == TriplePropertyType.KNORA_COMMENT_ON_VALUE
        assert metadata.object_value == ""
        assert metadata.object_type == TripleObjectType.STRING

    def test_boolean_with_permissions_corr(self):
        val = ParsedValue(HAS_PROP, "true", KnoraValueType.BOOLEAN_VALUE, "public", None)
        res = _get_one_value(val, LIST_LOOKUP)
        assert res.user_facing_prop == HAS_PROP
        assert res.user_facing_value == "true"
        assert res.knora_type == KnoraValueType.BOOLEAN_VALUE
        assert len(res.value_metadata) == 1
        metadata = res.value_metadata.pop(0)
        assert metadata.property_type == TriplePropertyType.KNORA_PERMISSIONS
        assert metadata.object_value == "public"
        assert metadata.object_type == TripleObjectType.STRING

    def test_boolean_none(self):
        val = ParsedValue(HAS_PROP, None, KnoraValueType.BOOLEAN_VALUE, None, None)
        res = _get_one_value(val, LIST_LOOKUP)
        assert res.user_facing_prop == HAS_PROP
        assert res.user_facing_value == None  # noqa: E711 Comparison to `None`
        assert res.knora_type == KnoraValueType.BOOLEAN_VALUE
        assert not res.value_metadata

    def test_color_corr(self):
        val = ParsedValue(HAS_PROP, "#5d1f1e", KnoraValueType.COLOR_VALUE, None, None)
        res = _get_one_value(val, LIST_LOOKUP)
        assert res.user_facing_prop == HAS_PROP
        assert res.user_facing_value == "#5d1f1e"
        assert res.knora_type == KnoraValueType.COLOR_VALUE
        assert not res.value_metadata

    def test_date_corr_with_date_range_yyyy(self):
        val = ParsedValue(HAS_PROP, "CE:1849:CE:1850", KnoraValueType.DATE_VALUE, None, None)
        res = _get_one_value(val, LIST_LOOKUP)
        assert res.user_facing_prop == HAS_PROP
        assert res.user_facing_value == "CE:1849:CE:1850"
        assert res.knora_type == KnoraValueType.DATE_VALUE
        assert len(res.value_metadata) == 2
        start = next(x for x in res.value_metadata if x.property_type == TriplePropertyType.KNORA_DATE_START)
        assert start.object_value == "1849-01-01"
        assert start.object_type == TripleObjectType.DATE_YYYY_MM_DD
        end = next(x for x in res.value_metadata if x.property_type == TriplePropertyType.KNORA_DATE_END)
        assert end.object_value == "1850-01-01"
        assert end.object_type == TripleObjectType.DATE_YYYY_MM_DD

    def test_get_xsd_like_dates_only_start(self):
        date_str = "GREGORIAN:CE:1800-01-01"
        result = _get_xsd_like_dates(date_str)
        assert len(result) == 2
        start, end = result
        assert start.property_type == TriplePropertyType.KNORA_DATE_START
        assert start.object_value == "1800-01-01"
        assert start.object_type == TripleObjectType.DATE_YYYY_MM_DD
        assert end.property_type == TriplePropertyType.KNORA_DATE_END
        assert end.object_value == "1800-01-01"
        assert end.object_type == TripleObjectType.DATE_YYYY_MM_DD

    def test_get_xsd_like_dates_mixed_precision(self):
        date_str = "GREGORIAN:CE:1800-01-01:CE:1900"
        result = _get_xsd_like_dates(date_str)
        assert len(result) == 2
        start, end = result
        assert start.property_type == TriplePropertyType.KNORA_DATE_START
        assert start.object_value == "1800-01-01"
        assert start.object_type == TripleObjectType.DATE_YYYY_MM_DD
        assert end.property_type == TriplePropertyType.KNORA_DATE_END
        assert end.object_value == "1900-01-01"
        assert end.object_type == TripleObjectType.DATE_YYYY_MM_DD

    def test_get_xsd_like_dates_second_era_wrong(self):
        date_str = "GREGORIAN:CE:2000:BCE:1900"
        result = _get_xsd_like_dates(date_str)
        assert len(result) == 1
        start = result.pop(0)
        assert start.property_type == TriplePropertyType.KNORA_DATE_START
        assert start.object_value == "2000-01-01"
        assert start.object_type == TripleObjectType.DATE_YYYY_MM_DD

    @pytest.mark.parametrize(
        "date",
        [
            "BCE:2020-01-01:BCE:2021-02-02",  # BCE is not supported
            "BC:2020-01-01:BC:2021-02-02",  # BC is not supported
        ],
    )
    def test_dates_not_supported(self, date):
        result = _get_xsd_like_dates(date)
        assert not result

    @pytest.mark.parametrize(
        ("date", "expected_str"),
        [
            (SingleDate(era=None, year=1900, month=10, day=1), "1900-10-01"),
            (SingleDate(era=None, year=1900, month=10, day=None), "1900-10-01"),
            (SingleDate(era=None, year=900, month=None, day=None), "0900-01-01"),
            (SingleDate(era=Era.CE, year=900, month=None, day=None), "0900-01-01"),
            (SingleDate(era=Era.AD, year=900, month=None, day=None), "0900-01-01"),
        ],
    )
    def test_get_date_str(self, date, expected_str):
        result_str = _get_date_str(date)
        assert result_str == expected_str

    def test_decimal_corr(self):
        val = ParsedValue(HAS_PROP, "1.4", KnoraValueType.DECIMAL_VALUE, None, None)
        res = _get_one_value(val, LIST_LOOKUP)
        assert res.user_facing_prop == HAS_PROP
        assert res.user_facing_value == "1.4"
        assert res.knora_type == KnoraValueType.DECIMAL_VALUE
        assert not res.value_metadata

    def test_geoname_corr(self):
        val = ParsedValue(HAS_PROP, "1111111", KnoraValueType.GEONAME_VALUE, None, None)
        res = _get_one_value(val, LIST_LOOKUP)
        assert res.user_facing_prop == HAS_PROP
        assert res.user_facing_value == "1111111"
        assert res.knora_type == KnoraValueType.GEONAME_VALUE
        assert not res.value_metadata

    def test_geom_corr(self):
        geometry = """{
                    "status": "active",
                    "type": "polygon",
                    "lineWidth": 5,
                    "points": [{"x": 0.4, "y": 0.6},
                    {"x": 0.5, "y": 0.9},
                    {"x": 0.8, "y": 0.9},
                    {"x": 0.7, "y": 0.6}]
                    }"""
        val = ParsedValue(f"{KNORA_API_STR}hasGeometry", geometry, KnoraValueType.GEOM_VALUE, None, None)
        res = _get_one_value(val, LIST_LOOKUP)
        assert res.user_facing_prop == f"{KNORA_API_STR}hasGeometry"
        assert res.user_facing_value is not None
        assert res.knora_type == KnoraValueType.GEOM_VALUE
        assert not res.value_metadata

    def test_geom_wrong(self):
        val = ParsedValue(f"{KNORA_API_STR}hasGeometry", "invalid", KnoraValueType.GEOM_VALUE, None, None)
        res = _get_one_value(val, LIST_LOOKUP)
        assert res.user_facing_prop == f"{KNORA_API_STR}hasGeometry"
        assert res.user_facing_value == None  # noqa: E711 Comparison to `None`
        assert res.knora_type == KnoraValueType.GEOM_VALUE
        assert not res.value_metadata

    def test_geom_none(self):
        val = ParsedValue(f"{KNORA_API_STR}hasGeometry", None, KnoraValueType.GEOM_VALUE, None, None)
        res = _get_one_value(val, LIST_LOOKUP)
        assert res.user_facing_prop == f"{KNORA_API_STR}hasGeometry"
        assert res.user_facing_value == None  # noqa: E711 Comparison to `None`
        assert res.knora_type == KnoraValueType.GEOM_VALUE
        assert not res.value_metadata

    def test_int_corr(self):
        val = ParsedValue(HAS_PROP, "1", KnoraValueType.INT_VALUE, None, None)
        res = _get_one_value(val, LIST_LOOKUP)
        assert res.user_facing_prop == HAS_PROP
        assert res.user_facing_value == "1"
        assert res.knora_type == KnoraValueType.INT_VALUE
        assert not res.value_metadata

    def test_interval_corr(self):
        val = ParsedValue(f"{KNORA_API_STR}hasSegmentBounds", ("1", "2"), KnoraValueType.INTERVAL_VALUE, None, None)
        res = _get_one_value(val, LIST_LOOKUP)
        assert res.user_facing_prop == "http://api.knora.org/ontology/knora-api/v2#hasSegmentBounds"
        assert res.user_facing_value == None  # noqa: E711 Comparison to `None`
        assert res.knora_type == KnoraValueType.INTERVAL_VALUE
        assert len(res.value_metadata) == 2
        interval_start = next(
            x for x in res.value_metadata if x.property_type == TriplePropertyType.KNORA_INTERVAL_START
        )
        assert interval_start.object_value == "1"
        assert interval_start.object_type == TripleObjectType.DECIMAL
        interval_end = next(x for x in res.value_metadata if x.property_type == TriplePropertyType.KNORA_INTERVAL_END)
        assert interval_end.object_value == "2"
        assert interval_end.object_type == TripleObjectType.DECIMAL

    def test_list_corr(self):
        val = ParsedValue(HAS_PROP, ("list", "node"), KnoraValueType.LIST_VALUE, None, None)
        res = _get_one_value(val, LIST_LOOKUP)
        assert res.user_facing_prop == HAS_PROP
        assert res.user_facing_value == "http://rdfh.ch/lists/9999/n1"
        assert res.knora_type == KnoraValueType.LIST_VALUE
        assert not res.value_metadata

    def test_list_none(self):
        val = ParsedValue(HAS_PROP, ("list", None), KnoraValueType.LIST_VALUE, None, None)
        res = _get_one_value(val, LIST_LOOKUP)
        assert res.user_facing_prop == HAS_PROP
        assert res.user_facing_value == "list"
        assert res.knora_type == KnoraValueType.LIST_VALUE
        assert not res.value_metadata

    def test_link_corr(self):
        val = ParsedValue(HAS_PROP, "other_id", KnoraValueType.LINK_VALUE, None, None)
        res = _get_one_value(val, LIST_LOOKUP)
        assert res.user_facing_prop == HAS_PROP
        assert res.user_facing_value == "other_id"
        assert res.knora_type == KnoraValueType.LINK_VALUE
        assert not res.value_metadata

    def test_simple_text_corr(self):
        val = ParsedValue(HAS_PROP, "text", KnoraValueType.SIMPLETEXT_VALUE, None, None)
        res = _get_one_value(val, LIST_LOOKUP)
        assert res.user_facing_prop == HAS_PROP
        assert res.user_facing_value == "text"
        assert res.knora_type == KnoraValueType.SIMPLETEXT_VALUE
        assert not res.value_metadata

    def test_simple_text_wrong(self):
        val = ParsedValue(HAS_PROP, None, KnoraValueType.SIMPLETEXT_VALUE, None, None)
        res = _get_one_value(val, LIST_LOOKUP)
        assert res.user_facing_prop == HAS_PROP
        assert res.user_facing_value == None  # noqa: E711 Comparison to `None`
        assert res.knora_type == KnoraValueType.SIMPLETEXT_VALUE
        assert not res.value_metadata

    def test_richtext_corr(self):
        val = ParsedValue(HAS_PROP, "<p>Text</p>", KnoraValueType.RICHTEXT_VALUE, None, None)
        res = _get_one_value(val, LIST_LOOKUP)
        assert res.user_facing_prop == HAS_PROP
        assert res.user_facing_value == "<p>Text</p>"
        assert res.knora_type == KnoraValueType.RICHTEXT_VALUE
        assert not res.value_metadata

    def test_richtext_with_standoff(self, richtext_with_standoff):
        res = _get_one_value(richtext_with_standoff, LIST_LOOKUP)
        assert res.user_facing_prop == HAS_PROP
        assert res.user_facing_value == 'With <a class="salsah-link" href="IRI:link:IRI">link text</a>.'
        assert res.knora_type == KnoraValueType.RICHTEXT_VALUE
        assert not res.value_metadata

    def test_time_corr(self):
        val = ParsedValue(HAS_PROP, "2019-10-23T13:45:12.01-14:00", KnoraValueType.TIME_VALUE, None, None)
        res = _get_one_value(val, LIST_LOOKUP)
        assert res.user_facing_prop == HAS_PROP
        assert res.user_facing_value == "2019-10-23T13:45:12.01-14:00"
        assert res.knora_type == KnoraValueType.TIME_VALUE
        assert not res.value_metadata

    def test_uri_corr(self):
        val = ParsedValue(HAS_PROP, "https://dasch.swiss", KnoraValueType.URI_VALUE, None, None)
        res = _get_one_value(val, LIST_LOOKUP)
        assert res.user_facing_prop == HAS_PROP
        assert res.user_facing_value == "https://dasch.swiss"
        assert res.knora_type == KnoraValueType.URI_VALUE
        assert not res.value_metadata


class TestFileValue:
    def test_iiif(self):
        metadata = ParsedFileValueMetadata(None, None, None, None)
        val = ParsedFileValue("https://this/is/a/uri.jpg", KnoraValueType.STILL_IMAGE_IIIF, metadata)
        res = _get_file_value(val, AUTHORSHIP_LOOKUP)
        assert isinstance(res, RdfLikeValue)
        assert res.user_facing_prop == f"{KNORA_API_STR}hasStillImageFileValue"
        assert res.user_facing_value == "https://this/is/a/uri.jpg"
        assert res.knora_type == KnoraValueType.STILL_IMAGE_IIIF
        assert not res.value_metadata

    def test_iiif_with_legal_info(self):
        metadata = ParsedFileValueMetadata("http://rdfh.ch/licenses/cc-by-nc-4.0", "copy", "auth_id", None)
        result = _get_file_metadata(metadata, AUTHORSHIP_LOOKUP)
        assert len(result) == 3
        license_res = next(x for x in result if x.property_type == TriplePropertyType.KNORA_LICENSE)
        assert license_res.object_value == "http://rdfh.ch/licenses/cc-by-nc-4.0"
        assert license_res.object_type == TripleObjectType.IRI
        author_res = next(x for x in result if x.property_type == TriplePropertyType.KNORA_AUTHORSHIP)
        assert author_res.object_value == "Author Resolved"
        assert author_res.object_type == TripleObjectType.STRING
        copyright_res = next(x for x in result if x.property_type == TriplePropertyType.KNORA_COPYRIGHT_HOLDER)
        assert copyright_res.object_value == "copy"
        assert copyright_res.object_type == TripleObjectType.STRING

    def test_iiif_with_legal_info_unknown_authorship(self):
        metadata = ParsedFileValueMetadata("http://rdfh.ch/licenses/cc-by-nc-4.0", "copy", "unknonw", None)
        result = _get_file_metadata(metadata, AUTHORSHIP_LOOKUP)
        assert len(result) == 3
        license_res = next(x for x in result if x.property_type == TriplePropertyType.KNORA_LICENSE)
        assert license_res.object_value == "http://rdfh.ch/licenses/cc-by-nc-4.0"
        assert license_res.object_type == TripleObjectType.IRI
        author_res = next(x for x in result if x.property_type == TriplePropertyType.KNORA_AUTHORSHIP)
        assert author_res.object_value == ""
        assert author_res.object_type == TripleObjectType.STRING
        copyright_res = next(x for x in result if x.property_type == TriplePropertyType.KNORA_COPYRIGHT_HOLDER)
        assert copyright_res.object_value == "copy"
        assert copyright_res.object_type == TripleObjectType.STRING

    def test_no_file(self):
        metadata = ParsedFileValueMetadata(None, None, None, None)
        val = ParsedFileValue(None, None, metadata)
        assert not _get_file_value(val, AUTHORSHIP_LOOKUP)

    def test_unknown_extension(self):
        metadata = ParsedFileValueMetadata(None, None, None, None)
        val = ParsedFileValue("unknown.extension", None, metadata)
        assert not _get_file_value(val, AUTHORSHIP_LOOKUP)


@pytest.mark.parametrize(
    ("input_val", "expected"),
    [
        (("list", "node"), "http://rdfh.ch/lists/9999/n1"),
        (("list", ""), "list / "),
        (("list", None), "list"),
        ((None, "node"), "node"),
        (("", ""), " / "),
    ],
)
def test_get_list_value_str(input_val, expected):
    assert _get_list_value_str(input_val, LIST_LOOKUP) == expected


class TestRichtextStandoff:
    def test_get_all_stand_off_links_no_links(self):
        val_str = ParsedValue(HAS_PROP, "text", KnoraValueType.RICHTEXT_VALUE, None, None)
        val_none = ParsedValue(HAS_PROP, None, KnoraValueType.RICHTEXT_VALUE, None, None)
        result = _get_all_stand_off_links([val_none, val_str])
        assert not result

    def test_get_all_stand_off_links_(self, richtext_with_standoff, bool_value):
        result = _get_all_stand_off_links([richtext_with_standoff, richtext_with_standoff, bool_value])
        assert len(result) == 1
        prop_obj = result.pop(0)
        assert prop_obj.property_type == TriplePropertyType.KNORA_STANDOFF_LINK
        assert prop_obj.object_value == "link"
        assert prop_obj.object_type == TripleObjectType.INTERNAL_ID

    def test_get_resource_ids_and_iri_strings_none_found(self):
        txt = "text"
        result = _get_resource_ids_and_iri_strings(txt)
        assert not result

    def test_get_resource_ids_and_iri_strings_multiple_found(self):
        link = "IRI:link:IRI"
        res_link = "http://rdfh.ch/4123/DiAmYQzQSzC7cdTo6OJMYA"
        txt = (
            f'With <a class="salsah-link" href="{link}">link text</a>.'
            f'Some more text <a class="salsah-link" href="{link}">with the same link</a>.'
            f'Text with <a class="salsah-link" href="{res_link}"> stand off</a> to resource in DB.'
            f'Text with an external link: <a href="https://www.google.com/">Google</a>'
        )
        result = _get_resource_ids_and_iri_strings(txt)
        expected = {link, res_link}
        assert result == expected

    def test_get_link_string_and_triple_object_type_internal_link(self):
        link = "IRI:link:IRI"
        link_str, triple_type = _get_link_string_and_triple_object_type(link)
        assert link_str == "link"
        assert triple_type == TripleObjectType.INTERNAL_ID

    def test_get_link_string_and_triple_object_type_iri(self):
        link = "http://rdfh.ch/4123/DiAmYQzQSzC7cdTo6OJMYA"
        link_str, triple_type = _get_link_string_and_triple_object_type(link)
        assert link_str == link
        assert triple_type == TripleObjectType.IRI

    def test_get_link_string_and_triple_object_malformed_content(self):
        link = "malformed_content"
        link_str, triple_type = _get_link_string_and_triple_object_type(link)
        assert link_str == link
        assert triple_type == TripleObjectType.INTERNAL_ID


if __name__ == "__main__":
    pytest.main([__file__])
