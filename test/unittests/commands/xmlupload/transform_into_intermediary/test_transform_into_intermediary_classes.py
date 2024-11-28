import pytest

from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import IIIFUriInfo
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLBitstream
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLProperty
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLValue
from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import XMLResource
from dsp_tools.commands.xmlupload.models.intermediary.file_values import IntermediaryFileValue
from dsp_tools.commands.xmlupload.models.intermediary.file_values import IntermediaryIIIFUri
from dsp_tools.commands.xmlupload.models.intermediary.resource import MigrationMetadata
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
from dsp_tools.commands.xmlupload.models.lookup_models import IntermediaryLookup
from dsp_tools.commands.xmlupload.transform_into_intermediary_classes import _transform_one_file_value
from dsp_tools.commands.xmlupload.transform_into_intermediary_classes import _transform_one_property
from dsp_tools.commands.xmlupload.transform_into_intermediary_classes import _transform_one_resource
from dsp_tools.commands.xmlupload.transform_into_intermediary_classes import _transform_one_value
from dsp_tools.models.exceptions import InputError

ONTO = "http://0.0.0.0:3333/ontology/9999/onto/v2#"


class TestTransformResource:
    def test_resource_one_prop(self, resource_one_prop: XMLResource, lookups: IntermediaryLookup) -> None:
        result = _transform_one_resource(resource_one_prop, lookups)
        assert result.res_id == "id"
        assert result.type_iri == f"{ONTO}ResourceType"
        assert result.label == "lbl"
        assert not result.permissions
        assert len(result.values) == 1
        assert not result.file_value
        assert not result.migration_metadata

    def test_resource_with_permissions(
        self, resource_with_permissions: XMLResource, lookups: IntermediaryLookup
    ) -> None:
        result = _transform_one_resource(resource_with_permissions, lookups)
        assert result.res_id == "id"
        assert result.type_iri == f"{ONTO}ResourceType"
        assert result.label == "lbl"
        assert result.permissions == ""
        assert len(result.values) == 0
        assert not result.file_value
        assert not result.migration_metadata

    def test_with_ark(self, resource_with_ark: XMLResource, lookups: IntermediaryLookup) -> None:
        result = _transform_one_resource(resource_with_ark, lookups)
        assert result.res_id == "id"
        assert result.type_iri == f"{ONTO}ResourceType"
        assert result.label == "lbl"
        assert not result.permissions
        assert len(result.values) == 0
        assert not result.file_value
        metadata = result.migration_metadata
        assert isinstance(metadata, MigrationMetadata)
        assert metadata.iri_str == ""
        assert metadata.creation_date == "1999-12-31T23:59:59.9999999+01:00"

    def test_with_iri(self, resource_with_iri: XMLResource, lookups: IntermediaryLookup) -> None:
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
        assert metadata.creation_date == "1999-12-31T23:59:59.9999999+01:00"

    def test_resource_with_ark_and_iri(
        self, resource_with_ark_and_iri: XMLResource, lookups: IntermediaryLookup
    ) -> None:
        result = _transform_one_resource(resource_with_ark_and_iri, lookups)
        assert result.res_id == "id"
        assert result.type_iri == f"{ONTO}ResourceType"
        assert result.label == "lbl"
        assert not result.permissions
        assert len(result.values) == 0
        assert not result.file_value
        metadata = result.migration_metadata
        assert isinstance(metadata, MigrationMetadata)
        assert metadata.iri_str == ""
        assert metadata.creation_date == "1999-12-31T23:59:59.9999999+01:00"

    def test_unknown_permission(
        self, resource_with_unknown_permissions: XMLResource, lookups: IntermediaryLookup
    ) -> None:
        with pytest.raises(InputError):
            _transform_one_resource(resource_with_unknown_permissions, lookups)

    def test_bitstream(self, resource_with_bitstream: XMLResource, lookups: IntermediaryLookup) -> None:
        result = _transform_one_resource(resource_with_bitstream, lookups)
        assert result.res_id == "id"
        assert result.type_iri == f"{ONTO}ResourceType"
        assert result.label == "lbl"
        assert not result.permissions
        assert len(result.values) == 0
        assert not result.file_value
        assert not result.migration_metadata

    def test_iiif_uri(self, resource_with_iiif_uri: XMLResource, lookups: IntermediaryLookup) -> None:
        result = _transform_one_resource(resource_with_iiif_uri, lookups)
        assert result.res_id == "id"
        assert result.type_iri == f"{ONTO}ResourceType"
        assert result.label == "lbl"
        assert not result.permissions
        assert len(result.values) == 0
        assert not result.file_value
        assert not result.migration_metadata


