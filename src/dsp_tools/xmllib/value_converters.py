from __future__ import annotations

import datetime
from typing import Any

import regex
from regex import Match

from dsp_tools.error.xmllib_warnings import MessageInfo
from dsp_tools.error.xmllib_warnings_util import emit_xmllib_input_warning
from dsp_tools.error.xmllib_warnings_util import raise_xmllib_input_error
from dsp_tools.xmllib.internal.checkers import is_date_internal
from dsp_tools.xmllib.internal.checkers import is_nonempty_value_internal
from dsp_tools.xmllib.models.config_options import NewlineReplacement
from dsp_tools.xmllib.models.date_formats import Calendar
from dsp_tools.xmllib.models.date_formats import DateFormat
from dsp_tools.xmllib.models.date_formats import Era


def convert_to_bool_string(value: Any) -> bool:
    """
    Turns a value into a bool string, suitable for an XML.
    It is case-insensitive, meaning that the words can also be capitalised.

    Accepted values:
         - `false`, `0`, `0.0`, `no`, `non`, `nein` -> `False`
         - `true`, `1`, `1.0`, `yes`, `oui`, `ja`, `sì` -> `True`

    Args:
        value: value to transform

    Returns:
        `True` or `False` if it is an accepted value.

    Raises:
        XmllibInputError: If the value is not convertable to a boolean

    Examples:
        ```python
        result = xmllib.convert_to_bool_string(1)
        # result == True
        ```

        ```python
        result = xmllib.convert_to_bool_string("nein")
        # result == False
        ```

        ```python
        result = xmllib.convert_to_bool_string(None)
        # raises XmllibInputError
        ```
    """
    str_val = str(value).lower().strip()
    if str_val in ("false", "0", "0.0", "no", "non", "nein"):
        return False
    elif str_val in ("true", "1", "1.0", "yes", "oui", "ja", "sì"):
        return True
    raise_xmllib_input_error(MessageInfo(f"The entered value '{value}' cannot be converted to a bool."))


def replace_newlines_with_tags(text: str, converter_option: NewlineReplacement) -> str:
    """
    Converts the newlines in a string to XML tags.

    Args:
        text: string to convert
        converter_option: specifies what tag to use instead of the newline

    Returns:
        String with replaced values

    Raises:
        XmllibInputError: If an invalid conversion option is given

    Examples:
        ```python
        result = xmllib.replace_newlines_with_tags(
            "Start\\nEnd", xmllib.NewlineReplacement.NONE
        )
        # result == "Start\\nEnd"
        ```

        ```python
        result = xmllib.replace_newlines_with_tags(
            "Start\\nEnd", xmllib.NewlineReplacement.LINEBREAK
        )
        # result == "Start<br/>End"
        ```

        ```python
        result = xmllib.replace_newlines_with_tags(
            "Start\\n\\nEnd", xmllib.NewlineReplacement.PARAGRAPH
        )
        # result == "<p>Start</p><p>End</p>"
        ```
    """
    match converter_option:
        case NewlineReplacement.NONE:
            return text
        case NewlineReplacement.LINEBREAK:
            return replace_newlines_with_br_tags(text)
        case NewlineReplacement.PARAGRAPH:
            return replace_newlines_with_paragraph_tags(text)


def replace_newlines_with_paragraph_tags(text: str) -> str:
    """
    Replace `Start\\nEnd` with `<p>Start</p><p>End</p>`

    Args:
        text: string to be formatted

    Returns:
        Formatted string with paragraph tags

    Examples:
        ```python
        result = xmllib.replace_newlines_with_paragraph_tags("Start\\nEnd")
        # result == "<p>Start</p><p>End</p>"
        ```

        ```python
        # multiple consecutive newlines will be treated as one newline

        result = xmllib.replace_newlines_with_paragraph_tags("Start\\n\\nEnd")
        # result == "<p>Start</p><p>End</p>"
        ```
    """
    splt = [x for x in text.split("\n") if x != ""]
    formatted = [f"<p>{x}</p>" for x in splt]
    return "".join(formatted)


def replace_newlines_with_br_tags(text: str) -> str:
    """
    Replaces `\\n` with `<br/>`

    Args:
        text: string to be formatted

    Returns:
        Formatted string with break-line tags

    Examples:
        ```python
        result = xmllib.replace_newlines_with_br_tags("Start\\nEnd")
        # result == "Start<br/>End"
        ```

        ```python
        # multiple consecutive newlines will be converted into multiple break-lines

        result = xmllib.replace_newlines_with_br_tags("Start\\n\\nEnd")
        # result == "Start<br/><br/>End"
        ```
    """
    return text.replace("\n", "<br/>")


