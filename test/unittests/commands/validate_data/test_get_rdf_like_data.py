# mypy: disable-error-code="method-assign,no-untyped-def"

import pytest

from dsp_tools.commands.validate_data.get_rdf_like_data import _get_file_metadata
from dsp_tools.commands.validate_data.get_rdf_like_data import _get_file_value
from dsp_tools.commands.validate_data.get_rdf_like_data import _get_list_value_str
from dsp_tools.commands.validate_data.get_rdf_like_data import _get_one_resource
from dsp_tools.commands.validate_data.get_rdf_like_data import _get_one_value
from dsp_tools.commands.validate_data.get_rdf_like_data import get_rdf_like_data
from dsp_tools.commands.validate_data.models.rdf_like_data import PropertyObject
from dsp_tools.commands.validate_data.models.rdf_like_data import RdfLikeResource
from dsp_tools.commands.validate_data.models.rdf_like_data import RdfLikeValue
from dsp_tools.commands.validate_data.models.rdf_like_data import TripleObjectType
from dsp_tools.commands.validate_data.models.rdf_like_data import TriplePropertyType
from dsp_tools.utils.rdflib_constants import KNORA_API_STR
from dsp_tools.utils.xml_parsing.models.parsed_resource import KnoraValueType
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedFileValue
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedFileValueMetadata
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

    def test_empty_permissions(self):
        res = ParsedResource(
            res_id="one",
            res_type=RES_TYPE,
            label="lbl",
            permissions_id="open",
            values=[],
            file_value=None,
            migration_metadata=None,
        )
        result = _get_one_resource(res)
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
        result_list = get_rdf_like_data([res])
        assert len(result_list.resources) == 1
        result = result_list.resources.pop(0)
        assert result.res_id == "one"
        assert len(result.property_objects) == 2
        assert not result.asset_value
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
        result = _get_one_resource(res)
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
        result = _get_one_resource(res)
        assert result.res_id == "one"
        assert len(result.property_objects) == 3
        assert not result.asset_value
        lbl, rdf_type, _ = _get_label_and_type(result)
        assert lbl.object_value == "lbl"
        assert lbl.object_type == TripleObjectType.STRING
        assert rdf_type.object_value == RES_TYPE
        assert rdf_type.object_type == TripleObjectType.IRI
        standoff = next(x for x in result.property_objects if x.property_type == TriplePropertyType.KNORA_STANDOFF_LINK)
        assert standoff.object_value == "link"
        assert standoff.object_type == TripleObjectType.IRI
        assert len(result.values) == 1


