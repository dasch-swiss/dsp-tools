from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import IIIFUriInfo
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLBitstream
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLProperty
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLValue
from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import XMLResource
from dsp_tools.commands.xmlupload.models.intermediary.file_values import IntermediaryAbstractFileValue
from dsp_tools.commands.xmlupload.models.intermediary.resource import IntermediaryResource
from dsp_tools.commands.xmlupload.models.intermediary.resource import MigrationMetadata
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryValue
from dsp_tools.commands.xmlupload.models.lookup_models import IntermediaryLookup


def transform_into_intermediary_classes(
    resources: list[XMLResource], lookups: IntermediaryLookup
) -> list[IntermediaryResource]:
    pass


def _transform_one_resource(resource: XMLResource, lookups: IntermediaryLookup) -> IntermediaryResource:
    pass


def _transform_migration_metadata(resource: XMLResource) -> MigrationMetadata:
    pass


def _transform_one_file_value(
    value: XMLBitstream | IIIFUriInfo, lookups: IntermediaryLookup
) -> IntermediaryAbstractFileValue:
    pass


def _transform_one_property(
    prop: XMLProperty, lookups: IntermediaryLookup, resource_type: str
) -> list[IntermediaryValue]:
    pass


def _transform_one_value(value: XMLValue, lookups: IntermediaryLookup, resource_type: str) -> list[IntermediaryValue]:
    pass
