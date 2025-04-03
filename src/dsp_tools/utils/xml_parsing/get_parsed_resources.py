from pathlib import Path

from lxml import etree

from dsp_tools.commands.validate_data.mappers import XML_TAG_TO_VALUE_TYPE_MAPPER
from dsp_tools.error.exceptions import InputError
from dsp_tools.utils.rdflib_constants import KNORA_API_STR
from dsp_tools.utils.xml_parsing.models.parsed_resource import KnoraValueType
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedFileValue
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedFileValueMetadata
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedMigrationMetadata
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedResource
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedValue

SEGMENT_TAG_TO_PROP_MAPPER = {
    "relatesTo": KnoraValueType.LINK_VALUE,
    "hasDescription": KnoraValueType.RICHTEXT_VALUE,
    "hasTitle": KnoraValueType.SIMPLETEXT_VALUE,
    "hasKeyword": KnoraValueType.SIMPLETEXT_VALUE,
    "hasComment": KnoraValueType.RICHTEXT_VALUE,
}


def get_parsed_resources(root: etree._Element, api_url: str) -> tuple[list[ParsedResource], set[str]]:
    iri_lookup = _create_from_local_name_to_absolute_iri_lookup(root, api_url)
    all_res: list[ParsedResource] = []
    for res in root.iterdescendants(tag="resource"):
        res_type = iri_lookup[res.attrib["restype"]]
        all_res.append(_parse_one_resource(res, res_type, iri_lookup))
    for res in root.iterdescendants(tag="region"):
        res_type = f"{KNORA_API_STR}Region"
        all_res.append(_parse_one_resource(res, res_type, iri_lookup))
    for res in root.iterdescendants(tag="link"):
        res_type = f"{KNORA_API_STR}LinkObj"
        all_res.append(_parse_one_resource(res, res_type, iri_lookup))
    for res in root.iterdescendants(tag="video-segment"):
        all_res.append(_parse_segment(res, "Video"))
    for res in root.iterdescendants(tag="audio-segment"):
        all_res.append(_parse_segment(res, "Audio"))
    return all_res, set(iri_lookup.values())


def _create_from_local_name_to_absolute_iri_lookup(root: etree._Element, api_url: str) -> dict[str, str]:
    shortcode = root.attrib["shortcode"]
    default_ontology = root.attrib["default-ontology"]
    local_names = {ele.attrib["restype"] for ele in root.iterdescendants(tag="resource")}
    props = {ele.attrib["name"] for ele in root.iter() if "name" in ele.attrib}
    local_names.update(props)
    lookup = {local: _get_one_absolute_iri(local, shortcode, default_ontology, api_url) for local in local_names}
    return lookup


def _get_one_absolute_iri(local_name: str, shortcode: str, default_ontology: str, api_url: str) -> str:
    split_name = local_name.split(":")
    if len(split_name) == 1:
        return f"{KNORA_API_STR}{local_name}"
    if len(split_name) == 2:
        if split_name[0] == "":
            return f"{_construct_namespace(api_url, shortcode, default_ontology)}{split_name[1]}"
        if split_name[0] == "knora-api":
            return f"{KNORA_API_STR}{split_name[1]}"
        return f"{_construct_namespace(api_url, shortcode, split_name[0])}{split_name[1]}"
    raise InputError(
        f"It is not permissible to have a colon in a property or resource class name. "
        f"Please correct the following: {local_name}"
    )


def _construct_namespace(api_url: str, shortcode: str, onto_name: str) -> str:
    return f"{api_url}/ontology/{shortcode}/{onto_name}/v2#"


def _parse_segment(segment: etree._Element, segment_type: str) -> ParsedResource:
    values = _parse_segment_values(segment, segment_type)
    migration_metadata = _parse_migration_metadata(segment)
    return ParsedResource(
        res_id=segment.attrib["id"],
        res_type=f"{KNORA_API_STR}{segment_type}Segment",
        label=segment.attrib["label"],
        permissions_id=segment.attrib.get("permissions"),
        values=values,
        file_value=None,
        migration_metadata=migration_metadata,
    )


def _parse_segment_values(segment: etree._Element, segment_type: str) -> list[ParsedValue]:
    values: list[ParsedValue] = []
    value: str | tuple[str, str] | None
    for val in segment.iterchildren():
        match val.tag:
            case "isSegmentOf":
                val_type = KnoraValueType.LINK_VALUE
                prop = f"{KNORA_API_STR}is{segment_type}SegmentOf"
                value = val.text
            case "hasSegmentBounds":
                val_type = KnoraValueType.INTERVAL_VALUE
                prop = f"{KNORA_API_STR}hasSegmentBounds"
                value = (val.attrib["segment_start"], val.attrib["segment_end"])
            case _:
                val_type = SEGMENT_TAG_TO_PROP_MAPPER[str(val.tag)]
                prop = f"{KNORA_API_STR}{val.tag!s}"
                value = _get_text_as_string(val)
        values.append(
            ParsedValue(
                prop_name=prop,
                value=value,
                value_type=val_type,
                permissions_id=val.attrib.get("permissions"),
                comment=val.attrib.get("comment"),
            )
        )
    return values