class TestValues:
    def test_boolean_corr(self):
        val = ParsedValue(HAS_PROP, "true", KnoraValueType.BOOLEAN_VALUE, None, None)
        res = _get_one_value(val)
        assert res.user_facing_prop == HAS_PROP
        assert res.user_facing_value == "true"
        assert res.knora_type == KnoraValueType.BOOLEAN_VALUE
        assert not res.value_metadata

    def test_boolean_with_comment_corr(self):
        val = ParsedValue(HAS_PROP, "true", KnoraValueType.BOOLEAN_VALUE, None, "comment")
        res = _get_one_value(val)
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
        res = _get_one_value(val)
        assert res.user_facing_prop == HAS_PROP
        assert res.user_facing_value == "true"
        assert res.knora_type == KnoraValueType.BOOLEAN_VALUE
        assert len(res.value_metadata) == 1
        metadata = res.value_metadata.pop(0)
        assert metadata.property_type == TriplePropertyType.KNORA_COMMENT_ON_VALUE
        assert metadata.object_value == ""
        assert metadata.object_type == TripleObjectType.STRING

    def test_boolean_with_permissions_corr(self):
        val = ParsedValue(HAS_PROP, "true", KnoraValueType.BOOLEAN_VALUE, "open", None)
        res = _get_one_value(val)
        assert res.user_facing_prop == HAS_PROP
        assert res.user_facing_value == "true"
        assert res.knora_type == KnoraValueType.BOOLEAN_VALUE
        assert len(res.value_metadata) == 1
        metadata = res.value_metadata.pop(0)
        assert metadata.property_type == TriplePropertyType.KNORA_PERMISSIONS
        assert metadata.object_value == "open"
        assert metadata.object_type == TripleObjectType.STRING

    def test_boolean_none(self):
        val = ParsedValue(HAS_PROP, None, KnoraValueType.BOOLEAN_VALUE, None, None)
        res = _get_one_value(val)
        assert res.user_facing_prop == HAS_PROP
        assert res.user_facing_value == None  # noqa: E711 Comparison to `None`
        assert res.knora_type == KnoraValueType.BOOLEAN_VALUE
        assert not res.value_metadata

    def test_color_corr(self):
        val = ParsedValue(HAS_PROP, "#5d1f1e", KnoraValueType.COLOR_VALUE, None, None)
        res = _get_one_value(val)
        assert res.user_facing_prop == HAS_PROP
        assert res.user_facing_value == "#5d1f1e"
        assert res.knora_type == KnoraValueType.COLOR_VALUE
        assert not res.value_metadata

    def test_date_corr(self):
        val = ParsedValue(HAS_PROP, "CE:1849:CE:1850", KnoraValueType.DATE_VALUE, None, None)
        res = _get_one_value(val)
        assert res.user_facing_prop == HAS_PROP
        assert res.user_facing_value == "CE:1849:CE:1850"
        assert res.knora_type == KnoraValueType.DATE_VALUE
        assert not res.value_metadata

    def test_decimal_corr(self):
        val = ParsedValue(HAS_PROP, "1.4", KnoraValueType.DECIMAL_VALUE, None, None)
        res = _get_one_value(val)
        assert res.user_facing_prop == HAS_PROP
        assert res.user_facing_value == "1.4"
        assert res.knora_type == KnoraValueType.DECIMAL_VALUE
        assert not res.value_metadata

    def test_geoname_corr(self):
        val = ParsedValue(HAS_PROP, "1111111", KnoraValueType.GEONAME_VALUE, None, None)
        res = _get_one_value(val)
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
        res = _get_one_value(val)
        assert res.user_facing_prop == f"{KNORA_API_STR}hasGeometry"
        assert res.user_facing_value is not None
        assert res.knora_type == KnoraValueType.GEOM_VALUE
        assert not res.value_metadata

    def test_geom_wrong(self):
        val = ParsedValue(f"{KNORA_API_STR}hasGeometry", "invalid", KnoraValueType.GEOM_VALUE, None, None)
        res = _get_one_value(val)
        assert res.user_facing_prop == f"{KNORA_API_STR}hasGeometry"
        assert res.user_facing_value == None  # noqa: E711 Comparison to `None`
        assert res.knora_type == KnoraValueType.GEOM_VALUE
        assert not res.value_metadata

    def test_geom_none(self):
        val = ParsedValue(f"{KNORA_API_STR}hasGeometry", None, KnoraValueType.GEOM_VALUE, None, None)
        res = _get_one_value(val)
        assert res.user_facing_prop == f"{KNORA_API_STR}hasGeometry"
        assert res.user_facing_value == None  # noqa: E711 Comparison to `None`
        assert res.knora_type == KnoraValueType.GEOM_VALUE
        assert not res.value_metadata

    def test_int_corr(self):
        val = ParsedValue(HAS_PROP, "1", KnoraValueType.INT_VALUE, None, None)
        res = _get_one_value(val)
        assert res.user_facing_prop == HAS_PROP
        assert res.user_facing_value == "1"
        assert res.knora_type == KnoraValueType.INT_VALUE
        assert not res.value_metadata

    def test_interval_corr(self):
        val = ParsedValue(f"{KNORA_API_STR}hasSegmentBounds", ("1", "2"), KnoraValueType.INTERVAL_VALUE, None, None)
        res = _get_one_value(val)
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
        res = _get_one_value(val)
        assert res.user_facing_prop == HAS_PROP
        assert res.user_facing_value == "list / node"
        assert res.knora_type == KnoraValueType.LIST_VALUE
        assert not res.value_metadata

    def test_list_none(self):
        val = ParsedValue(HAS_PROP, ("list", None), KnoraValueType.LIST_VALUE, None, None)
        res = _get_one_value(val)
        assert res.user_facing_prop == HAS_PROP
        assert res.user_facing_value == "list"
        assert res.knora_type == KnoraValueType.LIST_VALUE
        assert not res.value_metadata

    def test_link_corr(self):
        val = ParsedValue(HAS_PROP, "other_id", KnoraValueType.LINK_VALUE, None, None)
        res = _get_one_value(val)
        assert res.user_facing_prop == HAS_PROP
        assert res.user_facing_value == "other_id"
        assert res.knora_type == KnoraValueType.LINK_VALUE
        assert not res.value_metadata

    def test_simple_text_corr(self):
        val = ParsedValue(HAS_PROP, "text", KnoraValueType.SIMPLETEXT_VALUE, None, None)
        res = _get_one_value(val)
        assert res.user_facing_prop == HAS_PROP
        assert res.user_facing_value == "text"
        assert res.knora_type == KnoraValueType.SIMPLETEXT_VALUE
        assert not res.value_metadata

    def test_simple_text_wrong(self):
        val = ParsedValue(HAS_PROP, None, KnoraValueType.SIMPLETEXT_VALUE, None, None)
        res = _get_one_value(val)
        assert res.user_facing_prop == HAS_PROP
        assert res.user_facing_value == None  # noqa: E711 Comparison to `None`
        assert res.knora_type == KnoraValueType.SIMPLETEXT_VALUE
        assert not res.value_metadata

    def test_richtext_corr(self):
        val = ParsedValue(HAS_PROP, "<p>Text</p>", KnoraValueType.RICHTEXT_VALUE, None, None)
        res = _get_one_value(val)
        assert res.user_facing_prop == HAS_PROP
        assert res.user_facing_value == "<p>Text</p>"
        assert res.knora_type == KnoraValueType.RICHTEXT_VALUE
        assert not res.value_metadata

    def test_richtext_with_standoff(self, richtext_with_standoff):
        res = _get_one_value(richtext_with_standoff)
        assert res.user_facing_prop == HAS_PROP
        assert res.user_facing_value == 'With <a class="salsah-link" href="IRI:link:IRI">link text</a>.'
        assert res.knora_type == KnoraValueType.RICHTEXT_VALUE
        assert not res.value_metadata

    def test_time_corr(self):
        val = ParsedValue(HAS_PROP, "2019-10-23T13:45:12.01-14:00", KnoraValueType.TIME_VALUE, None, None)
        res = _get_one_value(val)
        assert res.user_facing_prop == HAS_PROP
        assert res.user_facing_value == "2019-10-23T13:45:12.01-14:00"
        assert res.knora_type == KnoraValueType.TIME_VALUE
        assert not res.value_metadata

    def test_uri_corr(self):
        val = ParsedValue(HAS_PROP, "https://dasch.swiss", KnoraValueType.URI_VALUE, None, None)
        res = _get_one_value(val)
        assert res.user_facing_prop == HAS_PROP
        assert res.user_facing_value == "https://dasch.swiss"
        assert res.knora_type == KnoraValueType.URI_VALUE
        assert not res.value_metadata