class TestTransformFileValue:
    def test_bitstream(self, bitstream: XMLBitstream, lookups: IntermediaryLookup) -> None:
        result = _transform_one_file_value(bitstream, lookups)
        assert isinstance(result, IntermediaryFileValue)

    def test_bitstream_with_permissions(
        self, bitstream_with_permission: XMLBitstream, lookups: IntermediaryLookup
    ) -> None:
        result = _transform_one_file_value(bitstream_with_permission, lookups)
        assert isinstance(result, IntermediaryFileValue)

    def test_iiif_uri(self, iiif_uri: IIIFUriInfo, lookups: IntermediaryLookup) -> None:
        result = _transform_one_file_value(iiif_uri, lookups)
        assert isinstance(result, IntermediaryIIIFUri)

    def test_iiif_uri_with_permission(self, iiif_uri_with_permission: IIIFUriInfo, lookups: IntermediaryLookup) -> None:
        result = _transform_one_file_value(iiif_uri_with_permission, lookups)
        assert isinstance(result, IntermediaryIIIFUri)


class TestTransformProperties:
    def test_bool_prop(self, bool_prop: XMLProperty, lookups: IntermediaryLookup) -> None:
        result = _transform_one_property(bool_prop, lookups)
        assert len(result) == 1
        transformed = result[0]
        assert isinstance(transformed, IntermediaryBoolean)
        assert transformed.value == ""
        assert transformed.prop_iri == ""
        assert not transformed.permissions
        assert not transformed.comment

    def test_color_prop(self, color_prop: XMLProperty, lookups: IntermediaryLookup) -> None:
        result = _transform_one_property(color_prop, lookups)
        assert len(result) == 1
        transformed = result[0]
        assert isinstance(transformed, IntermediaryColor)
        assert transformed.value == ""
        assert transformed.prop_iri == ""
        assert not transformed.permissions
        assert not transformed.comment

    def test_date_prop(self, date_prop: XMLProperty, lookups: IntermediaryLookup) -> None:
        result = _transform_one_property(date_prop, lookups)
        assert len(result) == 1
        transformed = result[0]
        assert isinstance(transformed, IntermediaryDate)
        assert transformed.value == ""
        assert transformed.prop_iri == ""
        assert not transformed.permissions
        assert not transformed.comment

    def test_decimal_prop(self, decimal_prop: XMLProperty, lookups: IntermediaryLookup) -> None:
        result = _transform_one_property(decimal_prop, lookups)
        assert len(result) == 1
        transformed = result[0]
        assert isinstance(transformed, IntermediaryDecimal)
        assert transformed.value == ""
        assert transformed.prop_iri == ""
        assert not transformed.permissions
        assert not transformed.comment

    def test_decimal_prop_with_two_values(
        self, decimal_prop_with_two_values: XMLProperty, lookups: IntermediaryLookup
    ) -> None:
        result = _transform_one_property(decimal_prop_with_two_values, lookups)
        assert len(result) == 2

    def test_simple_text_prop(self, simple_text_prop: XMLProperty, lookups: IntermediaryLookup) -> None:
        result = _transform_one_property(simple_text_prop, lookups)
        assert len(result) == 1
        transformed = result[0]
        assert isinstance(transformed, IntermediarySimpleText)
        assert transformed.value == ""
        assert transformed.prop_iri == ""
        assert not transformed.permissions
        assert not transformed.comment

    def test_richtext_prop(self, richtext_prop: XMLProperty, lookups: IntermediaryLookup) -> None:
        result = _transform_one_property(richtext_prop, lookups)
        assert len(result) == 1
        transformed = result[0]
        assert isinstance(transformed, IntermediaryRichtext)
        assert transformed.value == ""
        assert transformed.prop_iri == ""
        assert not transformed.permissions
        assert not transformed.comment

    def test_geoname_prop(self, geoname_prop: XMLProperty, lookups: IntermediaryLookup) -> None:
        result = _transform_one_property(geoname_prop, lookups)
        assert len(result) == 1
        transformed = result[0]
        assert isinstance(transformed, IntermediaryGeoname)
        assert transformed.value == ""
        assert transformed.prop_iri == ""
        assert not transformed.permissions
        assert not transformed.comment

    def test_integer_prop(self, integer_prop: XMLProperty, lookups: IntermediaryLookup) -> None:
        result = _transform_one_property(integer_prop, lookups)
        assert len(result) == 1
        transformed = result[0]
        assert isinstance(transformed, IntermediaryInt)
        assert transformed.value == ""
        assert transformed.prop_iri == ""
        assert not transformed.permissions
        assert not transformed.comment

    def test_list_prop(self, list_prop: XMLProperty, lookups: IntermediaryLookup) -> None:
        result = _transform_one_property(list_prop, lookups)
        assert len(result) == 1
        transformed = result[0]
        assert isinstance(transformed, IntermediaryList)
        assert transformed.value == ""
        assert transformed.prop_iri == ""
        assert not transformed.permissions
        assert not transformed.comment

    def test_resptr_prop(self, resptr_prop: XMLProperty, lookups: IntermediaryLookup) -> None:
        result = _transform_one_property(resptr_prop, lookups)
        assert len(result) == 1
        transformed = result[0]
        assert isinstance(transformed, IntermediaryLink)
        assert transformed.value == ""
        assert transformed.prop_iri == ""
        assert not transformed.permissions
        assert not transformed.comment

    def test_time_prop(self, time_prop: XMLProperty, lookups: IntermediaryLookup) -> None:
        result = _transform_one_property(time_prop, lookups)
        assert len(result) == 1
        transformed = result[0]
        assert isinstance(transformed, IntermediaryTime)
        assert transformed.value == ""
        assert transformed.prop_iri == ""
        assert not transformed.permissions
        assert not transformed.comment

    def test_uri_prop(self, uri_prop: XMLProperty, lookups: IntermediaryLookup) -> None:
        result = _transform_one_property(uri_prop, lookups)
        assert len(result) == 1
        transformed = result[0]
        assert isinstance(transformed, IntermediaryUri)
        assert transformed.value == ""
        assert transformed.prop_iri == ""
        assert not transformed.permissions
        assert not transformed.comment


