from dsp_tools.commands.xmlupload.models.intermediary.file_values import IntermediaryFileMetadata
from dsp_tools.commands.xmlupload.models.intermediary.file_values import IntermediaryFileValue
from dsp_tools.commands.xmlupload.models.intermediary.file_values import IntermediaryIIIFUri
from dsp_tools.commands.xmlupload.models.intermediary.res import IntermediaryResource
from dsp_tools.commands.xmlupload.models.intermediary.res import MigrationMetadata
from dsp_tools.commands.xmlupload.models.intermediary.res import ResourceInputConversionFailure
from dsp_tools.commands.xmlupload.models.intermediary.res import ResourceTransformationResult
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryBoolean
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryColor
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryDate
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryDecimal
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryGeometry
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryGeoname
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryInt
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryInterval
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryTime
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryUri
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryValue
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.prepare_xml_input.ark2iri import convert_ark_v0_to_resource_iri
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import TypeTransformerMapper
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import assert_is_string
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import transform_boolean
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import transform_date
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import transform_decimal
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import transform_geometry
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import transform_integer
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import transform_interval
from dsp_tools.models.exceptions import InvalidInputError
from dsp_tools.models.exceptions import PermissionNotExistsError
from dsp_tools.utils.xml_parsing.models.data_deserialised import DataDeserialised
from dsp_tools.utils.xml_parsing.models.data_deserialised import MigrationMetadataDeserialised
from dsp_tools.utils.xml_parsing.models.data_deserialised import PropertyObject
from dsp_tools.utils.xml_parsing.models.data_deserialised import ResourceDeserialised
from dsp_tools.utils.xml_parsing.models.data_deserialised import TriplePropertyType
from dsp_tools.utils.xml_parsing.models.data_deserialised import ValueInformation

TYPE_TRANSFORMER_MAPPER: dict[str, TypeTransformerMapper] = {
    "boolean": TypeTransformerMapper(IntermediaryBoolean, transform_boolean),
    "color": TypeTransformerMapper(IntermediaryColor, assert_is_string),
    "decimal": TypeTransformerMapper(IntermediaryDecimal, transform_decimal),
    "date": TypeTransformerMapper(IntermediaryDate, transform_date),
    "geometry": TypeTransformerMapper(IntermediaryGeometry, transform_geometry),
    "geoname": TypeTransformerMapper(IntermediaryGeoname, assert_is_string),
    "integer": TypeTransformerMapper(IntermediaryInt, transform_integer),
    "interval": TypeTransformerMapper(IntermediaryInterval, transform_interval),
    "time": TypeTransformerMapper(IntermediaryTime, assert_is_string),
    "uri": TypeTransformerMapper(IntermediaryUri, assert_is_string),
}


def transform_all_resources_into_intermediary_resources(
    data: DataDeserialised, permissions_lookup: dict[str, Permissions], listnodes: dict[str, str]
) -> ResourceTransformationResult:
    """
    Takes the XMLResources parsed from the XML file and converts them into the Intermediary format.
    Permissions, relative IRIs, etc. are resolved in this step.

    Args:
        data: deserialised data
        permissions_lookup: lookup for permissions
        listnodes: lookup for list node name to IRI

    Returns:
        An object containing the transformed resources and transformation failure information
    """
    failures = []
    transformed = []
    for res in data.resources:
        result = _transform_one_resource(res, permissions_lookup, listnodes)
        if isinstance(result, IntermediaryResource):
            transformed.append(result)
        else:
            failures.append(result)
    return ResourceTransformationResult(transformed, failures)


def _transform_one_resource(
    resource: ResourceDeserialised, permissions_lookup: dict[str, Permissions], listnodes: dict[str, str]
) -> IntermediaryResource | ResourceInputConversionFailure:
    failures = []
    file_value, iiif_uri = None, None
    migration_metadata = _transform_migration_metadata(resource.migration_metadata)
    try:
        resource_permission = _get_permission(resource.property_objects, permissions_lookup)
    except PermissionNotExistsError as e:
        failures.append(str(e))
    if resource.asset_value:
        file_value = _transform_file_value(resource.asset_value, permissions_lookup, resource.res_id)


def _transform_migration_metadata(migration_metadata: MigrationMetadataDeserialised) -> MigrationMetadata | None:
    if not migration_metadata.any():
        return None
    res_iri = migration_metadata.iri
    if migration_metadata.ark:
        res_iri = convert_ark_v0_to_resource_iri(migration_metadata.ark)
    return MigrationMetadata(res_iri, migration_metadata.creation_date)


def _transform_file_value(
    bitstream: ValueInformation, permissions_lookup: dict[str, Permissions], res_id: str, res_label: str
) -> IntermediaryFileValue:
    metadata = _resolve_file_value_metadata(bitstream.value_metadata, permissions_lookup)
    return IntermediaryFileValue(bitstream.user_facing_value, metadata, res_id, res_label)


def _transform_iiif_uri_value(
    iiif_uri: ValueInformation, permissions_lookup: dict[str, Permissions]
) -> IntermediaryIIIFUri:
    metadata = _resolve_file_value_metadata(iiif_uri.value_metadata, permissions_lookup)
    return IntermediaryIIIFUri(iiif_uri.user_facing_value, metadata)


def _resolve_file_value_metadata(
    file_val_metadata: list[PropertyObject], permissions_lookup: dict[str, Permissions]
) -> IntermediaryFileMetadata:
    pass


def _transform_all_properties(
    properties: list[ValueInformation],
    permissions_lookup: dict[str, Permissions],
    listnodes: dict[str, str],
) -> tuple[list[IntermediaryValue], list[str]]:
    all_values = []
    failures = []
    for prop in properties:
        try:
            all_values.append(_transform_one_property(prop, permissions_lookup, listnodes))
        except PermissionNotExistsError | InvalidInputError as e:
            failures.append(str(e))
    return all_values, failures


def _transform_one_property(
    prop: ValueInformation, permissions_lookup: dict[str, Permissions], listnodes: dict[str, str]
) -> IntermediaryValue:
    pass


def _resolve_value_metadata(
    metadata: list[PropertyObject], permissions_lookup: dict[str, Permissions]
) -> tuple[Permissions | None, str | None]:
    pass


def _get_permission(
    prop_objects: list[PropertyObject], permissions_lookup: dict[str, Permissions]
) -> Permissions | None:
    if perm := [x for x in prop_objects if x.property_type == TriplePropertyType.KNORA_PERMISSIONS]:
        return _resolve_permission(perm.pop(0).object_value, permissions_lookup)
    return None


def _resolve_permission(permissions: str | None, permissions_lookup: dict[str, Permissions]) -> Permissions | None:
    """Resolve the permission into a string that can be sent to the API."""
    if permissions:
        if not (per := permissions_lookup.get(permissions)):
            raise PermissionNotExistsError(f"Could not find permissions for value: {permissions}")
        return per
    return None
