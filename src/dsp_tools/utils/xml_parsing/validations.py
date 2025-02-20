from __future__ import annotations

import importlib.resources
import warnings
from datetime import datetime
from pathlib import Path

import regex
from lxml import etree

from dsp_tools.models.custom_warnings import DspToolsUserWarning
from dsp_tools.utils.xml_parsing.models.text_value_validation import InconsistentTextValueEncodings
from dsp_tools.utils.xml_parsing.models.text_value_validation import TextValueData
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


def find_mixed_encodings_in_text_tags(xml_no_namespace: etree._Element) -> list[str]:
    """Finds if any text tags contain mixed encoding."""
    problems = []
    _find_xml_tags_in_simple_text_elements(xml_no_namespace)
    problems.extend(_find_mixed_encodings_in_one_text_prop(xml_no_namespace))
    _check_for_deprecated_syntax(xml_no_namespace)
    return problems


def _find_xml_tags_in_simple_text_elements(xml_no_namespace: etree._Element) -> None:
    """
    Checks if there are angular brackets in simple text.
    It is possible that the user mistakenly added XML tags into a simple text field.
    But it is also possible that an angular bracket should be displayed.
    So that the user does not insert XML tags mistakenly into simple text fields,
    the user is warned, if there is any present.
    """
    resources_with_potential_xml_tags = []
    for text in xml_no_namespace.findall(path="resource/text-prop/text"):
        regex_finds_tags = bool(regex.search(r'<([a-zA-Z/"]+|[^\s0-9].*[^\s0-9])>', str(text.text)))
        etree_finds_tags = bool(list(text.iterchildren()))
        has_tags = regex_finds_tags or etree_finds_tags
        if text.attrib["encoding"] == "utf8" and has_tags:
            sourceline = f"line {text.sourceline}: " if text.sourceline else " "
            propname = text.getparent().attrib["name"]  # type: ignore[union-attr]
            resname = text.getparent().getparent().attrib["id"]  # type: ignore[union-attr]
            resources_with_potential_xml_tags.append(f"{sourceline}resource '{resname}', property '{propname}'")
    if resources_with_potential_xml_tags:
        err_msg = (
            "Angular brackets in the format of <text> were found in text properties with encoding=utf8.\n"
            "Please note that these will not be recognised as formatting in the text field, "
            "but will be displayed as-is.\n"
            f"The following resources of your XML file contain angular brackets:{list_separator}"
            f"{list_separator.join(resources_with_potential_xml_tags)}"
        )
        warnings.warn(DspToolsUserWarning(err_msg))


def _find_mixed_encodings_in_one_text_prop(xml_no_namespace: etree._Element) -> list[str]:
    problems = check_if_only_one_encoding_is_used_per_prop_in_root(xml_no_namespace)
    if not problems:
        return []
    msg, df = InconsistentTextValueEncodings(problems).execute_problem_protocol()
    if df is not None:
        csv_path = Path(f"XML_syntax_errors_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.csv")
        msg = f"\nAll the problems are listed in the file: '{csv_path.absolute()}'{msg}"
        df.to_csv(csv_path)
    return [msg]


def _check_for_deprecated_syntax(data_xml: etree._Element) -> None:
    pass


def check_if_only_one_encoding_is_used_per_prop_in_root(
    root: etree._Element,
) -> list[TextValueData]:
    """
    Check if all the encodings in the `<text>` elements are consistent within one `<text-prop>`

    This is correct:
    ```
    <text-prop name=":hasSimpleText">
        <text encoding="utf8">Text 1</text>
        <text encoding="utf8">Text 2</text>
    </text-prop>
    ```

    This is wrong:
    ```
    <text-prop name=":hasSimpleText">
        <text encoding="utf8">Text 1</text>
        <text encoding="xml">Text 2</text>
    </text-prop>
    ```

    Args:
        root: root of the data xml document

    Returns:
          A list of all the inconsistent `<text-props>`
    """
    text_props = _get_all_ids_and_encodings_from_root(root)
    return _find_all_text_props_with_multiple_encodings(text_props)


def _get_all_ids_and_encodings_from_root(
    root: etree._Element,
) -> list[TextValueData]:
    res_list = []
    for res_input in root.iterchildren(tag="resource"):
        res_list.extend(_get_encodings_from_one_resource(res_input))
    return res_list


def _get_encodings_from_one_resource(resource: etree._Element) -> list[TextValueData]:
    res_id = resource.attrib["id"]
    return [_get_encodings_from_one_property(res_id, child) for child in list(resource.iterchildren(tag="text-prop"))]


def _get_encodings_from_one_property(res_id: str, prop: etree._Element) -> TextValueData:
    prop_name = prop.attrib["name"]
    encodings = {x.attrib["encoding"] for x in prop.iterchildren()}
    return TextValueData(res_id, prop_name, encodings)


def _find_all_text_props_with_multiple_encodings(text_props: list[TextValueData]) -> list[TextValueData]:
    return [x for x in text_props if len(x.encoding) != 1]
