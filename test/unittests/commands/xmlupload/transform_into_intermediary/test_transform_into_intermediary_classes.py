# mypy: disable-error-code="method-assign,no-untyped-def"
import pytest
import regex

from dsp_tools.commands.xmlupload.models.formatted_text_value import FormattedTextValue
from dsp_tools.commands.xmlupload.models.intermediary.file_values import IntermediaryFileValue
from dsp_tools.commands.xmlupload.models.intermediary.file_values import IntermediaryIIIFUri
from dsp_tools.commands.xmlupload.models.intermediary.res import IntermediaryResource
from dsp_tools.commands.xmlupload.models.intermediary.res import MigrationMetadata
from dsp_tools.commands.xmlupload.models.intermediary.res import ResourceInputConversionFailure
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryBoolean
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryColor
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryDate
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryDecimal
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryGeoname
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryInt
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryLink
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryList
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryRichtext
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediarySimpleText
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryTime
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryUri
from dsp_tools.commands.xmlupload.models.lookup_models import IntermediaryLookups
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.permission import PermissionValue
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_into_intermediary_classes import _get_metadata
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_into_intermediary_classes import _transform_file_value
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_into_intermediary_classes import _transform_iiif_uri_value
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_into_intermediary_classes import (
    _transform_into_intermediary_resource,
)
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_into_intermediary_classes import _transform_one_resource
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_into_intermediary_classes import _transform_one_value
from dsp_tools.error.exceptions import InputError
from dsp_tools.error.exceptions import PermissionNotExistsError
from dsp_tools.legacy_models.datetimestamp import DateTimeStamp
from dsp_tools.utils.data_formats.date_util import Date
from dsp_tools.utils.xml_parsing.models.parsed_resource import KnoraValueType
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedValue

ONTO = "http://0.0.0.0:3333/ontology/9999/onto/v2#"
HAS_PROP = f"{ONTO}hasProp"


@pytest.fixture
def lookups() -> IntermediaryLookups:
    return IntermediaryLookups(
        permissions={"open": Permissions({PermissionValue.CR: ["knora-admin:ProjectAdmin"]})},
        listnodes={("list", "node"): "http://rdfh.ch/9999/node"},
        namespaces={
            "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
            "onto": "http://0.0.0.0:3333/ontology/9999/onto/v2#",
        },
        authorships={"auth_id": ["author"]},
    )


class TestTransformResources:
    def test_success(
        self,
    ):
        result = _transform_into_intermediary_resource(resource_one_prop, lookups)
        assert isinstance(result, IntermediaryResource)

    def test_failure(self, lookups: IntermediaryLookups):
        val = ParsedValue(HAS_PROP, "", KnoraValueType, "", "")
        result = _transform_into_intermediary_resource(resource_with_unknown_permissions, lookups)
        assert isinstance(result, ResourceInputConversionFailure)
        assert result.resource_id == "id"
        assert result.failure_msg == "Could not find permissions for value: nonExisting"