class TestTransformValue:
    def test_value_with_string_and_comment(
        self, value_with_string_and_comment: XMLValue, lookups: IntermediaryLookup
    ) -> None:
        result = _transform_one_value(value_with_string_and_comment, ":prop", lookups)
        assert len(result) == 1
        transformed = result[0]
        assert transformed.value == ""
        assert transformed.prop_iri == ""
        assert not transformed.permissions
        assert not transformed.comment

    def test_value_with_string_and_permissions(
        self, value_with_string_and_permissions: XMLValue, lookups: IntermediaryLookup
    ) -> None:
        result = _transform_one_value(value_with_string_and_permissions, ":prop", lookups)
        assert len(result) == 1
        transformed = result[0]
        assert transformed.value == ""
        assert transformed.prop_iri == ""
        assert not transformed.permissions
        assert not transformed.comment

    def test_value_with_string_and_non_existing_permissions(
        self, value_with_string_and_non_existing_permissions: XMLValue, lookups: IntermediaryLookup
    ) -> None:
        result = _transform_one_value(value_with_string_and_non_existing_permissions, ":prop", lookups)
        assert len(result) == 1
        transformed = result[0]
        assert transformed.value == ""
        assert transformed.prop_iri == ""
        assert not transformed.permissions
        assert not transformed.comment
