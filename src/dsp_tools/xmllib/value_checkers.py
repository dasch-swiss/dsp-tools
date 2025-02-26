import warnings
from typing import Any

import pandas as pd
import regex
from lxml import etree
from namedentities.core import numeric_entities  # type: ignore[import-untyped]

from dsp_tools.models.custom_warnings import DspToolsUserWarning
from dsp_tools.xmllib.constants import KNOWN_XML_TAGS
from dsp_tools.xmllib.internal_helpers import escape_reserved_xml_chars
from dsp_tools.xmllib.models.problems import IllegalTagProblem


def is_nonempty_value(value: Any) -> bool:
    """
    Check if a value is not empty.

    Args:
        value: value to check

    Returns:
        True if it is not empty

    Examples:
        ```python
        result = xmllib.is_nonempty_value("not empty")
        # result == True
        ```

        ```python
        result = xmllib.is_nonempty_value("")
        # result == False
        ```

        ```python
        result = xmllib.is_nonempty_value(None)
        # result == False
        ```
    """
    if isinstance(value, str) and len(value.strip()) == 0:
        return False
    return not pd.isna(value)


def is_bool_like(value: Any) -> bool:
    """
    Checks if a value is a bool or can be converted into a bool.
    It is case-insensitive, meaning that the words can also be capitalised.

    Accepted values:
         - `false`, `0`, `0.0`, `no`, `non`, `nein` -> `False`
         - `true`, `1`, `1.0`, `yes`, `oui`, `ja` -> `True`

    Args:
        value: value to check

    Returns:
        True if it conforms

    Examples:
        ```python
        result = xmllib.is_bool_like("yes")
        # result == True
        ```

        ```python
        result = xmllib.is_bool_like("not like a bool")
        # result == False
        ```
    """
    value = str(value).lower().strip()
    if value in ("false", "0", "0.0", "no", "non", "nein"):
        return True
    elif value in ("true", "1", "1.0", "yes", "oui", "ja"):
        return True
    return False


def is_color(value: Any) -> bool:
    """
    Checks if a value is a color value.

    Args:
        value: value to check

    Returns:
        True if it conforms

    Examples:
        ```python
        result = xmllib.is_color("#00ff66")
        # result == True
        ```

        ```python
        result = xmllib.is_color("not a color")
        # result == False
        ```
    """
    return bool(regex.search(r"^#[0-9a-f]{6}$", str(value).strip(), flags=regex.IGNORECASE))


def is_date(value: Any) -> bool:
    """
    Checks if a value is a date value.

    Args:
        value: value to check

    Returns:
        True if it conforms

    Examples:
        ```python
        result = xmllib.is_date("GREGORIAN:CE:2014-01-31:CE:2014-01-31")
        # result == True
        ```

        ```python
        result = xmllib.is_date("not a date")
        # result == False
        ```
    """
    calendar_optional = r"((GREGORIAN|JULIAN|ISLAMIC):)?"
    first_era_optional = r"((CE|BCE|BC|AD):)?"
    second_area_optional = r"(:(CE|BCE|BC|AD))?"
    date = r"\d{1,4}(?:-\d{1,2}){0,2}"
    date_mandatory = rf"({date})"
    date_optional = rf"(:{date})?"
    full_date_pattern = (
        rf"^{calendar_optional}{first_era_optional}{date_mandatory}{second_area_optional}{date_optional}$"
    )
    return bool(regex.search(full_date_pattern, str(value)))


def is_geoname(value: Any) -> bool:
    """
    Checks if a value is a geoname value.

    Args:
        value: value to check

    Returns:
        True if it conforms

    Examples:
        ```python
        result = xmllib.is_geoname("8879000")
        # result == True
        ```

        ```python
        result = xmllib.is_geoname("not a geoname code")
        # result == False
        ```
    """
    return is_integer(value)


def is_decimal(value: Any) -> bool:
    """
    Checks if a value is a float, an integer, or a string which can be converted into a float.

    Args:
        value: value to check

    Returns:
        True if conforms to the above-mentioned criteria.

    Examples:
        ```python
        result = xmllib.is_decimal("0.1")
        # result == True
        ```

        ```python
        # because this is equivalent to 9.0 it is accepted

        result = xmllib.is_decimal(9)
        # result == True
        ```

        ```python
        result = xmllib.is_decimal("not a decimal")
        # result == False
        ```
    """
    if pd.isna(value):
        return False

    match value:
        case bool():
            return False
        case int() | float():
            return True
    try:
        float(value)
        return True
    except ValueError:
        return False