class TestFileValue:
    def test_iiif(self):
        metadata = ParsedFileValueMetadata(None, None, None, None)
        val = ParsedFileValue("https://this/is/a/uri.jpg", KnoraValueType.STILL_IMAGE_IIIF, metadata)
        res = _get_file_value(val)
        assert isinstance(res, RdfLikeValue)
        assert res.user_facing_prop == f"{KNORA_API_STR}hasStillImageFileValue"
        assert res.user_facing_value == "https://this/is/a/uri.jpg"
        assert res.knora_type == KnoraValueType.STILL_IMAGE_IIIF
        assert not res.value_metadata

    def test_iiif_with_legal_info(self):
        metadata = ParsedFileValueMetadata("http://rdfh.ch/licenses/cc-by-nc-4.0", "copy", "auth_id", None)
        result = _get_file_metadata(metadata)
        assert len(result) == 3
        license_res = next(x for x in result if x.property_type == TriplePropertyType.KNORA_LICENSE)
        assert license_res.object_value == "http://rdfh.ch/licenses/cc-by-nc-4.0"
        assert license_res.object_type == TripleObjectType.IRI
        author_res = next(x for x in result if x.property_type == TriplePropertyType.KNORA_AUTHORSHIP)
        assert author_res.object_value == "auth_id"
        assert author_res.object_type == TripleObjectType.STRING
        copyright_res = next(x for x in result if x.property_type == TriplePropertyType.KNORA_COPYRIGHT_HOLDER)
        assert copyright_res.object_value == "copy"
        assert copyright_res.object_type == TripleObjectType.STRING

    def test_no_file(self):
        metadata = ParsedFileValueMetadata(None, None, None, None)
        val = ParsedFileValue(None, None, metadata)
        assert not _get_file_value(val)

    def test_unknown_extension(self):
        metadata = ParsedFileValueMetadata(None, None, None, None)
        val = ParsedFileValue("unknown.extension", None, metadata)
        assert not _get_file_value(val)


@pytest.mark.parametrize(
    ("input_val", "expected"),
    [
        (("list", "node"), "list / node"),
        ("not a tuple", None),
        (("list", ""), "list / "),
        (("list", None), "list"),
        ((None, "node"), "node"),
        (("", ""), " / "),
    ],
)
def test_get_list_value_str(input_val, expected):
    assert _get_list_value_str(input_val) == expected


if __name__ == "__main__":
    pytest.main([__file__])
