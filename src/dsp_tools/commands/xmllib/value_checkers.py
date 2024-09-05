from __future__ import annotations

from typing import Any

import pandas as pd
import regex


def is_bool(value: Any) -> bool:
    """
    Checks if a value is a bool or can be converted into a bool.

    Args:
        value: value to check

    Returns:
        True if it conforms
    """
    if isinstance(value, bool):
        return True
    if isinstance(value, str):
        value = value.lower()
    if value in (False, "false", "0", 0, 0.0, "no"):
        return True
    elif value in (True, "true", "1", 1, 1.0, "yes"):
        return True
    return False


def is_color(value: Any) -> bool:
    """
    Checks if a value is a color value.

    Args:
        value: value to check

    Returns:
        True if it conforms
    """

    return bool(regex.search(r"^#[0-9a-f]{6}$", str(value).strip(), flags=regex.IGNORECASE))


def is_date(value: Any) -> bool:
    """
    Checks if a value is a color value.

    Args:
        value: value to check

    Returns:
        True if it conforms
    """

    calendar = r"GREGORIAN|JULIAN|ISLAMIC"
    era = r"CE|BCE|BC|AD"
    year = r"\d{1,4}"
    month = r"\d{1,2}"
    day = r"\d{1,2}"
    full_date_pattern = rf"""
    ^
    (?:({calendar}):)?                         # optional calendar
    (?:({era}):)?                              # optional era
    ({year}(?:-{month})?(?:-{day})?)         # date
    (?::({era}))?                              # optional era
    (?::({year}(?:-{month})?(?:-{day})?))?   # optional date
    $
    """
    return bool(regex.search(full_date_pattern, str(value)))


def is_geoname(value: Any) -> bool:
    """
    Checks if a value is a color value.

    Args:
        value: value to check

    Returns:
        True if it conforms
    """
    return is_integer(value)


def is_decimal(value: Any) -> bool:
    """
    Checks if a value is a float.
    A valid integer is if it is a string, which can be converted into an integer,
    or a value of the type int.

    Args:
        value: value to check

    Returns:
        True if conforms to the above-mentioned criteria.
    """
    if isinstance(value, str):
        if regex.search(r"^\d+(\.\d+)?$", value):
            return True
    elif isinstance(value, int) or isinstance(value, float):
        return True
    return False


def is_integer(value: Any) -> bool:
    """
    Checks if a value is an integer.
    A valid integer is if it is a string, which can be converted into an integer,
    or a value of the type int.

    Args:
        value: value to check

    Returns:
        True if conforms to the above-mentioned criteria.
    """
    if isinstance(value, str):
        if regex.search(r"^\d+$", value):
            return True
    elif isinstance(value, int):
        return True
    return False


def is_list(node: Any, listname: Any) -> bool:
    """
    Checks if a value is valid.

    Args:
        node: value to check
        listname: name of the list

    Returns:
        True if it is not empty
    """
    if any([pd.isna(node), pd.isna(listname)]):
        return False
    if len(str(node)) == 0:
        return False
    if len(str(listname)) == 0:
        return False
    return True


def is_string(value: Any) -> bool:
    """
    Checks if a value is a string.

    Args:
        value: value to check

    Returns:
        True if it is a string
    """
    if pd.isna(value):
        return False
    value = str(value)
    if len(value) == 0:
        return False
    return bool(regex.search(r"[\p{L}\d_!?]", value, flags=regex.UNICODE))


def is_timestamp(value: Any) -> bool:
    """
    Checks if a value is a color value.

    Args:
        value: value to check

    Returns:
        True if it conforms
    """
    validation_regex = r"^\d{4}-[0-1]\d-[0-3]\dT[0-2]\d:[0-5]\d:[0-5]\d(.\d{1,12})?(Z|[+-][0-1]\d:[0-5]\d)$"
    return bool(regex.search(validation_regex, str(value)))


def is_uri(s: str) -> bool:
    """Checks if the given string is a valid URI."""
    # URI = scheme ":" ["//" host [":" port]] path ["?" query] ["#" fragment]
    scheme = r"(?<scheme>[a-z][a-z0-9+.\-]*)"
    host = r"(?<host>[\w_.\-~:\[\]]+)"
    port = r"(?<port>:\d{0,6})"
    path = r"(?<path>/[\w_.\-~:%()]*)"
    query = r"(?<query>\?[\w_.,;/\-:%=*&]+)"
    fragment = r"(?<fragment>#[\w_.\-~:/]*)"
    m = regex.match(rf"{scheme}:(//{host}{port}?){path}*{query}*{fragment}?", s, flags=regex.UNICODE)
    return m is not None


def is_iiif_uri(uri: str) -> bool:
    """
    Checks if the given URL is a valid IIIF URL.
    It should support all versions of IIIF servers,
    but was constructed with the syntax described in: https://iiif.io/api/image/3.0/#2-uri-syntax.
    IIIF is open to modifications which are not described in the official documentation
    (see https://iiif.io/api/annex/notes/design_principles/#define-success-not-failure).

    Args:
        uri: The URI to be checked.

    Returns:
        True if the URI is a valid IIIF URI, False otherwise.
    """
    # {scheme}://{server}/{prefix}/{identifier}/{region}/{size}/{rotation}/{quality}.{format}
    split_uri = uri.lower().split("/")
    try:
        region_seg, size_seg, rotation_seg, quality_format_seg = split_uri[-4:]
    except ValueError:
        return False
    # %5E is the URL encoded version of ^ ->
    # because we do change the uri to lower case we need to change that in the regex
    # (\d+(\.\d+)?) -> number, can be integer or float
    # everything needs to be encapsulated in a group
    # otherwise the ^ and $ only apply respectively to the first and last listed in the alternative options
    region_re = (
        r"^(full|square|"  # full | square
        r"((pct:)?(\d+(\.\d+)?,){3}(\d+(\.\d+)?)))$"  # x,y,w,h | pct:x,y,w,h
    )
    if not regex.search(region_re, region_seg):
        return False
    size_re = (
        r"^((\^|%5e)?max|"  # max | ^max
        r"(\^|%5e)?full|"  # full | ^full
        r"(\^|%5e)?pct:\d+(\.\d+)?|"  # pct:n | ^pct:n
        r"(\^|%5e)?(\d+(\.\d+)?)+,|"  # w, | ^w,
        r"(\^|%5e)?,\d+(\.\d+)?|"  # ,h | ^,h
        r"(\^|%5e)?!?\d+(\.\d+)?,\d+(\.\d+)?)$"  # w,h | ^w,h | !w,h | ^!w,h
    )
    if not regex.search(size_re, size_seg):
        return False
    # rotation -> floating point number 0-360 -> n | !n (positive and negative are allowed)
    rotation_re = r"^!?[+-]?\d+(\.\d+)?$"
    if not regex.search(rotation_re, rotation_seg):
        return False
    # quality -> color | colour | gray | grey | bitonal | default | native
    # format -> jpg | tif | png | gif | jp2 | pdf | webp
    quality_format_re = r"^(colou?r|gr[ae]y|bitonal|default|native)(\.(jpg|tif|png|jp2|gif|pdf|webp))?$"
    return bool(regex.search(quality_format_re, quality_format_seg))
