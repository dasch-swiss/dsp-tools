# mypy: disable-error-code="method-assign,no-untyped-def"
import datetime

import pandas as pd
import pytest
import regex

from dsp_tools.error.exceptions import InputError
from dsp_tools.error.xmllib_warnings import XmllibInputWarning
from dsp_tools.xmllib.helpers import ListLookup
from dsp_tools.xmllib.helpers import clean_whitespaces_from_string
from dsp_tools.xmllib.helpers import create_footnote_string
from dsp_tools.xmllib.helpers import create_list_from_string
from dsp_tools.xmllib.helpers import create_non_empty_list_from_string
from dsp_tools.xmllib.helpers import create_standoff_link_to_resource
from dsp_tools.xmllib.helpers import create_standoff_link_to_uri
from dsp_tools.xmllib.helpers import escape_reserved_xml_characters
from dsp_tools.xmllib.helpers import find_dates_in_string
from dsp_tools.xmllib.helpers import find_license_in_string
from dsp_tools.xmllib.helpers import make_xsd_compatible_id_with_uuid
from dsp_tools.xmllib.models.config_options import NewlineReplacement
from dsp_tools.xmllib.models.licenses.other import LicenseOther
from dsp_tools.xmllib.models.licenses.recommended import License
from dsp_tools.xmllib.models.licenses.recommended import LicenseRecommended

NBSP = "\u00a0"


@pytest.fixture
def list_lookup() -> ListLookup:
    return ListLookup(
        _lookup={
            "list1": {"Label 1": "list1_node1", "Label 2": "list1_node2"},
            "list2": {"Label 1": "list2_node1", "Label 2": "list2_node2"},
        },
        _prop_to_list_name={
            "default:defaultOntoHasListOne": "list1",
            ":defaultOntoHasListOne": "list1",
            "other-onto:otherOntoHasListOne": "list1",
            "other-onto:otherOntoHasListTwo": "list2",
        },
        _label_language="en",
    )


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
        assert find_dates_in_string(f"x 15.04.{nxt}-1.5.26 x") == {f"GREGORIAN:CE:19{nxt}-04-15:CE:1926-05-01"}

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
        assert find_dates_in_string("x 1850-1849 x") == set()
        assert find_dates_in_string("x 1850-1850 x") == set()
        assert find_dates_in_string("x 830-20 x") == set()
        assert find_dates_in_string("x 830-30 x") == set()
        assert find_dates_in_string("x 1811-10 x") == set()
        assert find_dates_in_string("x 1811-11 x") == set()
        assert find_dates_in_string("x 1811/10 x") == set()
        assert find_dates_in_string("x 1811/11 x") == set()

    @pytest.mark.parametrize("string", ["9 BC", "9 B.C.", "9 BCE", "9 B.C.E."])
    def test_find_dates_in_string_bc_different_notations(self, string: str) -> None:
        assert find_dates_in_string(string) == {"GREGORIAN:BC:9:BC:9"}

    @pytest.mark.parametrize("string", ["9 CE", "9 C.E.", "9 AD", "9 A.D."])
    def test_find_dates_in_string_ce_different_notations(self, string: str) -> None:
        assert find_dates_in_string(string) == {"GREGORIAN:CE:9:CE:9"}

    @pytest.mark.parametrize(
        ("string", "expected"),
        [
            ("x 9 BC x", {"GREGORIAN:BC:9:BC:9"}),
            ("x 10000 BC x", {"GREGORIAN:BC:10000:BC:10000"}),
            ("x 170 BC - 90 BC x", {"GREGORIAN:BC:170:BC:90"}),
            ("x 170-90 BCE x", {"GREGORIAN:BC:170:BC:90"}),
            ("x 20 BCE-50 CE x", {"GREGORIAN:BC:20:CE:50"}),
            ("x 20 BCE - 50 C.E. x", {"GREGORIAN:BC:20:CE:50"}),
        ],
    )
    def test_find_dates_in_string_bc(self, string: str, expected: set[str]) -> None:
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
            "1850/1850": None,
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


