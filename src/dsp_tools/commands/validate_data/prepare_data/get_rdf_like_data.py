import json
from json import JSONDecodeError
from typing import Any
from typing import cast

import regex
from lxml import etree

from dsp_tools.commands.validate_data.mappers import FILE_TYPE_TO_PROP
from dsp_tools.commands.validate_data.models.api_responses import ListLookup
from dsp_tools.commands.validate_data.models.rdf_like_data import MigrationMetadata
from dsp_tools.commands.validate_data.models.rdf_like_data import PropertyObject
from dsp_tools.commands.validate_data.models.rdf_like_data import RdfLikeData
from dsp_tools.commands.validate_data.models.rdf_like_data import RdfLikeResource
from dsp_tools.commands.validate_data.models.rdf_like_data import RdfLikeValue
from dsp_tools.commands.validate_data.models.rdf_like_data import TripleObjectType
from dsp_tools.commands.validate_data.models.rdf_like_data import TriplePropertyType
from dsp_tools.utils.data_formats.date_util import Era
from dsp_tools.utils.data_formats.date_util import SingleDate
from dsp_tools.utils.data_formats.date_util import parse_date_string
from dsp_tools.utils.xml_parsing.models.parsed_resource import KnoraValueType
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedFileValue
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedFileValueMetadata
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedResource
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedValue


def get_rdf_like_data(
    resources: list[ParsedResource], authorship_lookup: dict[str, list[str]], list_node_lookup: ListLookup
) -> RdfLikeData:
    rdf_like_resources = [_get_one_resource(x, authorship_lookup, list_node_lookup) for x in resources]
    return RdfLikeData(rdf_like_resources)


def _get_one_resource(
    resource: ParsedResource, authorship_lookup: dict[str, list[str]], list_node_lookup: ListLookup
) -> RdfLikeResource:
    values = [_get_one_value(x, list_node_lookup) for x in resource.values]
    if resource.file_value:
        if file_val := _get_file_value(resource.file_value, authorship_lookup):
            values.append(file_val)
    metadata = [
        PropertyObject(TriplePropertyType.RDFS_LABEL, resource.label, TripleObjectType.STRING),
        PropertyObject(TriplePropertyType.RDF_TYPE, resource.res_type, TripleObjectType.IRI),
    ]
    metadata.extend(_get_all_stand_off_links(resource.values))
    if resource.permissions_id is not None:
        metadata.append(
            PropertyObject(TriplePropertyType.KNORA_PERMISSIONS, resource.permissions_id, TripleObjectType.STRING)
        )
    return RdfLikeResource(
        res_id=resource.res_id,
        property_objects=metadata,
        values=values,
        migration_metadata=MigrationMetadata(),
    )


def _get_all_stand_off_links(values: list[ParsedValue]) -> list[PropertyObject]:
    stand_off_ids = set()
    for val in values:
        if val.value_type == KnoraValueType.RICHTEXT_VALUE:
            if isinstance(val.value, str):
                new_ids = _get_resource_ids_and_iri_strings(val.value)
                stand_off_ids.update(new_ids)
    return [_get_stand_off_links(x) for x in stand_off_ids]


def _get_resource_ids_and_iri_strings(text: str) -> set[str]:
    txt_wrapped = f"<wrapper>{text}</wrapper>"
    text_tree = etree.fromstring(txt_wrapped)
    all_hrefs = set()
    for a_link in text_tree.iterdescendants(tag="a"):
        if a_link.get("class") == "salsah-link":
            if found := a_link.get("href"):
                all_hrefs.add(found)
    return all_hrefs


def _get_stand_off_links(extracted: str) -> PropertyObject:
    link, obj_type = _get_link_string_and_triple_object_type(extracted)
    return PropertyObject(TriplePropertyType.KNORA_STANDOFF_LINK, link, obj_type)


def _get_link_string_and_triple_object_type(res_link: str) -> tuple[str, TripleObjectType]:
    if found := regex.search(r"IRI:(.*?):IRI", res_link):
        return found.group(1), TripleObjectType.INTERNAL_ID
    if res_link.startswith("http://rdfh.ch/"):
        return res_link, TripleObjectType.IRI
    # if it is not a valid IRI, rdflib may crash when trying to turn it into one
    # the TripleObjectType.INTERNAL_ID only expects a string and is therefore able to deal with malformed content
    return res_link, TripleObjectType.INTERNAL_ID


