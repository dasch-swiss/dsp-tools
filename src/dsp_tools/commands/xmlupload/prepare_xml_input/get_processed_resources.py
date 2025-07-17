from typing import cast
from uuid import uuid4

from loguru import logger

from dsp_tools.commands.xmlupload.models.lookup_models import XmlReferenceLookups
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.processed.file_values import ProcessedFileMetadata
from dsp_tools.commands.xmlupload.models.processed.file_values import ProcessedFileValue
from dsp_tools.commands.xmlupload.models.processed.file_values import ProcessedIIIFUri
from dsp_tools.commands.xmlupload.models.processed.res import MigrationMetadata
from dsp_tools.commands.xmlupload.models.processed.res import ProcessedResource
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
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedValue
from dsp_tools.commands.xmlupload.prepare_xml_input.ark2iri import convert_ark_v0_to_resource_iri
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import TypeTransformerMapper
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import assert_is_string
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import assert_is_tuple
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import transform_boolean
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import transform_date
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import transform_decimal
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import transform_geometry
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import transform_integer
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import transform_interval
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import transform_richtext
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import transform_simpletext
from dsp_tools.error.exceptions import XmlUploadAuthorshipsNotFoundError
from dsp_tools.error.exceptions import XmlUploadListNodeNotFoundError
from dsp_tools.error.exceptions import XmlUploadPermissionsNotFoundError
from dsp_tools.legacy_models.datetimestamp import DateTimeStamp
from dsp_tools.utils.xml_parsing.models.parsed_resource import KnoraValueType
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedFileValue
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedFileValueMetadata
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedMigrationMetadata
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedResource
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedValue

TYPE_TRANSFORMER_MAPPER: dict[KnoraValueType, TypeTransformerMapper] = {
    KnoraValueType.BOOLEAN_VALUE: TypeTransformerMapper(ProcessedBoolean, transform_boolean),
    KnoraValueType.COLOR_VALUE: TypeTransformerMapper(ProcessedColor, assert_is_string),
    KnoraValueType.DECIMAL_VALUE: TypeTransformerMapper(ProcessedDecimal, transform_decimal),
    KnoraValueType.DATE_VALUE: TypeTransformerMapper(ProcessedDate, transform_date),
    KnoraValueType.GEOM_VALUE: TypeTransformerMapper(ProcessedGeometry, transform_geometry),
    KnoraValueType.GEONAME_VALUE: TypeTransformerMapper(ProcessedGeoname, assert_is_string),
    KnoraValueType.INT_VALUE: TypeTransformerMapper(ProcessedInt, transform_integer),
    KnoraValueType.INTERVAL_VALUE: TypeTransformerMapper(ProcessedInterval, transform_interval),
    KnoraValueType.TIME_VALUE: TypeTransformerMapper(ProcessedTime, assert_is_string),
    KnoraValueType.SIMPLETEXT_VALUE: TypeTransformerMapper(ProcessedSimpleText, transform_simpletext),
    KnoraValueType.URI_VALUE: TypeTransformerMapper(ProcessedUri, assert_is_string),
}


def get_processed_resources(
    resources: list[ParsedResource], lookups: XmlReferenceLookups, is_on_prod_like_server: bool
) -> list[ProcessedResource]:
    logger.debug("Transform ParsedResource into ProcessedResource")
    return [_get_one_resource(res, lookups, is_on_prod_like_server) for res in resources]


def _get_one_resource(
    resource: ParsedResource, lookups: XmlReferenceLookups, is_on_prod_like_server: bool
) -> ProcessedResource:
    permissions = _resolve_permission(resource.permissions_id, lookups.permissions)
    values = [_get_one_processed_value(val, lookups) for val in resource.values]
    migration_metadata = None
    file_val, iiif_uri = _resolve_file_value(resource, lookups, is_on_prod_like_server)
    if resource.migration_metadata:
        migration_metadata = _get_resource_migration_metadata(resource.migration_metadata)
    return ProcessedResource(
        res_id=resource.res_id,
        type_iri=resource.res_type,
        label=resource.label,
        permissions=permissions,
        values=values,
        file_value=file_val,
        iiif_uri=iiif_uri,
        migration_metadata=migration_metadata,
    )


def _get_resource_migration_metadata(metadata: ParsedMigrationMetadata) -> MigrationMetadata:
    res_iri = metadata.iri
    # ARK takes precedence over the IRI,
    # but must be transformed into an IRI as it is only for external reference and not consistent with a DB IRI
    if metadata.ark:
        res_iri = convert_ark_v0_to_resource_iri(metadata.ark)
    date = DateTimeStamp(metadata.creation_date) if metadata.creation_date else None
    return MigrationMetadata(res_iri, date)


def _resolve_file_value(
    resource: ParsedResource, lookups: XmlReferenceLookups, is_on_prod_like_server: bool
) -> tuple[None | ProcessedFileValue, None | ProcessedIIIFUri]:
    file_val, iiif_uri = None, None
    if not resource.file_value:
        return file_val, iiif_uri

    if is_on_prod_like_server:
        metadata = _get_file_metadata(resource.file_value.metadata, lookups)
    else:
        metadata = _get_file_metadata_for_test_environments(resource.file_value.metadata, lookups)
    if resource.file_value.value_type == KnoraValueType.STILL_IMAGE_IIIF:
        iiif_uri = _get_iiif_uri_value(resource.file_value, metadata)
    else:
        file_val = _get_file_value(
            val=resource.file_value, metadata=metadata, res_id=resource.res_id, res_label=resource.label
        )
    return file_val, iiif_uri


