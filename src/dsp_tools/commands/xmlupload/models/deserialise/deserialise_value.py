from __future__ import annotations

from typing import Optional
from typing import Union
from typing import cast

import regex
from lxml import etree

from dsp_tools.commands.xmlupload.models.formatted_text_value import FormattedTextValue
from dsp_tools.models.exceptions import XmlUploadError


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

    def __init__(self, node: etree._Element, valtype: str, default_ontology: str) -> None:
        """
        The constructor for the DSP property

        Args:
            node: the property node, p.ex. <decimal-prop></decimal-prop>
            valtype: the type of value given by the name of the property node, p.ex. decimal in <decimal-prop>
            default_ontology: the name of the ontology

        Raises:
            XmlUploadError: If an upload fails
        """
        # get the property name which is in format namespace:propertyname, p.ex. rosetta:hasName
        tmp_prop_name = node.attrib["name"].split(":")
        if len(tmp_prop_name) > 1:
            if tmp_prop_name[0]:
                self.name = node.attrib["name"]
            else:
                # replace an empty namespace with the default ontology name
                self.name = default_ontology + ":" + tmp_prop_name[1]
        else:
            self.name = "knora-api:" + tmp_prop_name[0]
        listname = node.attrib.get("list")  # safe the list name if given (only for lists)
        self.valtype = valtype
        self.values = []

        # parse the subnodes of the property nodes which contain the actual values of the property
        for subnode in node:
            if subnode.tag == valtype:  # the subnode must correspond to the expected value type
                self.values.append(XMLValue(subnode, valtype, listname))
            else:
                raise XmlUploadError(f"ERROR Unexpected tag: '{subnode.tag}'. Property may contain only value tags!")


class XMLValue:
    """Represents a value of a resource property in the XML used for data import"""

    value: Union[str, FormattedTextValue]
    resrefs: Optional[list[str]]
    comment: Optional[str]
    permissions: Optional[str]
    link_uuid: Optional[str]

    def __init__(
        self,
        node: etree._Element,
        val_type: str,
        listname: Optional[str] = None,
    ) -> None:
        self.resrefs = None
        self.comment = node.get("comment")
        self.permissions = node.get("permissions")
        if val_type == "text" and node.get("encoding") == "xml":
            xmlstr_orig = etree.tostring(node, encoding="unicode", method="xml")
            xmlstr_cleaned = self._cleanup_formatted_text(xmlstr_orig)
            self.value = FormattedTextValue(xmlstr_cleaned)
            self.resrefs = list(self.value.find_internal_ids())
        elif val_type == "text" and node.get("encoding") == "utf8":
            str_orig = "".join(node.itertext())
            str_cleaned = self._cleanup_unformatted_text(str_orig)
            self.value = str_cleaned
        elif val_type == "list":
            listname = cast(str, listname)
            self.value = listname + ":" + "".join(node.itertext())
        else:
            self.value = "".join(node.itertext())
        self.link_uuid = node.attrib.get("linkUUID")  # not all richtexts have a link, so this attribute is optional

    def _cleanup_formatted_text(self, xmlstr_orig: str) -> str:
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

    def _cleanup_unformatted_text(self, string_orig: str) -> str:
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


class XMLBitstream:
    """
    Represents a bitstream object (file) of a resource in the XML used for data import

    Attributes:
        value: The file path of the bitstream object
        permissions: Reference to the set of permissions for the bitstream object
    """

    value: str
    permissions: Optional[str]

    def __init__(self, node: etree._Element) -> None:
        self.value = cast(str, node.text)
        self.permissions = node.get("permissions")


class IIIFUriInfo:
    """
    Represents a IIIF URI of a resource in the XML used for data import

    Attributes:
        value: The IIIF URI of the object
        permissions: Reference to the set of permissions for the IIIF URI
    """

    value: str
    permissions: str | None

    def __init__(self, node: etree._Element) -> None:
        self.value = cast(str, node.text)
        self.permissions = node.get("permissions")
