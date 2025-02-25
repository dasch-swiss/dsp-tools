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
from dsp_tools.models.exceptions import InvalidInputError
from dsp_tools.models.exceptions import PermissionNotExistsError
from dsp_tools.utils.xml_parsing.models.data_deserialised import DataDeserialised
from dsp_tools.utils.xml_parsing.models.data_deserialised import KnoraValueType
from dsp_tools.utils.xml_parsing.models.data_deserialised import MigrationMetadataDeserialised
from dsp_tools.utils.xml_parsing.models.data_deserialised import PropertyObject
from dsp_tools.utils.xml_parsing.models.data_deserialised import ResourceDeserialised
from dsp_tools.utils.xml_parsing.models.data_deserialised import ValueInformation

TYPE_TRANSFORMER_MAPPER: dict[KnoraValueType, TypeTransformerMapper] = {
    KnoraValueType.BOOLEAN_VALUE: TypeTransformerMapper(IntermediaryBoolean, transform_boolean),
    KnoraValueType.COLOR_VALUE: TypeTransformerMapper(IntermediaryColor, assert_is_string),
    KnoraValueType.DECIMAL_VALUE: TypeTransformerMapper(IntermediaryDecimal, transform_decimal),
    KnoraValueType.DATE_VALUE: TypeTransformerMapper(IntermediaryDate, transform_date),
    KnoraValueType.GEOM_VALUE: TypeTransformerMapper(IntermediaryGeometry, transform_geometry),
    KnoraValueType.GEONAME_VALUE: TypeTransformerMapper(IntermediaryGeoname, assert_is_string),
    KnoraValueType.INT_VALUE: TypeTransformerMapper(IntermediaryInt, transform_integer),
    KnoraValueType.TIME_VALUE: TypeTransformerMapper(IntermediaryTime, assert_is_string),
    KnoraValueType.URI_VALUE: TypeTransformerMapper(IntermediaryUri, assert_is_string),
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
    failures = set()
    file_value, resource_permission, iiif_uri = None, None, None
    migration_metadata = _transform_migration_metadata(resource.migration_metadata)
    try:
        resource_permission = _resolve_permission(resource.get_permission(), permissions_lookup)
    except PermissionNotExistsError as e:
        failures.add(str(e))
    if resource.asset_value:
        try:
            file_value = _transform_file_value(
                resource.asset_value, permissions_lookup, resource.res_id, resource.get_label()
            )
        except PermissionNotExistsError as e:
            failures.add(str(e))
    try:
        iiif_uri = _transform_iiif_uri_value(resource.values, permissions_lookup)
    except PermissionNotExistsError as e:
        failures.add(str(e))

    transformed_vals, val_fails = _transform_all_values(resource.values, permissions_lookup, listnodes)
    failures.update(val_fails)
    if failures:
        return ResourceInputConversionFailure(resource.res_id, ", ".join(failures))
    return IntermediaryResource(
        res_id=resource.res_id,
        type_iri=resource.get_restype(),
        label=resource.get_label(),
        permissions=resource_permission,
        values=transformed_vals,
        file_value=file_value,
        iiif_uri=iiif_uri,
        migration_metadata=migration_metadata,
    )


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
    properties: list[ValueInformation], permissions_lookup: dict[str, Permissions]
) -> IntermediaryIIIFUri | None:
    for prop in properties:
        if prop.knora_type == KnoraValueType.STILL_IMAGE_IIIF:
            metadata = _resolve_file_value_metadata(prop.value_metadata, permissions_lookup)
            return IntermediaryIIIFUri(prop.user_facing_value, metadata)
    return None


def _resolve_file_value_metadata(
    file_val_metadata: list[PropertyObject], permissions_lookup: dict[str, Permissions]
) -> IntermediaryFileMetadata:
    pass


def _transform_all_values(
    values: list[ValueInformation],
    permissions_lookup: dict[str, Permissions],
    listnodes: dict[str, str],
) -> tuple[list[IntermediaryValue], set[str]]:
    all_values = []
    failures = set()
    for prop in values:
        if prop.knora_type == KnoraValueType.STILL_IMAGE_IIIF:
            continue
        try:
            all_values.append(_transform_one_value(prop, permissions_lookup, listnodes))
        except PermissionNotExistsError | InvalidInputError as e:
            failures.add(str(e))
    return all_values, failures


def _transform_one_value(
    val: ValueInformation, permissions_lookup: dict[str, Permissions], listnodes: dict[str, str]
) -> IntermediaryValue:
    match val.knora_type:
        case KnoraValueType.LIST_VALUE:
            return _transform_list_value(val, permissions_lookup, listnodes)
        case KnoraValueType.RICHTEXT_VALUE:
            return _transform_richtext_value(val, permissions_lookup)
        case KnoraValueType.LINK_VALUE:
            return _transform_link_value(val, permissions_lookup)
        case KnoraValueType.INTERVAL_VALUE:
            return _transform_interval_value(val, permissions_lookup)
        case _ as val_type:
            transformation_mapper = TYPE_TRANSFORMER_MAPPER[val_type]
            return _transform_one_generic_value(val, permissions_lookup, transformation_mapper)


def _transform_one_generic_value(
    val: ValueInformation, permissions_lookup: dict[str, Permissions], transformation_mapper: TypeTransformerMapper
) -> IntermediaryValue:
    pass


def _transform_list_value(
    val: ValueInformation, permissions_lookup: dict[str, Permissions], listnodes: dict[str, str]
) -> IntermediaryValue:
    pass


def _transform_richtext_value(val: ValueInformation, permissions_lookup: dict[str, Permissions]) -> IntermediaryValue:
    pass


def _transform_link_value(val: ValueInformation, permissions_lookup: dict[str, Permissions]) -> IntermediaryValue:
    pass


def _transform_interval_value(val: ValueInformation, permissions_lookup: dict[str, Permissions]) -> IntermediaryValue:
    pass


def _resolve_value_metadata(
    metadata: list[PropertyObject], permissions_lookup: dict[str, Permissions]
) -> tuple[Permissions | None, str | None]:
    pass


def _resolve_permission(permissions: str | None, permissions_lookup: dict[str, Permissions]) -> Permissions | None:
    """Resolve the permission into a string that can be sent to the API."""
    if permissions:
        if not (per := permissions_lookup.get(permissions)):
            raise PermissionNotExistsError(f"Could not find permissions for value: {permissions}")
        return per
    return None