def reformat_date(
    date: str | int,
    date_precision_separator: str | None,
    date_range_separator: str | None,
    date_format: DateFormat,
    calendar: Calendar = Calendar.GREGORIAN,
    era: Era | None = Era.CE,
    resource_id: str | None = None,
) -> str:
    """
    Reformats a date string into the DSP format.

    - If the input cannot be reformatted according to the configuration, or if the result
      is not a valid DSP date, a warning is emitted and the original input is returned.
    - If the input is empty, a warning is emitted and an empty string is returned.
    - If the input is already a correctly formatted DSP-date, the original input is returned.

    Args:
        date: date string to be reformatted
        date_precision_separator: the separation between the day, month and year
        date_range_separator: the separation between two dates
        date_format: the format of the date, see [`DateFormat` for options](https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-docs/date_formats/#xmllib.models.date_formats.DateFormat)
        calendar: the calendar of the date, see [`Calendar` for options](https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-docs/date_formats/#xmllib.models.date_formats.Calendar)
        era: the era of the date, see [`Era` for options](https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-docs/date_formats/#xmllib.models.date_formats.Era)
        resource_id: the ID of the associated resource, this is to improve the error message

    Returns:
        A reformatted date or the original input if the reformatted result is not a valid DSP date

    Examples:
        ```python
        # default configuration, starting with the day
        result = xmllib.reformat_date(
            date="1.11.2000",
            date_precision_separator=".",
            date_range_separator=None,
            date_format=xmllib.DateFormat.DD_MM_YYYY
        )
        # result == "GREGORIAN:CE:2000-11-1:CE:2000-11-1"
        ```

        ```python
        # default configuration, but starting with the year
        result = xmllib.reformat_date(
            date="2000.11.1",
            date_precision_separator=".",
            date_range_separator=None,
            date_format=xmllib.DateFormat.YYYY_MM_DD,
        )
        # result == "GREGORIAN:CE:2000-11-1:CE:2000-11-1"
        ```

        ```python
        # with a date range
        result = xmllib.reformat_date(
            date="1.11.2000-2001",
            date_precision_separator=".",
            date_range_separator="-",
            date_format=xmllib.DateFormat.DD_MM_YYYY,
        )
        # result == "GREGORIAN:CE:2000-11-1:CE:2001"
        ```

        ```python
        # islamic calendar, where eras are not allowed
        result = xmllib.reformat_date(
            date="1.11.2000",
            date_precision_separator=".",
            date_range_separator=None,
            date_format=xmllib.DateFormat.DD_MM_YYYY,
            calendar=xmllib.Calendar.ISLAMIC,
            era=None
        )
        # result == "ISLAMIC:2000-11-1:2000-11-1"
        ```

        ```python
        # with a different era
        result = xmllib.reformat_date(
            date="1.11.2000",
            date_precision_separator=".",
            date_range_separator="-",
            date_format=xmllib.DateFormat.DD_MM_YYYY,
            era=xmllib.Era.AD
        )
        # result == "GREGORIAN:AD:2000-11-1:AD:2000-11-1"
        ```

        ```python
        # reformatted date, no precision in the date string is required
        result = xmllib.reformat_date(
            date="2000",
            date_precision_separator=".",
            date_range_separator="-",
            date_format=xmllib.DateFormat.DD_MM_YYYY,
        )
        # result == "GREGORIAN:CE:2000:CE:2000"
        ```

        ```python
        # already correctly formatted date
        result = xmllib.reformat_date(
            date="GREGORIAN:CE:2000:CE:2000",
            date_precision_separator=".",
            date_range_separator="-",
            date_format=xmllib.DateFormat.DD_MM_YYYY,
        )
        # result == "GREGORIAN:CE:2000:CE:2000"
        ```

        ```python
        # invalid input: a warning is emitted and the original input is returned
        result = xmllib.reformat_date(
            date="not-a-date",
            date_precision_separator=".",
            date_range_separator="-",
            date_format=xmllib.DateFormat.DD_MM_YYYY,
        )
        # WARNING is emitted
        # result == "not-a-date"
        ```
    """
    if not is_nonempty_value_internal(date):
        msg_info = MessageInfo(
            "The date to be reformatted is empty. An empty string is returned.", resource_id=resource_id
        )
        emit_xmllib_input_warning(msg_info)
        return ""
    date = str(date).strip()
    invalid_date_info = MessageInfo(
        f"The provided date '{date}' does not conform to the expected format, the original value is returned.",
        resource_id=resource_id,
    )
    # Here we want to check if the input is already a reformatted date. In that case, we would expect a calendar.
    # The function that checks if an input is a valid date does not require a calendar,
    # so unformatted input for example, '2000' may be accepted as a valid date.
    if regex.search(r"(GREGORIAN|JULIAN|ISLAMIC)", date):
        if is_date_internal(date):
            return date
        else:
            emit_xmllib_input_warning(invalid_date_info)
            return date
    if date_precision_separator and date_range_separator:
        if date_precision_separator == date_range_separator:
            msg_info = MessageInfo(
                f"The precision separator and range separator provided are identical: '{date_precision_separator}'. "
                f"This is not allowed.",
                resource_id=resource_id,
            )
            raise_xmllib_input_error(msg_info)
    if date_range_separator is not None:
        date_split = [found for x in date.split(date_range_separator) if (found := x.strip())]
    else:
        date_split = [date.strip()]
    all_dates = [_reformat_single_date(x, date_precision_separator, date_format, resource_id) for x in date_split]
    if era:
        all_dates = [f"{era.value}:{x}" for x in all_dates]
    if len(all_dates) == 1:
        all_dates.append(all_dates[0])
    reformatted_str = ":".join(all_dates)
    if calendar:
        reformatted_str = f"{calendar.value}:{reformatted_str}"
    if is_date_internal(reformatted_str):
        return reformatted_str
    emit_xmllib_input_warning(invalid_date_info)
    return date


