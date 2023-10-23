from copy import deepcopy
from itertools import chain
from typing import Iterable

import regex
from lxml import etree

from dsp_tools.models.exceptions import BaseError
from dsp_tools.utils.create_logger import get_logger
from dsp_tools.xml_upload.domain.model.resource import Resource, UploadResourceCollection
from dsp_tools.xml_upload.domain.model.value import (
    BooleanValue,
    ColorValue,
    DateValue,
    DecimalValue,
    FormattedTextValue,
    GeometryValue,
    GeonamesValue,
    IntegerValue,
    IntervalValue,
    LinkValue,
    ListValue,
    TimeValue,
    UnformattedTextValue,
    UriValue,
    Value,
)

logger = get_logger(__name__)


def get_resources_from_xml(root: etree._Element) -> UploadResourceCollection:
    # XXX: schema validation
    shortcode = root.attrib["shortcode"]
    default_ontology = root.attrib["default-ontology"]
    processed_root = _remove_qnames_and_transform_special_tags(root)
    resources = list(_parse(processed_root, default_ontology))
    return UploadResourceCollection(shortcode, default_ontology, resources)


def _remove_qnames_and_transform_special_tags(
    root: etree._Element,
) -> etree._Element:
    cp = deepcopy(root)
    for elem in cp.iter():
        elem.tag = etree.QName(elem).localname  # remove namespace URI in the element's name
        match elem.tag:
            case "annotation":
                elem.attrib["restype"] = "Annotation"
                elem.tag = "resource"
            case "region":
                elem.attrib["restype"] = "Region"
                elem.tag = "resource"
            case "link":
                # raise NotImplementedError("Link Objects are not supported right now.")
                elem.attrib["restype"] = "LinkObj"
                elem.tag = "resource"
    return cp


def _parse(root: etree._Element, default_ontology: str) -> Iterable[Resource]:
    resources = list(root.iter(tag="resource"))
    for res in resources:
        res_id = res.attrib["id"]
        res_type = _get_restype(res.attrib["restype"], default_ontology)
        label = res.attrib["label"]
        values = list(chain.from_iterable(_get_values(v) for v in res))
        bitstream = None
        if (bs := res.find("bitstream")) is not None:
            bitstream = bs.text
            assert bitstream
        permissions = res.attrib.get("permissions")
        # XXX: iri
        # XXX: ark
        # XXX: creation_date
        resource = Resource(
            resource_id=res_id,
            resource_type=res_type,
            label=label,
            values=values,
            bitstream=bitstream,
            permissions=permissions,
        )
        yield resource


def _get_restype(s: str, defaut_ontology: str) -> str:
    m = regex.match(r"((\w+)?(:))?(\w+)", s)
    match m.groups() if m else None:
        case (_, None, None, restype):
            return f"knora-api:{restype}"
        case (_, None, ":", restype):
            return f"{defaut_ontology}:{restype}"
        case (_, prefix, _, restype):
            return f"{prefix}:{restype}"
        case _:
            raise BaseError(f"Invalid resource type: {s}")


def _get_values(elem: etree._Element) -> list[Value]:
    match elem.tag:
        case "bitstream":
            return []  # XXX: handle more elegantly
        case "boolean-prop":
            return _get_boolean_value(elem)
        case "color-prop":
            return _get_color_values(elem)
        case "date-prop":
            return _get_date_values(elem)
        case "decimal-prop":
            return _get_decimal_values(elem)
        case "geometry-prop":
            return _get_geometry_values(elem)
        case "geoname-prop":
            return _get_geoname_values(elem)
        case "integer-prop":
            return _get_integer_values(elem)
        case "interval-prop":
            return _get_interval_values(elem)
        case "list-prop":
            return _get_list_values(elem)
        case "resptr-prop":
            return _get_link_values(elem)
        case "text-prop":
            return _get_text_values(elem)
        case "time-prop":
            return _get_time_values(elem)
        case "uri-prop":
            return _get_uri_values(elem)
        case _:
            raise NotImplementedError(f"Unknown property type: {elem.tag}")


def _get_boolean_value(elem: etree._Element) -> list[Value]:
    return [
        BooleanValue(
            property_name=elem.attrib["name"],
            value=_get_text_content(v),
            permissions=v.attrib.get("permissions"),
        )
        for v in elem
    ]


def _get_color_values(elem: etree._Element) -> list[Value]:
    return [
        ColorValue(
            property_name=elem.attrib["name"],
            value=_get_text_content(v),
            permissions=v.attrib.get("permissions"),
        )
        for v in elem
    ]


def _get_date_values(elem: etree._Element) -> list[Value]:
    return [
        DateValue(
            property_name=elem.attrib["name"],
            value=_get_text_content(v),
            permissions=v.attrib.get("permissions"),
        )
        for v in elem
    ]


def _get_decimal_values(elem: etree._Element) -> list[Value]:
    return [
        DecimalValue(
            property_name=elem.attrib["name"],
            value=_get_text_content(v),
            permissions=v.attrib.get("permissions"),
        )
        for v in elem
    ]


def _get_geometry_values(elem: etree._Element) -> list[Value]:
    return [
        GeometryValue(
            property_name=elem.attrib["name"],
            value=_get_text_content(v),
            permissions=v.attrib.get("permissions"),
        )
        for v in elem
    ]


