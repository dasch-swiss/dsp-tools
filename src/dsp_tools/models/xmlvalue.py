from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Union, cast

import regex
from lxml import etree

from dsp_tools.models.value import KnoraStandoffXml


@dataclass
class XMLValue:  # pylint: disable=too-few-public-methods
    """Represents a value of a resource property in the XML used for data import"""

    value: Union[str, KnoraStandoffXml]
    resrefs: Optional[list[str]]
    comment: Optional[str]
    permissions: Optional[str]

    @staticmethod
    def fromXml(
        node: etree._Element,
        val_type: str,
        listname: Optional[str] = None,
    ) -> XMLValue:
        value: Union[str, KnoraStandoffXml]
        resrefs = None
        comment = node.get("comment")
        permissions = node.get("permissions")
        if val_type == "text" and node.get("encoding") == "xml":
            xmlstr_orig = etree.tostring(node, encoding="unicode", method="xml")
            xmlstr_cleaned = _cleanup_formatted_text(xmlstr_orig)
            value = KnoraStandoffXml(xmlstr_cleaned)
            resrefs = list({x.split(":")[1] for x in value.get_all_iris() or []})
        elif val_type == "text" and node.get("encoding") == "utf8":
            str_orig = "".join(node.itertext())
            str_cleaned = _cleanup_unformatted_text(str_orig)
            value = str_cleaned
        elif val_type == "list":
            listname = cast(str, listname)
            value = listname + ":" + "".join(node.itertext())
        else:
            value = "".join(node.itertext())
        return XMLValue(value, resrefs, comment, permissions)


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