def _reformat_single_date(  # noqa: PLR0911 Too many return statements
    single_date: str, date_precision_separator: str | None, date_format: DateFormat, resource_id: str | None
) -> str:
    if date_precision_separator is None:
        return single_date
    date_split = [found for x in single_date.split(date_precision_separator) if (found := x.strip())]
    if date_format == DateFormat.YYYY_MM_DD:
        return "-".join(date_split)
    if date_format == DateFormat.DD_MM_YYYY:
        return "-".join(reversed(date_split))
    if date_format == DateFormat.MM_DD_YYYY:
        if len(date_split) == 3:
            month, day, year = date_split
            return f"{year}-{month}-{day}"
        if len(date_split) == 2:
            return "-".join(reversed(date_split))
        if len(date_split) == 1:
            return date_split.pop()
        else:
            msg_info = MessageInfo(
                f"The provided input of a single date '{single_date}' could not be reformatted correctly.",
                resource_id=resource_id,
            )
            emit_xmllib_input_warning(msg_info)
            return single_date
    msg_info = MessageInfo(
        f"The provided date format '{date_format}' to reformat the date is invalid.",
        resource_id=resource_id,
    )
    raise_xmllib_input_error(msg_info)


def find_dates_in_string(string: str) -> set[str]:
    """
    Checks if a string contains date values (single dates, or date ranges),
    and return all found dates as set of DSP-formatted strings.
    Returns an empty set if no date was found.
    [See XML documentation for details](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#date).

    Notes:
        - If no era or calendar is given, dates are interpreted in the Common Era and the Gregorian calendar.
        - Standalone numbers from 000-2999, in 3/4-digit form, are interpreted as years CE.
        - If a number (with any number of digits) is followed by CE, C.E., AD, A.D., it is interpreted as years CE.
        - If a number (with any number of digits) is followed by BCE, BC, B.C., B.C.E., av. J.-C.,
          it is interpreted as years BCE.
        - Dates written with slashes are always interpreted in a European manner: 5/11/2021 is the 5th of November.
        - In the European notation, 2-digit years are expanded to 4 digits, with the current year as watershed:
            - 30.4.24 -> 30.04.2024
            - 30.4.50 -> 30.04.1950

    Currently supported date formats:
        - 0476-09-04 -> GREGORIAN:CE:0476-09-04:CE:0476-09-04
        - 0476_09_04 -> GREGORIAN:CE:0476-09-04:CE:0476-09-04
        - 30.4.2021 -> GREGORIAN:CE:2021-04-30:CE:2021-04-30
        - 30.4.21 -> GREGORIAN:CE:2021-04-30:CE:2021-04-30
        - 5/11/2021 -> GREGORIAN:CE:2021-11-05:CE:2021-11-05
        - Jan 26, 1993 -> GREGORIAN:CE:1993-01-26:CE:1993-01-26
        - 26 Jan 1993 -> GREGORIAN:CE:1993-01-26:CE:1993-01-26
        - 26 January 1993 -> GREGORIAN:CE:1993-01-26:CE:1993-01-26
        - 26. Jan. 1993 -> GREGORIAN:CE:1993-01-26:CE:1993-01-26
        - 26. Januar 1993 -> GREGORIAN:CE:1993-01-26:CE:1993-01-26
        - 28.2.-1.12.1515 -> GREGORIAN:CE:1515-02-28:CE:1515-12-01
        - 25.-26.2.0800 -> GREGORIAN:CE:0800-02-25:CE:0800-02-26
        - 1.9.2022-3.1.2024 -> GREGORIAN:CE:2022-09-01:CE:2024-01-03
        - 1848 -> GREGORIAN:CE:1848:CE:1848
        - 1849/1850 -> GREGORIAN:CE:1849:CE:1850
        - 1849/50 -> GREGORIAN:CE:1849:CE:1850
        - 1845-50 -> GREGORIAN:CE:1845:CE:1850
        - 840-50 -> GREGORIAN:CE:840:CE:850
        - 840-1 -> GREGORIAN:CE:840:CE:841
        - 9 BC / 9 B.C. / 9 B.C.E. / 9 BCE -> GREGORIAN:BC:9:BC:9
        - 20 BCE - 50 CE -> GREGORIAN:BC:20:CE:50
        - 1000-900 av. J.-C. -> GREGORIAN:BC:1000:BC:900
        - 45 av. J.-C. -> GREGORIAN:BC:45:BC:45

    Args:
        string: string to check

    Returns:
        (possibly empty) set of DSP-formatted date strings

    Examples:
        ```python
        result = xmllib.find_dates_in_string("1849/1850")
        # result == {"GREGORIAN:CE:1849:CE:1850"}
        ```

        ```python
        result = xmllib.find_dates_in_string("not a valid date")
        # result == {}
        ```

        ```python
        result = xmllib.find_dates_in_string("first date: 2024. Second: 2025.")
        # result == {"GREGORIAN:CE:2024:CE:2024", "GREGORIAN:CE:2025:CE:2025"}
        ```
    """

    # sanitise input, just in case that the function was called on an empty or N/A cell
    if not is_nonempty_value_internal(string):
        return set()
    return _find_dates_in_string(string)


