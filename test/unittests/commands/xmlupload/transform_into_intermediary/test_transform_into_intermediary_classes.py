from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import XMLResource
from dsp_tools.commands.xmlupload.models.lookup_models import IntermediaryLookup
from dsp_tools.commands.xmlupload.transform_into_intermediary_classes import _transform_one_resource


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


class TestTransformFileValue: ...


class TestTransformProperties: ...
