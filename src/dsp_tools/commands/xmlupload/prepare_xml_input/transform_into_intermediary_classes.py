from uuid import uuid4

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
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryLink
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryList
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryRichtext
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediarySimpleText
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryTime
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryUri
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryValue
from dsp_tools.commands.xmlupload.models.lookup_models import IntermediaryLookups
from dsp_tools.commands.xmlupload.models.permission import Permissions
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
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import transform_simple_text
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
    KnoraValueType.BOOLEAN_VALUE: TypeTransformerMapper(IntermediaryBoolean, transform_boolean),
    KnoraValueType.COLOR_VALUE: TypeTransformerMapper(IntermediaryColor, assert_is_string),
    KnoraValueType.DECIMAL_VALUE: TypeTransformerMapper(IntermediaryDecimal, transform_decimal),
    KnoraValueType.DATE_VALUE: TypeTransformerMapper(IntermediaryDate, transform_date),
    KnoraValueType.GEOM_VALUE: TypeTransformerMapper(IntermediaryGeometry, transform_geometry),
    KnoraValueType.GEONAME_VALUE: TypeTransformerMapper(IntermediaryGeoname, assert_is_string),
    KnoraValueType.INT_VALUE: TypeTransformerMapper(IntermediaryInt, transform_integer),
    KnoraValueType.INTERVAL_VALUE: TypeTransformerMapper(IntermediaryInterval, transform_interval),
    KnoraValueType.TIME_VALUE: TypeTransformerMapper(IntermediaryTime, assert_is_string),
    KnoraValueType.SIMPLETEXT_VALUE: TypeTransformerMapper(IntermediarySimpleText, transform_simple_text),
    KnoraValueType.RICHTEXT_VALUE: TypeTransformerMapper(IntermediaryRichtext, transform_richtext),
    KnoraValueType.URI_VALUE: TypeTransformerMapper(IntermediaryUri, assert_is_string),
}


def transform_all_resources_into_intermediary_resources(
    resources: list[ParsedResource], lookups: IntermediaryLookups
) -> ResourceTransformationResult:
    failures = []
    transformed = []
    for res in resources:
        result = _transform_into_intermediary_resource(res, lookups)
        if isinstance(result, IntermediaryResource):
            transformed.append(result)
        else:
            failures.append(result)
    return ResourceTransformationResult(transformed, failures)


def _transform_into_intermediary_resource(
    resource: ParsedResource, lookups: IntermediaryLookups
) -> IntermediaryResource | ResourceInputConversionFailure:
    try:
        return _transform_one_resource(resource, lookups)
    except (PermissionNotExistsError, InputError) as e:
        return ResourceInputConversionFailure(resource.res_id, str(e))


def _transform_one_resource(resource: ParsedResource, lookups: IntermediaryLookups) -> IntermediaryResource:
    permissions = _resolve_permission(resource.permissions_id, lookups.permissions)
    values = _transform_all_values(resource.values, lookups)
    file_val, iiif_uri, migration_metadata = None, None, None
    if resource.file_value:
        if resource.file_value.value_type == KnoraValueType.STILL_IMAGE_IIIF:
            iiif_uri = _transform_iiif_uri_value(resource.file_value, lookups)
        else:
            file_val = _transform_file_value(resource.file_value, lookups, resource.res_id, resource.res_type)
    if resource.migration_metadata:
        migration_metadata = _transform_migration_metadata(resource.migration_metadata)
    return IntermediaryResource(
        res_id=resource.res_id,
        type_iri=resource.res_type,
        label=resource.label,
        permissions=permissions,
        values=values,
        file_value=file_val,
        iiif_uri=iiif_uri,
        migration_metadata=migration_metadata,
    )


def _transform_migration_metadata(metadata: ParsedMigrationMetadata) -> MigrationMetadata:
    res_iri = metadata.iri
    if metadata.ark:
        res_iri = convert_ark_v0_to_resource_iri(metadata.ark)
    date = None
    if metadata.creation_date:
        date = DateTimeStamp(metadata.creation_date)
    return MigrationMetadata(res_iri, date)


def _transform_file_value(
    val: ParsedFileValue, lookups: IntermediaryLookups, res_id: str, res_label: str
) -> IntermediaryFileValue:
    metadata = _get_metadata(val.metadata, lookups)
    return IntermediaryFileValue(value=val.value, metadata=metadata, res_id=res_id, res_label=res_label)


def _transform_iiif_uri_value(iiif_uri: ParsedFileValue, lookups: IntermediaryLookups) -> IntermediaryIIIFUri:
    metadata = _get_metadata(iiif_uri.metadata, lookups)
    return IntermediaryIIIFUri(iiif_uri.value, metadata)


def _get_metadata(file_metadata: ParsedFileValueMetadata, lookups: IntermediaryLookups) -> IntermediaryFileMetadata:
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
    return IntermediaryFileMetadata(
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


def _transform_all_values(values: list[ParsedValue], lookups: IntermediaryLookups) -> list[IntermediaryValue]:
    all_values = []
    for val in values:
        all_values.append(_transform_one_value(val, lookups))
    return all_values


def _transform_one_value(val: ParsedValue, lookups: IntermediaryLookups) -> IntermediaryValue:
    match val.value_type:
        case KnoraValueType.LIST_VALUE:
            return _transform_list_value(val, lookups)
        case KnoraValueType.LINK_VALUE:
            return _transform_link_value(val, lookups)
        case _ as val_type:
            transformation_mapper = TYPE_TRANSFORMER_MAPPER[val_type]
            return _transform_generic_value(val=val, lookups=lookups, transformation_mapper=transformation_mapper)


def _transform_generic_value(
    val: ParsedValue, lookups: IntermediaryLookups, transformation_mapper: TypeTransformerMapper
) -> IntermediaryValue:
    transformed_value = transformation_mapper.val_transformer(val.value)
    permission_val = _resolve_permission(val.permissions_id, lookups.permissions)
    return transformation_mapper.val_type(transformed_value, val.prop_name, val.comment, permission_val)


def _transform_link_value(val: ParsedValue, lookups: IntermediaryLookups) -> IntermediaryValue:
    transformed_value = assert_is_string(val.value)
    permission_val = _resolve_permission(val.permissions_id, lookups.permissions)
    link_val: IntermediaryValue = IntermediaryLink(
        value=transformed_value,
        prop_iri=val.prop_name,
        comment=val.comment,
        permissions=permission_val,
        value_uuid=str(uuid4()),
    )
    return link_val


def _transform_list_value(val: ParsedValue, lookups: IntermediaryLookups) -> IntermediaryValue:
    tuple_val = assert_is_tuple(val.value)
    if not (list_iri := lookups.listnodes.get(tuple_val)):
        raise InputError(f"Could not find list iri for node: {' / '.join(tuple_val)}")
    permission_val = _resolve_permission(val.permissions_id, lookups.permissions)
    list_val: IntermediaryValue = IntermediaryList(
        value=list_iri,
        prop_iri=val.prop_name,
        comment=val.comment,
        permissions=permission_val,
    )
    return list_val


def _resolve_permission(permissions: str | None, permissions_lookup: dict[str, Permissions]) -> Permissions | None:
    """Resolve the permission into a string that can be sent to the API."""
    if permissions:
        if not (per := permissions_lookup.get(permissions)):
            raise PermissionNotExistsError(f"Could not find permissions for value: {permissions}")
        return per
    return None