_months_dict = {
    "January": 1,
    "Januar": 1,
    "Jan": 1,
    "February": 2,
    "Februar": 2,
    "Feb": 2,
    "March": 3,
    "März": 3,
    "Mar": 3,
    "April": 4,
    "Apr": 4,
    "May": 5,
    "Mai": 5,
    "June": 6,
    "Juni": 6,
    "Jun": 6,
    "July": 7,
    "Juli": 7,
    "Jul": 7,
    "August": 8,
    "Aug": 8,
    "September": 9,
    "Sept": 9,
    "October": 10,
    "Oktober": 10,
    "Oct": 10,
    "Okt": 10,
    "November": 11,
    "Nov": 11,
    "December": 12,
    "Dezember": 12,
    "Dec": 12,
    "Dez": 12,
}
all_months = "|".join(_months_dict)


def _find_dates_in_string(string: str) -> set[str]:
    year_regex = r"([0-2]?[0-9][0-9][0-9])"
    year_regex_2_or_4_digits = r"((?:[0-2]?[0-9])?[0-9][0-9])"
    month_regex = r"([0-1]?[0-9])"
    day_regex = r"([0-3]?[0-9])"
    sep_regex = r"[\./]"
    lookbehind = r"(?<![0-9A-Za-z])"
    lookahead = r"(?![0-9A-Za-z])"
    range_operator_regex = r" ?- ?"

    remaining_string = string
    results: set[str | None] = set()

    remaining_string = _extract_already_parsed_date(remaining_string, results)

    remaining_string = _find_english_BC_or_CE_dates(
        string=remaining_string,
        lookbehind=lookbehind,
        lookahead=lookahead,
        range_operator_regex=range_operator_regex,
        results=results,
    )

    remaining_string = _find_french_bc_dates(
        string=remaining_string,
        lookbehind=lookbehind,
        lookahead=lookahead,
        range_operator_regex=range_operator_regex,
        results=results,
    )

    # template: 2021-01-01 | 2015_01_02
    iso_dates_regex = rf"{lookbehind}{year_regex}[_-]([0-1][0-9])[_-]([0-3][0-9]){lookahead}"
    if iso_dates := list(regex.finditer(iso_dates_regex, remaining_string)):
        results.update(_from_iso_date(x) for x in iso_dates)
        remaining_string = _remove_used_spans(remaining_string, [x.span() for x in iso_dates])

    # template: 6.-8.3.1948 | 6/2/1947 - 24.03.1948
    eur_date_range_regex = (
        rf"{lookbehind}"
        rf"{day_regex}{sep_regex}(?:{month_regex}{sep_regex}{year_regex_2_or_4_digits}?)?{range_operator_regex}"
        rf"{day_regex}{sep_regex}{month_regex}{sep_regex}{year_regex_2_or_4_digits}"
        rf"{lookahead}"
    )
    if eur_date_ranges := list(regex.finditer(eur_date_range_regex, remaining_string)):
        results.update(_from_eur_date_range(x) for x in eur_date_ranges)
        remaining_string = _remove_used_spans(remaining_string, [x.span() for x in eur_date_ranges])

    # template: 1.4.2021 | 5/11/2021
    eur_date_regex = rf"{lookbehind}{day_regex}{sep_regex}{month_regex}{sep_regex}{year_regex_2_or_4_digits}{lookahead}"
    if eur_dates := list(regex.finditer(eur_date_regex, remaining_string)):
        results.update(_from_eur_date(x) for x in eur_dates)
        remaining_string = _remove_used_spans(remaining_string, [x.span() for x in eur_dates])

    # template: March 9, 1908 | March5,1908 | May 11, 1906
    monthname_date_regex = rf"{lookbehind}({all_months}) ?{day_regex}, ?{year_regex}{lookahead}"
    if monthname_dates := list(regex.finditer(monthname_date_regex, remaining_string)):
        results.update(_from_monthname_date(x) for x in monthname_dates)
        remaining_string = _remove_used_spans(remaining_string, [x.span() for x in monthname_dates])

    # template: 9 March 1908
    monthname_after_day_regex = rf"{lookbehind}{day_regex} ?({all_months}) ?{year_regex}{lookahead}"
    if monthname_after_days := list(regex.finditer(monthname_after_day_regex, remaining_string)):
        results.update(_from_monthname_after_day(x) for x in monthname_after_days)
        remaining_string = _remove_used_spans(remaining_string, [x.span() for x in monthname_after_days])

    # template: 26. Januar 1993 | 26. Jan. 1993 | 26. Jan 1993
    german_monthname_date_regex = rf"{lookbehind}{day_regex}\.? ?({all_months})\.? ?{year_regex}{lookahead}"
    if german_monthname_dates := list(regex.finditer(german_monthname_date_regex, remaining_string)):
        results.update(_from_german_monthname_date(x) for x in german_monthname_dates)
        remaining_string = _remove_used_spans(remaining_string, [x.span() for x in german_monthname_dates])

    # template: 1849/50 | 1849-50 | 1849/1850
    if year_ranges := list(regex.finditer(lookbehind + year_regex + r"[/-](\d{1,4})" + lookahead, remaining_string)):
        results.update(_from_year_range(x) for x in year_ranges)
        remaining_string = _remove_used_spans(remaining_string, [x.span() for x in year_ranges])

    # template: 1907
    if year_onlies := list(regex.finditer(rf"{lookbehind}{year_regex}{lookahead}", remaining_string)):
        results.update(f"GREGORIAN:CE:{int(x.group(0))}:CE:{int(x.group(0))}" for x in year_onlies)
        remaining_string = _remove_used_spans(remaining_string, [x.span() for x in year_onlies])

    return {x for x in results if x}


