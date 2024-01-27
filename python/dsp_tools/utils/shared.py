from __future__ import annotations

import copy
import glob
import importlib.resources
import json
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, TypeGuard, Union

import pandas as pd
import regex
from lxml import etree

from dsp_tools.commands.excel2xml.propertyelement import PropertyElement
from dsp_tools.models.exceptions import BaseError, UserError
from dsp_tools.utils.create_logger import get_logger

logger = get_logger(__name__)


def validate_xml_against_schema(input_file: Union[str, Path, etree._ElementTree[Any]]) -> bool:
    """
    Validates an XML file against the DSP XSD schema.

    Args:
        input_file: path to the XML file to be validated, or parsed ElementTree

    Raises:
        UserError: if the XML file is invalid

    Returns:
        True if the XML file is valid
    """
    with importlib.resources.files("dsp_tools").joinpath("resources/schema/data.xsd").open(
        encoding="utf-8"
    ) as schema_file:
        xmlschema = etree.XMLSchema(etree.parse(schema_file))
    if isinstance(input_file, (str, Path)):
        try:
            doc = etree.parse(source=input_file)
        except etree.XMLSyntaxError as err:
            logger.error(f"The XML file contains the following syntax error: {err.msg}", exc_info=True)
            raise UserError(f"The XML file contains the following syntax error: {err.msg}") from None
    else:
        doc = input_file

    if not xmlschema.validate(doc):
        error_msg = "The XML file cannot be uploaded due to the following validation error(s):"
        for error in xmlschema.error_log:
            error_msg = error_msg + f"\n  Line {error.line}: {error.message}"
        error_msg = error_msg.replace("{https://dasch.swiss/schema}", "")
        logger.error(error_msg)
        raise UserError(error_msg)

    # make sure there are no XML tags in simple texts
    _validate_xml_tags_in_text_properties(doc)

    logger.info("The XML file is syntactically correct and passed validation.")
    print(f"{datetime.now()}: The XML file is syntactically correct and passed validation.")
    return True


