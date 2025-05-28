# mypy: disable-error-code="method-assign,no-untyped-def"
import pytest
import regex

from dsp_tools.commands.xmlupload.models.lookup_models import XmlReferenceLookups
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.permission import PermissionValue
from dsp_tools.commands.xmlupload.models.processed.file_values import ProcessedFileValue
from dsp_tools.commands.xmlupload.models.processed.file_values import ProcessedIIIFUri
from dsp_tools.commands.xmlupload.models.processed.res import MigrationMetadata
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedBoolean
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedColor
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedDate
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedDecimal
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedGeometry
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedGeoname
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedInt
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedInterval
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedLink
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedList
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedRichtext
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedSimpleText
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedTime
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedUri
from dsp_tools.commands.xmlupload.prepare_xml_input.get_processed_resources import _get_file_metadata
from dsp_tools.commands.xmlupload.prepare_xml_input.get_processed_resources import (
    _get_file_metadata_for_test_environments,
)
from dsp_tools.commands.xmlupload.prepare_xml_input.get_processed_resources import _get_one_processed_value
from dsp_tools.commands.xmlupload.prepare_xml_input.get_processed_resources import _get_one_resource
from dsp_tools.commands.xmlupload.prepare_xml_input.get_processed_resources import _resolve_file_value
from dsp_tools.commands.xmlupload.prepare_xml_input.get_processed_resources import _resolve_permission
from dsp_tools.commands.xmlupload.prepare_xml_input.get_processed_resources import get_processed_resources
from dsp_tools.error.exceptions import XmlUploadAuthorshipsNotFoundError
from dsp_tools.error.exceptions import XmlUploadListNodeNotFoundError
from dsp_tools.error.exceptions import XmlUploadPermissionsNotFoundError
from dsp_tools.legacy_models.datetimestamp import DateTimeStamp
from dsp_tools.utils.data_formats.date_util import Date
from dsp_tools.utils.rdflib_constants import KNORA_API_STR
from dsp_tools.utils.xml_parsing.models.parsed_resource import KnoraValueType
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedFileValue
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedFileValueMetadata
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedMigrationMetadata
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedResource
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedValue

ONTO = "http://0.0.0.0:3333/ontology/9999/onto/v2#"
HAS_PROP = f"{ONTO}hasProp"
RES_TYPE = f"{ONTO}ResourceType"

IS_ON_PROD_LIKE_SERVER = True


@pytest.fixture
def lookups() -> XmlReferenceLookups:
    return XmlReferenceLookups(
        permissions={"open": Permissions({PermissionValue.CR: ["knora-admin:ProjectAdmin"]})},
        listnodes={
            ("list", "node"): "http://rdfh.ch/9999/node",
            ("", "http://rdfh.ch/9999/node"): "http://rdfh.ch/9999/node",
        },
        authorships={"auth_id": ["author"], "auth_id2": ["author1", "author2"]},
    )


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


class TestResources:
    def test_success(self, lookups):
        res = ParsedResource(
            res_id="id",
            res_type=RES_TYPE,
            label="lbl",
            permissions_id=None,
            values=[],
            file_value=None,
            migration_metadata=None,
        )
        result = get_processed_resources([res], lookups, IS_ON_PROD_LIKE_SERVER)
        assert len(result) == 1

    def test_failure(self, lookups: XmlReferenceLookups):
        res = ParsedResource(
            res_id="id",
            res_type=RES_TYPE,
            label="lbl",
            permissions_id="nonExisting",
            values=[],
            file_value=None,
            migration_metadata=None,
        )
        with pytest.raises(XmlUploadPermissionsNotFoundError):
            get_processed_resources([res], lookups, IS_ON_PROD_LIKE_SERVER)