def _get_one_value(value: ParsedValue, list_node_lookup: ListLookup) -> RdfLikeValue:
    user_value = value.value
    match value.value_type:
        case KnoraValueType.DATE_VALUE:
            return _get_date_value(value)
        case KnoraValueType.INTERVAL_VALUE:
            return _get_interval_value(value)
        case KnoraValueType.LIST_VALUE:
            user_value = _get_list_value_str(user_value, list_node_lookup)
        case KnoraValueType.GEOM_VALUE:
            user_value = _get_geometry_value_str(user_value)
        case _:
            pass
    typed_val: str | None = user_value if isinstance(user_value, str) else None
    return _get_generic_value(value, typed_val)


def _get_generic_value(value: ParsedValue, user_value: str | None) -> RdfLikeValue:
    return RdfLikeValue(
        user_facing_prop=value.prop_name,
        user_facing_value=user_value,
        knora_type=value.value_type,
        value_metadata=_get_value_metadata(value),
    )


def _get_date_value(value: ParsedValue) -> RdfLikeValue:
    typed_val: str | None = value.value if isinstance(value.value, str) else None
    date_metadata = _get_value_metadata(value)
    if typed_val:
        date_metadata.extend(_get_xsd_like_dates(typed_val))
    return RdfLikeValue(
        user_facing_prop=value.prop_name,
        user_facing_value=typed_val,
        knora_type=value.value_type,
        value_metadata=date_metadata,
    )


def _get_xsd_like_dates(date_string: str) -> list[PropertyObject]:
    parsed_date = parse_date_string(date_string)
    dates = []
    if not (ce_start := _make_xsd_compatible_date(parsed_date.start, TriplePropertyType.KNORA_DATE_START)):
        return []
    dates.append(ce_start)
    if parsed_date.end:
        if ce_end := _make_xsd_compatible_date(parsed_date.end, TriplePropertyType.KNORA_DATE_END):
            dates.append(ce_end)
    return dates


def _make_xsd_compatible_date(single_date: SingleDate, prop_type: TriplePropertyType) -> PropertyObject | None:
    if single_date.era in (Era.BC, Era.BCE):
        return None
    date_str = _get_date_str(single_date)
    return PropertyObject(
        property_type=prop_type,
        object_value=date_str,
        object_type=TripleObjectType.DATE_YYYY_MM_DD,
    )


def _get_date_str(date: SingleDate) -> str:
    # SHACL cannot compare dates of varying precision, therefore we turn partial dates into full dates
    date_str = [str(date.year).zfill(4)]
    if date.month:
        date_str.append(str(date.month).zfill(2))
    else:
        date_str.append("01")
    if date.day:
        date_str.append(str(date.day).zfill(2))
    else:
        date_str.append("01")
    return "-".join(date_str)


def _get_interval_value(value: ParsedValue) -> RdfLikeValue:
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
    return RdfLikeValue(
        user_facing_prop=value.prop_name,
        user_facing_value=None,
        knora_type=value.value_type,
        value_metadata=property_objects,
    )


def _get_list_value_str(user_value: str | tuple[str | None, str | None] | None, list_node_lookup: ListLookup) -> str:
    in_tuple = cast(tuple[Any, Any], user_value)
    if found := list_node_lookup.lists.get(in_tuple):
        return found
    return " / ".join(x for x in in_tuple if x is not None)


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


def _get_file_value(file_value: ParsedFileValue, authorship_lookup: dict[str, list[str]]) -> RdfLikeValue | None:
    if not all([file_value.value, file_value.value_type]):
        return None
    file_type = cast(KnoraValueType, file_value.value_type)
    user_prop = FILE_TYPE_TO_PROP[file_type]
    return RdfLikeValue(
        user_facing_prop=user_prop,
        user_facing_value=file_value.value,
        knora_type=file_type,
        value_metadata=_get_file_metadata(file_value.metadata, authorship_lookup),
    )


def _get_file_metadata(
    metadata: ParsedFileValueMetadata, authorship_lookup: dict[str, list[str]]
) -> list[PropertyObject]:
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
        if not (found_authors := authorship_lookup.get(metadata.authorship_id)):
            property_objects.append(
                PropertyObject(
                    property_type=TriplePropertyType.KNORA_AUTHORSHIP,
                    object_value="",
                    object_type=TripleObjectType.STRING,
                )
            )
        else:
            for auth in found_authors:
                property_objects.append(
                    PropertyObject(
                        property_type=TriplePropertyType.KNORA_AUTHORSHIP,
                        object_value=auth,
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
