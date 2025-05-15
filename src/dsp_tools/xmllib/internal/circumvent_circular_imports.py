from __future__ import annotations

from lxml import etree

from dsp_tools.error.xmllib_warnings import MessageInfo
from dsp_tools.xmllib import escape_reserved_xml_characters
from dsp_tools.xmllib.internal.input_converters import numeric_entities


def parse_richtext_as_xml(
    input_str: str, resource_id: str | None = None, prop_name: str | None = None
) -> etree._Element | MessageInfo:
    """
    Parses an input string as XML. If it contains a syntax error a MessageInfo is returned.
    Else it returns the XML as etree

    Args:
        input_str: Richtext string
        resource_id: ID of the resource for improved error message
        prop_name: Property name for improved error message

    Returns:
        Parsed string or information for the user message.
    """
    escaped_text = escape_reserved_xml_characters(input_str)
    num_ent = numeric_entities(escaped_text)
    pseudo_xml = f"<ignore-this>{num_ent}</ignore-this>"
    try:
        return etree.fromstring(pseudo_xml)
    except etree.XMLSyntaxError as err:
        msg_str = (
            f"The entered richtext value could not be converted to a valid XML.\n"
            f"Original error message: {err.msg}\n"
            f"Potential line/column numbers are relative to this text: {pseudo_xml}"
        )
        return MessageInfo(resource_id=resource_id, prop_name=prop_name, message=msg_str)
