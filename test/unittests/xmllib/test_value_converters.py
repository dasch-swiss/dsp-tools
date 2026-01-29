import datetime
import warnings
from typing import Any

import pandas as pd
import pytest
import regex

from dsp_tools.xmllib.internal.exceptions import XmllibInputError
from dsp_tools.xmllib.internal.xmllib_warnings import XmllibInputWarning
from dsp_tools.xmllib.models.config_options import NewlineReplacement
from dsp_tools.xmllib.models.date_formats import Calendar
from dsp_tools.xmllib.models.date_formats import DateFormat
from dsp_tools.xmllib.models.date_formats import Era
from dsp_tools.xmllib.value_converters import convert_to_bool_string
from dsp_tools.xmllib.value_converters import find_dates_in_string
from dsp_tools.xmllib.value_converters import reformat_date
from dsp_tools.xmllib.value_converters import replace_newlines_with_tags


@pytest.mark.parametrize("val", ["false", "0  ", "  0.0", "NO", False, "non", "nein"])
def test_convert_to_bool_false(val: Any) -> None:
    assert convert_to_bool_string(val) == False  # noqa: E712 (Avoid equality comparisons to `False`)


@pytest.mark.parametrize("val", ["TRUE ", "  1", "1.0", "Yes", True, "ouI", "JA", "sì"])
def test_convert_to_bool_true(val: Any) -> None:
    assert convert_to_bool_string(val) == True  # noqa: E712 (Avoid equality comparisons to `True`)


@pytest.mark.parametrize("val", [pd.NA, None, 2.421, 10, "other", "  "])
def test_convert_to_bool_failure(val: Any) -> None:
    with pytest.raises(XmllibInputError):
        convert_to_bool_string(val)


def test_replace_newlines_with_tags_none() -> None:
    text = "Start\nMiddle\n\nFinal"
    result = replace_newlines_with_tags(text, NewlineReplacement.NONE)
    assert result == text


def test_replace_newlines_with_tags_newline() -> None:
    text = "Start\nMiddle\n\nFinal"
    result = replace_newlines_with_tags(text, NewlineReplacement.LINEBREAK)
    assert result == "Start<br/>Middle<br/><br/>Final"


def test_replace_newlines_with_tags_paragraph() -> None:
    text = "Start\nMiddle\n\nFinal"
    result = replace_newlines_with_tags(text, NewlineReplacement.PARAGRAPH)
    assert result == "<p>Start</p><p>Middle</p><p>Final</p>"


if __name__ == "__main__":
    pytest.main([__file__])


