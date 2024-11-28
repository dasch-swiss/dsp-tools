from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import XMLResource
from dsp_tools.commands.xmlupload.models.lookup_models import IntermediaryLookup
from dsp_tools.commands.xmlupload.transform_into_intermediary_classes import _transform_one_resource


class TestTransformResource:
    def test_success(self, resource: XMLResource, lookups: IntermediaryLookup) -> None:
        result = _transform_one_resource(resource, lookups)

    def test_with_migration_metadata(self, resource: XMLResource, lookups: IntermediaryLookup) -> None:
        result = _transform_one_resource(resource, lookups)

    def test_unknown_permission(self, resource: XMLResource, lookups: IntermediaryLookup) -> None:
        result = _transform_one_resource(resource, lookups)

    def test_iiif_uri(self, resource: XMLResource, lookups: IntermediaryLookup) -> None:
        result = _transform_one_resource(resource, lookups)

    def test_bitstream(self, resource: XMLResource, lookups: IntermediaryLookup) -> None:
        result = _transform_one_resource(resource, lookups)


class TestTransformFileValue: ...


class TestTransformProperties: ...