class TestOneResource:
    def test_resource_one_value(self, bool_value, lookups: XmlReferenceLookups):
        res = ParsedResource(
            res_id="id",
            res_type=RES_TYPE,
            label="lbl",
            permissions_id=None,
            values=[bool_value],
            file_value=None,
            migration_metadata=None,
        )
        result = _get_one_resource(res, lookups, IS_ON_PROD_LIKE_SERVER)
        assert result.res_id == "id"
        assert result.type_iri == RES_TYPE
        assert result.label == "lbl"
        assert not result.permissions
        assert len(result.values) == 1
        assert not result.file_value
        assert not result.migration_metadata

    def test_resource_with_permissions(self, lookups: XmlReferenceLookups):
        res = ParsedResource(
            res_id="id",
            res_type=RES_TYPE,
            label="lbl",
            permissions_id="open",
            values=[],
            file_value=None,
            migration_metadata=None,
        )
        result = _get_one_resource(res, lookups, IS_ON_PROD_LIKE_SERVER)
        assert result.res_id == "id"
        assert result.type_iri == RES_TYPE
        assert result.label == "lbl"
        assert isinstance(result.permissions, Permissions)
        assert len(result.values) == 0
        assert not result.file_value
        assert not result.migration_metadata

    def test_with_ark(self, lookups: XmlReferenceLookups):
        parsed_metadata = ParsedMigrationMetadata(
            iri=None, ark="ark:/72163/4123-43xc6ivb931-a.2022829", creation_date="1999-12-31T23:59:59.9999999+01:00"
        )
        res = ParsedResource(
            res_id="id",
            res_type=RES_TYPE,
            label="lbl",
            permissions_id=None,
            values=[],
            file_value=None,
            migration_metadata=parsed_metadata,
        )
        result = _get_one_resource(res, lookups, IS_ON_PROD_LIKE_SERVER)
        assert result.res_id == "id"
        assert result.type_iri == RES_TYPE
        assert result.label == "lbl"
        assert not result.permissions
        assert len(result.values) == 0
        assert not result.file_value
        metadata = result.migration_metadata
        assert isinstance(metadata, MigrationMetadata)
        assert metadata.iri_str == "http://rdfh.ch/4123/5d5d1FKaUC2Wfl4zicggfg"
        assert metadata.creation_date == "1999-12-31T23:59:59.9999999+01:00"

    def test_with_iri(self, lookups: XmlReferenceLookups):
        parsed_metadata = ParsedMigrationMetadata(
            iri="http://rdfh.ch/4123/DiAmYQzQSzC7cdTo6OJMYA", ark=None, creation_date=None
        )
        res = ParsedResource(
            res_id="id",
            res_type=RES_TYPE,
            label="lbl",
            permissions_id=None,
            values=[],
            file_value=None,
            migration_metadata=parsed_metadata,
        )
        result = _get_one_resource(res, lookups, IS_ON_PROD_LIKE_SERVER)
        assert result.res_id == "id"
        assert result.type_iri == RES_TYPE
        assert result.label == "lbl"
        assert not result.permissions
        assert len(result.values) == 0
        assert not result.file_value
        metadata = result.migration_metadata
        assert isinstance(metadata, MigrationMetadata)
        assert metadata.iri_str == "http://rdfh.ch/4123/DiAmYQzQSzC7cdTo6OJMYA"
        assert not metadata.creation_date

    def test_resource_with_ark_and_iri(self, lookups: XmlReferenceLookups):
        parsed_metadata = ParsedMigrationMetadata(
            iri="http://rdfh.ch/4123/DiAmYQzQSzC7cdTo6OJMYA",
            ark="ark:/72163/4123-43xc6ivb931-a.2022829",
            creation_date="1999-12-31T23:59:59.9999999+01:00",
        )
        res = ParsedResource(
            res_id="id",
            res_type=RES_TYPE,
            label="lbl",
            permissions_id=None,
            values=[],
            file_value=None,
            migration_metadata=parsed_metadata,
        )
        result = _get_one_resource(res, lookups, IS_ON_PROD_LIKE_SERVER)
        assert result.res_id == "id"
        assert result.type_iri == RES_TYPE
        assert result.label == "lbl"
        assert not result.permissions
        assert len(result.values) == 0
        assert not result.file_value
        metadata = result.migration_metadata
        assert isinstance(metadata, MigrationMetadata)
        assert metadata.iri_str == "http://rdfh.ch/4123/5d5d1FKaUC2Wfl4zicggfg"
        time_stamp = metadata.creation_date
        assert isinstance(time_stamp, DateTimeStamp)
        assert time_stamp == DateTimeStamp("1999-12-31T23:59:59.9999999+01:00")

    def test_unknown_permission(self, lookups: XmlReferenceLookups):
        msg = regex.escape(r"Could not find permissions for value: unknown")
        res = ParsedResource(
            res_id="id",
            res_type=RES_TYPE,
            label="lbl",
            permissions_id="unknown",
            values=[],
            file_value=None,
            migration_metadata=None,
        )
        with pytest.raises(XmlUploadPermissionsNotFoundError, match=msg):
            _get_one_resource(res, lookups, IS_ON_PROD_LIKE_SERVER)

    def test_with_file_value(self, file_with_permission, lookups: XmlReferenceLookups):
        res = ParsedResource(
            res_id="id",
            res_type=RES_TYPE,
            label="lbl",
            permissions_id=None,
            values=[],
            file_value=file_with_permission,
            migration_metadata=None,
        )
        result = _get_one_resource(res, lookups, IS_ON_PROD_LIKE_SERVER)
        assert result.res_id == "id"
        assert result.type_iri == RES_TYPE
        assert result.label == "lbl"
        assert not result.permissions
        assert len(result.values) == 0
        file_val = result.file_value
        assert isinstance(file_val, ProcessedFileValue)
        assert file_val.value == "file.jpg"
        assert file_val.metadata.permissions
        assert not result.iiif_uri
        assert not result.migration_metadata

    def test_with_file_value_not_on_prod_missing_legal_info(self, lookups: XmlReferenceLookups):
        metadata = ParsedFileValueMetadata(None, None, None, None)
        parsed_file = ParsedFileValue("file.jpg", KnoraValueType.STILL_IMAGE_FILE, metadata)
        res = ParsedResource(
            res_id="id",
            res_type=RES_TYPE,
            label="lbl",
            permissions_id=None,
            values=[],
            file_value=parsed_file,
            migration_metadata=None,
        )
        result = _get_one_resource(res, lookups, is_on_prod_like_server=False)
        assert result.res_id == "id"
        assert result.type_iri == RES_TYPE
        assert result.label == "lbl"
        assert not result.permissions
        assert len(result.values) == 0
        file_val = result.file_value
        assert isinstance(file_val, ProcessedFileValue)
        assert file_val.value == "file.jpg"
        assert not file_val.metadata.permissions
        assert file_val.metadata.copyright_holder == "DUMMY"
        assert file_val.metadata.authorships == ["DUMMY"]
        assert file_val.metadata.license_iri == "http://rdfh.ch/licenses/unknown"
        assert not result.iiif_uri
        assert not result.migration_metadata

    def test_with_iiif_uri(self, iiif_file_value, lookups: XmlReferenceLookups):
        res = ParsedResource(
            res_id="id",
            res_type=RES_TYPE,
            label="lbl",
            permissions_id=None,
            values=[],
            file_value=iiif_file_value,
            migration_metadata=None,
        )
        result = _get_one_resource(res, lookups, IS_ON_PROD_LIKE_SERVER)
        assert result.res_id == "id"
        assert result.type_iri == RES_TYPE
        assert result.label == "lbl"
        assert not result.permissions
        assert len(result.values) == 0
        assert not result.file_value
        assert isinstance(result.iiif_uri, ProcessedIIIFUri)
        assert not result.migration_metadata