def is_integer(value: Any) -> bool:
    """
    Checks if a value is an integer or a string which can be converted into an integer.

    Args:
        value: value to check

    Returns:
        True if conforms to the above-mentioned criteria.

    Examples:
        ```python
        result = xmllib.is_integer("1")
        # result == True
        ```

        ```python
        result = xmllib.is_integer(9.1)
        # result == False
        ```

        ```python
        result = xmllib.is_integer("not an integer")
        # result == False
        ```
    """
    match value:
        case bool():
            return False
        case int():
            return True
        case str():
            return bool(regex.search(r"^\d+$", value))
        case _:
            return False


def is_string_like(value: Any) -> bool:
    """
    Checks if a value is a string.

    Args:
        value: value to check

    Returns:
        True if it is a string

    Examples:
        ```python
        result = xmllib.is_string_like("this is a string")
        # result == True
        ```

        ```python
        # because numbers, floats, etc. can be converted to strings they are accepted

        result = xmllib.is_string_like(1)
        # result == True
        ```

        ```python
        result = xmllib.is_string_like(None)
        # result == False
        ```
    """
    if pd.isna(value):
        return False
    value = str(value).strip()
    if len(value) == 0:
        return False
    return bool(regex.search(r"\S", value, flags=regex.UNICODE))


def is_timestamp(value: Any) -> bool:
    """
    Checks if a value is a valid timestamp.

    Args:
        value: value to check

    Returns:
        True if it conforms

    Examples:
        ```python
        result = xmllib.is_timestamp("2019-10-23T13:45:12Z")
        # result == True
        ```

        ```python
        result = xmllib.is_timestamp("not a time stamp")
        # result == False
        ```
    """
    validation_regex = r"^\d{4}-[0-1]\d-[0-3]\dT[0-2]\d:[0-5]\d:[0-5]\d(\.\d{1,12})?(Z|[+-][0-1]\d:[0-5]\d)$"
    return bool(regex.search(validation_regex, str(value)))


def is_dsp_iri(value: Any) -> bool:
    """
    Check if a value is a valid internal DSP IRI.

    Args:
        value: IRI

    Returns:
        True if it is valid, else false

    Examples:
        ```python
        result = xmllib.is_dsp_iri("http://rdfh.ch/4123/54SYvWF0QUW6a")
        # result == True
        ```

        ```python
        result = xmllib.is_dsp_iri("http://dbpedia.org/resource/Internationalized_Resource_Identifier")
        # result == False
        ```
    """
    return bool(regex.search(r"^http://rdfh\.ch/\d{4}/", str(value)))


def is_dsp_ark(value: Any) -> bool:
    """
    Checks if a value is a valid ARK.

    Args:
        value: ARK

    Returns:
        True if it is valid, else false

    Examples:
        ```python
        result = xmllib.is_dsp_ark("ark:/72163/4123-31ec6eab334-a.2022829")
        # result == True
        ```

        ```python
        result = xmllib.is_dsp_ark("http://rdfh.ch/4123/54SYvWF0QUW6a")
        # result == False
        ```
    """
    return bool(regex.search(r"^ark:/", str(value)))


def check_richtext_syntax(richtext: str) -> None:
    """
    DSP richtexts must be convertible into valid XML.
    This checker escapes the reserved characters `<`, `>` and `&`,
    but only if they are not part of a standard standoff tag or escape sequence.
    Then, it tries to parse the resulting XML.

    Note: Only DSP standard standoff tags are allowed in richtexts. They are documented
    [here](https://docs.dasch.swiss/latest/DSP-API/03-endpoints/api-v2/text/standard-standoff/).

    Args:
        richtext: richtext to check

    Warns:
        DspToolsUserWarning: if the input contains XML syntax problems
    """
    escaped_text = escape_reserved_xml_chars(richtext, KNOWN_XML_TAGS)
    # transform named entities (=character references) to numeric entities, e.g. &nbsp; -> &#160;
    num_ent = numeric_entities(escaped_text)
    pseudo_xml = f"<text>{num_ent}</text>"
    try:
        _ = etree.fromstring(pseudo_xml)
    except etree.XMLSyntaxError as err:
        prob = IllegalTagProblem(orig_err_msg=err.msg, pseudo_xml=pseudo_xml)
        warnings.warn(DspToolsUserWarning(prob.execute_error_protocol()))
