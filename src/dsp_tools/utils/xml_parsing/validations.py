from __future__ import annotations

import importlib.resources

from lxml import etree

from dsp_tools.utils.xml_parsing.schema_validation import separator

list_separator = "\n    - "


def validate_xml_against_schema(data_xml: etree._Element) -> list[str]:
    """Validate agains XML Schema, this requires a cleaned tree."""
    schema_res = importlib.resources.files("dsp_tools").joinpath("resources/schema/data.xsd")
    with schema_res.open(encoding="utf-8") as schema_file:
        xmlschema = etree.XMLSchema(etree.parse(schema_file))
    if not xmlschema.validate(data_xml):
        error_msg = "The XML file cannot be uploaded due to the following validation error(s):"
        for error in xmlschema.error_log:
            error_msg = f"{error_msg}{separator}Line {error.line}: {error.message}"
        error_msg = error_msg.replace("{https://dasch.swiss/schema}", "")
        return [error_msg]
    return []