def _remove_used_spans(string: str, spans: list[tuple[int, int]]) -> str:
    """Once a regex has matched parts of the original string, remove these parts, so that they're not matched again."""
    for start, end in reversed(spans):
        string = string[:start] + string[end:]
    return string


def _find_english_BC_or_CE_dates(
    string: str,
    lookbehind: str,
    lookahead: str,
    range_operator_regex: str,
    results: set[str | None],
) -> str:
    eraless_date_regex = r"(\d+)"
    bc_era_regex = r"(?:BC|BCE|B\.C\.|B\.C\.E\.)"
    bc_date_regex = rf"(?:{eraless_date_regex} ?{bc_era_regex})"
    ce_era_regex = r"(?:CE|AD|C\.E\.|A\.D\.)"
    ce_date_regex = rf"(?:{eraless_date_regex} ?{ce_era_regex})"
    bc_or_ce_date_regex = rf"(?:{bc_date_regex}|{ce_date_regex})"

    remaining_string = string
    results_new: set[str | None] = set()

    range_regex = (
        rf"{lookbehind}(?:{bc_or_ce_date_regex}|{eraless_date_regex})"
        rf"{range_operator_regex}"
        rf"{bc_or_ce_date_regex}{lookahead}"
    )
    if matchs := list(regex.finditer(range_regex, remaining_string)):
        results_new.update(
            _from_english_BC_or_CE_range(
                string=x.group(0),
                range_operator_regex=range_operator_regex,
                bc_era_regex=bc_era_regex,
                ce_era_regex=ce_era_regex,
                eraless_date_regex=eraless_date_regex,
            )
            for x in matchs
        )
        remaining_string = _remove_used_spans(remaining_string, [x.span() for x in matchs])

    if matchs := list(regex.finditer(rf"{lookbehind}{bc_date_regex}{lookahead}", remaining_string)):
        results_new.update({f"GREGORIAN:BC:{x.group(1)}:BC:{x.group(1)}" for x in matchs})
        remaining_string = _remove_used_spans(remaining_string, [x.span() for x in matchs])

    if matchs := list(regex.finditer(rf"{lookbehind}{ce_date_regex}{lookahead}", remaining_string)):
        results_new.update({f"GREGORIAN:CE:{x.group(1)}:CE:{x.group(1)}" for x in matchs})
        remaining_string = _remove_used_spans(remaining_string, [x.span() for x in matchs])

    results.update({x for x in results_new if x})
    return remaining_string


