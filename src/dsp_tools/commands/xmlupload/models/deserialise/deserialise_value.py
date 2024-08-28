from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Optional
from typing import Union
from typing import cast

import regex
from lxml import etree

from dsp_tools.commands.xmlupload.models.formatted_text_value import FormattedTextValue
from dsp_tools.models.exceptions import XmlUploadError


@dataclass(frozen=True)
class XMLProperty:
    """
    Represents a property of a resource in the XML used for data import.

    Attributes:
        name: The name of the property
        valtype: The type of the property
        values: The list of values of the property
    """

    name: str
    valtype: str
    values: list[XMLValue]

    @staticmethod
    def from_node(node: etree._Element, valtype: str, default_ontology: str) -> XMLProperty:
        """
        The factory for the DSP property

        Args:
            node: the property node, p.ex. `<decimal-prop></decimal-prop>`
            valtype: the type of value given by the name of the property node, p.ex. decimal in `<decimal-prop>`
            default_ontology: the name of the ontology

        Raises:
            XmlUploadError: If an upload fails

        Returns:
            The DSP property
        """
        name = XMLProperty._get_name(node, default_ontology)
        if node.tag.endswith("-prop"):
            values = XMLProperty._get_values_from_normal_props(node, valtype)
        else:
            values = [XMLProperty._get_value_from_knora_base_prop(node)]
        return XMLProperty(name, valtype, values)

    @staticmethod
    def _get_name(node: etree._Element, default_ontology: str) -> str:
        # get the property name which is in format namespace:propertyname, p.ex. rosetta:hasName
        orig = node.attrib.get("name")
        if not orig:  # tags like <isSegmentOf> don't have a name attribute
            return f"knora-api:{node.tag}"
        elif ":" not in orig:
            return f"knora-api:{orig}"
        elif orig.startswith(":"):
            # replace an empty namespace with the default ontology name
            return f"{default_ontology}{orig}"
        else:
            return orig

    @staticmethod
    def _get_values_from_normal_props(node: etree._Element, valtype: str) -> list[XMLValue]:
        # parse the subnodes of the property nodes which contain the actual values of the property
        listname = node.attrib.get("list")  # save the list name if given (only for lists)
        values: list[XMLValue] = []
        for subnode in node:
            if subnode.tag == valtype:  # the subnode must correspond to the expected value type
                values.append(XMLValue.from_node(subnode, valtype, listname))
            else:
                raise XmlUploadError(f"ERROR Unexpected tag: '{subnode.tag}'. Property may contain only value tags!")
        return values

    @staticmethod
    def _get_value_from_knora_base_prop(node: etree._Element) -> XMLValue:
        resrefs = set()
        if node.tag.endswith("hasSegmentBounds"):
            value: str | FormattedTextValue = f"{node.attrib["segment_start"]}:{node.attrib["segment_end"]}"
        elif node.tag.endswith(("hasDescription", "hasComment")):
            value = _extract_formatted_text_from_node(node)
            resrefs = value.find_internal_ids()
        else:
            str_orig = "".join(node.itertext())
            value = _cleanup_unformatted_text(str_orig)
        comment = node.attrib.get("comment")
        permissions = node.attrib.get("permissions")
        link_uuid = node.attrib.get("linkUUID")
        return XMLValue(value=value, resrefs=resrefs, comment=comment, permissions=permissions, link_uuid=link_uuid)


@dataclass
class XMLValue:
    """Represents a value of a resource property in the XML used for data import"""

    value: Union[str, FormattedTextValue]
    resrefs: set[str] = field(default_factory=set)
    comment: Optional[str] = None
    permissions: Optional[str] = None
    link_uuid: Optional[str] = None

    @staticmethod
    def from_node(
        node: etree._Element,
        val_type: str,
        listname: Optional[str] = None,
    ) -> XMLValue:
        """Factory method to create an XMLValue from an XML node"""
        value: Union[str, FormattedTextValue] = ""
        resrefs = set()
        comment = node.get("comment")
        permissions = node.get("permissions")
        if val_type == "text" and node.get("encoding") == "xml":
            value = _extract_formatted_text_from_node(node)
            resrefs = value.find_internal_ids()
        elif val_type == "text" and node.get("encoding") == "utf8":
            str_orig = "".join(node.itertext())
            value = _cleanup_unformatted_text(str_orig)
        elif val_type == "list":
            listname = cast(str, listname)
            value = f"{listname}:" + "".join(node.itertext())
        else:
            value = "".join(node.itertext())
        link_uuid = node.attrib.get("linkUUID")  # not all richtexts have a link, so this attribute is optional
        return XMLValue(value=value, resrefs=resrefs, comment=comment, permissions=permissions, link_uuid=link_uuid)


def _extract_formatted_text_from_node(node: etree._Element) -> FormattedTextValue:
    xmlstr = etree.tostring(node, encoding="unicode", method="xml")
    xmlstr = regex.sub(f"<{node.tag}.*?>|</{node.tag}>", "", xmlstr)
    xmlstr = _cleanup_formatted_text(xmlstr)
    return FormattedTextValue(xmlstr)


def _cleanup_formatted_text(xmlstr_orig: str) -> str:
    """
    In a xml-encoded text value from the XML file,
    there may be non-text characters that must be removed.
    This function:
        - replaces (multiple) line breaks by a space
        - replaces multiple spaces or tabstops by a single space (except within `<code>` or `<pre>` tags)

    Args:
        xmlstr_orig: content of the tag from the XML file, in serialized form

    Returns:
        purged string, suitable to be sent to DSP-API
    """
    # replace (multiple) line breaks by a space
    xmlstr = regex.sub("\n+", " ", xmlstr_orig)

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
    This function:
        - removes the `<text>` tags
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
    return string.strip()


@dataclass(frozen=True)
class XMLBitstream:
    """
    Represents a bitstream object (file) of a resource in the XML used for data import

    Attributes:
        value: The file path of the bitstream object
        permissions: Reference to the set of permissions for the bitstream object
    """

    value: str
    permissions: Optional[str] = None

    @staticmethod
    def from_node(node: etree._Element) -> XMLBitstream:
        """Factory that parses a bitstream node from the XML DOM"""
        if not node.text:
            raise XmlUploadError("Empty bitstream tag")
        return XMLBitstream(node.text, node.get("permissions"))


@dataclass(frozen=True)
class IIIFUriInfo:
    """
    Represents a IIIF URI of a resource in the XML used for data import

    Attributes:
        value: The IIIF URI of the object
        permissions: Reference to the set of permissions for the IIIF URI
    """

    value: str
    permissions: str | None = None

    @staticmethod
    def from_node(node: etree._Element) -> IIIFUriInfo:
        """Factory that parses an IIIF URI node from the XML DOM"""
        if not node.text:
            raise XmlUploadError("Empty IIIF URI tag")
        return IIIFUriInfo(node.text, node.get("permissions"))