class TestTransformOneResource:
    def test_resource_one_value(self, lookups: IntermediaryLookups):
        val = ParsedValue(HAS_PROP, "", KnoraValueType, "", "")
        result = _transform_one_resource(resource_one_prop, lookups)
        assert result.res_id == "id"
        assert result.type_iri == f"{ONTO}ResourceType"
        assert result.label == "lbl"
        assert not result.permissions
        assert len(result.values) == 1
        assert not result.file_value
        assert not result.migration_metadata

    def test_resource_with_permissions(self, lookups: IntermediaryLookups):
        val = ParsedValue(HAS_PROP, "", KnoraValueType, "", "")
        result = _transform_one_resource(resource_with_permissions, lookups)
        assert result.res_id == "id"
        assert result.type_iri == f"{ONTO}ResourceType"
        assert result.label == "lbl"
        assert isinstance(result.permissions, Permissions)
        assert len(result.values) == 0
        assert not result.file_value
        assert not result.migration_metadata

    def test_with_ark(self, lookups: IntermediaryLookups):
        val = ParsedValue(HAS_PROP, "", KnoraValueType, "", "")
        result = _transform_one_resource(resource_with_ark, lookups)
        assert result.res_id == "id"
        assert result.type_iri == f"{ONTO}ResourceType"
        assert result.label == "lbl"
        assert not result.permissions
        assert len(result.values) == 0
        assert not result.file_value
        metadata = result.migration_metadata
        assert isinstance(metadata, MigrationMetadata)
        assert metadata.iri_str == "http://rdfh.ch/4123/5d5d1FKaUC2Wfl4zicggfg"
        assert metadata.creation_date == "1999-12-31T23:59:59.9999999+01:00"

    def test_with_iri(self, lookups: IntermediaryLookups):
        val = ParsedValue(HAS_PROP, "", KnoraValueType, "", "")
        result = _transform_one_resource(resource_with_iri, lookups)
        assert result.res_id == "id"
        assert result.type_iri == f"{ONTO}ResourceType"
        assert result.label == "lbl"
        assert not result.permissions
        assert len(result.values) == 0
        assert not result.file_value
        metadata = result.migration_metadata
        assert isinstance(metadata, MigrationMetadata)
        assert metadata.iri_str == "http://rdfh.ch/4123/DiAmYQzQSzC7cdTo6OJMYA"
        assert not metadata.creation_date

    def test_resource_with_ark_and_iri(self, lookups: IntermediaryLookups):
        val = ParsedValue(HAS_PROP, "", KnoraValueType, "", "")
        result = _transform_one_resource(resource_with_ark_and_iri, lookups)
        assert result.res_id == "id"
        assert result.type_iri == f"{ONTO}ResourceType"
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

    def test_unknown_permission(self, lookups: IntermediaryLookups):
        val = ParsedValue(HAS_PROP, "", KnoraValueType, "", "")
        with pytest.raises(PermissionNotExistsError):
            _transform_one_resource(resource_with_unknown_permissions, lookups)

    def test_with_file_value(self, lookups: IntermediaryLookups):
        val = ParsedValue(HAS_PROP, "", KnoraValueType, "", "")
        result = _transform_one_resource(resource_with_bitstream, lookups)
        assert result.res_id == "id"
        assert result.type_iri == f"{ONTO}ResourceType"
        assert result.label == "lbl"
        assert not result.permissions
        assert len(result.values) == 0
        file_val = result.file_value
        assert isinstance(file_val, IntermediaryFileValue)
        assert file_val.value == "file.jpg"
        assert not file_val.metadata.permissions
        assert not result.migration_metadata

    def test_with_iiif_uri(self, lookups: IntermediaryLookups):
        val = ParsedValue(HAS_PROP, "", KnoraValueType, "", "")
        result = _transform_one_resource(resource_with_iiif_uri, lookups)
        assert result.res_id == "id"
        assert result.type_iri == f"{ONTO}ResourceType"
        assert result.label == "lbl"
        assert not result.permissions
        assert len(result.values) == 0
        assert not result.file_value
        assert not result.migration_metadata


class TestTransformFileValue:
    def test_transform_file_value(self, lookups: IntermediaryLookups):
        val = ParsedValue(HAS_PROP, "", KnoraValueType, "", "")
        result = _transform_file_value(bitstream, lookups, "id", "lbl")
        assert result.value == "file.jpg"
        assert isinstance(result, IntermediaryFileValue)
        metadata = result.metadata
        assert not metadata.permissions
        assert metadata.license_iri == "http://rdfh.ch/licenses/cc-by-nc-4.0"
        assert metadata.copyright_holder == "copy"
        assert metadata.authorships == ["author"]

    def test_transform_file_value_with_permissions(self, lookups: IntermediaryLookups):
        result = _transform_file_value(bitstream_with_permission, lookups, "id", "lbl")
        assert isinstance(result, IntermediaryFileValue)
        assert result.value == "file.jpg"
        metadata = result.metadata
        assert isinstance(metadata.permissions, Permissions)
        assert metadata.license_iri == "http://rdfh.ch/licenses/cc-by-nc-4.0"
        assert metadata.copyright_holder == "copy"
        assert metadata.authorships == ["author"]

    def test_transform_iiif_uri_value(self, lookups: IntermediaryLookups):
        val = ParsedValue(HAS_PROP, "", KnoraValueType, "", "")
        result = _transform_iiif_uri_value(iiif_uri, lookups)
        assert result.value == "https://this/is/a/uri.jpg"
        assert isinstance(result, IntermediaryIIIFUri)
        metadata = result.metadata
        assert not metadata.permissions
        assert metadata.license_iri == "http://rdfh.ch/licenses/cc-by-nc-4.0"
        assert metadata.copyright_holder == "copy"
        assert metadata.authorships == ["author"]

    def test_transform_iiif_uri_value_with_permission(self, lookups: IntermediaryLookups):
        result = _transform_iiif_uri_value(iiif_uri_with_permission, lookups)
        assert isinstance(result, IntermediaryIIIFUri)
        assert result.value == "https://this/is/a/uri.jpg"
        metadata = result.metadata
        assert isinstance(metadata.permissions, Permissions)
        assert metadata.license_iri == "http://rdfh.ch/licenses/cc-by-nc-4.0"
        assert metadata.copyright_holder == "copy"
        assert metadata.authorships == ["author"]

    def test_get_metadata_soon_deprecated_without_metadata(self, lookups):
        file = ""
        result = _transform_iiif_uri_value(file, lookups)
        assert not result.metadata.permissions
        assert not result.metadata.license_iri
        assert not result.metadata.copyright_holder
        assert not result.metadata.authorships

    def test_get_metadata_raises(self, lookups):
        metadata = ""
        msg = regex.escape(
            "The license 'unknown' used for an image or iiif-uri is unknown. "
            "See documentation for accepted pre-defined licenses."
        )
        with pytest.raises(InputError, match=msg):
            _get_metadata(metadata, lookups)

    def test_get_metadata_unknown_author(self, lookups):
        metadata = 'XMLFileMetadata("http://rdfh.ch/licenses/cc-by-nc-4.0", "copy", "unknown")'
        msg = regex.escape(
            "The authorship id 'unknown' referenced in a multimedia file or iiif-uri is unknown. "
            "Ensure that all referenced ids are defined in the `<authorship>` elements of your XML."
        )
        with pytest.raises(InputError, match=msg):
            _get_metadata(metadata, lookups)