class TestListLookup:
    def test_get_node_via_list_name(self, list_lookup):
        assert list_lookup.get_node_via_list_name("list1", "Label 1") == "list1_node1"

    def test_get_node_via_list_name_warns_wrong_list(self, list_lookup):
        msg = regex.escape("The entered list name 'inexistent' was not found. An empty string is returned.")
        with pytest.warns(XmllibInputWarning, match=msg):
            result = list_lookup.get_node_via_list_name("inexistent", "Label 1")
        assert result == ""

    def test_get_node_via_list_name_warns_wrong_node(self, list_lookup):
        msg = regex.escape(
            "'inexistent' was not recognised as label of the list 'list1'. "
            "This ListLookup is configured for 'en' labels."
        )
        with pytest.warns(XmllibInputWarning, match=msg):
            result = list_lookup.get_node_via_list_name("list1", "inexistent")
        assert result == ""

    def test_get_node_via_property(self, list_lookup):
        list_name, node_name = list_lookup.get_list_name_and_node_via_property(
            "other-onto:otherOntoHasListTwo", "Label 2"
        )
        assert list_name == "list2"
        assert node_name == "list2_node2"

    def test_get_node_via_property_warns_wrong_property(self, list_lookup):
        msg = regex.escape("The entered property ':inexistent' was not found. An empty string is returned.")
        with pytest.warns(XmllibInputWarning, match=msg):
            result = list_lookup.get_list_name_and_node_via_property(":inexistent", "Label 2")
        assert result == ("", "")


@pytest.mark.parametrize(
    ("input_val", "expected"),
    [
        ("Text no escape", "Text no escape"),
        ("known tag <strong>content</strong>", "known tag <strong>content</strong>"),
        ("Ampersand &", "Ampersand &amp;"),
        ("Unknow tags <unknown></unknown>", "Unknow tags &lt;unknown&gt;&lt;/unknown&gt;"),
        ("<text in brackets>", "&lt;text in brackets&gt;"),
    ],
)
def test_escape_reserved_xml_characters(input_val: str, expected: str) -> None:
    result = escape_reserved_xml_characters(input_val)
    assert result == expected


@pytest.mark.parametrize(
    ("input_val", "expected"),
    [
        ("Text after space", "Text after space"),
        ("\t Text\nafter newline", "Text after newline"),
        ("\n More text\r    with lots   of spaces    \n", "More text with lots of spaces"),
    ],
)
def test_clean_whitespaces_from_string(input_val: str, expected: str) -> None:
    result = clean_whitespaces_from_string(input_val)
    assert result == expected


def test_clean_whitespaces_from_string_warns() -> None:
    expected = regex.escape("The entered string is empty after all redundant whitespaces were removed.")
    with pytest.warns(XmllibInputWarning, match=expected):
        result = clean_whitespaces_from_string("   \r   \n\t ")
    assert result == ""


