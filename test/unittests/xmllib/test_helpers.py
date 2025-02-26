import datetime

import pandas as pd
import pytest
import regex

from dsp_tools.models.exceptions import InputError
from dsp_tools.xmllib.helpers import create_footnote_string
from dsp_tools.xmllib.helpers import create_list_from_string
from dsp_tools.xmllib.helpers import create_non_empty_list_from_string
from dsp_tools.xmllib.helpers import create_standoff_link_to_resource
from dsp_tools.xmllib.helpers import create_standoff_link_to_uri
from dsp_tools.xmllib.helpers import find_date_in_string
from dsp_tools.xmllib.models.config_options import NewlineReplacement


class TestFootnotes:
    @pytest.mark.parametrize(
        ("input_text", "newline_replacement", "expected"),
        [
            ("Text", NewlineReplacement.NONE, "Text"),
            ("With escape &", NewlineReplacement.NONE, "With escape &amp;"),
            ("With escape <", NewlineReplacement.NONE, "With escape &lt;"),
            ("With escape >", NewlineReplacement.NONE, "With escape &gt;"),
            ("<With escape>", NewlineReplacement.LINEBREAK, "&lt;With escape&gt;"),
            ("Already escaped &lt;&gt;", NewlineReplacement.LINEBREAK, "Already escaped &lt;&gt;"),
            (
                "Non-ASCII àéèêëôû äöüß 0123456789 _-'()+=!?| 漢が글ርبيةб中",
                NewlineReplacement.NONE,
                "Non-ASCII àéèêëôû äöüß 0123456789 _-'()+=!?| 漢が글ርبيةб中",
            ),
        ],
    )
    def test_create_footnote_string_correct(
        self, input_text: str, newline_replacement: NewlineReplacement, expected: str
    ) -> None:
        result = create_footnote_string(input_text, newline_replacement)
        expected = f'<footnote content="{expected}"/>'
        assert result == expected

    @pytest.mark.parametrize(
        ("input_text", "newline_replacement", "expected_msg"),
        [
            (
                "Text",
                NewlineReplacement.PARAGRAPH,
                "Currently the only supported newline replacement is linebreak (<br/>) or None.",
            ),
            (pd.NA, NewlineReplacement.NONE, "The input value is empty."),
        ],
    )
    def test_create_footnote_string_raises(
        self, input_text: str, newline_replacement: NewlineReplacement, expected_msg: str
    ) -> None:
        with pytest.raises(InputError, match=regex.escape(expected_msg)):
            create_footnote_string(input_text, newline_replacement)


def test_create_standoff_link_to_resource_success() -> None:
    result = create_standoff_link_to_resource("id", "Text")
    assert result == '<a class="salsah-link" href="IRI:id:IRI">Text</a>'


def test_create_standoff_link_to_resource_id_empty() -> None:
    with pytest.raises(InputError):
        create_standoff_link_to_resource("", "Text")


def test_create_standoff_link_to_resource_text_empty() -> None:
    with pytest.raises(InputError):
        create_standoff_link_to_resource("id", "")


def test_create_standoff_link_to_uri_success() -> None:
    result = create_standoff_link_to_uri("https://uri.ch", "Text")
    assert result == '<a href="https://uri.ch">Text</a>'


def test_create_standoff_link_to_uri_empty() -> None:
    with pytest.raises(InputError):
        create_standoff_link_to_uri("", "Text")


def test_create_standoff_link_to_uri_text_empty() -> None:
    with pytest.raises(InputError):
        create_standoff_link_to_uri("https://uri.ch", "")


