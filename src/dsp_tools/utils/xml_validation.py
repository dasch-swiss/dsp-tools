from __future__ import annotations

import importlib.resources
from datetime import datetime
from pathlib import Path
from typing import Any
from typing import Union

import regex
from lxml import etree

from dsp_tools.models.exceptions import InputError
from dsp_tools.utils.create_logger import get_logger
from dsp_tools.utils.xml_utils import parse_and_remove_comments_from_xml_file
from dsp_tools.utils.xml_utils import remove_namespaces_from_xml
from dsp_tools.utils.xml_validation_models import InconsistentTextValueEncodings
from dsp_tools.utils.xml_validation_models import TextValueData

logger = get_logger(__name__)

separator = "\n    "
list_separator = "\n    - "
medium_separator = "\n----------------------------\n"
grand_separator = "\n\n---------------------------------------\n\n"


def validate_xml(input_file: Union[str, Path, etree._ElementTree[Any]]) -> bool:
    """
    Validates an XML file against the DSP XSD schema.

    Args:
        input_file: path to the XML file to be validated, or parsed ElementTree

    Raises:
        InputError: if the XML file is invalid

    Returns:
        True if the XML file is valid
    """
    data_xml, xmlschema = _parse_schema_and_data_files(input_file)

    problems = []

    all_good, msg = _validate_xml_against_schema(xmlschema, data_xml)
    if not all_good:
        problems.append(msg)

    xml_no_namespace = remove_namespaces_from_xml(data_xml)

    all_good, msg = _find_xml_tags_in_simple_text_elements(xml_no_namespace)
    if not all_good:
        problems.append(msg)

    all_good, msg = _find_mixed_encodings_in_one_text_prop(xml_no_namespace)
    if not all_good:
        problems.append(msg)

    if len(problems) > 0:
        err_msg = grand_separator.join(problems)
        logger.error(err_msg, exc_info=True)
        raise InputError(err_msg)

    logger.info("The XML file is syntactically correct and passed validation.")
    print(f"{datetime.now()}: The XML file is syntactically correct and passed validation.")
    return True


def _parse_schema_and_data_files(
    input_file: Union[str, Path, etree._ElementTree[Any]],
) -> tuple[etree._Element, etree.XMLSchema]:
    with (
        importlib.resources.files("dsp_tools")
        .joinpath("resources/schema/data.xsd")
        .open(encoding="utf-8") as schema_file
    ):
        xmlschema = etree.XMLSchema(etree.parse(schema_file))
    data_xml = parse_and_remove_comments_from_xml_file(input_file)
    return data_xml, xmlschema


def _validate_xml_against_schema(xmlschema: etree.XMLSchema, data_xml: etree._Element) -> tuple[bool, str]:
    if not xmlschema.validate(data_xml):
        error_msg = "The XML file cannot be uploaded due to the following validation error(s):"
        for error in xmlschema.error_log:
            error_msg = error_msg + f"{separator}Line {error.line}: {error.message}"
        error_msg = error_msg.replace("{https://dasch.swiss/schema}", "")
        return False, error_msg
    return True, ""


def _find_xml_tags_in_simple_text_elements(
    xml_no_namespace: etree._Element,
) -> tuple[bool, str]:
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
        xml_no_namespace: parsed XML file with the namespaces removed

    Returns:
        True if there are no XML tags in the simple texts
    """
    resources_with_illegal_xml_tags = []
    for text in xml_no_namespace.findall(path="resource/text-prop/text"):
        regex_finds_tags = bool(regex.search(r'<([a-zA-Z/"]+|[^\s0-9].*[^\s0-9])>', str(text.text)))
        etree_finds_tags = bool(list(text.iterchildren()))
        has_tags = regex_finds_tags or etree_finds_tags
        if text.attrib["encoding"] == "utf8" and has_tags:
            sourceline = f"line {text.sourceline}: " if text.sourceline else " "
            propname = text.getparent().attrib["name"]  # type: ignore[union-attr]
            resname = text.getparent().getparent().attrib["id"]  # type: ignore[union-attr]
            resources_with_illegal_xml_tags.append(f"{sourceline}resource '{resname}', property '{propname}'")
    if resources_with_illegal_xml_tags:
        err_msg = (
            "XML-tags are not allowed in text properties with encoding=utf8.\n"
            "The following resources of your XML file violate this rule:"
        )
        err_msg += list_separator + list_separator.join(resources_with_illegal_xml_tags)
        return False, err_msg
    return True, ""


def _find_mixed_encodings_in_one_text_prop(
    xml_no_namespace: etree._Element,
) -> tuple[bool, str]:
    problems = check_if_only_one_encoding_is_used_per_prop_in_root(xml_no_namespace)
    if not problems:
        return True, ""
    msg, df = InconsistentTextValueEncodings(problems).execute_problem_protocol()
    if df is not None:
        csv_path = Path(f"XML_syntax_errors_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.csv")
        msg = f"\nAll the problems are listed in the file: '{csv_path.absolute()}'" + msg
        df.to_csv(csv_path)
    return False, msg


def check_if_only_one_encoding_is_used_per_prop_in_root(
    root: etree._Element,
) -> list[TextValueData]:
    """
    Check if all the encodings in the <text> elements are consistent within one <text-prop>

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
          A list of all the inconsistent <text-props>
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
    return [x for x in text_props if not len(x.encoding) == 1]
