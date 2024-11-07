import datetime
import json
import uuid
from typing import Any
from typing import Iterable

import regex
from regex import Match

from dsp_tools.models.exceptions import InputError
from dsp_tools.xmllib.value_checkers import is_nonempty_value


def create_label_to_name_list_node_mapping(
    project_json_path: str,
    list_name: str,
    language_of_label: str,
) -> dict[str, str]:
    """
    Often, data sources contain list values named after the "label" of the JSON project list node, instead of the "name"
    which is needed for the `dsp-tools xmlupload`.
    To create a correct XML, you need a dictionary that maps the "labels" to their correct "names".

    Args:
        project_json_path: path to a JSON project file (a.k.a. ontology)
        list_name: name of a list in the JSON project
        language_of_label: which language of the label to choose

    Returns:
        a dictionary of the form {label: name}
    """
    with open(project_json_path, encoding="utf-8") as f:
        json_file = json.load(f)
    json_subset = [x for x in json_file["project"]["lists"] if x["name"] == list_name]
    # json_subset is a list containing one item, namely the json object containing the entire json-list
    res = {}
    for label, name in _name_label_mapper_iterator(json_subset, language_of_label):
        if name != list_name:
            res[label] = name
            res[label.strip().lower()] = name
    return res


def _name_label_mapper_iterator(
    json_subset: list[dict[str, Any]],
    language_of_label: str,
) -> Iterable[tuple[str, str]]:
    """
    Go through list nodes of a JSON project and yield (label, name) pairs.

    Args:
        json_subset: list of DSP lists (a DSP list being a dictionary with the keys "name", "labels" and "nodes")
        language_of_label: which language of the label to choose

    Yields:
        (label, name) pairs
    """
    for node in json_subset:
        # node is the json object containing the entire json-list
        if "nodes" in node:
            # "nodes" is the json sub-object containing the entries of the json-list
            yield from _name_label_mapper_iterator(node["nodes"], language_of_label)
            # each yielded value is a (label, name) pair of a single list entry
        if "name" in node:
            yield node["labels"][language_of_label], node["name"]
            # the actual values of the name and the label


def escape_reserved_xml_characters(text: str) -> str:
    """
    From richtext strings (encoding="xml"), escape the reserved characters `<`, `>` and `&`,
    but only if they are not part of a standard standoff tag or escape sequence.

    [See the documentation for the standard standoff tags allowed by DSP-API,
    which will not be escaped.](https://docs.dasch.swiss/latest/DSP-API/03-endpoints/api-v2/text/standard-standoff/)

    Args:
        text: the richtext string to be escaped

    Returns:
        The escaped richtext string
    """
    allowed_tags = [
        "a( [^>]+)?",  # <a> is the only tag that can have attributes
        "p",
        "em",
        "strong",
        "u",
        "sub",
        "sup",
        "strike",
        "h1",
        "ol",
        "ul",
        "li",
        "tbody",
        "table",
        "tr",
        "td",
        "br",
        "hr",
        "pre",
        "cite",
        "blockquote",
        "code",
    ]
    allowed_tags_regex = "|".join(allowed_tags)
    lookahead = rf"(?!/?({allowed_tags_regex})/?>)"
    illegal_lt = rf"<{lookahead}"
    lookbehind = rf"(?<!</?({allowed_tags_regex})/?)"
    illegal_gt = rf"{lookbehind}>"
    illegal_amp = r"&(?![#a-zA-Z0-9]+;)"
    text = regex.sub(illegal_lt, "&lt;", text)
    text = regex.sub(illegal_gt, "&gt;", text)
    text = regex.sub(illegal_amp, "&amp;", text)
    return text


def find_date_in_string(string: str) -> str | None:
    """
    Checks if a string contains a date value (single date, or date range),
    and returns the first found date as DSP-formatted string,
    [see XML documentation for details](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#date)
    Returns None if no date was found.

    Notes:
        - All dates are interpreted in the Christian era and the Gregorian calendar.
        - BC dates are only supported in French notation (e.g. 1000-900 av. J.-C.).
        - The years 0000-2999 are supported, in 3/4-digit form.
        - Dates written with slashes are always interpreted in a European manner: 5/11/2021 is the 5th of November.
        - In the European notation, 2-digit years are expanded to 4 digits, with the current year as watershed:
            - 30.4.24 -> 30.04.2024
            - 30.4.25 -> 30.04.1925

    Currently supported date formats:
        - 0476-09-04 -> GREGORIAN:CE:0476-09-04:CE:0476-09-04
        - 0476_09_04 -> GREGORIAN:CE:0476-09-04:CE:0476-09-04
        - 30.4.2021 -> GREGORIAN:CE:2021-04-30:CE:2021-04-30
        - 30.4.21 -> GREGORIAN:CE:2021-04-30:CE:2021-04-30
        - 5/11/2021 -> GREGORIAN:CE:2021-11-05:CE:2021-11-05
        - Jan 26, 1993 -> GREGORIAN:CE:1993-01-26:CE:1993-01-26
        - 28.2.-1.12.1515 -> GREGORIAN:CE:1515-02-28:CE:1515-12-01
        - 25.-26.2.0800 -> GREGORIAN:CE:0800-02-25:CE:0800-02-26
        - 1.9.2022-3.1.2024 -> GREGORIAN:CE:2022-09-01:CE:2024-01-03
        - 1848 -> GREGORIAN:CE:1848:CE:1848
        - 1849/1850 -> GREGORIAN:CE:1849:CE:1850
        - 1849/50 -> GREGORIAN:CE:1849:CE:1850
        - 1845-50 -> GREGORIAN:CE:1845:CE:1850
        - 840-50 -> GREGORIAN:CE:840:CE:850
        - 840-1 -> GREGORIAN:CE:840:CE:841
        - 1000-900 av. J.-C. -> GREGORIAN:BC:1000:BC:900
        - 45 av. J.-C. -> GREGORIAN:BC:45:BC:45

    Args:
        string: string to check

    Returns:
        DSP-formatted date string, or None
    """

    # sanitise input, just in case that the method was called on an empty or N/A cell
    if not is_nonempty_value(string):
        return None
    try:
        return _find_date_in_string_throwing(string)
    except ValueError:
        return None