class TestFindDate:
    def test_find_date_in_string_ignore_subsequent(self) -> None:
        assert find_date_in_string("x 1492-10-12, 2025-01-01x") == "GREGORIAN:CE:1492-10-12:CE:1492-10-12"
        assert find_date_in_string("first date: 2024. Second is ignored: 2025.") == "GREGORIAN:CE:2024:CE:2024"

    def test_find_date_in_string_accept_only_dash_as_range_delimiter(self) -> None:
        assert find_date_in_string("01.01.1900:31.12.2000") == "GREGORIAN:CE:1900-01-01:CE:1900-01-01"
        assert find_date_in_string("01.01.1900 to 31.12.2000") == "GREGORIAN:CE:1900-01-01:CE:1900-01-01"
        assert find_date_in_string("1900:2000") == "GREGORIAN:CE:1900:CE:1900"
        assert find_date_in_string("1900 to 2000") == "GREGORIAN:CE:1900:CE:1900"

    def test_find_date_in_string_iso(self) -> None:
        """template: 2021-01-01"""
        assert find_date_in_string("x 1492-10-12, x") == "GREGORIAN:CE:1492-10-12:CE:1492-10-12"
        assert find_date_in_string("x 0476-09-04. x") == "GREGORIAN:CE:0476-09-04:CE:0476-09-04"
        assert find_date_in_string("x (0476-09-04) x") == "GREGORIAN:CE:0476-09-04:CE:0476-09-04"
        assert find_date_in_string("x [1492-10-32?] x") is None

    def test_find_date_in_string_eur_date(self) -> None:
        """template: 31.4.2021 | 5/11/2021 | 2015_01_02"""
        assert find_date_in_string("x (30.4.2021) x") == "GREGORIAN:CE:2021-04-30:CE:2021-04-30"
        assert find_date_in_string("x (5/11/2021) x") == "GREGORIAN:CE:2021-11-05:CE:2021-11-05"
        assert find_date_in_string("x ...2193_01_26... x") == "GREGORIAN:CE:2193-01-26:CE:2193-01-26"
        assert find_date_in_string("x -2193_01_26- x") == "GREGORIAN:CE:2193-01-26:CE:2193-01-26"
        assert find_date_in_string("x 2193_02_30 x") is None

    def test_find_date_in_string_eur_date_2_digit(self) -> None:
        cur = str(datetime.date.today().year - 2000)  # in 2024, this will be "24"
        nxt = str(datetime.date.today().year - 2000 + 1)  # in 2024, this will be "25"
        assert find_date_in_string(f"x 30.4.{cur} x") == f"GREGORIAN:CE:20{cur}-04-30:CE:20{cur}-04-30"
        assert find_date_in_string(f"x 30.4.{nxt} x") == f"GREGORIAN:CE:19{nxt}-04-30:CE:19{nxt}-04-30"
        assert find_date_in_string(f"x 31.4.{nxt} x") is None

    def test_find_date_in_string_eur_date_range(self) -> None:
        """template: 27.-28.1.1900"""
        assert find_date_in_string("x 25.-26.2.0800 x") == "GREGORIAN:CE:0800-02-25:CE:0800-02-26"
        assert find_date_in_string("x 25. - 26.2.0800 x") == "GREGORIAN:CE:0800-02-25:CE:0800-02-26"
        assert find_date_in_string("x 25.-25.2.0800 x") == "GREGORIAN:CE:0800-02-25:CE:0800-02-25"
        assert find_date_in_string("x 25.-24.2.0800 x") is None

    def test_find_date_in_string_eur_date_range_2_digit(self) -> None:
        cur = str(datetime.date.today().year - 2000)  # in 2024, this will be "24"
        nxt = str(datetime.date.today().year - 2000 + 1)  # in 2024, this will be "25"
        assert find_date_in_string(f"x 15.-16.4.{cur} x") == f"GREGORIAN:CE:20{cur}-04-15:CE:20{cur}-04-16"
        assert find_date_in_string(f"x 15.-16.4.{nxt} x") == f"GREGORIAN:CE:19{nxt}-04-15:CE:19{nxt}-04-16"

    def test_find_date_in_string_eur_date_range_across_month(self) -> None:
        """template: 26.2.-24.3.1948"""
        assert find_date_in_string("x _1.3. - 25.4.2022_ x") == "GREGORIAN:CE:2022-03-01:CE:2022-04-25"
        assert find_date_in_string("x (01.03. - 25.04.2022) x") == "GREGORIAN:CE:2022-03-01:CE:2022-04-25"
        assert find_date_in_string("x 28.2.-1.12.1515 x") == "GREGORIAN:CE:1515-02-28:CE:1515-12-01"
        assert find_date_in_string("x 28.2.-28.2.1515 x") == "GREGORIAN:CE:1515-02-28:CE:1515-02-28"
        assert find_date_in_string("x 28.2.-26.2.1515 x") is None

    def test_find_date_in_string_eur_date_range_across_month_2_digit(self) -> None:
        cur = str(datetime.date.today().year - 2000)  # in 2024, this will be "24"
        nxt = str(datetime.date.today().year - 2000 + 1)  # in 2024, this will be "25"
        assert find_date_in_string(f"x 15.04.-1.5.{cur} x") == f"GREGORIAN:CE:20{cur}-04-15:CE:20{cur}-05-01"
        assert find_date_in_string(f"x 15.04.-1.5.{nxt} x") == f"GREGORIAN:CE:19{nxt}-04-15:CE:19{nxt}-05-01"

    def test_find_date_in_string_eur_date_range_across_year(self) -> None:
        """template: 1.12.1973 - 6.1.1974"""
        assert find_date_in_string("x 1.9.2022-3.1.2024 x") == "GREGORIAN:CE:2022-09-01:CE:2024-01-03"
        assert find_date_in_string("x 25.12.2022 - 3.1.2024 x") == "GREGORIAN:CE:2022-12-25:CE:2024-01-03"
        assert find_date_in_string("x 25/12/2022-03/01/2024 x") == "GREGORIAN:CE:2022-12-25:CE:2024-01-03"
        assert find_date_in_string("x 25/12/2022 - 3/1/2024 x") == "GREGORIAN:CE:2022-12-25:CE:2024-01-03"
        assert find_date_in_string("x 25.12.2022-25.12.2022 x") == "GREGORIAN:CE:2022-12-25:CE:2022-12-25"
        assert find_date_in_string("x 25/12/2022-25/12/2022 x") == "GREGORIAN:CE:2022-12-25:CE:2022-12-25"
        assert find_date_in_string("x 25.12.2022-03.01.2022 x") is None
        assert find_date_in_string("x 25/12/2022-03/01/2022 x") is None

    def test_find_date_in_string_eur_date_range_across_year_2_digit(self) -> None:
        cur = str(datetime.date.today().year - 2000)  # in 2024, this will be "24"
        nxt = str(datetime.date.today().year - 2000 + 1)  # in 2024, this will be "25"
        assert find_date_in_string(f"x 15.04.23-1.5.{cur} x") == f"GREGORIAN:CE:2023-04-15:CE:20{cur}-05-01"
        assert find_date_in_string(f"x 15.04.{nxt}-1.5.26 x") == f"GREGORIAN:CE:19{nxt}-04-15:CE:1926-05-01"

    def test_find_date_in_string_monthname(self) -> None:
        """template: February 9, 1908 | Dec 5,1908"""
        assert find_date_in_string("x Jan 26, 1993 x") == "GREGORIAN:CE:1993-01-26:CE:1993-01-26"
        assert find_date_in_string("x February26,2051 x") == "GREGORIAN:CE:2051-02-26:CE:2051-02-26"
        assert find_date_in_string("x Sept 1, 1000 x") == "GREGORIAN:CE:1000-09-01:CE:1000-09-01"
        assert find_date_in_string("x October 01, 1000 x") == "GREGORIAN:CE:1000-10-01:CE:1000-10-01"
        assert find_date_in_string("x Nov 6,1000 x") == "GREGORIAN:CE:1000-11-06:CE:1000-11-06"

    def test_find_date_in_string_monthname_after_day(self) -> None:
        """template: 15 Jan 1927 | 15 January 1927"""
        assert find_date_in_string("x 15 Jan 1927 x") == "GREGORIAN:CE:1927-01-15:CE:1927-01-15"
        assert find_date_in_string("x 15Jan1927 x") == "GREGORIAN:CE:1927-01-15:CE:1927-01-15"
        assert find_date_in_string("x 15 January 1927 x") == "GREGORIAN:CE:1927-01-15:CE:1927-01-15"
        assert find_date_in_string("x 15January1927 x") == "GREGORIAN:CE:1927-01-15:CE:1927-01-15"

    def test_find_date_in_string_german_monthnames(self) -> None:
        """template: 26. Jan. 1993 | 26. Januar 1993"""
        assert find_date_in_string("x 26 Jan 1993 x") == "GREGORIAN:CE:1993-01-26:CE:1993-01-26"
        assert find_date_in_string("x 26. Jan 1993 x") == "GREGORIAN:CE:1993-01-26:CE:1993-01-26"
        assert find_date_in_string("x 26 Jan. 1993 x") == "GREGORIAN:CE:1993-01-26:CE:1993-01-26"
        assert find_date_in_string("x 26. Jan. 1993 x") == "GREGORIAN:CE:1993-01-26:CE:1993-01-26"
        assert find_date_in_string("x 26.Jan. 1993 x") == "GREGORIAN:CE:1993-01-26:CE:1993-01-26"
        assert find_date_in_string("x 26.Jan.1993 x") == "GREGORIAN:CE:1993-01-26:CE:1993-01-26"
        assert find_date_in_string("x 26Jan1993 x") == "GREGORIAN:CE:1993-01-26:CE:1993-01-26"
        assert find_date_in_string("x 26. Januar 1993 x") == "GREGORIAN:CE:1993-01-26:CE:1993-01-26"

    def test_find_date_in_string_single_year(self) -> None:
        """template: 1907 | 476"""
        assert find_date_in_string("Text 1848 text") == "GREGORIAN:CE:1848:CE:1848"
        assert find_date_in_string("Text 0476 text") == "GREGORIAN:CE:476:CE:476"
        assert find_date_in_string("Text 476 text") == "GREGORIAN:CE:476:CE:476"

    def test_find_date_in_string_year_range(self) -> None:
        """template: 1849/50 | 1845-50 | 1849/1850"""
        assert find_date_in_string("x 1849/1850? x") == "GREGORIAN:CE:1849:CE:1850"
        assert find_date_in_string("x 1845-1850, x") == "GREGORIAN:CE:1845:CE:1850"
        assert find_date_in_string("x 800-900, x") == "GREGORIAN:CE:800:CE:900"
        assert find_date_in_string("x 840-50, x") == "GREGORIAN:CE:840:CE:850"
        assert find_date_in_string("x 844-8, x") == "GREGORIAN:CE:844:CE:848"
        assert find_date_in_string("x 1840-1, x") == "GREGORIAN:CE:1840:CE:1841"
        assert find_date_in_string("x 0750-0760 x") == "GREGORIAN:CE:750:CE:760"
        assert find_date_in_string("x 1849/50. x") == "GREGORIAN:CE:1849:CE:1850"
        assert find_date_in_string("x (1845-50) x") == "GREGORIAN:CE:1845:CE:1850"
        assert find_date_in_string("x [1849/1850] x") == "GREGORIAN:CE:1849:CE:1850"
        assert find_date_in_string("x 1850-1849 x") is None
        assert find_date_in_string("x 1850-1850 x") is None
        assert find_date_in_string("x 830-20 x") is None
        assert find_date_in_string("x 830-30 x") is None
        assert find_date_in_string("x 1811-10 x") is None
        assert find_date_in_string("x 1811-11 x") is None
        assert find_date_in_string("x 1811/10 x") is None
        assert find_date_in_string("x 1811/11 x") is None

    def test_find_date_in_string_french_bc(self) -> None:
        assert find_date_in_string("Text 12345 av. J.-C. text") == "GREGORIAN:BC:12345:BC:12345"
        assert find_date_in_string("Text 2000 av. J.-C. text") == "GREGORIAN:BC:2000:BC:2000"
        assert find_date_in_string("Text 250 av. J.-C. text") == "GREGORIAN:BC:250:BC:250"
        assert find_date_in_string("Text 33 av. J.-C. text") == "GREGORIAN:BC:33:BC:33"
        assert find_date_in_string("Text 1 av. J.-C. text") == "GREGORIAN:BC:1:BC:1"

    def test_find_date_in_string_french_bc_ranges(self) -> None:
        assert find_date_in_string("Text 99999-1000 av. J.-C. text") == "GREGORIAN:BC:99999:BC:1000"
        assert find_date_in_string("Text 1125-1050 av. J.-C. text") == "GREGORIAN:BC:1125:BC:1050"
        assert find_date_in_string("Text 1234-987 av. J.-C. text") == "GREGORIAN:BC:1234:BC:987"
        assert find_date_in_string("Text 350-340 av. J.-C. text") == "GREGORIAN:BC:350:BC:340"
        assert find_date_in_string("Text 842-98 av. J.-C. text") == "GREGORIAN:BC:842:BC:98"
        assert find_date_in_string("Text 45-26 av. J.-C. text") == "GREGORIAN:BC:45:BC:26"
        assert find_date_in_string("Text 53-7 av. J.-C. text") == "GREGORIAN:BC:53:BC:7"
        assert find_date_in_string("Text 6-5 av. J.-C. text") == "GREGORIAN:BC:6:BC:5"

    def test_find_date_in_string_french_bc_orthographical_variants(self) -> None:
        assert find_date_in_string("Text 1 av. J.-C. text") == "GREGORIAN:BC:1:BC:1"
        assert find_date_in_string("Text 1 av J.-C. text") == "GREGORIAN:BC:1:BC:1"
        assert find_date_in_string("Text 1 av.J.-C. text") == "GREGORIAN:BC:1:BC:1"
        assert find_date_in_string("Text 1 av. J.C. text") == "GREGORIAN:BC:1:BC:1"
        assert find_date_in_string("Text 1 av. J-C text") == "GREGORIAN:BC:1:BC:1"
        assert find_date_in_string("Text 1 av.JC text") == "GREGORIAN:BC:1:BC:1"
        assert find_date_in_string("Text 1 av JC text") == "GREGORIAN:BC:1:BC:1"
        assert find_date_in_string("Text 1 av. J.-C.text") == "GREGORIAN:BC:1:BC:1"

    def test_find_date_in_string_french_bc_dash_variants(self) -> None:
        assert find_date_in_string("Text 2000-1000 av. J.-C. text") == "GREGORIAN:BC:2000:BC:1000"
        assert find_date_in_string("Text 2000- 1000 av. J.-C. text") == "GREGORIAN:BC:2000:BC:1000"
        assert find_date_in_string("Text 2000 -1000 av. J.-C. text") == "GREGORIAN:BC:2000:BC:1000"
        assert find_date_in_string("Text 2000 - 1000 av. J.-C. text") == "GREGORIAN:BC:2000:BC:1000"

    def test_find_date_in_string_french_bc_invalid_syntax(self) -> None:
        assert find_date_in_string("Text12 av. J.-C. text") is None
        assert find_date_in_string("Text 12 av. J.-Ctext") is None
        assert find_date_in_string("Text 1 avJC text") is None

    def test_find_date_in_string_french_bc_invalid_range(self) -> None:
        assert find_date_in_string("Text 12-20 av. J.-C. text") is None


class TestCreateListFromString:
    def test_create_list_from_string_ok(self) -> None:
        result = create_list_from_string("ab, cd , ", ",")
        assert set(result) == {"ab", "cd"}

    def test_create_list_from_string_not_string(self) -> None:
        msg = regex.escape("The input for this function must be a string. Your input is a bool.")
        with pytest.raises(InputError, match=msg):
            create_list_from_string(True, ",")  # type: ignore[arg-type]

    def test_create_list_from_string_empty(self) -> None:
        result = create_list_from_string(" , ", ",")
        assert isinstance(result, list)
        assert result == []

    def test_create_non_empty_list_from_string_ok(self) -> None:
        result = create_non_empty_list_from_string("ab, cd , ", ",")
        assert set(result) == {"ab", "cd"}

    def test_create_non_empty_list_from_string_raises(self) -> None:
        msg = regex.escape(
            "The input for this function must result in a non-empty list. Your input results in an empty list."
        )
        with pytest.raises(InputError, match=msg):
            create_non_empty_list_from_string(" , ", ",")