class TestReformatDate:
    def test_default_values_no_precision(self):
        result = reformat_date(
            "2000", date_precision_separator=None, date_range_separator=None, date_format=DateFormat.DD_MM_YYYY
        )
        assert result == "GREGORIAN:CE:2000:CE:2000"

    @pytest.mark.parametrize(
        ("date", "expected"),
        [
            ("1.11.2000", "GREGORIAN:CE:2000-11-1:CE:2000-11-1"),
            ("11.2000", "GREGORIAN:CE:2000-11:CE:2000-11"),
            ("2000", "GREGORIAN:CE:2000:CE:2000"),
            (2000, "GREGORIAN:CE:2000:CE:2000"),
        ],
    )
    def test_default_values_with_precision_dd_mm_yyyy(self, date, expected):
        result = reformat_date(
            date, date_precision_separator=".", date_range_separator=None, date_format=DateFormat.DD_MM_YYYY
        )
        assert result == expected

    def test_default_values_with_precision_blank_space(self):
        result = reformat_date(
            "11  2000", date_precision_separator=" ", date_range_separator=None, date_format=DateFormat.DD_MM_YYYY
        )
        assert result == "GREGORIAN:CE:2000-11:CE:2000-11"

    @pytest.mark.parametrize(
        ("date", "expected"),
        [
            ("2000.11.1", "GREGORIAN:CE:2000-11-1:CE:2000-11-1"),
            ("2000.11", "GREGORIAN:CE:2000-11:CE:2000-11"),
            ("2000", "GREGORIAN:CE:2000:CE:2000"),
        ],
    )
    def test_default_values_with_precision_yyyy_mm_dd(self, date, expected):
        result = reformat_date(
            date, date_format=DateFormat.YYYY_MM_DD, date_precision_separator=".", date_range_separator=None
        )
        assert result == expected

    @pytest.mark.parametrize(
        ("date", "expected"),
        [
            ("11.1.2000", "GREGORIAN:CE:2000-11-1:CE:2000-11-1"),
            ("11.2000", "GREGORIAN:CE:2000-11:CE:2000-11"),
            ("2000", "GREGORIAN:CE:2000:CE:2000"),
        ],
    )
    def test_default_values_with_precision_mm_dd_yyyy(self, date, expected):
        result = reformat_date(
            date, date_format=DateFormat.MM_DD_YYYY, date_precision_separator=".", date_range_separator=None
        )
        assert result == expected

    @pytest.mark.parametrize(
        ("date", "expected"),
        [
            ("1.11.2000-05.4.2001", "GREGORIAN:CE:2000-11-1:CE:2001-4-05"),
            ("11.2000-2001", "GREGORIAN:CE:2000-11:CE:2001"),
            ("2000-4.2001", "GREGORIAN:CE:2000:CE:2001-4"),
            ("2000-", "GREGORIAN:CE:2000:CE:2000"),
        ],
    )
    def test_default_values_with_range(self, date, expected):
        result = reformat_date(
            date, date_precision_separator=".", date_range_separator="-", date_format=DateFormat.DD_MM_YYYY
        )
        assert result == expected

    @pytest.mark.parametrize(
        ("date", "calendar", "era", "expected"),
        [
            ("1.11.2000 - 05.4.2001", Calendar.JULIAN, Era.AD, "JULIAN:AD:2000-11-1:AD:2001-4-05"),
            ("11.2000-2001", Calendar.ISLAMIC, None, "ISLAMIC:2000-11:2001"),
        ],
    )
    def test_non_default_calendar(self, date, calendar, era, expected):
        result = reformat_date(
            date,
            date_format=DateFormat.DD_MM_YYYY,
            date_precision_separator=".",
            date_range_separator="-",
            calendar=calendar,
            era=era,
        )
        assert result == expected

    @pytest.mark.parametrize(
        ("date", "era", "expected"),
        [
            ("1.11.2000-05.4.2001", Era.BCE, "GREGORIAN:BCE:2000-11-1:BCE:2001-4-05"),
            ("11.2000-2001", Era.AD, "GREGORIAN:AD:2000-11:AD:2001"),
            (" 2000- 4.2001 ", Era.BC, "GREGORIAN:BC:2000:BC:2001-4"),
        ],
    )
    def test_non_default_era(self, date, era, expected):
        result = reformat_date(
            date, date_format=DateFormat.DD_MM_YYYY, date_precision_separator=".", date_range_separator="-", era=era
        )
        assert result == expected

    @pytest.mark.parametrize(
        "date",
        ["GREGORIAN:BCE:2000-11-1:BCE:2001-4-05", "ISLAMIC:2000-11-1:2001-4-05"],
    )
    def test_is_dsp_date(self, date):
        result = reformat_date(
            date, date_precision_separator=":", date_range_separator="-", date_format=DateFormat.DD_MM_YYYY
        )
        assert result == date

    @pytest.mark.parametrize(
        "date",
        ["GREGORIAN:BCE:2000-11-1:BCE:2001-4-05", "2000", "20", "1.40", "1.4.200-06.7.300"],
    )
    def test_no_warnings(self, date):
        with warnings.catch_warnings(record=True) as caught_warnings:
            reformat_date(
                date, date_precision_separator=".", date_range_separator="-", date_format=DateFormat.DD_MM_YYYY
            )
        assert len(caught_warnings) == 0

    @pytest.mark.parametrize(
        "date",
        [
            "11.2000.12.2000",  # too many numbers
            "not-a-date",  # contains letters
            "11.2000.1",  # invalid date
            "2000.11.1",  # wrong order
            "1.11.200-1.12.200-1.1.300",  # too many dates
            "JULIAN-00.1.",  # contains a calendar but is an invalid dsp date
        ],
    )
    def test_warns(self, date):
        msg = rf"The provided date '{date}' does not conform to the expected format, the original value is returned."
        with pytest.warns(XmllibInputWarning, match=regex.escape(msg)):
            result = reformat_date(
                date, date_precision_separator=".", date_range_separator="-", date_format=DateFormat.DD_MM_YYYY
            )
        assert result == date

    def test_warns_empty(self):
        msg = r"The date to be reformatted is empty. An empty string is returned."
        with pytest.warns(XmllibInputWarning, match=regex.escape(msg)):
            result = reformat_date(
                "", date_precision_separator=".", date_range_separator="-", date_format=DateFormat.DD_MM_YYYY
            )
        assert result == ""

    def test_warns_islamic_with_era(self):
        date = "2000.11.1"
        msg = rf"The provided date '{date}' does not conform to the expected format, the original value is returned."
        with pytest.warns(XmllibInputWarning, match=regex.escape(msg)):
            result = reformat_date(
                date,
                date_precision_separator=".",
                date_range_separator="-",
                date_format=DateFormat.YYYY_MM_DD,
                calendar=Calendar.ISLAMIC,
            )
        assert result == date

    def test_raises_invalid_precision_and_range_is_the_same(self):
        date = "11.2000.12.2000"
        msg = "The precision separator and range separator provided are identical: '.'. This is not allowed."
        with pytest.raises(XmllibInputError, match=regex.escape(msg)):
            reformat_date(
                date, date_precision_separator=".", date_range_separator=".", date_format=DateFormat.DD_MM_YYYY
            )

    def test_raises_invalid_invalid_date_order(self):
        date = "11.2000-12.2000"
        msg = "The provided date format 'some string' to reformat the date is invalid."
        with pytest.raises(XmllibInputError, match=regex.escape(msg)):
            reformat_date(date, date_precision_separator=".", date_range_separator="-", date_format="some string")  # type:ignore[arg-type]


