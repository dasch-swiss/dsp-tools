from typing import Callable

from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import IIIFUriInfo
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLBitstream
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLProperty
from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import XMLResource
from dsp_tools.commands.xmlupload.models.formatted_text_value import FormattedTextValue
from dsp_tools.commands.xmlupload.models.intermediary.file_values import IntermediaryAbstractFileValue
from dsp_tools.commands.xmlupload.models.intermediary.resource import IntermediaryResource
from dsp_tools.commands.xmlupload.models.intermediary.resource import MigrationMetadata
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
from dsp_tools.commands.xmlupload.models.intermediary.values import ValueTypes
from dsp_tools.commands.xmlupload.models.lookup_models import IntermediaryLookup
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.transform_input_values import assert_is_string
from dsp_tools.commands.xmlupload.transform_input_values import transform_boolean
from dsp_tools.commands.xmlupload.transform_input_values import transform_date
from dsp_tools.commands.xmlupload.transform_input_values import transform_decimal
from dsp_tools.commands.xmlupload.transform_input_values import transform_geometry
from dsp_tools.commands.xmlupload.transform_input_values import transform_integer
from dsp_tools.commands.xmlupload.transform_input_values import transform_interval
from dsp_tools.models.exceptions import InputError
from dsp_tools.models.exceptions import PermissionNotExistsError

TYPE_TRANSFORMER_MAPPER = {
    "bool": (IntermediaryBoolean, transform_boolean),
    "color": (IntermediaryColor, assert_is_string),
    "decimal": (IntermediaryDecimal, transform_decimal),
    "date": (IntermediaryDate, transform_date),
    "geometry": (IntermediaryGeometry, transform_geometry),
    "geoname": (IntermediaryGeoname, assert_is_string),
    "integer": (IntermediaryInt, transform_integer),
    "interval": (IntermediaryInterval, transform_interval),
    "resptr": (IntermediaryLink, assert_is_string),
    "time": (IntermediaryTime, assert_is_string),
    "uri": (IntermediaryUri, assert_is_string),
}


def transform_into_intermediary_classes(
    resources: list[XMLResource], lookups: IntermediaryLookup
) -> list[IntermediaryResource]:
    pass


def _transform_one_resource(resource: XMLResource, lookups: IntermediaryLookup) -> IntermediaryResource:
    pass


def _transform_segment(resource: XMLResource, lookups: IntermediaryLookup) -> IntermediaryResource:
    pass


def _transform_migration_metadata(resource: XMLResource) -> MigrationMetadata:
    pass


def _transform_one_file_value(
    value: XMLBitstream | IIIFUriInfo, lookups: IntermediaryLookup
) -> IntermediaryAbstractFileValue:
    pass


def _transform_one_property(prop: XMLProperty, lookups: IntermediaryLookup) -> list[IntermediaryValue]:
    match prop.valtype:
        case "list":
            return _transform_list_values(prop, lookups)
        case "text":
            return _transform_text_values(prop, lookups)
        case _ as val_type:
            prop_type, transformer = TYPE_TRANSFORMER_MAPPER[val_type]
            return _transform_one_generic_value(
                prop=prop,
                lookups=lookups,
                prop_intermediary=prop_type,
                transformer=transformer,
            )


def _transform_one_generic_value(
    prop: XMLProperty,
    lookups: IntermediaryLookup,
    prop_intermediary: Callable[[ValueTypes, str, str | None, Permissions | None], IntermediaryValue],
    transformer: Callable[[str | FormattedTextValue], ValueTypes],
) -> list[IntermediaryValue]:
    intermediary_values = []
    prop_iri = _get_absolute_iri(prop.name, lookups.namespaces)
    for val in prop.values:
        transformed_value = transformer(val.value)
        permission_val = _resolve_permission(val.permissions, lookups.permissions)
        intermediary_values.append(prop_intermediary(transformed_value, prop_iri, val.comment, permission_val))
    return intermediary_values


def _transform_list_values(prop: XMLProperty, lookups: IntermediaryLookup) -> list[IntermediaryValue]:
    intermediary_values: list[IntermediaryValue] = []
    prop_iri = _get_absolute_iri(prop.name, lookups.namespaces)
    for val in prop.values:
        str_val = assert_is_string(val.value)
        if not (list_iri := lookups.listnodes.get(str_val)):
            raise InputError(f"Could not find list iri for node: {list_iri}")
        permission_val = _resolve_permission(val.permissions, lookups.permissions)
        intermediary_values.append(IntermediaryList(list_iri, prop_iri, val.comment, permission_val))
    return intermediary_values


def _transform_text_values(prop: XMLProperty, lookups: IntermediaryLookup) -> list[IntermediaryValue]:
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