def _parse_one_resource(resource: etree._Element, res_type: str, iri_lookup: dict[str, str]) -> ParsedResource:
    values, file_value = _parse_values(resource, iri_lookup)
    migration_metadata = _parse_migration_metadata(resource)
    return ParsedResource(
        res_id=resource.attrib["id"],
        res_type=res_type,
        label=resource.attrib["label"],
        permissions_id=resource.attrib.get("permissions"),
        values=values,
        file_value=file_value,
        migration_metadata=migration_metadata,
    )


def _parse_migration_metadata(resource: etree._Element) -> ParsedMigrationMetadata | None:
    metadata = (resource.attrib.get("iri"), resource.attrib.get("ark"), resource.attrib.get("creation_date"))
    if any(metadata):
        return ParsedMigrationMetadata(
            iri=metadata[0],
            ark=metadata[1],
            creation_date=metadata[2],
        )
    return None


def _parse_values(
    resource: etree._Element, iri_lookup: dict[str, str]
) -> tuple[list[ParsedValue], ParsedFileValue | None]:
    values = []
    asset_value = None
    for val in resource.iterchildren():
        match val.tag:
            case "bitstream":
                asset_value = _parse_file_values(val)
            case "iiif-uri":
                asset_value = _parse_iiif_uri(val)
            case _:
                values.extend(_parse_one_value(val, iri_lookup))
    return values, asset_value


def _parse_one_value(values: etree._Element, iri_lookup: dict[str, str]) -> list[ParsedValue]:
    prop_name = iri_lookup[values.attrib["name"]]
    match values.tag:
        case "list-prop":
            return _parse_list_value(values, prop_name)
        case "text-prop":
            return _parse_text_value(values, prop_name)
        case _:
            return _parse_generic_values(values, prop_name)


def _parse_generic_values(values: etree._Element, prop_name: str) -> list[ParsedValue]:
    value_type = XML_TAG_TO_VALUE_TYPE_MAPPER[str(values.tag)]
    parsed_values = []
    for val in values:
        parsed_values.append(
            ParsedValue(
                prop_name=prop_name,
                value=val.text,
                value_type=value_type,
                permissions_id=val.attrib.get("permissions"),
                comment=val.attrib.get("comment"),
            )
        )
    return parsed_values


def _parse_list_value(values: etree._Element, prop_name: str) -> list[ParsedValue]:
    parsed_values = []
    list_name = values.attrib["list"]
    for val in values:
        parsed_values.append(
            ParsedValue(
                prop_name=prop_name,
                value=(list_name, val.text),
                value_type=KnoraValueType.LIST_VALUE,
                permissions_id=val.attrib.get("permissions"),
                comment=val.attrib.get("comment"),
            )
        )
    return parsed_values


def _parse_text_value(values: etree._Element, prop_name: str) -> list[ParsedValue]:
    parsed_values = []
    for val in values:
        if val.attrib["encoding"] == "xml":
            val_type = KnoraValueType.RICHTEXT_VALUE
        else:
            val_type = KnoraValueType.SIMPLETEXT_VALUE
        parsed_values.append(
            ParsedValue(
                prop_name=prop_name,
                value=_get_text_as_string(val),
                value_type=val_type,
                permissions_id=val.attrib.get("permissions"),
                comment=val.attrib.get("comment"),
            )
        )
    return parsed_values


def _get_text_as_string(value: etree._Element) -> str | None:
    if len(value) > 0:
        text_list = []
        if found := value.text:
            text_list = [found]
        text_list.extend([etree.tostring(child, encoding="unicode", method="xml") for child in value])
        return "".join(text_list).strip()
    else:
        return value.text


def _parse_iiif_uri(iiif_uri: etree._Element) -> ParsedFileValue:
    return ParsedFileValue(
        value=iiif_uri.text,
        value_type=KnoraValueType.STILL_IMAGE_IIIF,
        metadata=_parse_file_metadata(iiif_uri),
    )


def _parse_file_values(file_value: etree._Element) -> ParsedFileValue:
    return ParsedFileValue(
        value=file_value.text,
        value_type=_get_file_value_type(file_value.text),
        metadata=_parse_file_metadata(file_value),
    )


def _parse_file_metadata(file_value: etree._Element) -> ParsedFileValueMetadata:
    return ParsedFileValueMetadata(
        license_iri=file_value.attrib.get("license"),
        copyright_holder=file_value.attrib.get("copyright-holder"),
        authorship_id=file_value.attrib.get("authorship-id"),
        permissions_id=file_value.attrib.get("permissions"),
    )


def _get_file_value_type(file_name: str | None) -> KnoraValueType | None:  # noqa:PLR0911 (Too many return statements)
    if not file_name:
        return None
    file_extension = Path(file_name).suffix[1:].lower()
    match file_extension:
        case "zip" | "tar" | "gz" | "z" | "tgz" | "gzip" | "7z":
            return KnoraValueType.ARCHIVE_FILE
        case "mp3" | "wav":
            return KnoraValueType.AUDIO_FILE
        case "pdf" | "doc" | "docx" | "xls" | "xlsx" | "ppt" | "pptx":
            return KnoraValueType.DOCUMENT_FILE
        case "mp4":
            return KnoraValueType.MOVING_IMAGE_FILE
        # jpx is the extension of the files returned by dsp-ingest
        case "jpg" | "jpeg" | "jp2" | "png" | "tif" | "tiff" | "jpx":
            return KnoraValueType.STILL_IMAGE_FILE
        case "odd" | "rng" | "txt" | "xml" | "xsd" | "xsl" | "csv" | "json":
            return KnoraValueType.TEXT_FILE
        case _:
            return None