def _get_geoname_values(elem: etree._Element) -> list[Value]:
    return [
        GeonamesValue(
            property_name=elem.attrib["name"],
            value=_get_text_content(v),
            permissions=v.attrib.get("permissions"),
        )
        for v in elem
    ]


def _get_integer_values(elem: etree._Element) -> list[Value]:
    return [
        IntegerValue(
            property_name=elem.attrib["name"],
            value=_get_text_content(v),
            permissions=v.attrib.get("permissions"),
        )
        for v in elem
    ]


def _get_interval_values(elem: etree._Element) -> list[Value]:
    return [
        IntervalValue(
            property_name=elem.attrib["name"],
            value=_get_text_content(v),
            permissions=v.attrib.get("permissions"),
        )
        for v in elem
    ]


def _get_list_values(elem: etree._Element) -> list[Value]:
    return [
        ListValue(
            property_name=elem.attrib["name"],
            value=_get_text_content(v),
            permissions=v.attrib.get("permissions"),
        )
        for v in elem
    ]


def _get_link_values(elem: etree._Element) -> list[Value]:
    return [
        LinkValue(
            property_name=elem.attrib["name"],
            value=_get_text_content(v),
            permissions=v.attrib.get("permissions"),
        )
        for v in elem
    ]


def _get_text_values(elem: etree._Element) -> list[Value]:
    res: list[Value] = []
    name = elem.attrib["name"]
    for v in elem:
        match v.get("encoding"):
            case "xml":
                xmlstr_orig = etree.tostring(v, encoding="unicode", method="xml")
                xmlstr_cleaned = _cleanup_formatted_text(xmlstr_orig)
                # XXX: resrefs!
                res.append(
                    FormattedTextValue(
                        property_name=name,
                        value=xmlstr_cleaned,
                        permissions=v.attrib.get("permissions"),
                    )
                )
            case "utf8":
                str_orig = "".join(v.itertext())
                str_cleaned = _cleanup_unformatted_text(str_orig)
                res.append(
                    UnformattedTextValue(
                        property_name=name,
                        value=str_cleaned,
                        permissions=v.attrib.get("permissions"),
                    )
                )
            case _:
                raise NotImplementedError(f"Unknown encoding: {elem.get('encoding')}")
    return res


def _get_time_values(elem: etree._Element) -> list[Value]:
    return [
        TimeValue(
            property_name=elem.attrib["name"],
            value=_get_text_content(v),
            permissions=v.attrib.get("permissions"),
        )
        for v in elem
    ]


def _get_uri_values(elem: etree._Element) -> list[Value]:
    return [
        UriValue(
            property_name=elem.attrib["name"],
            value=_get_text_content(v),
            permissions=v.attrib.get("permissions"),
        )
        for v in elem
    ]


def _get_text_content(elem: etree._Element) -> str:
    if elem.text:
        return elem.text
    else:
        raise BaseError(f"Element {elem.tag} has no text content. ({etree.tostring(elem, encoding='unicode')})")


def _cleanup_formatted_text(xmlstr_orig: str) -> str:
    """
    In a xml-encoded text value from the XML file,
    there may be non-text characters that must be removed.
    This method:
        - removes the <text> tags
        - replaces (multiple) line breaks by a space
        - replaces multiple spaces or tabstops by a single space (except within <code> or <pre> tags)

    Args:
        xmlstr_orig: original string from the XML file

    Returns:
        purged string, suitable to be sent to DSP-API
    """
    # remove the <text> tags
    xmlstr = regex.sub("<text.*?>", "", xmlstr_orig)
    xmlstr = regex.sub("</text>", "", xmlstr)

    # replace (multiple) line breaks by a space
    xmlstr = regex.sub("\n+", " ", xmlstr)

    # replace multiple spaces or tabstops by a single space (except within <code> or <pre> tags)
    # the regex selects all spaces/tabstops not followed by </xyz> without <xyz in between.
    # credits: https://stackoverflow.com/a/46937770/14414188
    xmlstr = regex.sub("( {2,}|\t+)(?!(.(?!<(code|pre)))*</(code|pre)>)", " ", xmlstr)

    # remove spaces after <br/> tags (except within <code> tags)
    xmlstr = regex.sub("((?<=<br/?>) )(?!(.(?!<code))*</code>)", "", xmlstr)

    # remove leading and trailing spaces
    xmlstr = xmlstr.strip()

    return xmlstr


def _cleanup_unformatted_text(string_orig: str) -> str:
    """
    In a utf8-encoded text value from the XML file,
    there may be non-text characters that must be removed.
    This method:
        - removes the <text> tags
        - replaces multiple spaces or tabstops by a single space

    Args:
        string_orig: original string from the XML file

    Returns:
        purged string, suitable to be sent to DSP-API
    """
    # remove the <text> tags
    string = regex.sub("<text.*?>", "", string_orig)
    string = regex.sub("</text>", "", string)

    # replace multiple spaces or tabstops by a single space
    string = regex.sub(r" {2,}|\t+", " ", string)

    # remove leading and trailing spaces (of every line, but also of the entire string)
    string = "\n".join([s.strip() for s in string.split("\n")])
    string = string.strip()

    return string
