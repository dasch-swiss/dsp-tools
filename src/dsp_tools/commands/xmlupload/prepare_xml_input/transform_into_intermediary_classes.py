from uuid import uuid4

from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import IIIFUriInfo
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLBitstream
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLFileMetadata
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLProperty
from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import XMLResource
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
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import transform_boolean
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import transform_date
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import transform_decimal
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import transform_geometry
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import transform_integer
from dsp_tools.commands.xmlupload.prepare_xml_input.transform_input_values import transform_interval
from dsp_tools.models.exceptions import InputError
from dsp_tools.models.exceptions import PermissionNotExistsError

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
    resources: list[XMLResource], lookups: IntermediaryLookups
) -> ResourceTransformationResult:
    """
    Takes the XMLResources parsed from the XML file and converts them into the Intermediary format.
    Permissions, relative IRIs, etc. are resolved in this step.

    Args:
        resources: resource list
        lookups: lookup for permissions, prefixes, etc.

    Returns:
        An object containing the transformed resources and transformation failure information
    """
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
    resource: XMLResource, lookups: IntermediaryLookups
) -> IntermediaryResource | ResourceInputConversionFailure:
    try:
        return _transform_one_resource(resource, lookups)
    except (PermissionNotExistsError, InputError) as e:
        return ResourceInputConversionFailure(resource.res_id, str(e))


def _transform_one_resource(resource: XMLResource, lookups: IntermediaryLookups) -> IntermediaryResource:
    file_value, iiif_uri, migration_metadata = None, None, None
    if resource.bitstream:
        file_value = _transform_file_value(resource.bitstream, lookups, resource.res_id, resource.label)
    elif resource.iiif_uri:
        iiif_uri = _transform_iiif_uri_value(resource.iiif_uri, lookups)
    if any([resource.ark, resource.creation_date, resource.iri]):
        migration_metadata = _transform_migration_metadata(resource)
    all_values = _transform_all_properties(resource.properties, lookups)
    permissions = _resolve_permission(resource.permissions, lookups.permissions)
    type_iri = _get_absolute_iri(resource.restype, lookups.namespaces)
    return IntermediaryResource(
        res_id=resource.res_id,
        type_iri=type_iri,
        label=resource.label,
        permissions=permissions,
        values=all_values,
        file_value=file_value,
        iiif_uri=iiif_uri,
        migration_metadata=migration_metadata,
    )


def _transform_migration_metadata(resource: XMLResource) -> MigrationMetadata:
    res_iri = resource.iri
    if resource.ark:
        res_iri = convert_ark_v0_to_resource_iri(resource.ark)
    return MigrationMetadata(res_iri, resource.creation_date)


def _transform_file_value(
    bitstream: XMLBitstream, lookups: IntermediaryLookups, res_id: str, res_label: str
) -> IntermediaryFileValue:
    metadata = _get_metadata(bitstream.metadata, lookups)
    return IntermediaryFileValue(bitstream.value, metadata, res_id, res_label)


def _transform_iiif_uri_value(iiif_uri: IIIFUriInfo, lookups: IntermediaryLookups) -> IntermediaryIIIFUri:
    metadata = _get_metadata(iiif_uri.metadata, lookups)
    return IntermediaryIIIFUri(iiif_uri.value, metadata)


def _get_metadata(file_metadata: XMLFileMetadata, lookups: IntermediaryLookups) -> IntermediaryFileMetadata:
    permissions = _resolve_permission(file_metadata.permissions, lookups.permissions)
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
    if file_metadata.license_ and file_metadata.license_ not in predefined_licenses:
        raise InputError(
            f"The license '{file_metadata.license_}' used for an image or iiif-uri is unknown. "
            f"See documentation for accepted pre-defined licenses."
        )
    return IntermediaryFileMetadata(
        license_iri=file_metadata.license_,
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
            f"Ensure that all referenced ids are defined in the `<authorship>` elements of your XML."
        )
    return found