def _from_english_BC_or_CE_range(
    string: str, range_operator_regex: str, bc_era_regex: str, ce_era_regex: str, eraless_date_regex: str
) -> str | None:
    split_result = regex.split(range_operator_regex, string)
    if len(split_result) != 2:
        return None
    start_raw, end_raw = split_result
    if regex.search(bc_era_regex, end_raw):
        end_era = "BC"
    elif regex.search(ce_era_regex, end_raw):
        end_era = "CE"
    else:
        return None

    if regex.search(bc_era_regex, start_raw):
        start_era = "BC"
    elif regex.search(ce_era_regex, start_raw):
        start_era = "CE"
    else:
        start_era = end_era

    if not (start_year_match := regex.search(eraless_date_regex, start_raw)):
        return None
    if not (end_year_match := regex.search(eraless_date_regex, end_raw)):
        return None

    return f"GREGORIAN:{start_era}:{start_year_match.group(0)}:{end_era}:{end_year_match.group(0)}"


def _find_french_bc_dates(
    string: str,
    lookbehind: str,
    lookahead: str,
    range_operator_regex: str,
    results: set[str | None],
) -> str:
    remaining_string = string
    results_new: set[str | None] = set()
    french_bc_regex = r"av(?:\. |\.| )J\.?-?C\.?"

    year_regex = r"\d{1,5}"
    year_range_regex = rf"{lookbehind}({year_regex}){range_operator_regex}({year_regex}) {french_bc_regex}{lookahead}"
    for year_range in reversed(list(regex.finditer(year_range_regex, remaining_string))):
        start_year = int(year_range.group(1))
        end_year = int(year_range.group(2))
        if end_year > start_year:
            continue
        results_new.add(f"GREGORIAN:BC:{start_year}:BC:{end_year}")
        remaining_string = _remove_used_spans(remaining_string, [year_range.span()])

    single_year_regex = rf"{lookbehind}({year_regex}) {french_bc_regex}{lookahead}"
    for single_year in reversed(list(regex.finditer(single_year_regex, remaining_string))):
        start_year = int(single_year.group(1))
        results_new.add(f"GREGORIAN:BC:{start_year}:BC:{start_year}")
        remaining_string = _remove_used_spans(remaining_string, [single_year.span()])

    results.update({x for x in results_new if x})
    return remaining_string