class TestFileValue:
    def test_resolve_file_value_iiif(self, iiif_file_value, lookups):
        resource = ParsedResource(
            res_id="id",
            res_type=RES_TYPE,
            label="lbl",
            permissions_id=None,
            values=[],
            file_value=iiif_file_value,
            migration_metadata=None,
        )
        file_res, iiif_res = _resolve_file_value(resource, lookups, IS_ON_PROD_LIKE_SERVER)
        assert file_res is None
        assert isinstance(iiif_res, ProcessedIIIFUri)
        result_metadata = iiif_res.metadata
        assert not result_metadata.permissions
        assert iiif_res.value == iiif_file_value.value
        assert result_metadata.license_iri == "http://rdfh.ch/licenses/cc-by-nc-4.0"
        assert result_metadata.copyright_holder == "copy"
        assert result_metadata.authorships == ["author"]

    def test_resolve_file_value_none(self, lookups):
        resource = ParsedResource(
            res_id="id",
            res_type=RES_TYPE,
            label="lbl",
            permissions_id=None,
            values=[],
            file_value=None,
            migration_metadata=None,
        )
        file_res, iiif_res = _resolve_file_value(resource, lookups, IS_ON_PROD_LIKE_SERVER)
        assert file_res is None
        assert iiif_res is None

    def test_resolve_file_value_file(self, file_with_permission, lookups):
        resource = ParsedResource(
            res_id="id",
            res_type=RES_TYPE,
            label="lbl",
            permissions_id=None,
            values=[],
            file_value=file_with_permission,
            migration_metadata=None,
        )
        file_res, iiif_res = _resolve_file_value(resource, lookups, IS_ON_PROD_LIKE_SERVER)
        assert iiif_res is None
        assert isinstance(file_res, ProcessedFileValue)
        result_metadata = file_res.metadata
        assert file_res.value == file_res.value
        assert file_res.file_type == file_with_permission.value_type
        assert isinstance(result_metadata.permissions, Permissions)
        assert result_metadata.license_iri == "http://rdfh.ch/licenses/cc-by-nc-4.0"
        assert result_metadata.copyright_holder == "copy"
        assert result_metadata.authorships == ["author"]