def _transform_all_properties(properties: list[XMLProperty], lookups: IntermediaryLookups) -> list[IntermediaryValue]:
    all_values = []
    for prop in properties:
        all_values.extend(_transform_one_property(prop, lookups))
    return all_values


def _transform_one_property(prop: XMLProperty, lookups: IntermediaryLookups) -> list[IntermediaryValue]:
    match prop.valtype:
        case "list":
            return _transform_list_values(prop, lookups)
        case "text":
            return _transform_text_values(prop, lookups)
        case "resptr":
            return _transform_one_link_value(prop, lookups)
        case _ as val_type:
            transformation_mapper = TYPE_TRANSFORMER_MAPPER[val_type]
            return _transform_one_generic_value(prop=prop, lookups=lookups, transformation_mapper=transformation_mapper)


def _transform_one_generic_value(
    prop: XMLProperty, lookups: IntermediaryLookups, transformation_mapper: TypeTransformerMapper
) -> list[IntermediaryValue]:
    intermediary_values = []
    prop_iri = _get_absolute_iri(prop.name, lookups.namespaces)
    for val in prop.values:
        transformed_value = transformation_mapper.val_transformer(val.value)
        permission_val = _resolve_permission(val.permissions, lookups.permissions)
        intermediary_values.append(
            transformation_mapper.val_type(transformed_value, prop_iri, val.comment, permission_val)
        )
    return intermediary_values


def _transform_one_link_value(prop: XMLProperty, lookups: IntermediaryLookups) -> list[IntermediaryValue]:
    intermediary_values: list[IntermediaryValue] = []
    prop_iri = _get_absolute_iri(prop.name, lookups.namespaces)
    for val in prop.values:
        transformed_value = assert_is_string(val.value)
        permission_val = _resolve_permission(val.permissions, lookups.permissions)
        intermediary_values.append(
            IntermediaryLink(transformed_value, prop_iri, val.comment, permission_val, str(uuid4()))
        )
    return intermediary_values


def _transform_list_values(prop: XMLProperty, lookups: IntermediaryLookups) -> list[IntermediaryValue]:
    intermediary_values: list[IntermediaryValue] = []
    prop_iri = _get_absolute_iri(prop.name, lookups.namespaces)
    for val in prop.values:
        str_val = assert_is_string(val.value)
        if not (list_iri := lookups.listnodes.get(str_val)):
            raise InputError(f"Could not find list iri for node: {str_val}")
        permission_val = _resolve_permission(val.permissions, lookups.permissions)
        intermediary_values.append(IntermediaryList(list_iri, prop_iri, val.comment, permission_val))
    return intermediary_values


def _transform_text_values(prop: XMLProperty, lookups: IntermediaryLookups) -> list[IntermediaryValue]:
    intermediary_values: list[IntermediaryValue] = []
    prop_iri = _get_absolute_iri(prop.name, lookups.namespaces)
    for val in prop.values:
        permission_val = _resolve_permission(val.permissions, lookups.permissions)
        if isinstance(val.value, str):
            intermediary_values.append(IntermediarySimpleText(val.value, prop_iri, val.comment, permission_val))
        else:
            intermediary_values.append(
                IntermediaryRichtext(
                    value=val.value,
                    prop_iri=prop_iri,
                    comment=val.comment,
                    permissions=permission_val,
                    resource_references=val.resrefs,
                    value_uuid=str(uuid4()),
                )
            )
    return intermediary_values


def _get_absolute_iri(prefixed_iri: str, namespaces: dict[str, str]) -> str:
    prefix, prop = prefixed_iri.split(":", maxsplit=1)
    if not (namespace := namespaces.get(prefix)):
        raise InputError(f"Could not find namespace for prefix: {prefix}")
    return f"{namespace}{prop}"


def _resolve_permission(permissions: str | None, permissions_lookup: dict[str, Permissions]) -> Permissions | None:
    """Resolve the permission into a string that can be sent to the API."""
    if permissions:
        if not (per := permissions_lookup.get(permissions)):
            raise PermissionNotExistsError(f"Could not find permissions for value: {permissions}")
        return per
    return None
