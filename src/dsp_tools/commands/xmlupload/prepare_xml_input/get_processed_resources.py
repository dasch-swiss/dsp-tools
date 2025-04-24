from uuid import uuid4

from dsp_tools.commands.xmlupload.models.lookup_models import XmlReferenceLookups
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.processed.file_values import ProcessedFileMetadata
from dsp_tools.commands.xmlupload.models.processed.file_values import ProcessedFileValue
from dsp_tools.commands.xmlupload.models.processed.file_values import ProcessedIIIFUri
from dsp_tools.commands.xmlupload.models.processed.res import MigrationMetadata
from dsp_tools.commands.xmlupload.models.processed.res import ProcessedResource
from dsp_tools.commands.xmlupload.models.processed.res import ResourceInputProcessingFailure
from dsp_tools.commands.xmlupload.models.processed.res import ResourceProcessingResult
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
from dsp_tools.error.exceptions import InputError
from dsp_tools.error.exceptions import PermissionNotExistsError
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


def get_processed_resources(resources: list[ParsedResource], lookups: XmlReferenceLookups) -> ResourceProcessingResult:
    failures = []
    processed = []
    for res in resources:
        try:
            result = _get_one_resource(res, lookups)
            processed.append(result)
        except (PermissionNotExistsError, InputError) as e:
            failures.append(ResourceInputProcessingFailure(res.res_id, str(e)))
    return ResourceProcessingResult(processed, failures)


def _get_one_resource(resource: ParsedResource, lookups: XmlReferenceLookups) -> ProcessedResource:
    permissions = _resolve_permission(resource.permissions_id, lookups.permissions)
    values = [_get_one_processed_value(val, lookups) for val in resource.values]
    file_val, iiif_uri, migration_metadata = None, None, None
    if resource.file_value:
        if resource.file_value.value_type == KnoraValueType.STILL_IMAGE_IIIF:
            iiif_uri = _get_iiif_uri_value(resource.file_value, lookups)
        else:
            file_val = _get_file_value(
                val=resource.file_value, lookups=lookups, res_id=resource.res_id, res_label=resource.label
            )
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


def _get_file_value(
    val: ParsedFileValue, lookups: XmlReferenceLookups, res_id: str, res_label: str
) -> ProcessedFileValue:
    metadata = _get_file_metadata(val.metadata, lookups)
    file_val = assert_is_string(val.value)
    return ProcessedFileValue(value=file_val, metadata=metadata, res_id=res_id, res_label=res_label)


def _get_iiif_uri_value(iiif_uri: ParsedFileValue, lookups: XmlReferenceLookups) -> ProcessedIIIFUri:
    metadata = _get_file_metadata(iiif_uri.metadata, lookups)
    file_val = assert_is_string(iiif_uri.value)
    return ProcessedIIIFUri(file_val, metadata)


def _get_file_metadata(file_metadata: ParsedFileValueMetadata, lookups: XmlReferenceLookups) -> ProcessedFileMetadata:
    permissions = _resolve_permission(file_metadata.permissions_id, lookups.permissions)
    predefined_licenses = [
        "http://rdfh.ch/licenses/cc-by-4.0",
        "http://rdfh.ch/licenses/cc-by-sa-4.0",
        "http://rdfh.ch/licenses/cc-by-nc-4.0",
        "http://rdfh.ch/licenses/cc-by-nc-sa-4.0",
        "http://rdfh.ch/licenses/cc-by-nd-4.0",
        "http://rdfh.ch/licenses/cc-by-nc-nd-4.0",
        "http://rdfh.ch/licenses/ai-generated",
        "http://rdfh.ch/licenses/unknown",
        "http://rdfh.ch/licenses/public-domain",
    ]
    if file_metadata.license_iri and file_metadata.license_iri not in predefined_licenses:
        raise InputError(
            f"The license '{file_metadata.license_iri}' used for an image or iiif-uri is unknown. "
            f"See documentation for accepted pre-defined licenses."
        )
    return ProcessedFileMetadata(
        license_iri=file_metadata.license_iri,
        copyright_holder=file_metadata.copyright_holder,
        authorships=_resolve_authorship(file_metadata.authorship_id, lookups.authorships),
        permissions=permissions,
    )


def _resolve_authorship(authorship_id: str | None, lookup: dict[str, list[str]]) -> list[str] | None:
    if not authorship_id:
        return None
    if not (found := lookup.get(authorship_id)):
        raise InputError(
            f"The authorship id '{authorship_id}' referenced in a multimedia file or iiif-uri is unknown. "
            f"Ensure that all referenced ids are defined in the `<authorship>` elements of your XML file."
        )
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
        raise InputError(f"Could not find list iri for node: {' / '.join(tuple_val)}")
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
            raise PermissionNotExistsError(f"Could not find permissions for value: {permissions}")
        return per
    return None