def _get_file_value(
    val: ParsedFileValue, metadata: ProcessedFileMetadata, res_id: str, res_label: str
) -> ProcessedFileValue:
    file_type = cast(KnoraValueType, val.value_type)
    file_val = assert_is_string(val.value)
    return ProcessedFileValue(
        value=file_val,
        file_type=file_type,
        metadata=metadata,
        res_id=res_id,
        res_label=res_label,
    )


def _get_iiif_uri_value(iiif_uri: ParsedFileValue, metadata: ProcessedFileMetadata) -> ProcessedIIIFUri:
    file_val = assert_is_string(iiif_uri.value)
    return ProcessedIIIFUri(file_val, metadata)


def _get_file_metadata(file_metadata: ParsedFileValueMetadata, lookups: XmlReferenceLookups) -> ProcessedFileMetadata:
    license_iri = assert_is_string(file_metadata.license_iri)
    copyright_holder = assert_is_string(file_metadata.copyright_holder)
    auth_id = assert_is_string(file_metadata.authorship_id)
    authorships = _resolve_authorship(auth_id, lookups.authorships)
    permissions = _resolve_permission(file_metadata.permissions_id, lookups.permissions)
    return ProcessedFileMetadata(
        license_iri=license_iri,
        copyright_holder=copyright_holder,
        authorships=authorships,
        permissions=permissions,
    )


def _get_file_metadata_for_test_environments(
    metadata: ParsedFileValueMetadata, lookups: XmlReferenceLookups
) -> ProcessedFileMetadata:
    lic_iri = metadata.license_iri or "http://rdfh.ch/licenses/unknown"
    copy_right = metadata.copyright_holder if metadata.copyright_holder else "DUMMY"
    if not metadata.authorship_id:
        authorship = ["DUMMY"]
    else:
        authorship = _resolve_authorship(metadata.authorship_id, lookups.authorships)
    permissions = _resolve_permission(metadata.permissions_id, lookups.permissions)
    return ProcessedFileMetadata(
        license_iri=lic_iri,
        copyright_holder=copy_right,
        authorships=authorship,
        permissions=permissions,
    )


def _resolve_authorship(authorship_id: str, lookup: dict[str, list[str]]) -> list[str]:
    if not (found := lookup.get(authorship_id)):
        raise XmlUploadAuthorshipsNotFoundError(f"Could not find authorships for value: {authorship_id}")
    return found


def _get_one_processed_value(val: ParsedValue, lookups: XmlReferenceLookups) -> ProcessedValue:
    match val.value_type:
        case KnoraValueType.LIST_VALUE:
            return _get_list_value(val, lookups)
        case KnoraValueType.LINK_VALUE:
            return _get_link_value(val, lookups)
        case KnoraValueType.RICHTEXT_VALUE:
            return _get_richtext_value(val, lookups)
        case _ as val_type:
            transformation_mapper = TYPE_TRANSFORMER_MAPPER[val_type]
            return _get_generic_value(val=val, lookups=lookups, transformation_mapper=transformation_mapper)


def _get_generic_value(
    val: ParsedValue, lookups: XmlReferenceLookups, transformation_mapper: TypeTransformerMapper
) -> ProcessedValue:
    transformed_value = transformation_mapper.val_transformer(val.value)
    permission_val = _resolve_permission(val.permissions_id, lookups.permissions)
    return transformation_mapper.val_type(transformed_value, val.prop_name, val.comment, permission_val)


def _get_link_value(val: ParsedValue, lookups: XmlReferenceLookups) -> ProcessedValue:
    transformed_value = assert_is_string(val.value)
    permission_val = _resolve_permission(val.permissions_id, lookups.permissions)
    link_val: ProcessedValue = ProcessedLink(
        value=transformed_value,
        prop_iri=val.prop_name,
        comment=val.comment,
        permissions=permission_val,
        value_uuid=str(uuid4()),
    )
    return link_val


def _get_list_value(val: ParsedValue, lookups: XmlReferenceLookups) -> ProcessedValue:
    tuple_val = assert_is_tuple(val.value)
    if not (list_iri := lookups.listnodes.get(tuple_val)):
        raise XmlUploadListNodeNotFoundError(f"Could not find list IRI for value: {tuple_val}")
    permission_val = _resolve_permission(val.permissions_id, lookups.permissions)
    list_val: ProcessedValue = ProcessedList(
        value=list_iri,
        prop_iri=val.prop_name,
        comment=val.comment,
        permissions=permission_val,
    )
    return list_val


def _get_richtext_value(val: ParsedValue, lookups: XmlReferenceLookups) -> ProcessedValue:
    transformed_value = transform_richtext(val.value)
    permission_val = _resolve_permission(val.permissions_id, lookups.permissions)
    richtext: ProcessedValue = ProcessedRichtext(
        value=transformed_value,
        prop_iri=val.prop_name,
        comment=val.comment,
        permissions=permission_val,
        resource_references=transformed_value.find_internal_ids(),
        value_uuid=str(uuid4()),
    )
    return richtext


def _resolve_permission(permissions: str | None, permissions_lookup: dict[str, Permissions]) -> Permissions | None:
    """Resolve the permission into a string that can be sent to the API."""
    if permissions:
        if not (per := permissions_lookup.get(permissions)):
            raise XmlUploadPermissionsNotFoundError(f"Could not find permissions for value: {permissions}")
        return per
    return None
