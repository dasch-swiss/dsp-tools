import copy
import importlib.resources
import json
from pathlib import Path
import time
import unicodedata
from datetime import datetime
from typing import Callable, Any, Optional, Union

import pandas as pd
import regex
from lxml import etree
from requests import RequestException

from dsp_tools.models.connection import Connection
from dsp_tools.models.helpers import BaseError
from dsp_tools.models.propertyelement import PropertyElement


def login(server: str, user: str, password: str) -> Connection:
    """
    Logs in and returns the active connection. Raises a BaseError if the login fails.

    Args:
        server: URL of the DSP server to connect to
        user: Username (e-mail)
        password: Password of the user

    Return:
        Connection instance
    """
    con = Connection(server)
    try_network_action(
        action=lambda: con.login(email=user, password=password),
        failure_msg="ERROR: Cannot login to DSP server"
    )
    return con


def try_network_action(
    failure_msg: str,
    action: Callable[..., Any]
) -> Any:
    """
    Helper method that tries 7 times to execute an action. Each time, it catches ConnectionError and
    requests.exceptions.RequestException, which lead to a waiting time and a retry. The waiting times are 1,
    2, 4, 8, 16, 32, 64 seconds.

    In case of a BaseError or Exception, a BaseError is raised with failure_msg, followed by the original
    error message.

    If there is no success at the end, a BaseError with failure_msg is raised.

    Args:
        failure_msg: message of the raised BaseError if action cannot be executed
        action: a lambda with the code to be executed

    Returns:
        the return value of action
    """

    for i in range(7):
        try:
            return action()
        except ConnectionError:
            print(f'{datetime.now().isoformat()}: Try reconnecting to DSP server, next attempt in {2 ** i} seconds...')
            time.sleep(2 ** i)
            continue
        except RequestException:
            print(f'{datetime.now().isoformat()}: Try reconnecting to DSP server, next attempt in {2 ** i} seconds...')
            time.sleep(2 ** i)
            continue
        except BaseError as err:
            if regex.search(r'try again later', err.message) or regex.search(r'status code=5\d\d', err.message):
                print(f'{datetime.now().isoformat()}: Try reconnecting to DSP server, next attempt in {2 ** i} seconds...')
                time.sleep(2 ** i)
                continue
            if hasattr(err, 'message'):
                err_message = err.message
            else:
                err_message = str(err).replace('\n', ' ')
                err_message = err_message[:150] if len(err_message) > 150 else err_message
            raise BaseError(f"{failure_msg} Error message: {err_message}")
        except Exception as exc:
            if hasattr(exc, 'message'):
                exc_message = exc.message
            else:
                exc_message = str(exc).replace('\n', ' ')
                exc_message = exc_message[:150] if len(exc_message) > 150 else exc_message
            raise BaseError(f"{failure_msg} Error message: {exc_message}")

    raise BaseError(failure_msg)


def validate_xml_against_schema(input_file: str) -> bool:
    """
    Validates an XML file against an XSD schema

    Args:
        input_file: path to the XML file to be validated

    Raises:
        BaseError with a detailed error log if the XML file is invalid
    
    Returns:
        True if the XML file is valid
    """
    with importlib.resources.files("dsp_tools").joinpath("schemas").joinpath("data.xsd").open() as schema_file:
        xmlschema = etree.XMLSchema(etree.parse(schema_file))
    try:
        doc = etree.parse(input_file)
    except etree.XMLSyntaxError as err:
        raise BaseError(f"The XML file contains the following syntax error: {err.msg}") from None

    # remove namespaces
    doc_without_namespace = copy.deepcopy(doc)
    for elem in doc_without_namespace.getiterator():
        if not (isinstance(elem, etree._Comment) or isinstance(elem, etree._ProcessingInstruction)):
            elem.tag = etree.QName(elem).localname
    
    # make sure there are no XML tags in simple texts
    lines_with_illegal_xml_tags = list()
    for text in doc_without_namespace.findall(path="resource/text-prop/text"):
        if text.attrib["encoding"] == "utf8":
            if regex.search(r'<([a-zA-Z/"]+|\S.*\S)>', str(text.text)) or len(text.getchildren()) > 0:
                lines_with_illegal_xml_tags.append(text.sourceline)
    if lines_with_illegal_xml_tags:
        raise BaseError(f"XML-tags are not allowed in text properties with encoding=utf8. "
                        f"The following lines of your XML file are affected: {lines_with_illegal_xml_tags}")

    if xmlschema.validate(doc):
        print("The XML file is syntactically correct and passed validation.")
        return True
    else:
        error_msg = "The XML file cannot be uploaded due to the following validation error(s):"
        for error in xmlschema.error_log:
            error_msg = error_msg + f"\n  Line {error.line}: {error.message}"
        raise BaseError(error_msg)


def prepare_dataframe(df: pd.DataFrame, required_columns: list[str], location_of_sheet: str) -> pd.DataFrame:
    """
    Takes a pandas DataFrame, strips the column headers from whitespaces and transforms them to lowercase,
    strips every cell from whitespaces and inserts "" if there is no string in it, and deletes the rows that don't have
    a value in one of the required cells.

    Args:
        df: pandas DataFrame
        required_columns: headers of the columns where a value is required
        location_of_sheet: for better error messages, provide this information of the caller

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
            raise ValueError(f"{location_of_sheet} requires a column named '{req}'")
        new_df = new_df[pd.notna(new_df[req])]
        new_df = new_df[[bool(regex.search(r"[\w\p{L}]", x, flags=regex.U)) for x in new_df[req]]]
    if len(new_df) < 1:
        raise ValueError(f"{location_of_sheet} requires at least one row")
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

    if any([
        isinstance(value, int),
        isinstance(value, float) and pd.notna(value),   # necessary because isinstance(np.nan, float)
        isinstance(value, bool)
    ]):
        return True
    elif isinstance(value, str):
        return all([
            regex.search(r"[\p{L}\d_!?]", value, flags=regex.UNICODE),
            not bool(regex.search(r"^(none|<NA>|-|n/a)$", value, flags=regex.IGNORECASE))
        ])
    else:
        return False


def parse_json_input(project_file_as_path_or_parsed: Union[str, dict[str, Any]]) -> dict[str, Any]:
    """
    Check the input for a method that expects a JSON project definition, either as file path or as parsed JSON object: 
    If it is parsed already, return it unchanged.
    If the input is a file path, parse it.

    Args:
        project_file_as_path_or_parsed: path to the JSON project definition, or parsed JSON object

    Returns:
        the parsed JSON object
    """
    if isinstance(project_file_as_path_or_parsed, str) and Path(project_file_as_path_or_parsed).exists():
        with open(project_file_as_path_or_parsed) as f:
            try:
                project_definition: dict[str, Any] = json.load(f)
            except:
                raise BaseError(f"The input file '{project_file_as_path_or_parsed}' cannot be parsed to a JSON object.")
    elif isinstance(project_file_as_path_or_parsed, dict):
        project_definition = project_file_as_path_or_parsed
    else:
        raise BaseError(f"Invalid input: The input must be a path to a JSON file or a parsed JSON object.")
    return project_definition
