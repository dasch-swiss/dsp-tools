from typing import Any

import pandas as pd
import regex

from dsp_tools.error.xmllib_warnings import MessageInfo
from dsp_tools.error.xmllib_warnings_util import emit_xmllib_input_warning
from dsp_tools.xmllib.internal.circumvent_circular_imports import parse_richtext_as_xml


def is_nonempty_value(value: Any) -> bool:
    """
    Check if a value is not None-like
    or that its string representation contains at least one of the following characters:

    - ``\\p{S}`` = symbols and special characters
    - ``\\p{P}`` = punctuation
    - ``\\w`` = all Unicode letters, numbers, and _

    Args:
        value: value of any type

    Returns:
        True if the value is not None-like and contains at least one of the above-mentioned characters

    Examples:
        ```python
        # True values:
        assert xmllib.is_nonempty_value("word") == True
        assert xmllib.is_nonempty_value("None") == True
        assert xmllib.is_nonempty_value("-") == True
        assert xmllib.is_nonempty_value(0) == True
        assert xmllib.is_nonempty_value(1) == True
        assert xmllib.is_nonempty_value("0") == True
        assert xmllib.is_nonempty_value("1") == True
        assert xmllib.is_nonempty_value(True) == True
        assert xmllib.is_nonempty_value(False) == True
        assert xmllib.is_nonempty_value("עִבְרִית") == True

        # False values:
        assert xmllib.is_nonempty_value(pd.NA) == False
        assert xmllib.is_nonempty_value(None) == False
        assert xmllib.is_nonempty_value("") == False
        assert xmllib.is_nonempty_value(" ") == False
        assert xmllib.is_nonempty_value("\\n") == False
        ```
    """
    if pd.isna(value):
        return False
    if regex.search(r"[\p{S}\p{P}\w]", str(value), flags=regex.UNICODE):
        return True
    return False


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
    calendar_optional = r"(?:(GREGORIAN|JULIAN|ISLAMIC):)?"
    first_era_optional = r"(?:(CE|BCE|BC|AD):)?"
    second_area_optional = r"(?::(CE|BCE|BC|AD))?"
    date = r"\d{1,4}(?:-\d{1,2}){0,2}"
    date_mandatory = rf"({date})"
    date_optional = rf"(:{date})?"
    full_date_pattern = (
        rf"^{calendar_optional}{first_era_optional}{date_mandatory}{second_area_optional}{date_optional}$"
    )
    found = regex.search(full_date_pattern, str(value))
    if not found:
        return False
    if found.group(1) == "ISLAMIC" and (found.group(2) or found.group(4)):
        # eras are not supported yet for the islamic calendar
        return False
    return True


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
        XmllibInputWarning: if the input contains XML syntax problems
    """
    result = parse_richtext_as_xml(richtext)
    if isinstance(result, MessageInfo):
        emit_xmllib_input_warning(result)