_months_dict = {
    "January": 1,
    "Jan": 1,
    "February": 2,
    "Feb": 2,
    "March": 3,
    "Mar": 3,
    "April": 4,
    "Apr": 4,
    "May": 5,
    "June": 6,
    "Jun": 6,
    "July": 7,
    "Jul": 7,
    "August": 8,
    "Aug": 8,
    "September": 9,
    "Sept": 9,
    "October": 10,
    "Oct": 10,
    "November": 11,
    "Nov": 11,
    "December": 12,
    "Dec": 12,
}


def _find_date_in_string_throwing(string: str) -> str | None:
    """
    This function is the same as find_date_in_string(), but may raise a ValueError instead of returning None.
    """
    year_regex = r"([0-2]?[0-9][0-9][0-9])"
    year_regex_2_or_4_digits = r"((?:[0-2]?[0-9])?[0-9][0-9])"
    month_regex = r"([0-1]?[0-9])"
    day_regex = r"([0-3]?[0-9])"
    sep_regex = r"[\./]"
    lookbehind = r"(?<![0-9A-Za-z])"
    lookahead = r"(?![0-9A-Za-z])"

    if french_bc_date := _find_french_bc_date(string=string, lookbehind=lookbehind, lookahead=lookahead):
        return french_bc_date

    # template: 2021-01-01 | 2015_01_02
    iso_date = regex.search(rf"{lookbehind}{year_regex}[_-]([0-1][0-9])[_-]([0-3][0-9]){lookahead}", string)

    # template: 6.-8.3.1948 | 6/2/1947 - 24.03.1948
    eur_date_range_regex = (
        rf"{lookbehind}"
        rf"{day_regex}{sep_regex}(?:{month_regex}{sep_regex}{year_regex_2_or_4_digits}?)? ?(?:-|:|to) ?"
        rf"{day_regex}{sep_regex}{month_regex}{sep_regex}{year_regex_2_or_4_digits}"
        rf"{lookahead}"
    )
    eur_date_range = regex.search(eur_date_range_regex, string)

    # template: 1.4.2021 | 5/11/2021
    eur_date_regex = rf"{lookbehind}{day_regex}{sep_regex}{month_regex}{sep_regex}{year_regex_2_or_4_digits}{lookahead}"
    eur_date = regex.search(
        eur_date_regex,
        string,
    )

    # template: March 9, 1908 | March5,1908 | May 11, 1906
    all_months = "|".join(_months_dict)
    monthname_date_regex = rf"{lookbehind}({all_months}) ?{day_regex}, ?{year_regex}{lookahead}"
    monthname_date = regex.search(monthname_date_regex, string)

    # template: 1849/50 | 1849-50 | 1849/1850
    year_range = regex.search(lookbehind + year_regex + r"[/-](\d{1,4})" + lookahead, string)

    # template: 1907
    year_only = regex.search(rf"{lookbehind}{year_regex}{lookahead}", string)

    res: str | None = None
    if iso_date:
        res = _from_iso_date(iso_date)
    elif eur_date_range:
        res = _from_eur_date_range(eur_date_range)
    elif eur_date:
        res = _from_eur_date(eur_date)
    elif monthname_date:
        res = _from_monthname_date(monthname_date)
    elif year_range:
        res = _from_year_range(year_range)
    elif year_only:
        year = int(year_only.group(0))
        res = f"GREGORIAN:CE:{year}:CE:{year}"
    return res


def _find_french_bc_date(
    string: str,
    lookbehind: str,
    lookahead: str,
) -> str | None:
    french_bc_regex = r"av(?:\. |\.| )J\.?-?C\.?"
    if not regex.search(french_bc_regex, string):
        return None

    year_regex = r"\d{1,5}"
    sep_regex = r" ?- ?"

    year_range_regex = rf"{lookbehind}({year_regex}){sep_regex}({year_regex}) {french_bc_regex}{lookahead}"
    year_range = regex.search(year_range_regex, string)
    if year_range:
        start_year = int(year_range.group(1))
        end_year = int(year_range.group(2))
        if end_year > start_year:
            return None
        return f"GREGORIAN:BC:{start_year}:BC:{end_year}"

    single_year_regex = rf"{lookbehind}({year_regex}) {french_bc_regex}{lookahead}"
    single_year = regex.search(single_year_regex, string)
    if single_year:
        start_year = int(single_year.group(1))
        return f"GREGORIAN:BC:{start_year}:BC:{start_year}"

    return None


