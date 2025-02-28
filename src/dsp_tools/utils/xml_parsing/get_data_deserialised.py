import json
from json import JSONDecodeError
from pathlib import Path

import regex
from lxml import etree

from dsp_tools.commands.validate_data.constants import AUDIO_SEGMENT_RESOURCE
from dsp_tools.commands.validate_data.constants import KNORA_API_STR
from dsp_tools.commands.validate_data.constants import VIDEO_SEGMENT_RESOURCE
from dsp_tools.commands.validate_data.mappers import SEGMENT_TAG_TO_PROP_MAPPER
from dsp_tools.commands.validate_data.mappers import XML_ATTRIB_TO_PROP_TYPE_MAPPER
from dsp_tools.commands.validate_data.mappers import XML_TAG_TO_VALUE_TYPE_MAPPER
from dsp_tools.models.datetimestamp import DateTimeStamp
from dsp_tools.models.exceptions import BaseError
from dsp_tools.utils.xml_parsing.models.data_deserialised import DataDeserialised
from dsp_tools.utils.xml_parsing.models.data_deserialised import KnoraValueType
from dsp_tools.utils.xml_parsing.models.data_deserialised import MigrationMetadata
from dsp_tools.utils.xml_parsing.models.data_deserialised import PropertyObject
from dsp_tools.utils.xml_parsing.models.data_deserialised import ResourceDeserialised
from dsp_tools.utils.xml_parsing.models.data_deserialised import TripleObjectType
from dsp_tools.utils.xml_parsing.models.data_deserialised import TriplePropertyType
from dsp_tools.utils.xml_parsing.models.data_deserialised import ValueInformation


def get_data_deserialised(root: etree._Element) -> tuple[str, DataDeserialised]:
    """
    Takes the root of an XML
    Extracts the data of the project and transforms all its resources.

    Args:
        root: root of an xml with qnames and comments removed

    Returns:
        Shortcode and deserialised data
    """
    shortcode = root.attrib["shortcode"]
    data_deserialised = _deserialise_all_resources(root)
    return shortcode, data_deserialised


def _deserialise_all_resources(root: etree._Element) -> DataDeserialised:
    all_res: list[ResourceDeserialised] = []
    for res in root.iterdescendants(tag="resource"):
        all_res.append(_deserialise_one_resource(res))
    return DataDeserialised(all_res)


def _extract_metadata(element: etree._Element) -> list[PropertyObject]:
    property_objects = []
    for k, v in element.attrib.items():
        if not (knora_prop := XML_ATTRIB_TO_PROP_TYPE_MAPPER.get(k)):
            continue
        object_type = TripleObjectType.STRING
        if knora_prop == TriplePropertyType.KNORA_LICENSE:
            object_type = TripleObjectType.IRI
        property_objects.append(PropertyObject(property_type=knora_prop, object_value=v, object_type=object_type))
    return property_objects


def _deserialise_one_resource(resource: etree._Element) -> ResourceDeserialised:
    res_type = resource.attrib["restype"]
    asset_value = None
    if res_type in {VIDEO_SEGMENT_RESOURCE, AUDIO_SEGMENT_RESOURCE}:
        values = _deserialise_segment_properties(resource)
    else:
        values, asset_value = _deserialise_generic_properties(resource)
    metadata = _extract_metadata(resource)
    metadata.extend(_get_all_stand_off_links(values))
    metadata.append(PropertyObject(TriplePropertyType.RDFS_LABEL, resource.attrib["label"], TripleObjectType.STRING))
    metadata.append(PropertyObject(TriplePropertyType.RDF_TYPE, res_type, TripleObjectType.IRI))
    return ResourceDeserialised(
        res_id=resource.attrib["id"],
        property_objects=metadata,
        values=values,
        asset_value=asset_value,
        migration_metadata=_deserialise_migration_metadata(resource),
    )


def _deserialise_migration_metadata(resource: etree._Element) -> MigrationMetadata:
    date = resource.attrib.get("creation_date")
    creation_date = DateTimeStamp(date) if date else None
    return MigrationMetadata(
        iri=resource.attrib.get("iri"),
        ark=resource.attrib.get("ark"),
        creation_date=creation_date,
    )


def _deserialise_generic_properties(resource: etree._Element) -> tuple[list[ValueInformation], ValueInformation | None]:
    values = []
    asset_value = None
    for val in resource.iterchildren():
        if val.tag == "bitstream":
            asset_value = _deserialise_bitstream(val)
        else:
            # iiif links are handled like all other values
            values.extend(_deserialise_one_property(val))
    return values, asset_value


def _deserialise_one_property(prop_ele: etree._Element) -> list[ValueInformation]:
    match prop_ele.tag:
        case (
            (
                "boolean-prop"
                | "color-prop"
                | "date-prop"
                | "decimal-prop"
                | "geoname-prop"
                | "integer-prop"
                | "resptr-prop"
                | "time-prop"
                | "uri-prop"
            ) as prop_tag
        ):
            return _extract_generic_value_information(prop_ele, XML_TAG_TO_VALUE_TYPE_MAPPER[prop_tag])
        case "list-prop":
            return _extract_list_value_information(prop_ele)
        case "text-prop":
            return _extract_text_value_information(prop_ele)
        case "iiif-uri":
            return _deserialise_iiif_uri(prop_ele)
        case "geometry-prop":
            return _extract_geometry_value_information(prop_ele)
        case _:
            return []


def _extract_generic_value_information(prop: etree._Element, value_type: KnoraValueType) -> list[ValueInformation]:
    prop_name = prop.attrib["name"]
    return [
        ValueInformation(
            user_facing_prop=prop_name,
            user_facing_value=val.text,
            knora_type=value_type,
            value_metadata=_extract_metadata(val),
        )
        for val in prop.iterchildren()
    ]