class TestFileMetadata:
    def test_prod_good_with_permissions(self, lookups):
        metadata = ParsedFileValueMetadata("http://rdfh.ch/licenses/cc-by-nc-4.0", "copy", "auth_id", "open")
        result_metadata = _get_file_metadata(metadata, lookups)
        assert isinstance(result_metadata.permissions, Permissions)
        assert result_metadata.license_iri == "http://rdfh.ch/licenses/cc-by-nc-4.0"
        assert result_metadata.copyright_holder == "copy"
        assert result_metadata.authorships == ["author"]

    def test_prod_good_without_permissions(self, lookups):
        metadata = ParsedFileValueMetadata("http://rdfh.ch/licenses/cc-by-nc-4.0", "copy", "auth_id2", None)
        result_metadata = _get_file_metadata(metadata, lookups)
        assert not result_metadata.permissions
        assert result_metadata.license_iri == "http://rdfh.ch/licenses/cc-by-nc-4.0"
        assert result_metadata.copyright_holder == "copy"
        assert result_metadata.authorships
        assert set(result_metadata.authorships) == {"author1", "author2"}

    def test_prod_with_unknown_authorship_id(self, lookups: XmlReferenceLookups):
        metadata = ParsedFileValueMetadata("http://rdfh.ch/licenses/cc-by-nc-4.0", "copy", "unkown_auth_id", None)
        with pytest.raises(XmlUploadAuthorshipsNotFoundError):
            _get_file_metadata(metadata, lookups)

    def test_get_file_metadata_for_test_environments_no_values(self, lookups):
        metadata = ParsedFileValueMetadata(None, None, None, None)
        result_metadata = _get_file_metadata_for_test_environments(metadata, lookups)
        assert not result_metadata.permissions
        assert result_metadata.license_iri == "http://rdfh.ch/licenses/unknown"
        assert result_metadata.copyright_holder == "DUMMY"
        assert result_metadata.authorships == ["DUMMY"]

    def test_get_file_metadata_for_test_environments_some_values(self, lookups):
        metadata = ParsedFileValueMetadata(None, "copy", None, None)
        result_metadata = _get_file_metadata_for_test_environments(metadata, lookups)
        assert not result_metadata.permissions
        assert result_metadata.license_iri == "http://rdfh.ch/licenses/unknown"
        assert result_metadata.copyright_holder == "copy"
        assert result_metadata.authorships == ["DUMMY"]

    def test_get_file_metadata_for_test_environments_all_values(self, lookups):
        metadata = ParsedFileValueMetadata("http://rdfh.ch/licenses/cc-by-nc-4.0", "copy", "auth_id", "open")
        result_metadata = _get_file_metadata_for_test_environments(metadata, lookups)
        assert isinstance(result_metadata.permissions, Permissions)
        assert result_metadata.license_iri == "http://rdfh.ch/licenses/cc-by-nc-4.0"
        assert result_metadata.copyright_holder == "copy"
        assert result_metadata.authorships == ["author"]


