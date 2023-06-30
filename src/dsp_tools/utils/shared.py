from __future__ import annotations

import copy
import importlib.resources
import json
import time
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional, Union

import pandas as pd
import regex
from lxml import etree
from requests import ReadTimeout, RequestException

from dsp_tools.models.connection import Connection
from dsp_tools.models.exceptions import BaseError, UserError
from dsp_tools.models.propertyelement import PropertyElement
from dsp_tools.utils.logging import get_logger

logger = get_logger(__name__)


def login(
    server: str,
    user: str,
    password: str,
) -> Connection:
    """
    Creates a connection,
    makes a login (handling temporary network interruptions),
    and returns the active connection.

    Args:
        server: URL of the DSP server to connect to
        user: Username (e-mail)
        password: Password of the user

    Raises:
        UserError if the login fails permanently

    Return:
        Connection instance
    """
    con = Connection(server)
    try:
        try_network_action(lambda: con.login(email=user, password=password))
    except BaseError:
        logger.error("Cannot login to DSP server", exc_info=True)
        raise UserError("Cannot login to DSP server") from None
    return con


def try_network_action(
    action: Callable[..., Any],
    *args: Any,
    **kwargs: Any,
) -> Any:
    """
    Helper method that tries 7 times to execute an action.
    If a ConnectionError, a requests.exceptions.RequestException, or a non-permanent BaseError occors,
    it waits and retries.
    The waiting times are 1, 2, 4, 8, 16, 32, 64 seconds.
    If another exception occurs, it escalates.

    Args:
        action: a lambda with the code to be executed, or a function
        args: positional arguments for the action
        kwargs: keyword arguments for the action

    Raises:
        BaseError or unexpected exception if the action fails permanently

    Returns:
        the return value of action
    """
    action_as_str = f"action='{action}', args='{args}', kwargs='{kwargs}'"
    for i in range(7):
        try:
            if args and not kwargs:
                return action(*args)
            elif kwargs and not args:
                return action(**kwargs)
            elif args and kwargs:
                return action(*args, **kwargs)
            else:
                return action()
        except (TimeoutError, ReadTimeout):
            msg = f"Timeout Error: Try reconnecting to DSP server, next attempt in {2 ** i} seconds..."
            print(f"{datetime.now().isoformat()}: {msg}")
            logger.error(f"{msg} {action_as_str} (retry-counter i={i})", exc_info=True)
            time.sleep(2**i)
            continue
        except (ConnectionError, RequestException):
            msg = f"Network Error: Try reconnecting to DSP server, next attempt in {2 ** i} seconds..."
            print(f"{datetime.now().isoformat()}: {msg}")
            logger.error(f"{msg} {action_as_str} (retry-counter i={i})", exc_info=True)
            time.sleep(2**i)
            continue
        except BaseError as err:
            in_500_range = False
            if err.status_code:
                in_500_range = 500 <= err.status_code < 600
            try_again_later = "try again later" in err.message
            if try_again_later or in_500_range:
                msg = f"Transient Error: Try reconnecting to DSP server, next attempt in {2 ** i} seconds..."
                print(f"{datetime.now().isoformat()}: {msg}")
                logger.error(f"{msg} {action_as_str} (retry-counter i={i})", exc_info=True)
                time.sleep(2**i)
                continue
            else:
                raise err

    logger.error("Permanently unable to execute the network action. See logs for more details.")
    raise BaseError("Permanently unable to execute the network action. See logs for more details.")


def validate_xml_against_schema(input_file: Union[str, Path, etree._ElementTree[Any]]) -> bool:
    """
    Validates an XML file against the DSP XSD schema.

    Args:
        input_file: path to the XML file to be validated, or parsed ElementTree

    Raises:
        UserError with a detailed error log if the XML file is invalid

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
    print("The XML file is syntactically correct and passed validation.")
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
        # pylint: disable-next=protected-access
        if not isinstance(elem, (etree._Comment, etree._ProcessingInstruction)):
            elem.tag = etree.QName(elem).localname

    # then: make the test
    resources_with_illegal_xml_tags = list()
    for text in doc_without_namespace.findall(path="resource/text-prop/text"):
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
        BaseError if one of the required columns doesn't exist, or if the resulting DataFrame would be empty

    Returns:
        prepared DataFrame
    """
    # strip column headers and transform to lowercase, so that the script doesn't break when the headers vary a bit
    new_df = df.rename(columns=lambda x: x.strip().lower())
    required_columns = [x.strip().lower() for x in required_columns]
    # strip every cell, and insert "" if there is no valid word in it
    new_df = new_df.applymap(
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
    simplified_value = str(value).lower()

    # normalize characters (p.ex. ä becomes a)
    simplified_value = unicodedata.normalize("NFKD", simplified_value)

    # replace forward slash and whitespace with a dash
    simplified_value = regex.sub("[/\\s]+", "-", simplified_value)

    # delete all characters which are not letters, numbers or dashes
    simplified_value = regex.sub("[^A-Za-z0-9\\-]+", "", simplified_value)

    return simplified_value


def check_notna(value: Optional[Any]) -> bool:
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
            except:
                msg = f"The input file '{project_file_as_path_or_parsed}' cannot be parsed to a JSON object."
                logger.error(msg, exc_info=True)
                raise BaseError(msg) from None
    else:
        raise BaseError("Invalid input: The input must be a path to a JSON file or a parsed JSON object.")
    return project_definition