class TestFindDate:
    def test_find_dates_in_string_accept_only_dash_as_range_delimiter(self) -> None:
        assert find_dates_in_string("01.01.1900:31.12.2000") == {
            "GREGORIAN:CE:1900-01-01:CE:1900-01-01",
            "GREGORIAN:CE:2000-12-31:CE:2000-12-31",
        }
        assert find_dates_in_string("01.01.1900 to 31.12.2000") == {
            "GREGORIAN:CE:1900-01-01:CE:1900-01-01",
            "GREGORIAN:CE:2000-12-31:CE:2000-12-31",
        }
        assert find_dates_in_string("1900:2000") == {"GREGORIAN:CE:1900:CE:1900", "GREGORIAN:CE:2000:CE:2000"}
        assert find_dates_in_string("1900 to 2000") == {"GREGORIAN:CE:1900:CE:1900", "GREGORIAN:CE:2000:CE:2000"}

    def test_find_dates_in_string_iso(self) -> None:
        """template: 2021-01-01"""
        assert find_dates_in_string("x 1492-10-12, x") == {"GREGORIAN:CE:1492-10-12:CE:1492-10-12"}
        assert find_dates_in_string("x 0476-09-04. x") == {"GREGORIAN:CE:0476-09-04:CE:0476-09-04"}
        assert find_dates_in_string("x (0476-09-04) x") == {"GREGORIAN:CE:0476-09-04:CE:0476-09-04"}
        assert find_dates_in_string("x [1492-10-32?] x") == set()

    def test_find_dates_in_string_eur_date(self) -> None:
        """template: 31.4.2021 | 5/11/2021 | 2015_01_02"""
        assert find_dates_in_string("x (30.4.2021) x") == {"GREGORIAN:CE:2021-04-30:CE:2021-04-30"}
        assert find_dates_in_string("x (5/11/2021) x") == {"GREGORIAN:CE:2021-11-05:CE:2021-11-05"}
        assert find_dates_in_string("x ...2193_01_26... x") == {"GREGORIAN:CE:2193-01-26:CE:2193-01-26"}
        assert find_dates_in_string("x -2193_01_26- x") == {"GREGORIAN:CE:2193-01-26:CE:2193-01-26"}
        assert find_dates_in_string("x 2193_02_30 x") == set()

    def test_find_dates_in_string_eur_date_2_digit(self) -> None:
        cur = str(datetime.date.today().year - 2000)  # in 2024, this will be "24"
        nxt = str(datetime.date.today().year - 2000 + 1)  # in 2024, this will be "25"
        assert find_dates_in_string(f"x 30.4.{cur} x") == {f"GREGORIAN:CE:20{cur}-04-30:CE:20{cur}-04-30"}
        assert find_dates_in_string(f"x 30.4.{nxt} x") == {f"GREGORIAN:CE:19{nxt}-04-30:CE:19{nxt}-04-30"}
        assert find_dates_in_string(f"x 31.4.{nxt} x") == set()

    def test_find_dates_in_string_eur_date_range(self) -> None:
        """template: 27.-28.1.1900"""
        assert find_dates_in_string("x 25.-26.2.0800 x") == {"GREGORIAN:CE:0800-02-25:CE:0800-02-26"}
        assert find_dates_in_string("x 25. - 26.2.0800 x") == {"GREGORIAN:CE:0800-02-25:CE:0800-02-26"}
        assert find_dates_in_string("x 25.-25.2.0800 x") == {"GREGORIAN:CE:0800-02-25:CE:0800-02-25"}
        assert find_dates_in_string("x 25.-24.2.0800 x") == set()

    def test_find_dates_in_string_eur_date_range_2_digit(self) -> None:
        cur = str(datetime.date.today().year - 2000)  # in 2024, this will be "24"
        nxt = str(datetime.date.today().year - 2000 + 1)  # in 2024, this will be "25"
        assert find_dates_in_string(f"x 15.-16.4.{cur} x") == {f"GREGORIAN:CE:20{cur}-04-15:CE:20{cur}-04-16"}
        assert find_dates_in_string(f"x 15.-16.4.{nxt} x") == {f"GREGORIAN:CE:19{nxt}-04-15:CE:19{nxt}-04-16"}

    def test_find_dates_in_string_eur_date_range_across_month(self) -> None:
        """template: 26.2.-24.3.1948"""
        assert find_dates_in_string("x _1.3. - 25.4.2022_ x") == {"GREGORIAN:CE:2022-03-01:CE:2022-04-25"}
        assert find_dates_in_string("x (01.03. - 25.04.2022) x") == {"GREGORIAN:CE:2022-03-01:CE:2022-04-25"}
        assert find_dates_in_string("x 28.2.-1.12.1515 x") == {"GREGORIAN:CE:1515-02-28:CE:1515-12-01"}
        assert find_dates_in_string("x 28.2.-28.2.1515 x") == {"GREGORIAN:CE:1515-02-28:CE:1515-02-28"}
        assert find_dates_in_string("x 28.2.-26.2.1515 x") == set()

    def test_find_dates_in_string_eur_date_range_across_month_2_digit(self) -> None:
        cur = str(datetime.date.today().year - 2000)  # in 2024, this will be "24"
        nxt = str(datetime.date.today().year - 2000 + 1)  # in 2024, this will be "25"
        assert find_dates_in_string(f"x 15.04.-1.5.{cur} x") == {f"GREGORIAN:CE:20{cur}-04-15:CE:20{cur}-05-01"}
        assert find_dates_in_string(f"x 15.04.-1.5.{nxt} x") == {f"GREGORIAN:CE:19{nxt}-04-15:CE:19{nxt}-05-01"}

    def test_find_dates_in_string_eur_date_range_across_year(self) -> None:
        """template: 1.12.1973 - 6.1.1974"""
        assert find_dates_in_string("x 1.9.2022-3.1.2024 x") == {"GREGORIAN:CE:2022-09-01:CE:2024-01-03"}
        assert find_dates_in_string("x 25.12.2022 - 3.1.2024 x") == {"GREGORIAN:CE:2022-12-25:CE:2024-01-03"}
        assert find_dates_in_string("x 25/12/2022-03/01/2024 x") == {"GREGORIAN:CE:2022-12-25:CE:2024-01-03"}
        assert find_dates_in_string("x 25/12/2022 - 3/1/2024 x") == {"GREGORIAN:CE:2022-12-25:CE:2024-01-03"}
        assert find_dates_in_string("x 25.12.2022-25.12.2022 x") == {"GREGORIAN:CE:2022-12-25:CE:2022-12-25"}
        assert find_dates_in_string("x 25/12/2022-25/12/2022 x") == {"GREGORIAN:CE:2022-12-25:CE:2022-12-25"}
        assert find_dates_in_string("x 25.12.2022-03.01.2022 x") == set()
        assert find_dates_in_string("x 25/12/2022-03/01/2022 x") == set()

    def test_find_dates_in_string_eur_date_range_across_year_2_digit(self) -> None:
        cur = str(datetime.date.today().year - 2000)  # in 2024, this will be "24"
        nxt = str(datetime.date.today().year - 2000 + 1)  # in 2024, this will be "25"
        assert find_dates_in_string(f"x 15.04.23-1.5.{cur} x") == {f"GREGORIAN:CE:2023-04-15:CE:20{cur}-05-01"}
        assert find_dates_in_string(f"x 15.04.{nxt}-1.5.99 x") == {f"GREGORIAN:CE:19{nxt}-04-15:CE:1999-05-01"}

    def test_find_dates_in_string_monthname(self) -> None:
        """template: February 9, 1908 | Dec 5,1908"""
        assert find_dates_in_string("x Jan 26, 1993 x") == {"GREGORIAN:CE:1993-01-26:CE:1993-01-26"}
        assert find_dates_in_string("x February26,2051 x") == {"GREGORIAN:CE:2051-02-26:CE:2051-02-26"}
        assert find_dates_in_string("x Sept 1, 1000 x") == {"GREGORIAN:CE:1000-09-01:CE:1000-09-01"}
        assert find_dates_in_string("x October 01, 1000 x") == {"GREGORIAN:CE:1000-10-01:CE:1000-10-01"}
        assert find_dates_in_string("x Nov 6,1000 x") == {"GREGORIAN:CE:1000-11-06:CE:1000-11-06"}

    def test_find_dates_in_string_monthname_after_day(self) -> None:
        """template: 15 Jan 1927 | 15 January 1927"""
        assert find_dates_in_string("x 15 Jan 1927 x") == {"GREGORIAN:CE:1927-01-15:CE:1927-01-15"}
        assert find_dates_in_string("x 15Jan1927 x") == {"GREGORIAN:CE:1927-01-15:CE:1927-01-15"}
        assert find_dates_in_string("x 15 January 1927 x") == {"GREGORIAN:CE:1927-01-15:CE:1927-01-15"}
        assert find_dates_in_string("x 15January1927 x") == {"GREGORIAN:CE:1927-01-15:CE:1927-01-15"}

    def test_find_dates_in_string_german_monthnames(self) -> None:
        """template: 26. Jan. 1993 | 26. Januar 1993"""
        assert find_dates_in_string("x 26 Jan 1993 x") == {"GREGORIAN:CE:1993-01-26:CE:1993-01-26"}
        assert find_dates_in_string("x 26. Jan 1993 x") == {"GREGORIAN:CE:1993-01-26:CE:1993-01-26"}
        assert find_dates_in_string("x 26 Jan. 1993 x") == {"GREGORIAN:CE:1993-01-26:CE:1993-01-26"}
        assert find_dates_in_string("x 26. Jan. 1993 x") == {"GREGORIAN:CE:1993-01-26:CE:1993-01-26"}
        assert find_dates_in_string("x 26.Jan. 1993 x") == {"GREGORIAN:CE:1993-01-26:CE:1993-01-26"}
        assert find_dates_in_string("x 26.Jan.1993 x") == {"GREGORIAN:CE:1993-01-26:CE:1993-01-26"}
        assert find_dates_in_string("x 26Jan1993 x") == {"GREGORIAN:CE:1993-01-26:CE:1993-01-26"}
        assert find_dates_in_string("x 26. Januar 1993 x") == {"GREGORIAN:CE:1993-01-26:CE:1993-01-26"}

    def test_find_dates_in_string_single_year(self) -> None:
        """template: 1907 | 476"""
        assert find_dates_in_string("Text 1848 text") == {"GREGORIAN:CE:1848:CE:1848"}
        assert find_dates_in_string("Text 0476 text") == {"GREGORIAN:CE:476:CE:476"}
        assert find_dates_in_string("Text 476 text") == {"GREGORIAN:CE:476:CE:476"}

    def test_find_dates_in_string_year_range(self) -> None:
        """template: 1849/50 | 1845-50 | 1849/1850"""
        assert find_dates_in_string("x 1849/1850? x") == {"GREGORIAN:CE:1849:CE:1850"}
        assert find_dates_in_string("x 1845-1850, x") == {"GREGORIAN:CE:1845:CE:1850"}
        assert find_dates_in_string("x 800-900, x") == {"GREGORIAN:CE:800:CE:900"}
        assert find_dates_in_string("x 840-50, x") == {"GREGORIAN:CE:840:CE:850"}
        assert find_dates_in_string("x 844-8, x") == {"GREGORIAN:CE:844:CE:848"}
        assert find_dates_in_string("x 1840-1, x") == {"GREGORIAN:CE:1840:CE:1841"}
        assert find_dates_in_string("x 0750-0760 x") == {"GREGORIAN:CE:750:CE:760"}
        assert find_dates_in_string("x 1849/50. x") == {"GREGORIAN:CE:1849:CE:1850"}
        assert find_dates_in_string("x (1845-50) x") == {"GREGORIAN:CE:1845:CE:1850"}
        assert find_dates_in_string("x [1849/1850] x") == {"GREGORIAN:CE:1849:CE:1850"}
        assert find_dates_in_string("x 1850-1850 x") == {"GREGORIAN:CE:1850:CE:1850"}
        assert find_dates_in_string("x 830-30 x") == {"GREGORIAN:CE:830:CE:830"}
        assert find_dates_in_string("x 1811-11 x") == {"GREGORIAN:CE:1811:CE:1811"}
        assert find_dates_in_string("x 1811/11 x") == {"GREGORIAN:CE:1811:CE:1811"}
        assert find_dates_in_string("x 1850-1849 x") == set()
        assert find_dates_in_string("x 830-20 x") == set()
        assert find_dates_in_string("x 1811-10 x") == set()
        assert find_dates_in_string("x 1811/10 x") == set()

    @pytest.mark.parametrize("string", ["x 9 BC x", "9 B.C.", "9 BCE", "9 B.C.E."])
    def test_find_dates_in_string_bc_different_notations(self, string: str) -> None:
        assert find_dates_in_string(string) == {"GREGORIAN:BC:9:BC:9"}

    @pytest.mark.parametrize("string", ["9 CE", "9 C.E.", "9 AD", "9 A.D."])
    def test_find_dates_in_string_ce_different_notations(self, string: str) -> None:
        assert find_dates_in_string(string) == {"GREGORIAN:CE:9:CE:9"}

    @pytest.mark.parametrize(
        ("string", "expected"),
        [
            ("x 100 AD - 120 AD x", {"GREGORIAN:CE:100:CE:120"}),
            ("x 100 CE - 120 CE x", {"GREGORIAN:CE:100:CE:120"}),
            ("x 100 AD - 100 AD x", {"GREGORIAN:CE:100:CE:100"}),
            ("x 100 CE - 100 CE x", {"GREGORIAN:CE:100:CE:100"}),
            ("x 170 BC - 90 BC x", {"GREGORIAN:BC:170:BC:90"}),
            ("x 170-90 BCE x", {"GREGORIAN:BC:170:BC:90"}),
            ("x 20 BCE-50 CE x", {"GREGORIAN:BC:20:CE:50"}),
            ("x 20 BCE - 50 C.E. x", {"GREGORIAN:BC:20:CE:50"}),
            ("x 20 BCE - 20 BC x", {"GREGORIAN:BC:20:BC:20"}),
            ("x 20 BCE - 50 BC x", set()),
            ("x 50 AD - 20 AD x", set()),
            ("x 50 CE - 20 CE x", set()),
        ],
    )
    def test_find_dates_in_string_ce_and_bc_ranges(self, string: str, expected: set[str]) -> None:
        assert find_dates_in_string(string) == expected

    def test_find_dates_in_string_french_bc(self) -> None:
        assert find_dates_in_string("Text 12345 av. J.-C. text") == {"GREGORIAN:BC:12345:BC:12345"}
        assert find_dates_in_string("Text 2000 av. J.-C. text") == {"GREGORIAN:BC:2000:BC:2000"}
        assert find_dates_in_string("Text 250 av. J.-C. text") == {"GREGORIAN:BC:250:BC:250"}
        assert find_dates_in_string("Text 33 av. J.-C. text") == {"GREGORIAN:BC:33:BC:33"}
        assert find_dates_in_string("Text 1 av. J.-C. text") == {"GREGORIAN:BC:1:BC:1"}

    def test_find_dates_in_string_french_bc_ranges(self) -> None:
        assert find_dates_in_string("Text 99999-1000 av. J.-C. text") == {"GREGORIAN:BC:99999:BC:1000"}
        assert find_dates_in_string("Text 1125-1050 av. J.-C. text") == {"GREGORIAN:BC:1125:BC:1050"}
        assert find_dates_in_string("Text 1234-987 av. J.-C. text") == {"GREGORIAN:BC:1234:BC:987"}
        assert find_dates_in_string("Text 350-340 av. J.-C. text") == {"GREGORIAN:BC:350:BC:340"}
        assert find_dates_in_string("Text 842-98 av. J.-C. text") == {"GREGORIAN:BC:842:BC:98"}
        assert find_dates_in_string("Text 45-26 av. J.-C. text") == {"GREGORIAN:BC:45:BC:26"}
        assert find_dates_in_string("Text 53-7 av. J.-C. text") == {"GREGORIAN:BC:53:BC:7"}
        assert find_dates_in_string("Text 6-5 av. J.-C. text") == {"GREGORIAN:BC:6:BC:5"}

    def test_find_dates_in_string_french_bc_orthographical_variants(self) -> None:
        assert find_dates_in_string("Text 1 av. J.-C. text") == {"GREGORIAN:BC:1:BC:1"}
        assert find_dates_in_string("Text 1 av J.-C. text") == {"GREGORIAN:BC:1:BC:1"}
        assert find_dates_in_string("Text 1 av.J.-C. text") == {"GREGORIAN:BC:1:BC:1"}
        assert find_dates_in_string("Text 1 av. J.C. text") == {"GREGORIAN:BC:1:BC:1"}
        assert find_dates_in_string("Text 1 av. J-C text") == {"GREGORIAN:BC:1:BC:1"}
        assert find_dates_in_string("Text 1 av.JC text") == {"GREGORIAN:BC:1:BC:1"}
        assert find_dates_in_string("Text 1 av JC text") == {"GREGORIAN:BC:1:BC:1"}
        assert find_dates_in_string("Text 1 av. J.-C.text") == {"GREGORIAN:BC:1:BC:1"}

    def test_find_dates_in_string_french_bc_dash_variants(self) -> None:
        assert find_dates_in_string("Text 2000-1000 av. J.-C. text") == {"GREGORIAN:BC:2000:BC:1000"}
        assert find_dates_in_string("Text 2000- 1000 av. J.-C. text") == {"GREGORIAN:BC:2000:BC:1000"}
        assert find_dates_in_string("Text 2000 -1000 av. J.-C. text") == {"GREGORIAN:BC:2000:BC:1000"}
        assert find_dates_in_string("Text 2000 - 1000 av. J.-C. text") == {"GREGORIAN:BC:2000:BC:1000"}

    def test_find_dates_in_string_french_bc_invalid_syntax(self) -> None:
        assert find_dates_in_string("Text12 av. J.-C. text") == set()
        assert find_dates_in_string("Text 12 av. J.-Ctext") == set()
        assert find_dates_in_string("Text 1 avJC text") == set()

    @pytest.mark.parametrize(
        "already_parsed",
        [
            "GREGORIAN:BC:2001:BC:2000",
            "GREGORIAN:BC:2001-01:BC:2000-02",
            "GREGORIAN:BC:2001-01-01:BC:2000-01-02",
            "GREGORIAN:BC:1:CE:1",
            "GREGORIAN:CE:1993:CE:1994",
            "GREGORIAN:CE:1993-01:CE:1993-02",
            "GREGORIAN:CE:1993-01-26:CE:1993-01-27",
            "JULIAN:CE:1900:CE:1901",
        ],
    )
    def test_find_dates_in_string_already_parsed(self, already_parsed: str) -> None:
        assert find_dates_in_string(f"text {already_parsed} text") == {already_parsed}

    def test_find_dates_in_string_multiple(self) -> None:
        all_inputs = {
            "01.01.1900-31.12.2000": "GREGORIAN:CE:1900-01-01:CE:2000-12-31",
            "1492-10-12": "GREGORIAN:CE:1492-10-12:CE:1492-10-12",
            "30.4.2021": "GREGORIAN:CE:2021-04-30:CE:2021-04-30",
            "5/11/2021": "GREGORIAN:CE:2021-11-05:CE:2021-11-05",
            "2193_01_26": "GREGORIAN:CE:2193-01-26:CE:2193-01-26",
            "2193_02_30": None,
            "25.-26.2.0800": "GREGORIAN:CE:0800-02-25:CE:0800-02-26",
            "1.3. - 25.4.2022": "GREGORIAN:CE:2022-03-01:CE:2022-04-25",
            "25/12/2022 - 3/1/2024": "GREGORIAN:CE:2022-12-25:CE:2024-01-03",
            "Jan 26, 1993": "GREGORIAN:CE:1993-01-26:CE:1993-01-26",
            "15 January 1927": "GREGORIAN:CE:1927-01-15:CE:1927-01-15",
            "476": "GREGORIAN:CE:476:CE:476",
            "1849/1850": "GREGORIAN:CE:1849:CE:1850",
            "1850/1850": "GREGORIAN:CE:1850:CE:1850",
            "1845-1850": "GREGORIAN:CE:1845:CE:1850",
            "844-8": "GREGORIAN:CE:844:CE:848",
            "9 B.C.": "GREGORIAN:BC:9:BC:9",
            "9 AD": "GREGORIAN:CE:9:CE:9",
            "20 BCE - 50 C.E.": "GREGORIAN:BC:20:CE:50",
            "33 av. J.-C.": "GREGORIAN:BC:33:BC:33",
            "842-98 av. J.-C.": "GREGORIAN:BC:842:BC:98",
            "1 av JC": "GREGORIAN:BC:1:BC:1",
            "GREGORIAN:BC:2001:BC:2000": "GREGORIAN:BC:2001:BC:2000",
            "GREGORIAN:BC:2001-01-01:BC:2000-01-02": "GREGORIAN:BC:2001-01-01:BC:2000-01-02",
            "GREGORIAN:CE:1993:CE:1994": "GREGORIAN:CE:1993:CE:1994",
            "GREGORIAN:CE:1993-01-26:CE:1993-01-27": "GREGORIAN:CE:1993-01-26:CE:1993-01-27",
        }
        input_string = " ".join(all_inputs.keys())
        expected = {x for x in all_inputs.values() if x}
        assert find_dates_in_string(input_string) == expected