def _from_iso_date(iso_date: Match[str]) -> str | None:
    year = int(iso_date.group(1))
    month = int(iso_date.group(2))
    day = int(iso_date.group(3))
    try:
        date = datetime.date(year, month, day)
        return f"GREGORIAN:CE:{date.isoformat()}:CE:{date.isoformat()}"
    except ValueError:
        return None


def _expand_2_digit_year(year: int) -> int:
    current_year = datetime.date.today().year - 2000
    if year <= current_year:
        return year + 2000
    elif year <= 99:
        return year + 1900
    else:
        return year


def _from_eur_date_range(eur_date_range: Match[str]) -> str | None:
    startday = int(eur_date_range.group(1))
    startmonth = int(eur_date_range.group(2)) if eur_date_range.group(2) else int(eur_date_range.group(5))
    startyear = int(eur_date_range.group(3)) if eur_date_range.group(3) else int(eur_date_range.group(6))
    startyear = _expand_2_digit_year(startyear)
    endday = int(eur_date_range.group(4))
    endmonth = int(eur_date_range.group(5))
    endyear = int(eur_date_range.group(6))
    endyear = _expand_2_digit_year(endyear)
    try:
        startdate = datetime.date(startyear, startmonth, startday)
        enddate = datetime.date(endyear, endmonth, endday)
    except ValueError:
        return None
    if enddate < startdate:
        return None
    return f"GREGORIAN:CE:{startdate.isoformat()}:CE:{enddate.isoformat()}"


def _from_eur_date(eur_date: Match[str]) -> str | None:
    startday = int(eur_date.group(1))
    startmonth = int(eur_date.group(2))
    startyear = int(eur_date.group(3))
    startyear = _expand_2_digit_year(startyear)
    try:
        date = datetime.date(startyear, startmonth, startday)
        return f"GREGORIAN:CE:{date.isoformat()}:CE:{date.isoformat()}"
    except ValueError:
        return None


def _from_monthname_date(monthname_date: Match[str]) -> str | None:
    day = int(monthname_date.group(2))
    month = _months_dict[monthname_date.group(1)]
    year = int(monthname_date.group(3))
    try:
        date = datetime.date(year, month, day)
        return f"GREGORIAN:CE:{date.isoformat()}:CE:{date.isoformat()}"
    except ValueError:
        return None


def _from_monthname_after_day(monthname_after_day: Match[str]) -> str | None:
    day = int(monthname_after_day.group(1))
    month = _months_dict[monthname_after_day.group(2)]
    year = int(monthname_after_day.group(3))
    try:
        date = datetime.date(year, month, day)
        return f"GREGORIAN:CE:{date.isoformat()}:CE:{date.isoformat()}"
    except ValueError:
        return None


def _from_german_monthname_date(german_monthname_date: Match[str]) -> str | None:
    day = int(german_monthname_date.group(1))
    month = _months_dict[german_monthname_date.group(2)]
    year = int(german_monthname_date.group(3))
    try:
        date = datetime.date(year, month, day)
        return f"GREGORIAN:CE:{date.isoformat()}:CE:{date.isoformat()}"
    except ValueError:
        return None


def _from_year_range(year_range: Match[str]) -> str | None:
    startyear = int(year_range.group(1))
    endyear = int(year_range.group(2))
    if endyear // 10 == 0:
        # endyear is only 1-digit: add the first 2-3 digits of startyear
        endyear = startyear // 10 * 10 + endyear
    elif endyear // 100 == 0:
        # endyear is only 2-digit: add the first 1-2 digits of startyear
        endyear = startyear // 100 * 100 + endyear
    if endyear <= startyear:
        return None
    return f"GREGORIAN:CE:{startyear}:CE:{endyear}"


def _extract_already_parsed_date(string: str, results: set[str | None]) -> str:
    rgx_year = r"\d+(-\d{2}(-\d{2})?)?"
    era_with_colon = r"(CE:|BC:)"
    rgx = rf"(GREGORIAN|JULIAN|ISLAMIC):{era_with_colon}{rgx_year}:{era_with_colon}?{rgx_year}"
    if matchs := list(regex.finditer(rgx, string)):
        results.update({x.group(0) for x in matchs})
        remaining_string = _remove_used_spans(string, [x.span() for x in matchs])
        return remaining_string
    return string
