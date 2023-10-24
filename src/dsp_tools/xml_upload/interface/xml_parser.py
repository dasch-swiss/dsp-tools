from __future__ import annotations

import importlib.resources
from copy import deepcopy
from dataclasses import dataclass
from itertools import chain
from pathlib import Path
from typing import Iterable

import regex
from lxml import etree

from dsp_tools.models.exceptions import BaseError
from dsp_tools.utils.create_logger import get_logger
from dsp_tools.utils.xml_utils import read_xml_file
from dsp_tools.xml_upload.domain.model.resource import InputPermissions, InputResource, InputResourceCollection
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


def _validate_xml_against_schema(xml: etree._Element) -> tuple[bool, str | None]:
    """
    Validates an XML file against the DSP XSD schema.

    Args:
        xml: the xml element tree to be validated

    Returns:
        True and None if the XML file is valid, False and an error message if not
    """
    with importlib.resources.files("dsp_tools").joinpath("resources/schema/data.xsd").open(
        encoding="utf-8"
    ) as schema_file:
        xmlschema = etree.XMLSchema(etree.parse(schema_file))

    if not xmlschema.validate(xml):
        error_msg = "The XML file cannot be uploaded due to the following validation error(s):"
        for error in xmlschema.error_log:
            error_msg = error_msg + f"\n  Line {error.line}: {error.message}"
        error_msg = error_msg.replace("{https://dasch.swiss/schema}", "")
        return False, error_msg

    logger.info("The XML file is syntactically correct and passed validation.")
    print("The XML file is syntactically correct and passed validation.")
    return True, None


def _validate_xml_tags_in_text_properties(xml: etree._Element) -> tuple[bool, str | None]:
    """
    Makes sure that there are no XML tags in simple texts.
    This can only be done with a regex,
    because even if the simple text contains some XML tags,
    the simple text itself is not valid XML that could be parsed.
    The extra challenge is that lxml transforms
    "pebble (&lt;2cm) and boulder (&gt;20cm)" into
    "pebble (<2cm) and boulder (>20cm)"
    (but only if &gt; follows &lt;).
    This forces us to write a regex that carefully distinguishes
    between a real tag (which is not allowed) and a false-positive-tag.

    Args:
        xml: parsed XML file

    Returns:
        True and None if the XML file is valid, False and an error message if not
    """
    resources_with_illegal_xml_tags = list()
    for text in xml.findall(path="resource/text-prop/text"):
        if text.attrib["encoding"] == "utf8":
            if (
                regex.search(r'<([a-zA-Z/"]+|[^\s0-9].*[^\s0-9])>', str(text.text))
                or len(list(text.iterchildren())) > 0
            ):
                sourceline = f" line {text.sourceline}: " if text.sourceline else " "
                propname = text.getparent().attrib["name"]  # type: ignore[union-attr]
                resname = text.getparent().getparent().attrib["id"]  # type: ignore[union-attr]
                resources_with_illegal_xml_tags.append(f" -{sourceline}resource '{resname}', property '{propname}'")
    if resources_with_illegal_xml_tags:
        err_msg = (
            "XML-tags are not allowed in text properties with encoding=utf8. "
            "The following resources of your XML file violate this rule:\n"
        )
        err_msg += "\n".join(resources_with_illegal_xml_tags)
        return False, err_msg

    return True, None


# XXX: should this be a service with interface?