def _from_iso_date(iso_date: Match[str]) -> str:
    year = int(iso_date.group(1))
    month = int(iso_date.group(2))
    day = int(iso_date.group(3))
    date = datetime.date(year, month, day)
    return f"GREGORIAN:CE:{date.isoformat()}:CE:{date.isoformat()}"


def _expand_2_digit_year(year: int) -> int:
    current_year = datetime.date.today().year - 2000
    if year <= current_year:
        return year + 2000
    elif year <= 99:
        return year + 1900
    else:
        return year


def _from_eur_date_range(eur_date_range: Match[str]) -> str:
    startday = int(eur_date_range.group(1))
    startmonth = int(eur_date_range.group(2)) if eur_date_range.group(2) else int(eur_date_range.group(5))
    startyear = int(eur_date_range.group(3)) if eur_date_range.group(3) else int(eur_date_range.group(6))
    startyear = _expand_2_digit_year(startyear)
    endday = int(eur_date_range.group(4))
    endmonth = int(eur_date_range.group(5))
    endyear = int(eur_date_range.group(6))
    endyear = _expand_2_digit_year(endyear)
    startdate = datetime.date(startyear, startmonth, startday)
    enddate = datetime.date(endyear, endmonth, endday)
    if enddate < startdate:
        raise ValueError
    return f"GREGORIAN:CE:{startdate.isoformat()}:CE:{enddate.isoformat()}"


def _from_eur_date(eur_date: Match[str]) -> str:
    startday = int(eur_date.group(1))
    startmonth = int(eur_date.group(2))
    startyear = int(eur_date.group(3))
    startyear = _expand_2_digit_year(startyear)
    date = datetime.date(startyear, startmonth, startday)
    return f"GREGORIAN:CE:{date.isoformat()}:CE:{date.isoformat()}"


def _from_monthname_date(monthname_date: Match[str]) -> str:
    day = int(monthname_date.group(2))
    month = _months_dict[monthname_date.group(1)]
    year = int(monthname_date.group(3))
    date = datetime.date(year, month, day)
    return f"GREGORIAN:CE:{date.isoformat()}:CE:{date.isoformat()}"


def _from_year_range(year_range: Match[str]) -> str:
    startyear = int(year_range.group(1))
    endyear = int(year_range.group(2))
    if endyear // 10 == 0:
        # endyear is only 1-digit: add the first 2-3 digits of startyear
        endyear = startyear // 10 * 10 + endyear
    elif endyear // 100 == 0:
        # endyear is only 2-digit: add the first 1-2 digits of startyear
        endyear = startyear // 100 * 100 + endyear
    if endyear <= startyear:
        raise ValueError
    return f"GREGORIAN:CE:{startyear}:CE:{endyear}"


def make_xsd_compatible_id(input_value: str | float | int) -> str:
    """
    An xsd:ID may not contain all types of special characters,
    and it must start with a letter or underscore.
    Replace illegal characters with "_", and prepend a leading "_" if necessary.

    The string must contain at least one Unicode letter (matching the regex ``\\p{L}``),
    _, !, ?, or number, but must not be `None`, `<NA>`, `N/A`, or `-`.

    Args:
        input_value: input value

    Raises:
        InputError: if the input cannot be transformed to an xsd:ID

    Returns:
        An xsd ID compatible string based on the input value
    """
    if not is_nonempty_value(input_value):
        raise InputError(f"The input '{input_value}' cannot be transformed to an xsd:ID")
    # if the start of string is neither letter nor underscore, add an underscore
    res = regex.sub(r"^(?=[^A-Za-z_])", "_", str(input_value))
    # replace all illegal characters by underscore
    res = regex.sub(r"[^\w_\-.]", "_", res, flags=regex.ASCII)
    return res


def make_xsd_compatible_id_with_uuid(input_value: str | float | int) -> str:
    """
    An xsd:ID may not contain all types of special characters,
    and it must start with a letter or underscore.
    Replace illegal characters with "_", and prepend a leading "_" if necessary.
    Additionally, add a UUID at the end.
    The UUID will be different each time the function is called.

    The string must contain at least one Unicode letter (matching the regex ``\\p{L}``),
    _, !, ?, or number, but must not be `None`, `<NA>`, `N/A`, or `-`.

    Args:
        input_value: input value

    Raises:
        InputError: if the input cannot be transformed to an xsd:ID

    Returns:
        an xsd ID based on the input value, with a UUID attached.
    """
    res = make_xsd_compatible_id(input_value)
    _uuid = uuid.uuid4()
    res = f"{res}_{_uuid}"
    return res