def _extract_list_value_information(prop: etree._Element) -> list[ValueInformation]:
    prop_name = prop.attrib["name"]
    list_name = prop.attrib["list"]
    all_vals = []
    for val in prop.iterchildren():
        found_value = f"{list_name} / {val.text}" if val.text else None
        all_vals.append(
            ValueInformation(
                user_facing_prop=prop_name,
                user_facing_value=found_value,
                knora_type=KnoraValueType.LIST_VALUE,
                value_metadata=_extract_metadata(val),
            )
        )
    return all_vals


def _extract_text_value_information(prop: etree._Element) -> list[ValueInformation]:
    prop_name = prop.attrib["name"]
    all_vals = []
    for val in prop.iterchildren():
        encoding = val.attrib["encoding"]
        match encoding:
            case "utf8":
                val_type = KnoraValueType.SIMPLETEXT_VALUE
            case "xml":
                val_type = KnoraValueType.RICHTEXT_VALUE
            case _:
                raise BaseError(f"Unknown encoding: {encoding}.")
        all_vals.append(
            ValueInformation(
                user_facing_prop=prop_name,
                user_facing_value=_get_text_as_string(val),
                knora_type=val_type,
                value_metadata=_extract_metadata(val),
            )
        )
    return all_vals


def _get_text_as_string(value: etree._Element) -> str | None:
    if len(value):
        text_list = []
        if found := value.text:
            text_list = [found]
        text_list.extend([etree.tostring(child, encoding="unicode", method="xml") for child in value])
        return "".join(text_list).strip()
    else:
        return value.text


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


def _extract_geometry_value_information(prop: etree._Element) -> list[ValueInformation]:
    prop_name = prop.attrib["name"]

    def check_for_geometry_json(value: str | None) -> str | None:
        if not value:
            return None
        try:
            return json.dumps(json.loads(value))
        except JSONDecodeError:
            return None

    return [
        ValueInformation(
            user_facing_prop=prop_name,
            user_facing_value=check_for_geometry_json(val.text),
            knora_type=KnoraValueType.GEOM_VALUE,
            value_metadata=_extract_metadata(val),
        )
        for val in prop.iterchildren()
    ]


def _deserialise_iiif_uri(value: etree._Element) -> list[ValueInformation]:
    if (file_str := value.text) is None:
        return []
    file_str = file_str.strip()
    return [
        ValueInformation(
            user_facing_prop=f"{KNORA_API_STR}hasStillImageFileValue",
            user_facing_value=file_str,
            knora_type=KnoraValueType.STILL_IMAGE_IIIF,
            value_metadata=_extract_metadata(value),
        )
    ]


def _deserialise_bitstream(value: etree._Element) -> ValueInformation | None:
    if (file_str := value.text) is None:
        return None
    file_str = file_str.strip()
    file_type, prop_str = _get_file_value_type(file_str)
    if not file_type:
        return None
    return ValueInformation(
        user_facing_prop=prop_str,
        user_facing_value=file_str,
        knora_type=file_type,
        value_metadata=_extract_metadata(value),
    )


def _get_file_value_type(file_name: str) -> tuple[KnoraValueType | None, str]:  # noqa:PLR0911 (Too many return statements)
    file_ending = Path(file_name).suffix[1:].lower()
    match file_ending:
        case "zip" | "tar" | "gz" | "z" | "tgz" | "gzip" | "7z":
            return KnoraValueType.ARCHIVE_FILE, f"{KNORA_API_STR}hasArchiveFileValue"
        case "mp3" | "wav":
            return KnoraValueType.AUDIO_FILE, f"{KNORA_API_STR}hasAudioFileValue"
        case "pdf" | "doc" | "docx" | "xls" | "xlsx" | "ppt" | "pptx":
            return KnoraValueType.DOCUMENT_FILE, f"{KNORA_API_STR}hasDocumentFileValue"
        case "mp4":
            return KnoraValueType.MOVING_IMAGE_FILE, f"{KNORA_API_STR}hasMovingImageFileValue"
        # jpx is the extension of the files returned by dsp-ingest
        case "jpg" | "jpeg" | "jp2" | "png" | "tif" | "tiff" | "jpx":
            return KnoraValueType.STILL_IMAGE_FILE, f"{KNORA_API_STR}hasStillImageFileValue"
        case "odd" | "rng" | "txt" | "xml" | "xsd" | "xsl" | "csv" | "json":
            return KnoraValueType.TEXT_FILE, f"{KNORA_API_STR}hasTextFileValue"
        case _:
            return None, ""


def _deserialise_segment_properties(resource: etree._Element) -> list[ValueInformation]:
    values = []
    for val in resource.iterchildren():
        prop_name = str(val.tag)
        property_objects = _extract_metadata(val)
        if prop_name == "hasSegmentBounds":
            property_objects.append(
                PropertyObject(
                    TriplePropertyType.KNORA_INTERVAL_START,
                    val.attrib["segment_start"],
                    TripleObjectType.DECIMAL,
                )
            )
            property_objects.append(
                PropertyObject(
                    TriplePropertyType.KNORA_INTERVAL_END,
                    val.attrib["segment_end"],
                    TripleObjectType.DECIMAL,
                )
            )
        values.append(
            ValueInformation(
                user_facing_prop=f"{KNORA_API_STR}{prop_name}",
                user_facing_value=_get_text_as_string(val),
                knora_type=SEGMENT_TAG_TO_PROP_MAPPER[prop_name],
                value_metadata=property_objects,
            )
        )
    return values