class TestValues:
    def test_bool_value(self, bool_value, lookups: XmlReferenceLookups):
        result = _get_one_processed_value(bool_value, lookups)
        assert isinstance(result, ProcessedBoolean)
        assert result.value == True  # noqa:E712 (Avoid equality comparisons)
        assert result.prop_iri == HAS_PROP
        assert not result.permissions
        assert not result.comment

    def test_bool_value_with_comment(self, lookups: XmlReferenceLookups):
        val = ParsedValue(HAS_PROP, "false", KnoraValueType.BOOLEAN_VALUE, None, "comment")
        result = _get_one_processed_value(val, lookups)
        assert result.value == False  # noqa:E712 (Avoid equality comparisons)
        assert result.prop_iri == HAS_PROP
        assert not result.permissions
        assert result.comment == "comment"

    def test_bool_value_with_permissions(self, lookups: XmlReferenceLookups):
        val = ParsedValue(HAS_PROP, "true", KnoraValueType.BOOLEAN_VALUE, "open", None)
        result = _get_one_processed_value(val, lookups)
        assert result.value == True  # noqa:E712 (Avoid equality comparisons)
        assert result.prop_iri == HAS_PROP
        assert isinstance(result.permissions, Permissions)
        assert not result.comment

    def test_bool_value_with_non_existing_permissions(self, lookups: XmlReferenceLookups):
        val = ParsedValue(HAS_PROP, "true", KnoraValueType.BOOLEAN_VALUE, "nonExisting", None)
        with pytest.raises(XmlUploadPermissionsNotFoundError):
            _get_one_processed_value(val, lookups)

    def test_color_value(self, lookups: XmlReferenceLookups):
        val = ParsedValue(HAS_PROP, "#5d1f1e", KnoraValueType.COLOR_VALUE, None, None)
        result = _get_one_processed_value(val, lookups)
        assert isinstance(result, ProcessedColor)
        assert result.value == "#5d1f1e"
        assert result.prop_iri == HAS_PROP
        assert not result.permissions
        assert not result.comment

    def test_date_value(self, lookups: XmlReferenceLookups):
        val = ParsedValue(HAS_PROP, "CE:1849:CE:1850", KnoraValueType.DATE_VALUE, None, None)
        result = _get_one_processed_value(val, lookups)
        assert isinstance(result, ProcessedDate)
        assert isinstance(result.value, Date)
        assert result.prop_iri == HAS_PROP
        assert not result.permissions
        assert not result.comment

    def test_decimal_value(self, lookups: XmlReferenceLookups):
        val = ParsedValue(HAS_PROP, "1.4", KnoraValueType.DECIMAL_VALUE, None, None)
        result = _get_one_processed_value(val, lookups)
        assert isinstance(result, ProcessedDecimal)
        assert result.value == 1.4
        assert result.prop_iri == HAS_PROP
        assert not result.permissions
        assert not result.comment

    def test_geometry_value(self, lookups: XmlReferenceLookups):
        val = ParsedValue(f"{KNORA_API_STR}hasGeometry", "{}", KnoraValueType.GEOM_VALUE, None, None)
        result = _get_one_processed_value(val, lookups)
        assert isinstance(result, ProcessedGeometry)
        assert result.value == "{}"
        assert result.prop_iri == f"{KNORA_API_STR}hasGeometry"
        assert not result.permissions
        assert not result.comment

    def test_geoname_value(self, lookups: XmlReferenceLookups):
        val = ParsedValue(HAS_PROP, "5416656", KnoraValueType.GEONAME_VALUE, None, None)
        result = _get_one_processed_value(val, lookups)
        assert isinstance(result, ProcessedGeoname)
        assert result.value == "5416656"
        assert result.prop_iri == HAS_PROP
        assert not result.permissions
        assert not result.comment

    def test_integer_value(self, lookups: XmlReferenceLookups):
        val = ParsedValue(HAS_PROP, "1", KnoraValueType.INT_VALUE, None, None)
        result = _get_one_processed_value(val, lookups)
        assert isinstance(result, ProcessedInt)
        assert result.value == 1
        assert result.prop_iri == HAS_PROP
        assert not result.permissions
        assert not result.comment

    def test_interval_value(self, lookups: XmlReferenceLookups):
        val = ParsedValue(f"{KNORA_API_STR}hasSegmentBounds", ("1", "2"), KnoraValueType.INTERVAL_VALUE, None, None)
        result = _get_one_processed_value(val, lookups)
        assert isinstance(result, ProcessedInterval)
        assert result.value.start == 1.0
        assert result.value.end == 2.0
        assert result.prop_iri == f"{KNORA_API_STR}hasSegmentBounds"
        assert not result.permissions
        assert not result.comment

    def test_list_value(self, lookups: XmlReferenceLookups):
        val = ParsedValue(HAS_PROP, ("list", "node"), KnoraValueType.LIST_VALUE, "open", "cmt")
        result = _get_one_processed_value(val, lookups)
        assert isinstance(result, ProcessedList)
        assert result.value == "http://rdfh.ch/9999/node"
        assert result.prop_iri == HAS_PROP
        assert isinstance(result.permissions, Permissions)
        assert result.comment == "cmt"

    def test_list_value_raises(self, lookups: XmlReferenceLookups):
        val = ParsedValue(HAS_PROP, ("unknown", "unknown"), KnoraValueType.LIST_VALUE, None, None)
        with pytest.raises(XmlUploadListNodeNotFoundError):
            _get_one_processed_value(val, lookups)

    def test_list_value_with_iri(self, lookups: XmlReferenceLookups):
        val = ParsedValue(HAS_PROP, ("", "http://rdfh.ch/9999/node"), KnoraValueType.LIST_VALUE, "open", "cmt")
        result = _get_one_processed_value(val, lookups)
        assert isinstance(result, ProcessedList)
        assert result.value == "http://rdfh.ch/9999/node"
        assert result.prop_iri == HAS_PROP
        assert isinstance(result.permissions, Permissions)
        assert result.comment == "cmt"

    def test_simple_text_value(self, lookups: XmlReferenceLookups):
        val = ParsedValue(HAS_PROP, "text", KnoraValueType.SIMPLETEXT_VALUE, None, None)
        result = _get_one_processed_value(val, lookups)
        assert isinstance(result, ProcessedSimpleText)
        assert result.value == "text"
        assert result.prop_iri == HAS_PROP
        assert not result.permissions
        assert not result.comment

    def test_richtext_value(self, lookups: XmlReferenceLookups):
        text_str = "<text>this is text</text>"
        val = ParsedValue(HAS_PROP, text_str, KnoraValueType.RICHTEXT_VALUE, "open", "cmt")
        result = _get_one_processed_value(val, lookups)
        assert isinstance(result, ProcessedRichtext)
        assert result.value.xmlstr == text_str
        assert result.prop_iri == HAS_PROP
        assert isinstance(result.permissions, Permissions)
        assert result.comment == "cmt"
        assert result.resource_references == set()

    def test_richtext_value_with_standoff(self, lookups: XmlReferenceLookups):
        text_str = 'Comment with <a class="salsah-link" href="IRI:link:IRI">link text</a>.'
        val = ParsedValue(HAS_PROP, text_str, KnoraValueType.RICHTEXT_VALUE, "open", "cmt")
        result = _get_one_processed_value(val, lookups)
        assert isinstance(result, ProcessedRichtext)
        assert result.value.xmlstr == text_str
        assert result.prop_iri == HAS_PROP
        assert isinstance(result.permissions, Permissions)
        assert result.comment == "cmt"
        assert result.resource_references == {"link"}

    def test_link_value(self, lookups: XmlReferenceLookups):
        val = ParsedValue(HAS_PROP, "other_id", KnoraValueType.LINK_VALUE, "open", "cmt")
        result = _get_one_processed_value(val, lookups)
        assert isinstance(result, ProcessedLink)
        assert result.value == "other_id"
        assert result.prop_iri == f"{HAS_PROP}Value"
        assert isinstance(result.permissions, Permissions)
        assert result.comment == "cmt"

    def test_time_value(self, lookups: XmlReferenceLookups):
        val = ParsedValue(HAS_PROP, "2019-10-23T13:45:12.01-14:00", KnoraValueType.TIME_VALUE, None, None)
        result = _get_one_processed_value(val, lookups)
        assert isinstance(result, ProcessedTime)
        assert result.value == "2019-10-23T13:45:12.01-14:00"
        assert result.prop_iri == HAS_PROP
        assert not result.permissions
        assert not result.comment

    def test_uri_value(self, lookups: XmlReferenceLookups):
        val = ParsedValue(HAS_PROP, "https://dasch.swiss", KnoraValueType.URI_VALUE, None, None)
        result = _get_one_processed_value(val, lookups)
        assert isinstance(result, ProcessedUri)
        assert result.value == "https://dasch.swiss"
        assert result.prop_iri == HAS_PROP
        assert not result.permissions
        assert not result.comment


class TestPermissions:
    def test_good(self, lookups):
        result = _resolve_permission("open", lookups.permissions)
        assert isinstance(result, Permissions)
        assert str(result) == "CR knora-admin:ProjectAdmin"

    def test_none(self, lookups):
        result = _resolve_permission(None, lookups.permissions)
        assert not result

    def test_empty_string(self, lookups):
        result = _resolve_permission("", lookups.permissions)
        assert not result

    def test_raises(self, lookups):
        msg = regex.escape("Could not find permissions for value: inexistent")
        with pytest.raises(XmlUploadPermissionsNotFoundError, match=msg):
            _resolve_permission("inexistent", lookups.permissions)
