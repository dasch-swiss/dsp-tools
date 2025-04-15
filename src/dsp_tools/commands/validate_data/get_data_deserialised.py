import json
from json import JSONDecodeError
from typing import cast

import regex

from dsp_tools.commands.validate_data.mappers import FILE_TYPE_TO_PROP
from dsp_tools.utils.xml_parsing.models.data_deserialised import DataDeserialised
from dsp_tools.utils.xml_parsing.models.data_deserialised import MigrationMetadata
from dsp_tools.utils.xml_parsing.models.data_deserialised import PropertyObject
from dsp_tools.utils.xml_parsing.models.data_deserialised import ResourceDeserialised
from dsp_tools.utils.xml_parsing.models.data_deserialised import TripleObjectType
from dsp_tools.utils.xml_parsing.models.data_deserialised import TriplePropertyType
from dsp_tools.utils.xml_parsing.models.data_deserialised import ValueInformation
from dsp_tools.utils.xml_parsing.models.parsed_resource import KnoraValueType
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedFileValue
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedFileValueMetadata
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedResource
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedValue


def get_data_deserialised(resources: list[ParsedResource]) -> DataDeserialised:
    deserialised_resources = [_get_one_resource(x) for x in resources]
    return DataDeserialised(deserialised_resources)


def _get_one_resource(resource: ParsedResource) -> ResourceDeserialised:
    values = [_get_one_value(x) for x in resource.values]
    if resource.file_value:
        if file_val := _get_file_value(resource.file_value):
            values.append(file_val)
    metadata = [
        PropertyObject(TriplePropertyType.RDFS_LABEL, resource.label, TripleObjectType.STRING),
        PropertyObject(TriplePropertyType.RDF_TYPE, resource.res_type, TripleObjectType.IRI),
    ]
    metadata.extend(_get_all_stand_off_links(values))
    if resource.permissions_id is not None:
        metadata.append(
            PropertyObject(TriplePropertyType.KNORA_PERMISSIONS, resource.permissions_id, TripleObjectType.STRING)
        )
    return ResourceDeserialised(
        res_id=resource.res_id,
        property_objects=metadata,
        values=values,
        asset_value=None,
        migration_metadata=MigrationMetadata(),
    )


def _get_all_stand_off_links(values: list[ValueInformation]) -> list[PropertyObject]:
    stand_offs = []
    for val in values:
        if val.knora_type.RICHTEXT_VALUE:
            stand_offs.extend(_get_stand_off_links(val.user_facing_value))
    return stand_offs


def _get_stand_off_links(text: str | None) -> list[PropertyObject]:
    if not text:
        return []
    links = set(regex.findall(pattern='href="IRI:(.*?):IRI"', string=text))
    return [PropertyObject(TriplePropertyType.KNORA_STANDOFF_LINK, lnk, TripleObjectType.IRI) for lnk in links]


def _get_one_value(value: ParsedValue) -> ValueInformation:
    user_value = value.value
    match value.value_type:
        case KnoraValueType.INTERVAL_VALUE:
            return _get_interval_value(value)
        case KnoraValueType.LIST_VALUE:
            user_value = _get_list_value_str(user_value)
        case KnoraValueType.GEOM_VALUE:
            user_value = _get_geometry_value_str(user_value)
        case _:
            pass
    typed_val: str | None = user_value if isinstance(user_value, str) else None
    return _get_generic_value(value, typed_val)


def _get_generic_value(value: ParsedValue, user_value: str | None) -> ValueInformation:
    return ValueInformation(
        user_facing_prop=value.prop_name,
        user_facing_value=user_value,
        knora_type=value.value_type,
        value_metadata=_get_value_metadata(value),
    )


def _get_interval_value(value: ParsedValue) -> ValueInformation:
    property_objects = []
    tuple_val = value.value
    if isinstance(tuple_val, tuple):
        if first := tuple_val[0]:
            property_objects.append(
                PropertyObject(
                    property_type=TriplePropertyType.KNORA_INTERVAL_START,
                    object_value=first,
                    object_type=TripleObjectType.DECIMAL,
                )
            )
        if second := tuple_val[1]:
            property_objects.append(
                PropertyObject(
                    property_type=TriplePropertyType.KNORA_INTERVAL_END,
                    object_value=second,
                    object_type=TripleObjectType.DECIMAL,
                )
            )
    property_objects.extend(_get_value_metadata(value))
    return ValueInformation(
        user_facing_prop=value.prop_name,
        user_facing_value=None,
        knora_type=value.value_type,
        value_metadata=property_objects,
    )


def _get_list_value_str(user_value: str | tuple[str | None, str | None] | None) -> str | None:
    if not isinstance(user_value, tuple):
        return None
    return " / ".join(x for x in user_value if x is not None)


def _get_geometry_value_str(user_value: str | tuple[str | None, str | None] | None) -> str | None:
    try:
        if isinstance(user_value, str):
            return json.dumps(json.loads(user_value))
        return None
    except JSONDecodeError:
        return None


def _get_value_metadata(value: ParsedValue) -> list[PropertyObject]:
    metadata = []
    if value.permissions_id is not None:
        metadata.append(
            PropertyObject(
                property_type=TriplePropertyType.KNORA_PERMISSIONS,
                object_value=value.permissions_id,
                object_type=TripleObjectType.STRING,
            )
        )
    if value.comment is not None:
        metadata.append(
            PropertyObject(
                property_type=TriplePropertyType.KNORA_COMMENT_ON_VALUE,
                object_value=value.comment,
                object_type=TripleObjectType.STRING,
            )
        )
    return metadata


def _get_file_value(file_value: ParsedFileValue) -> ValueInformation | None:
    if not all([file_value.value, file_value.value_type]):
        return None
    file_type = cast(KnoraValueType, file_value.value_type)
    user_prop = FILE_TYPE_TO_PROP[file_type]
    return ValueInformation(
        user_facing_prop=user_prop,
        user_facing_value=file_value.value,
        knora_type=file_type,
        value_metadata=_get_file_metadata(file_value.metadata),
    )


def _get_file_metadata(metadata: ParsedFileValueMetadata) -> list[PropertyObject]:
    property_objects = []
    if metadata.license_iri is not None:
        property_objects.append(
            PropertyObject(
                property_type=TriplePropertyType.KNORA_LICENSE,
                object_value=metadata.license_iri,
                object_type=TripleObjectType.IRI,
            )
        )
    if metadata.copyright_holder is not None:
        property_objects.append(
            PropertyObject(
                property_type=TriplePropertyType.KNORA_COPYRIGHT_HOLDER,
                object_value=metadata.copyright_holder,
                object_type=TripleObjectType.STRING,
            )
        )
    if metadata.authorship_id is not None:
        property_objects.append(
            PropertyObject(
                property_type=TriplePropertyType.KNORA_AUTHORSHIP,
                object_value=metadata.authorship_id,
                object_type=TripleObjectType.STRING,
            )
        )
    if metadata.permissions_id is not None:
        property_objects.append(
            PropertyObject(
                property_type=TriplePropertyType.KNORA_PERMISSIONS,
                object_value=metadata.permissions_id,
                object_type=TripleObjectType.STRING,
            )
        )
    return property_objects
