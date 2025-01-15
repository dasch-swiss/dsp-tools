from pathlib import Path

from lxml import etree

from dsp_tools.commands.validate_data.constants import AUDIO_SEGMENT_RESOURCE
from dsp_tools.commands.validate_data.constants import REGION_RESOURCE
from dsp_tools.commands.validate_data.constants import VIDEO_SEGMENT_RESOURCE
from dsp_tools.commands.validate_data.constants import XML_TAG_TO_VALUE_TYPE_MAPPER
from dsp_tools.commands.validate_data.models.data_deserialised import AbstractFileValueDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import BitstreamDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import DataDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import FileValueInformation
from dsp_tools.commands.validate_data.models.data_deserialised import IIIFUriDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import KnoraFileValueType
from dsp_tools.commands.validate_data.models.data_deserialised import KnoraValueType
from dsp_tools.commands.validate_data.models.data_deserialised import ProjectDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import ProjectInformation
from dsp_tools.commands.validate_data.models.data_deserialised import PropertyObject
from dsp_tools.commands.validate_data.models.data_deserialised import ResourceDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import TripleObjectType
from dsp_tools.commands.validate_data.models.data_deserialised import TriplePropertyType
from dsp_tools.commands.validate_data.models.data_deserialised import ValueInformation
from dsp_tools.models.exceptions import BaseError


def deserialise_xml(root: etree._Element) -> ProjectDeserialised:
    """
    Takes the root of an XML
    Extracts the data of the project and transforms all its resources.

    Args:
        root: root of an xml with qnames and comments removed

    Returns:
        Class instance with the information reformatted
    """
    shortcode = root.attrib["shortcode"]
    default_ontology = root.attrib["default-ontology"]
    project_info = ProjectInformation(shortcode, default_ontology)
    data_deserialised = _deserialise_all_resources(root)
    return ProjectDeserialised(project_info, data_deserialised)


def _deserialise_all_resources(root: etree._Element) -> DataDeserialised:
    all_res: list[ResourceDeserialised] = []
    for res in root.iterdescendants(tag="resource"):
        dsp_type = None
        res_type = res.attrib["restype"]
        if res_type == REGION_RESOURCE:
            dsp_type = REGION_RESOURCE
        elif res_type == VIDEO_SEGMENT_RESOURCE:
            dsp_type = VIDEO_SEGMENT_RESOURCE
        elif res_type == AUDIO_SEGMENT_RESOURCE:
            dsp_type = AUDIO_SEGMENT_RESOURCE
        if dsp_type:
            all_res.append(_deserialise_one_in_built(res, dsp_type))
        else:
            all_res.append(_deserialise_one_resource(res))
    file_values = _deserialise_file_value(root)
    return DataDeserialised(all_res, file_values)


def _deserialise_one_in_built(resource: etree._Element, res_type: str) -> ResourceDeserialised:
    lbl = PropertyObject(TriplePropertyType.RDFS_LABEL, resource.attrib["label"], TripleObjectType.STRING)
    rdf_type = PropertyObject(TriplePropertyType.RDF_TYPE, res_type, TripleObjectType.IRI)
    return ResourceDeserialised(
        res_id=resource.attrib["id"],
        property_objects=[rdf_type, lbl],
        values=[],
    )


def _deserialise_one_resource(resource: etree._Element) -> ResourceDeserialised:
    values = []
    for val in resource.iterchildren():
        values.extend(_deserialise_one_property(val))
    lbl = PropertyObject(TriplePropertyType.RDFS_LABEL, resource.attrib["label"], TripleObjectType.STRING)
    rdf_type = PropertyObject(TriplePropertyType.RDF_TYPE, resource.attrib["restype"], TripleObjectType.IRI)
    return ResourceDeserialised(
        res_id=resource.attrib["id"],
        property_objects=[rdf_type, lbl],
        values=values,
    )


def _deserialise_one_property(prop_ele: etree._Element) -> list[ValueInformation | FileValueInformation]:
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
        case "iiif-uri" | "bitstream" as file_tag:
            return _deserialise_file_values(prop_ele, file_tag)
        case _:
            return []


def _extract_generic_value_information(prop: etree._Element, value_type: KnoraValueType) -> list[ValueInformation]:
    prop_name = prop.attrib["name"]
    return [
        ValueInformation(
            user_facing_prop=prop_name,
            user_facing_value=x.text,
            knora_type=value_type,
            value_metadata=[],
        )
        for x in prop.iterchildren()
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
                value_metadata=[],
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
                value_metadata=[],
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


def _deserialise_file_values(value: etree._Element, tag_name: str) -> list[FileValueInformation]:
    if not (file_str := value.text):
        return []
    if tag_name == "iiif-uri":
        file_type = KnoraFileValueType.STILL_IMAGE_IIIF
    elif not (file_type := _get_file_value_type(file_str)):
        return []
    return [FileValueInformation(file_value_str=file_str, knora_type=file_type, value_metadata=[])]


def _get_file_value_type(file_name: str) -> KnoraFileValueType | None:  # noqa:PLR0911 (Too many return statements)
    file_ending = Path(file_name).suffix[1:].lower()
    match file_ending:
        case "zip" | "tar" | "gz" | "z" | "tgz" | "gzip" | "7z":
            return KnoraFileValueType.ARCHIVE
        case "mp3" | "wav":
            return KnoraFileValueType.AUDIO
        case "pdf" | "doc" | "docx" | "xls" | "xlsx" | "ppt" | "pptx":
            return KnoraFileValueType.DOCUMENT
        case "mp4":
            return KnoraFileValueType.MOVING_IMAGE
        # jpx is the extension of the files returned by dsp-ingest
        case "jpg" | "jpeg" | "jp2" | "png" | "tif" | "tiff" | "jpx":
            return KnoraFileValueType.STILL_IMAGE_FILE
        case "odd" | "rng" | "txt" | "xml" | "xsd" | "xsl" | "csv" | "json":
            return KnoraFileValueType.TEXT
        case _:
            return None


def _deserialise_file_value(root: etree._Element) -> list[AbstractFileValueDeserialised]:
    file_values: list[AbstractFileValueDeserialised] = []
    for res in root.iterchildren(tag="resource"):
        res_id = res.attrib["id"]
        if (bitstream := res.find("bitstream")) is not None:
            file_values.append(BitstreamDeserialised(res_id, bitstream.text))
        elif (iiif_uri := res.find("iiif-uri")) is not None:
            file_values.append(IIIFUriDeserialised(res_id, iiif_uri.text))
    return file_values