def _validate_xml_tags_in_text_properties(doc: Union[etree._ElementTree[etree._Element], etree._Element]) -> bool:
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
        doc: parsed XML file

    Raises:
        UserError: if there is an XML tag in one of the simple texts

    Returns:
        True if there are no XML tags in the simple texts
    """
    # first: remove namespaces
    doc_without_namespace = copy.deepcopy(doc)
    for elem in doc_without_namespace.iter():
        if not isinstance(elem, (etree._Comment, etree._ProcessingInstruction)):
            elem.tag = etree.QName(elem).localname

    # then: make the test
    resources_with_illegal_xml_tags = []
    for text in doc_without_namespace.findall(path="resource/text-prop/text"):
        regex_finds_tags = bool(regex.search(r'<([a-zA-Z/"]+|[^\s0-9].*[^\s0-9])>', str(text.text)))
        etree_finds_tags = bool(list(text.iterchildren()))
        has_tags = regex_finds_tags or etree_finds_tags
        if text.attrib["encoding"] == "utf8" and has_tags:
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
        logger.error(err_msg, exc_info=True)
        raise UserError(err_msg)

    return True


def prepare_dataframe(
    df: pd.DataFrame,
    required_columns: list[str],
    location_of_sheet: str,
) -> pd.DataFrame:
    """
    Takes a pandas DataFrame,
    strips the column headers from whitespaces and transforms them to lowercase,
    strips every cell from whitespaces and inserts "" if there is no string in it,
    and deletes the rows that don't have a value in one of the required cells.

    Args:
        df: pandas DataFrame
        required_columns: headers of the columns where a value is required
        location_of_sheet: for better error messages, provide this information of the caller

    Raises:
        BaseError: if one of the required columns doesn't exist, or if the resulting DataFrame would be empty

    Returns:
        prepared DataFrame
    """
    # strip column headers and transform to lowercase, so that the script doesn't break when the headers vary a bit
    new_df = df.rename(columns=lambda x: x.strip().lower())
    required_columns = [x.strip().lower() for x in required_columns]
    # strip every cell, and insert "" if there is no valid word in it
    new_df = new_df.map(
        lambda x: str(x).strip() if pd.notna(x) and regex.search(r"[\w\p{L}]", str(x), flags=regex.U) else ""
    )
    # delete rows that don't have the required columns
    for req in required_columns:
        if req not in new_df:
            raise BaseError(f"{location_of_sheet} requires a column named '{req}'")
        new_df = new_df[pd.notna(new_df[req])]
        new_df = new_df[[bool(regex.search(r"[\w\p{L}]", x, flags=regex.U)) for x in new_df[req]]]
    if len(new_df) < 1:
        raise BaseError(f"{location_of_sheet} requires at least one row")
    return new_df


def simplify_name(value: str) -> str:
    """
    Simplifies a given value in order to use it as node name

    Args:
        value: The value to be simplified

    Returns:
        str: The simplified value
    """
    simplified_value = value.lower()

    # normalize characters (p.ex. ä becomes a)
    simplified_value = unicodedata.normalize("NFKD", simplified_value)

    # replace forward slash and whitespace with a dash
    simplified_value = regex.sub("[/\\s]+", "-", simplified_value)

    # delete all characters which are not letters, numbers or dashes
    simplified_value = regex.sub("[^A-Za-z0-9\\-]+", "", simplified_value)

    return simplified_value


def check_notna(value: Optional[Any]) -> TypeGuard[Any]:
    """
    Check a value if it is usable in the context of data archiving. A value is considered usable if it is
     - a number (integer or float, but not np.nan)
     - a boolean
     - a string with at least one Unicode letter (matching the regex ``\\p{L}``) or number, or at least one _, !, or ?
       (The strings "None", "<NA>", "N/A", and "-" are considered invalid.)
     - a PropertyElement whose "value" fulfills the above criteria

    Args:
        value: any object encountered when analysing data

    Returns:
        True if the value is usable, False if it is N/A or otherwise unusable

    Examples:
        >>> check_notna(0)      == True
        >>> check_notna(False)  == True
        >>> check_notna("œ")    == True
        >>> check_notna("0")    == True
        >>> check_notna("_")    == True
        >>> check_notna("!")    == True
        >>> check_notna("?")    == True
        >>> check_notna(None)   == False
        >>> check_notna("None") == False
        >>> check_notna(<NA>)   == False
        >>> check_notna("<NA>") == False
        >>> check_notna("-")    == False
        >>> check_notna(" ")    == False
    """

    if isinstance(value, PropertyElement):
        value = value.value

    if isinstance(value, (bool, int)) or (
        isinstance(value, float) and pd.notna(value)
    ):  # necessary because isinstance(np.nan, float)
        return True
    elif isinstance(value, str):
        return bool(regex.search(r"[\p{L}\d_!?]", value, flags=regex.UNICODE)) and not bool(
            regex.search(r"^(none|<NA>|-|n/a)$", value, flags=regex.IGNORECASE)
        )
    else:
        return False


def parse_json_input(project_file_as_path_or_parsed: Union[str, Path, dict[str, Any]]) -> dict[str, Any]:
    """
    Check the input for a method that expects a JSON project definition, either as file path or as parsed JSON object:
    If it is parsed already, return it unchanged.
    If the input is a file path, parse it.

    Args:
        project_file_as_path_or_parsed: path to the JSON project definition, or parsed JSON object

    Raises:
        BaseError: if the input is invalid

    Returns:
        the parsed JSON object
    """
    if isinstance(project_file_as_path_or_parsed, dict):
        project_definition: dict[str, Any] = project_file_as_path_or_parsed
    elif isinstance(project_file_as_path_or_parsed, (str, Path)) and Path(project_file_as_path_or_parsed).exists():
        with open(project_file_as_path_or_parsed, encoding="utf-8") as f:
            try:
                project_definition = json.load(f)
            except json.JSONDecodeError:
                msg = f"The input file '{project_file_as_path_or_parsed}' cannot be parsed to a JSON object."
                logger.error(msg, exc_info=True)
                raise BaseError(msg) from None
    else:
        raise BaseError("Invalid input: The input must be a path to a JSON file or a parsed JSON object.")
    return project_definition


def get_most_recent_glob_match(glob_pattern: Union[str, Path]) -> Path:
    """
    Find the most recently created file that matches a glob pattern.

    Args:
        glob_pattern: glob pattern, either absolute or relative to the cwd of the caller

    Returns:
        the most recently created file that matches the glob pattern
    """
    candidates = [Path(x) for x in glob.glob(str(glob_pattern))]
    return max(candidates, key=lambda item: item.stat().st_ctime)