class TestFindLicense:
    @pytest.mark.parametrize(
        ("string", "expected"),
        [
            ("text Creative Commons BY 4.0 text", LicenseRecommended.CC.BY),
            ("text Creative Commons BY text", LicenseRecommended.CC.BY),
            ("text CC BY 4.0 text", LicenseRecommended.CC.BY),
            (f"text CC{NBSP}BY{NBSP}4.0 text", LicenseRecommended.CC.BY),
            ("text CC-BY-4.0 text", LicenseRecommended.CC.BY),
            ("text CC_BY_4.0 text", LicenseRecommended.CC.BY),
            ("text CC BY text", LicenseRecommended.CC.BY),
            ("text CC-BY text", LicenseRecommended.CC.BY),
            ("text CC_BY text", LicenseRecommended.CC.BY),
            ("CC BY 4.0", LicenseRecommended.CC.BY),
            ("CC BY", LicenseRecommended.CC.BY),
            ("CC-BY", LicenseRecommended.CC.BY),
        ],
    )
    def test_find_license_different_syntax(self, string: str, expected: License) -> None:
        assert find_license_in_string(string) == expected

    @pytest.mark.parametrize(
        ("string", "expected"),
        [
            ("text, CC BY, text", LicenseRecommended.CC.BY),
            (f"text, CC{NBSP}BY, text", LicenseRecommended.CC.BY),
            ("text. CC-BY. text", LicenseRecommended.CC.BY),
            ("text-CC BY-text", LicenseRecommended.CC.BY),
            ("text-CC-BY-text", LicenseRecommended.CC.BY),
            ("text (CC BY) text", LicenseRecommended.CC.BY),
        ],
    )
    def test_find_license_punctuation(self, string: str, expected: License) -> None:
        assert find_license_in_string(string) == expected

    @pytest.mark.parametrize(
        ("string", "expected"),
        [
            ("text CC BY text", LicenseRecommended.CC.BY),
            ("text CC BY ND text", LicenseRecommended.CC.BY_ND),
            ("text CC BY SA text", LicenseRecommended.CC.BY_SA),
            ("text CC BY NC text", LicenseRecommended.CC.BY_NC),
            ("text CC BY NC ND text", LicenseRecommended.CC.BY_NC_ND),
            ("text CC BY NC SA text", LicenseRecommended.CC.BY_NC_SA),
            (f"text CC{NBSP}BY{NBSP}NC{NBSP}SA text", LicenseRecommended.CC.BY_NC_SA),
        ],
    )
    def test_find_license_different_licenses(self, string: str, expected: License) -> None:
        assert find_license_in_string(string) == expected

    @pytest.mark.parametrize(
        ("string", "expected"),
        [
            ("text cc by text", LicenseRecommended.CC.BY),
            ("text cc by nd text", LicenseRecommended.CC.BY_ND),
            ("text cc by sa text", LicenseRecommended.CC.BY_SA),
            ("text cc by nc text", LicenseRecommended.CC.BY_NC),
            ("text cc by nc nd text", LicenseRecommended.CC.BY_NC_ND),
            ("text cc by nc sa text", LicenseRecommended.CC.BY_NC_SA),
        ],
    )
    def test_find_license_lowercase(self, string: str, expected: License) -> None:
        assert find_license_in_string(string) == expected

    @pytest.mark.parametrize(
        ("string", "expected"),
        [
            ("CC BY NC SA 1.0", LicenseRecommended.CC.BY_NC_SA),
            ("CC BY NC SA 2.0", LicenseRecommended.CC.BY_NC_SA),
            ("CC BY NC SA 3.1", LicenseRecommended.CC.BY_NC_SA),
            ("CC BY NC SA 10.20", LicenseRecommended.CC.BY_NC_SA),
        ],
    )
    def test_find_license_different_versions(self, string: str, expected: License) -> None:
        assert find_license_in_string(string) == expected

    def test_find_license_ignore_subsequent(self) -> None:
        assert find_license_in_string("CC BY and CC BY SA") == LicenseRecommended.CC.BY

    @pytest.mark.parametrize(
        ("string", "expected"),
        [
            ("CC SA BY 4.0", LicenseRecommended.CC.BY_SA),
            ("CC BY SA NC", LicenseRecommended.CC.BY_NC_SA),
            ("CC BY-ND-NC", LicenseRecommended.CC.BY_NC_ND),
        ],
    )
    def test_find_license_wrong_order(self, string: str, expected: License) -> None:
        assert find_license_in_string(string) == expected

    @pytest.mark.parametrize(
        "string",
        [
            "CC",
            "CC/BY/SA",
            "CC,BY,SA",
            "CC.BY.SA",
            "textCC-BY-SAtext",
            "CC BY BY",
            "CC BY NC NC",
        ],
    )
    def test_find_license_wrong_format(self, string: str) -> None:
        assert not find_license_in_string(string)

    @pytest.mark.parametrize("string", ["CC ND SA"])
    def test_find_license_non_existent(self, string: str) -> None:
        assert not find_license_in_string(string)

    @pytest.mark.parametrize(
        ("string", "expected"),
        [
            ("text AI Generated text", LicenseRecommended.DSP.AI_GENERATED),
            ("text ai generated text", LicenseRecommended.DSP.AI_GENERATED),
            ("text AI text", LicenseRecommended.DSP.AI_GENERATED),
            ("text ai text", LicenseRecommended.DSP.AI_GENERATED),
            ("text IA text", LicenseRecommended.DSP.AI_GENERATED),
            ("text ia text", LicenseRecommended.DSP.AI_GENERATED),
            ("text KI text", LicenseRecommended.DSP.AI_GENERATED),
            ("text ki text", LicenseRecommended.DSP.AI_GENERATED),
            ("textkitext", None),
            ("textKItext", None),
            ("textaitext", None),
            ("textAItext", None),
            ("textiatext", None),
            ("textIAtext", None),
        ],
    )
    def test_find_license_ai_generated(self, string: str, expected: License | None) -> None:
        assert find_license_in_string(string) == expected

    @pytest.mark.parametrize(
        ("string", "expected"),
        [
            ("text PUBLIC DOMAIN text", LicenseRecommended.DSP.PUBLIC_DOMAIN),
            ("text public domain text", LicenseRecommended.DSP.PUBLIC_DOMAIN),
            (f"text public{NBSP}domain text", LicenseRecommended.DSP.PUBLIC_DOMAIN),
            ("text GEMEINFREI text", LicenseRecommended.DSP.PUBLIC_DOMAIN),
            ("text gemeinfrei text", LicenseRecommended.DSP.PUBLIC_DOMAIN),
            ("text frei von Urheberrechten text", LicenseRecommended.DSP.PUBLIC_DOMAIN),
            ("text urheberrechtsbefreit text", LicenseRecommended.DSP.PUBLIC_DOMAIN),
            ("text libre de droits text", LicenseRecommended.DSP.PUBLIC_DOMAIN),
            ("text domaine public text", LicenseRecommended.DSP.PUBLIC_DOMAIN),
        ],
    )
    def test_find_public_domain(self, string: str, expected: License) -> None:
        assert find_license_in_string(string) == expected

    @pytest.mark.parametrize(
        ("string", "expected"),
        [
            ("text UNKNOWN text", LicenseRecommended.DSP.UNKNOWN),
            ("text unknown text", LicenseRecommended.DSP.UNKNOWN),
            ("text UNBEKANNT text", LicenseRecommended.DSP.UNKNOWN),
            ("text unbekannt text", LicenseRecommended.DSP.UNKNOWN),
            ("text INCONNU text", LicenseRecommended.DSP.UNKNOWN),
            ("text inconnu text", LicenseRecommended.DSP.UNKNOWN),
        ],
    )
    def test_find_unknown(self, string: str, expected: License) -> None:
        assert find_license_in_string(string) == expected

    @pytest.mark.parametrize(
        "string",
        [
            "text Creative Commons 0 1.0 text",
            "text CC 0 1.0 text",
            "text CC-0-1.0 text",
            "text CC-0 text",
            "text CC 0 text",
            "text CC_0_1.0 text",
            f"text CC{NBSP}0 text",
            f"text CC{NBSP}0{NBSP}1.0 text",
        ],
    )
    def test_find_cc_0(self, string: str) -> None:
        assert find_license_in_string(string) == LicenseOther.Public.CC_0_1_0

    @pytest.mark.parametrize(
        "string",
        [
            "text Creative Commons PDM 1.0 text",
            "text CC PDM 1.0 text",
            "text CC-PDM-1.0 text",
            "text CC-PDM text",
            "text CC PDM text",
            "text CC_PDM_1.0 text",
            f"text CC{NBSP}PDM text",
            f"text CC{NBSP}PDM{NBSP}1.0 text",
        ],
    )
    def test_find_public_domain_mark(self, string: str) -> None:
        assert find_license_in_string(string) == LicenseOther.Public.CC_PDM_1_0

    @pytest.mark.parametrize(
        "string",
        [
            "text BORIS Standard License text",
            f"text BORIS{NBSP}Standard{NBSP}License text",
            "text BORIS-Standard-License text",
            "text BORIS_Standard_License text",
            "text Bern Open Repository and Information System Standard License text",
        ],
    )
    def test_find_boris(self, string: str) -> None:
        assert find_license_in_string(string) == LicenseOther.Various.BORIS_STANDARD

    @pytest.mark.parametrize(
        "string",
        [
            "text LICENCE OUVERTE 2.0 text",
            "text licence ouverte text",
            f"text{NBSP}licence{NBSP}ouverte{NBSP}text",
            "text France-licence-ouverte text",
            "text Etalab Licence ouverte text",
        ],
    )
    def test_find_france_ouverte(self, string: str) -> None:
        assert find_license_in_string(string) == LicenseOther.Various.FRANCE_OUVERTE

    @pytest.mark.parametrize(
        ("iri", "lic"),
        [
            ("http://rdfh.ch/licenses/cc-by-4.0", LicenseRecommended.CC.BY),
            ("http://rdfh.ch/licenses/cc-by-nd-4.0", LicenseRecommended.CC.BY_ND),
            ("http://rdfh.ch/licenses/cc-by-nc-4.0", LicenseRecommended.CC.BY_NC),
            ("http://rdfh.ch/licenses/cc-by-nc-nd-4.0", LicenseRecommended.CC.BY_NC_ND),
            ("http://rdfh.ch/licenses/cc-by-nc-sa-4.0", LicenseRecommended.CC.BY_NC_SA),
            ("http://rdfh.ch/licenses/cc-by-sa-4.0", LicenseRecommended.CC.BY_SA),
            ("http://rdfh.ch/licenses/ai-generated", LicenseRecommended.DSP.AI_GENERATED),
            ("http://rdfh.ch/licenses/unknown", LicenseRecommended.DSP.UNKNOWN),
            ("http://rdfh.ch/licenses/public-domain", LicenseRecommended.DSP.PUBLIC_DOMAIN),
            ("http://rdfh.ch/licenses/cc-0-1.0", LicenseOther.Public.CC_0_1_0),
            ("http://rdfh.ch/licenses/cc-pdm-1.0", LicenseOther.Public.CC_PDM_1_0),
            ("http://rdfh.ch/licenses/boris", LicenseOther.Various.BORIS_STANDARD),
            ("http://rdfh.ch/licenses/open-licence-2.0", LicenseOther.Various.FRANCE_OUVERTE),
        ],
    )
    def test_find_license_already_parsed(self, iri: str, lic: License) -> None:
        assert find_license_in_string(iri) == lic

    def test_find_license_edge_cases(self) -> None:
        assert not find_license_in_string("BORIS")  # BORIS alone is not enough; must be followed by "Standard License"


def test_make_xsd_compatible_id() -> None:
    teststring = "0aüZ/_-äöü1234567890?`^':.;+*ç%&/()=±“#Ç[]|{}≠₂₃āṇśṣr̥ṁñἄ𝝺𝝲𝛆’الشعرُאדםПопрыгуньяşğ"  # noqa: RUF001
    _expected = "_0a_Z__-___1234567890_____.__________________________r______________________________"

    result_1 = make_xsd_compatible_id_with_uuid(teststring)
    result_2 = make_xsd_compatible_id_with_uuid(teststring)
    assert result_1 != result_2
    assert result_1.startswith(_expected)
    assert result_2.startswith(_expected)
    assert bool(regex.search(r"^[a-zA-Z_][\w.-]*$", result_1))
    assert bool(regex.search(r"^[a-zA-Z_][\w.-]*$", result_2))

    # test that invalid inputs lead to an error
    with pytest.raises(InputError):
        make_xsd_compatible_id_with_uuid(None)  # type: ignore[arg-type]

    with pytest.raises(InputError):
        make_xsd_compatible_id_with_uuid("")

    with pytest.raises(InputError):
        make_xsd_compatible_id_with_uuid(" ")