class TransformValues:
    def test_bool_prop(self, lookups: IntermediaryLookups):
        val = ParsedValue(HAS_PROP, "", KnoraValueType, "", "")
        result = _transform_one_value(val, lookups)
        assert len(result) == 1
        transformed = result[0]
        assert isinstance(transformed, IntermediaryBoolean)
        assert transformed.value == True  # noqa:E712 (Avoid equality comparisons)
        assert transformed.prop_iri == f"{ONTO}boolProp"
        assert not transformed.permissions
        assert not transformed.comment

    def test_color_prop(self, lookups: IntermediaryLookups):
        val = ParsedValue(HAS_PROP, "", KnoraValueType, "", "")
        result = _transform_one_value(val, lookups)
        assert len(result) == 1
        transformed = result[0]
        assert isinstance(transformed, IntermediaryColor)
        assert transformed.value == "#5d1f1e"
        assert transformed.prop_iri == f"{ONTO}colorProp"
        assert not transformed.permissions
        assert not transformed.comment

    def test_date_prop(self, lookups: IntermediaryLookups):
        val = ParsedValue(HAS_PROP, "", KnoraValueType, "", "")
        result = _transform_one_value(val, lookups)
        assert len(result) == 1
        transformed = result[0]
        assert isinstance(transformed, IntermediaryDate)
        assert isinstance(transformed.value, Date)
        assert transformed.prop_iri == f"{ONTO}dateProp"
        assert not transformed.permissions
        assert not transformed.comment

    def test_decimal_prop(self, lookups: IntermediaryLookups):
        val = ParsedValue(HAS_PROP, "", KnoraValueType, "", "")
        result = _transform_one_value(val, lookups)
        assert len(result) == 1
        transformed = result[0]
        assert isinstance(transformed, IntermediaryDecimal)
        assert transformed.value == 1.4
        assert transformed.prop_iri == f"{ONTO}decimalProp"
        assert not transformed.permissions
        assert not transformed.comment

    def test_decimal_prop_with_two_values(self, lookups: IntermediaryLookups):
        val = ParsedValue(HAS_PROP, "", KnoraValueType, "", "")
        result = _transform_one_value(val, lookups)
        assert len(result) == 2

    def test_simple_text_prop(self, lookups: IntermediaryLookups):
        val = ParsedValue(HAS_PROP, "", KnoraValueType, "", "")
        result = _transform_one_value(val, lookups)
        assert len(result) == 1
        transformed = result[0]
        assert isinstance(transformed, IntermediarySimpleText)
        assert transformed.value == "text"
        assert transformed.prop_iri == f"{ONTO}simpleTextProp"
        assert not transformed.permissions
        assert not transformed.comment

    def test_richtext_prop(self, lookups: IntermediaryLookups):
        val = ParsedValue(HAS_PROP, "", KnoraValueType, "", "")
        result = _transform_one_value(val, lookups)
        assert len(result) == 1
        transformed = result[0]
        assert isinstance(transformed, IntermediaryRichtext)
        assert isinstance(transformed.value, FormattedTextValue)
        assert transformed.prop_iri == f"{ONTO}richTextProp"
        assert not transformed.permissions
        assert not transformed.comment
        assert transformed.resource_references == {"id"}

    def test_geoname_prop(self, lookups: IntermediaryLookups):
        val = ParsedValue(HAS_PROP, "", KnoraValueType, "", "")
        result = _transform_one_value(val, lookups)
        assert len(result) == 1
        transformed = result[0]
        assert isinstance(transformed, IntermediaryGeoname)
        assert transformed.value == "5416656"
        assert transformed.prop_iri == f"{ONTO}geonameProp"
        assert not transformed.permissions
        assert not transformed.comment

    def test_integer_prop(self, lookups: IntermediaryLookups):
        val = ParsedValue(HAS_PROP, "", KnoraValueType, "", "")
        result = _transform_one_value(lookups)
        assert len(result) == 1
        transformed = result[0]
        assert isinstance(transformed, IntermediaryInt)
        assert transformed.value == 1
        assert transformed.prop_iri == f"{ONTO}integerProp"
        assert not transformed.permissions
        assert not transformed.comment

    def test_list_prop(self, lookups: IntermediaryLookups):
        val = ParsedValue(HAS_PROP, "", KnoraValueType, "", "")
        result = _transform_one_value(val, lookups)
        assert len(result) == 1
        transformed = result[0]
        assert isinstance(transformed, IntermediaryList)
        assert transformed.value == "http://rdfh.ch/9999/node"
        assert transformed.prop_iri == f"{ONTO}listProp"
        assert not transformed.permissions
        assert not transformed.comment

    def test_resptr_prop(self, lookups: IntermediaryLookups):
        val = ParsedValue(HAS_PROP, "", KnoraValueType, "", "")
        result = _transform_one_value(val, lookups)
        assert len(result) == 1
        transformed = result[0]
        assert isinstance(transformed, IntermediaryLink)
        assert transformed.value == "other_id"
        assert transformed.prop_iri == f"{ONTO}linkPropValue"
        assert not transformed.permissions
        assert not transformed.comment

    def test_time_prop(self, lookups: IntermediaryLookups):
        val = ParsedValue(HAS_PROP, "", KnoraValueType, "", "")
        result = _transform_one_value(val, lookups)
        assert len(result) == 1
        transformed = result[0]
        assert isinstance(transformed, IntermediaryTime)
        assert transformed.value == "2019-10-23T13:45:12.01-14:00"
        assert transformed.prop_iri == f"{ONTO}timeProp"
        assert not transformed.permissions
        assert not transformed.comment

    def test_uri_prop(self, lookups: IntermediaryLookups):
        val = ParsedValue(HAS_PROP, "", KnoraValueType, "", "")
        result = _transform_one_value(val, lookups)
        assert len(result) == 1
        transformed = result[0]
        assert isinstance(transformed, IntermediaryUri)
        assert transformed.value == "https://dasch.swiss"
        assert transformed.prop_iri == f"{ONTO}uriProp"
        assert not transformed.permissions
        assert not transformed.comment

    def test_bool_prop_with_comment(self, lookups: IntermediaryLookups):
        val = ParsedValue(HAS_PROP, "", KnoraValueType, "", "")
        result = _transform_one_value(val, lookups)
        assert len(result) == 1
        transformed = result[0]
        assert transformed.value == True  # noqa:E712 (Avoid equality comparisons)
        assert transformed.prop_iri == f"{ONTO}boolProp"
        assert not transformed.permissions
        assert transformed.comment == "comment"

    def test_bool_prop_with_permissions(self, lookups: IntermediaryLookups):
        val = ParsedValue(HAS_PROP, "", KnoraValueType, "", "")
        result = _transform_one_value(val, lookups)
        assert len(result) == 1
        transformed = result[0]
        assert transformed.value == True  # noqa:E712 (Avoid equality comparisons)
        assert transformed.prop_iri == f"{ONTO}boolProp"
        assert isinstance(transformed.permissions, Permissions)
        assert not transformed.comment

    def test_bool_prop_with_non_existing_permissions(self, lookups: IntermediaryLookups):
        val = ParsedValue(HAS_PROP, "", KnoraValueType, "", "")
        with pytest.raises(PermissionNotExistsError):
            _transform_one_value(val, lookups)