@dataclass(frozen=True)
class XmlParserLive:
    """XML parser"""

    shortcode: str
    default_ontology: str
    root: etree._Element

    @staticmethod
    def from_file(path: Path) -> XmlParserLive | None:
        """Creates an XML parser from a file. Returns None, if the file is invalid."""
        root = read_xml_file(path)
        return XmlParserLive.make(root)

    @staticmethod
    def make(root: etree._Element) -> XmlParserLive | None:
        """Creates an XML parser from an XML ElementTree. Returns None, if the XML is invalid."""
        valid, error_msg = _validate_xml_against_schema(root)
        if not valid:
            print(f"ERROR: {error_msg}")
            logger.error(error_msg)
            return None
        shortcode = root.attrib["shortcode"]
        default_ontology = root.attrib["default-ontology"]
        processed_root = _remove_qnames_and_transform_special_tags(root)
        valid, error_msg = _validate_xml_tags_in_text_properties(processed_root)
        if not valid:
            print(f"ERROR: {error_msg}")
            logger.error(error_msg)
            return None
        return XmlParserLive(shortcode, default_ontology, processed_root)

    def get_resources(self) -> InputResourceCollection:
        """Get a collection of resources from the XML file."""
        resources = list(self._parse())
        return InputResourceCollection(self.shortcode, self.default_ontology, resources)

    def _parse(self) -> Iterable[InputResource]:
        permission_lookup = self._get_permission_lookup()
        resources = list(self.root.iter(tag="resource"))
        for res in resources:
            res_id = res.attrib["id"]
            res_type = self._with_prefix(res.attrib["restype"])
            label = res.attrib["label"]
            values = list(chain.from_iterable(self._get_values(v) for v in res))
            bitstream = None
            if (bs := res.find("bitstream")) is not None:
                bitstream = bs.text
                assert bitstream
            permission_id = res.attrib.get("permissions")
            permissions = permission_lookup[permission_id] if permission_id else None
            # XXX: iri
            # XXX: ark
            # XXX: creation_date
            resource = InputResource(
                resource_id=res_id,
                resource_type=res_type,
                label=label,
                values=values,
                bitstream_path=bitstream,
                permissions=permissions,
            )
            yield resource

    def _get_permission_lookup(self) -> dict[str, InputPermissions]:
        permissions = self.root.findall("permissions")
        res = {}
        for perm in permissions:
            name = perm.attrib["id"]
            allows = perm.findall("allow")
            res[name] = InputPermissions({a.attrib["group"]: a.text or "" for a in allows})
        return res

    def _with_prefix(self, s: str) -> str:
        m = regex.match(r"((\w+)?(:))?(\w+)", s)
        match m.groups() if m else None:
            case (_, None, None, restype):
                return f"knora-api:{restype}"
            case (_, None, ":", restype):
                return f"{self.default_ontology}:{restype}"
            case (_, prefix, _, restype):
                return f"{prefix}:{restype}"
            case _:
                raise BaseError(f"Invalid resource type: {s}")

    def _get_values(self, elem: etree._Element) -> list[Value]:
        if elem.tag == "bitstream":
            return []  # XXX: handle more elegantly
        name = self._with_prefix(elem.attrib["name"])
        match elem.tag:
            case "boolean-prop":
                return _get_boolean_value(name, elem)
            case "color-prop":
                return _get_color_values(name, elem)
            case "date-prop":
                return _get_date_values(name, elem)
            case "decimal-prop":
                return _get_decimal_values(name, elem)
            case "geometry-prop":
                return _get_geometry_values(name, elem)
            case "geoname-prop":
                return _get_geoname_values(name, elem)
            case "integer-prop":
                return _get_integer_values(name, elem)
            case "interval-prop":
                return _get_interval_values(name, elem)
            case "list-prop":
                return _get_list_values(name, elem)
            case "resptr-prop":
                return _get_link_values(name, elem)
            case "text-prop":
                return _get_text_values(name, elem)
            case "time-prop":
                return _get_time_values(name, elem)
            case "uri-prop":
                return _get_uri_values(name, elem)
            case _:
                raise NotImplementedError(f"Unknown property type: {elem.tag}")


def _get_boolean_value(name: str, elem: etree._Element) -> list[Value]:
    return [BooleanValue(name, _get_text_content(v), v.attrib.get("permissions")) for v in elem]


def _get_color_values(name: str, elem: etree._Element) -> list[Value]:
    return [ColorValue(name, _get_text_content(v), v.attrib.get("permissions")) for v in elem]


def _get_date_values(name: str, elem: etree._Element) -> list[Value]:
    return [DateValue(name, _get_text_content(v), v.attrib.get("permissions")) for v in elem]


def _get_decimal_values(name: str, elem: etree._Element) -> list[Value]:
    return [DecimalValue(name, _get_text_content(v), v.attrib.get("permissions")) for v in elem]


def _get_geometry_values(name: str, elem: etree._Element) -> list[Value]:
    return [GeometryValue(name, _get_text_content(v), v.attrib.get("permissions")) for v in elem]


def _get_geoname_values(name: str, elem: etree._Element) -> list[Value]:
    return [GeonamesValue(name, _get_text_content(v), v.attrib.get("permissions")) for v in elem]


def _get_integer_values(name: str, elem: etree._Element) -> list[Value]:
    return [IntegerValue(name, _get_text_content(v), v.attrib.get("permissions")) for v in elem]


def _get_interval_values(name: str, elem: etree._Element) -> list[Value]:
    return [IntervalValue(name, _get_text_content(v), v.attrib.get("permissions")) for v in elem]


def _get_list_values(name: str, elem: etree._Element) -> list[Value]:
    return [ListValue(name, _get_text_content(v), v.attrib.get("permissions")) for v in elem]


def _get_link_values(name: str, elem: etree._Element) -> list[Value]:
    return [LinkValue(name, _get_text_content(v), v.attrib.get("permissions")) for v in elem]


def _get_time_values(name: str, elem: etree._Element) -> list[Value]:
    return [TimeValue(name, _get_text_content(v), v.attrib.get("permissions")) for v in elem]


def _get_uri_values(name: str, elem: etree._Element) -> list[Value]:
    return [UriValue(name, _get_text_content(v), v.attrib.get("permissions")) for v in elem]


def _get_text_values(name: str, elem: etree._Element) -> list[Value]:
    res: list[Value] = []
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
