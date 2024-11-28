from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import IIIFUriInfo
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLBitstream
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLProperty
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLValue
from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import XMLResource
from dsp_tools.commands.xmlupload.models.lookup_models import IntermediaryLookup
from dsp_tools.commands.xmlupload.transform_into_intermediary_classes import _transform_one_file_value
from dsp_tools.commands.xmlupload.transform_into_intermediary_classes import _transform_one_property
from dsp_tools.commands.xmlupload.transform_into_intermediary_classes import _transform_one_resource
from dsp_tools.commands.xmlupload.transform_into_intermediary_classes import _transform_one_value


class TestTransformResource:
    def test_success(self, resource_with_permissions: XMLResource, lookups: IntermediaryLookup) -> None:
        result = _transform_one_resource(resource_with_permissions, lookups)

    def test_with_ark(self, resource_with_ark: XMLResource, lookups: IntermediaryLookup) -> None:
        result = _transform_one_resource(resource_with_ark, lookups)

    def test_with_iri(self, resource_with_iri: XMLResource, lookups: IntermediaryLookup) -> None:
        result = _transform_one_resource(resource_with_iri, lookups)

    def test_unknown_permission(
        self, resource_with_unknown_permissions: XMLResource, lookups: IntermediaryLookup
    ) -> None:
        result = _transform_one_resource(resource_with_unknown_permissions, lookups)

    def test_bitstream(self, resource_with_bitstream: XMLResource, lookups: IntermediaryLookup) -> None:
        result = _transform_one_resource(resource_with_bitstream, lookups)

    def test_iiif_uri(self, resource_with_iiif_uri: XMLResource, lookups: IntermediaryLookup) -> None:
        result = _transform_one_resource(resource_with_iiif_uri, lookups)


class TestTransformFileValue:
    def test_bitstream(self, bitstream: XMLBitstream, lookups: IntermediaryLookup) -> None:
        result = _transform_one_file_value(bitstream, lookups)

    def test_bitstream_with_permissions(
        self, bitstream_with_permission: XMLBitstream, lookups: IntermediaryLookup
    ) -> None:
        result = _transform_one_file_value(bitstream_with_permission, lookups)

    def test_iiif_uri(self, iiif_uri: IIIFUriInfo, lookups: IntermediaryLookup) -> None:
        result = _transform_one_file_value(iiif_uri, lookups)

    def test_iiif_uri_with_permission(self, iiif_uri_with_permission: IIIFUriInfo, lookups: IntermediaryLookup) -> None:
        result = _transform_one_file_value(iiif_uri_with_permission, lookups)


class TestTransformProperties:
    def test_bool_prop(self, bool_prop: XMLProperty, lookups: IntermediaryLookup) -> None:
        result = _transform_one_property(bool_prop, lookups, ":ResourceType")

    def test_color_prop(self, color_prop: XMLProperty, lookups: IntermediaryLookup) -> None:
        result = _transform_one_property(color_prop, lookups, ":ResourceType")

    def test_date_prop(self, date_prop: XMLProperty, lookups: IntermediaryLookup) -> None:
        result = _transform_one_property(date_prop, lookups, ":ResourceType")

    def test_decimal_prop(self, decimal_prop: XMLProperty, lookups: IntermediaryLookup) -> None:
        result = _transform_one_property(decimal_prop, lookups, ":ResourceType")

    def test_decimal_prop_with_two_values(
        self, decimal_prop_with_two_values: XMLProperty, lookups: IntermediaryLookup
    ) -> None:
        result = _transform_one_property(decimal_prop_with_two_values, lookups, ":ResourceType")

    def test_simple_text_prop(self, simple_text_prop: XMLProperty, lookups: IntermediaryLookup) -> None:
        result = _transform_one_property(simple_text_prop, lookups, ":ResourceType")

    def test_richtext_prop(self, richtext_prop: XMLProperty, lookups: IntermediaryLookup) -> None:
        result = _transform_one_property(richtext_prop, lookups, ":ResourceType")

    def test_geoname_prop(self, geoname_prop: XMLProperty, lookups: IntermediaryLookup) -> None:
        result = _transform_one_property(geoname_prop, lookups, ":ResourceType")

    def test_integer_prop(self, integer_prop: XMLProperty, lookups: IntermediaryLookup) -> None:
        result = _transform_one_property(integer_prop, lookups, ":ResourceType")

    def test_list_prop(self, list_prop: XMLProperty, lookups: IntermediaryLookup) -> None:
        result = _transform_one_property(list_prop, lookups, ":ResourceType")

    def test_resptr_prop(self, resptr_prop: XMLProperty, lookups: IntermediaryLookup) -> None:
        result = _transform_one_property(resptr_prop, lookups, ":ResourceType")

    def test_time_prop(self, time_prop: XMLProperty, lookups: IntermediaryLookup) -> None:
        result = _transform_one_property(time_prop, lookups, ":ResourceType")

    def test_uri_prop(self, uri_prop: XMLProperty, lookups: IntermediaryLookup) -> None:
        result = _transform_one_property(uri_prop, lookups, ":ResourceType")


class TestTransformValue:
    def test_value_with_string_and_comment(
        self, value_with_string_and_comment: XMLValue, lookups: IntermediaryLookup
    ) -> None:
        result = _transform_one_value(value_with_string_and_comment, lookups, ":ResourceType")

    def test_value_with_string_and_permissions(
        self, value_with_string_and_permissions: XMLValue, lookups: IntermediaryLookup
    ) -> None:
        result = _transform_one_value(value_with_string_and_permissions, lookups, ":ResourceType")

    def test_value_with_string_and_non_existing_permissions(
        self, value_with_string_and_non_existing_permissions: XMLValue, lookups: IntermediaryLookup
    ) -> None:
        result = _transform_one_value(value_with_string_and_non_existing_permissions, lookups, ":ResourceType")
