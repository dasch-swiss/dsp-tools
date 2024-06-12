import datetime
import unittest
import warnings
from pathlib import Path
from typing import Any
from typing import Callable
from typing import Optional
from typing import Sequence
from typing import Union

import numpy as np
import pytest
import regex
from lxml import etree

from dsp_tools import excel2xml
from dsp_tools.commands.excel2xml.excel2xml_lib import _escape_reserved_chars
from dsp_tools.commands.excel2xml.excel2xml_lib import create_interval_value
from dsp_tools.models.custom_warnings import DspToolsUserWarning
from dsp_tools.models.exceptions import BaseError

# ruff: noqa: PT009 (pytest-unittest-assertion) (remove this line when pytest is used instead of unittest)
# ruff: noqa: PT027 (pytest-unittest-raises-assertion) (remove this line when pytest is used instead of unittest)


class TestExcel2xmlLib(unittest.TestCase):
    def test_prepare_value(self) -> None:
        identical_values = ["Test", "Test", "Test"]
        different_values: list[Union[str, int, float]] = [1, 1.0, "1", "1.0", " 1 "]
        values_with_nas: list[Union[str, int, float]] = ["test", "", 1, np.nan, 0]

        for val in different_values:
            values_output = excel2xml.prepare_value(val)
            self.assertEqual([x.value for x in values_output], [val])

            values_output = excel2xml.prepare_value(excel2xml.PropertyElement(val))
            self.assertEqual([x.value for x in values_output], [val])

        values_output = excel2xml.prepare_value(identical_values)
        self.assertEqual([x.value for x in values_output], identical_values)

        values_output = excel2xml.prepare_value([excel2xml.PropertyElement(x) for x in identical_values])
        self.assertEqual([x.value for x in values_output], identical_values)

        values_output = excel2xml.prepare_value(different_values)
        self.assertEqual([x.value for x in values_output], different_values)

        values_output = excel2xml.prepare_value([excel2xml.PropertyElement(x) for x in different_values])
        self.assertEqual([x.value for x in values_output], different_values)

        values_output = excel2xml.prepare_value(values_with_nas)
        self.assertEqual([x.value for x in values_output], values_with_nas)

        values_output = excel2xml.prepare_value([excel2xml.PropertyElement(x) for x in values_with_nas])
        self.assertEqual([x.value for x in values_output], values_with_nas)


def test_find_date_in_string_iso() -> None:
    """template: 2021-01-01"""
    assert excel2xml.find_date_in_string("x 1492-10-12, x") == "GREGORIAN:CE:1492-10-12:CE:1492-10-12"
    assert excel2xml.find_date_in_string("x 0476-09-04. x") == "GREGORIAN:CE:0476-09-04:CE:0476-09-04"
    assert excel2xml.find_date_in_string("x (0476-09-04) x") == "GREGORIAN:CE:0476-09-04:CE:0476-09-04"
    assert excel2xml.find_date_in_string("x [1492-10-32?] x") is None


def test_find_date_in_string_eur_date() -> None:
    """template: 31.4.2021 | 5/11/2021 | 2015_01_02"""
    assert excel2xml.find_date_in_string("x (30.4.2021) x") == "GREGORIAN:CE:2021-04-30:CE:2021-04-30"
    assert excel2xml.find_date_in_string("x (5/11/2021) x") == "GREGORIAN:CE:2021-11-05:CE:2021-11-05"
    assert excel2xml.find_date_in_string("x ...2193_01_26... x") == "GREGORIAN:CE:2193-01-26:CE:2193-01-26"
    assert excel2xml.find_date_in_string("x -2193_01_26- x") == "GREGORIAN:CE:2193-01-26:CE:2193-01-26"
    assert excel2xml.find_date_in_string("x 2193_02_30 x") is None


def test_find_date_in_string_eur_date_2_digit() -> None:
    cur = str(datetime.date.today().year - 2000)  # in 2024, this will be "24"
    nxt = str(datetime.date.today().year - 2000 + 1)  # in 2024, this will be "25"
    assert excel2xml.find_date_in_string(f"x 30.4.{cur} x") == f"GREGORIAN:CE:20{cur}-04-30:CE:20{cur}-04-30"
    assert excel2xml.find_date_in_string(f"x 30.4.{nxt} x") == f"GREGORIAN:CE:19{nxt}-04-30:CE:19{nxt}-04-30"
    assert excel2xml.find_date_in_string(f"x 31.4.{nxt} x") is None


def test_find_date_in_string_eur_date_range() -> None:
    """template: 27.-28.1.1900"""
    assert excel2xml.find_date_in_string("x 25.-26.2.0800 x") == "GREGORIAN:CE:0800-02-25:CE:0800-02-26"
    assert excel2xml.find_date_in_string("x 25. - 26.2.0800 x") == "GREGORIAN:CE:0800-02-25:CE:0800-02-26"
    assert excel2xml.find_date_in_string("x 25.-25.2.0800 x") == "GREGORIAN:CE:0800-02-25:CE:0800-02-25"
    assert excel2xml.find_date_in_string("x 25.-24.2.0800 x") is None


def test_find_date_in_string_eur_date_range_2_digit() -> None:
    cur = str(datetime.date.today().year - 2000)  # in 2024, this will be "24"
    nxt = str(datetime.date.today().year - 2000 + 1)  # in 2024, this will be "25"
    assert excel2xml.find_date_in_string(f"x 15.-16.4.{cur} x") == f"GREGORIAN:CE:20{cur}-04-15:CE:20{cur}-04-16"
    assert excel2xml.find_date_in_string(f"x 15.-16.4.{nxt} x") == f"GREGORIAN:CE:19{nxt}-04-15:CE:19{nxt}-04-16"


def test_find_date_in_string_eur_date_range_across_month() -> None:
    """template: 26.2.-24.3.1948"""
    assert excel2xml.find_date_in_string("x _1.3. - 25.4.2022_ x") == "GREGORIAN:CE:2022-03-01:CE:2022-04-25"
    assert excel2xml.find_date_in_string("x (01.03. - 25.04.2022) x") == "GREGORIAN:CE:2022-03-01:CE:2022-04-25"
    assert excel2xml.find_date_in_string("x 28.2.-1.12.1515 x") == "GREGORIAN:CE:1515-02-28:CE:1515-12-01"
    assert excel2xml.find_date_in_string("x 28.2.-28.2.1515 x") == "GREGORIAN:CE:1515-02-28:CE:1515-02-28"
    assert excel2xml.find_date_in_string("x 28.2.-26.2.1515 x") is None


def test_find_date_in_string_eur_date_range_across_month_2_digit() -> None:
    cur = str(datetime.date.today().year - 2000)  # in 2024, this will be "24"
    nxt = str(datetime.date.today().year - 2000 + 1)  # in 2024, this will be "25"
    assert excel2xml.find_date_in_string(f"x 15.04.-1.5.{cur} x") == f"GREGORIAN:CE:20{cur}-04-15:CE:20{cur}-05-01"
    assert excel2xml.find_date_in_string(f"x 15.04.-1.5.{nxt} x") == f"GREGORIAN:CE:19{nxt}-04-15:CE:19{nxt}-05-01"


def test_find_date_in_string_eur_date_range_across_year() -> None:
    """template: 1.12.1973 - 6.1.1974"""
    assert excel2xml.find_date_in_string("x 1.9.2022-3.1.2024 x") == "GREGORIAN:CE:2022-09-01:CE:2024-01-03"
    assert excel2xml.find_date_in_string("x 25.12.2022 - 3.1.2024 x") == "GREGORIAN:CE:2022-12-25:CE:2024-01-03"
    assert excel2xml.find_date_in_string("x 25/12/2022-03/01/2024 x") == "GREGORIAN:CE:2022-12-25:CE:2024-01-03"
    assert excel2xml.find_date_in_string("x 25/12/2022 - 3/1/2024 x") == "GREGORIAN:CE:2022-12-25:CE:2024-01-03"
    assert excel2xml.find_date_in_string("x 25.12.2022-25.12.2022 x") == "GREGORIAN:CE:2022-12-25:CE:2022-12-25"
    assert excel2xml.find_date_in_string("x 25/12/2022-25/12/2022 x") == "GREGORIAN:CE:2022-12-25:CE:2022-12-25"
    assert excel2xml.find_date_in_string("x 25.12.2022-03.01.2022 x") is None
    assert excel2xml.find_date_in_string("x 25/12/2022-03/01/2022 x") is None


def test_find_date_in_string_eur_date_range_across_year_2_digit() -> None:
    cur = str(datetime.date.today().year - 2000)  # in 2024, this will be "24"
    nxt = str(datetime.date.today().year - 2000 + 1)  # in 2024, this will be "25"
    assert excel2xml.find_date_in_string(f"x 15.04.23-1.5.{cur} x") == f"GREGORIAN:CE:2023-04-15:CE:20{cur}-05-01"
    assert excel2xml.find_date_in_string(f"x 15.04.{nxt}-1.5.26 x") == f"GREGORIAN:CE:19{nxt}-04-15:CE:1926-05-01"


def test_find_date_in_string_monthname() -> None:
    """template: February 9, 1908 | Dec 5,1908"""
    assert excel2xml.find_date_in_string("x Jan 26, 1993 x") == "GREGORIAN:CE:1993-01-26:CE:1993-01-26"
    assert excel2xml.find_date_in_string("x February26,2051 x") == "GREGORIAN:CE:2051-02-26:CE:2051-02-26"
    assert excel2xml.find_date_in_string("x Sept 1, 1000 x") == "GREGORIAN:CE:1000-09-01:CE:1000-09-01"
    assert excel2xml.find_date_in_string("x October 01, 1000 x") == "GREGORIAN:CE:1000-10-01:CE:1000-10-01"
    assert excel2xml.find_date_in_string("x Nov 6,1000 x") == "GREGORIAN:CE:1000-11-06:CE:1000-11-06"


def test_find_date_in_string_single_year() -> None:
    """template: 1907 | 476"""
    assert excel2xml.find_date_in_string("Text 1848 text") == "GREGORIAN:CE:1848:CE:1848"
    assert excel2xml.find_date_in_string("Text 0476 text") == "GREGORIAN:CE:476:CE:476"
    assert excel2xml.find_date_in_string("Text 476 text") == "GREGORIAN:CE:476:CE:476"


def test_find_date_in_string_year_range() -> None:
    """template: 1849/50 | 1845-50 | 1849/1850"""
    assert excel2xml.find_date_in_string("x 1849/1850? x") == "GREGORIAN:CE:1849:CE:1850"
    assert excel2xml.find_date_in_string("x 1845-1850, x") == "GREGORIAN:CE:1845:CE:1850"
    assert excel2xml.find_date_in_string("x 800-900, x") == "GREGORIAN:CE:800:CE:900"
    assert excel2xml.find_date_in_string("x 840-50, x") == "GREGORIAN:CE:840:CE:850"
    assert excel2xml.find_date_in_string("x 844-8, x") == "GREGORIAN:CE:844:CE:848"
    assert excel2xml.find_date_in_string("x 1840-1, x") == "GREGORIAN:CE:1840:CE:1841"
    assert excel2xml.find_date_in_string("x 0750-0760 x") == "GREGORIAN:CE:750:CE:760"
    assert excel2xml.find_date_in_string("x 1849/50. x") == "GREGORIAN:CE:1849:CE:1850"
    assert excel2xml.find_date_in_string("x (1845-50) x") == "GREGORIAN:CE:1845:CE:1850"
    assert excel2xml.find_date_in_string("x [1849/1850] x") == "GREGORIAN:CE:1849:CE:1850"
    assert excel2xml.find_date_in_string("x 1850-1849 x") is None
    assert excel2xml.find_date_in_string("x 1850-1850 x") is None
    assert excel2xml.find_date_in_string("x 830-20 x") is None
    assert excel2xml.find_date_in_string("x 830-30 x") is None
    assert excel2xml.find_date_in_string("x 1811-10 x") is None
    assert excel2xml.find_date_in_string("x 1811-11 x") is None
    assert excel2xml.find_date_in_string("x 1811/10 x") is None
    assert excel2xml.find_date_in_string("x 1811/11 x") is None


def test_find_date_in_string_french_bc() -> None:
    assert excel2xml.find_date_in_string("Text 12345 av. J.-C. text") == "GREGORIAN:BC:12345:BC:12345"
    assert excel2xml.find_date_in_string("Text 2000 av. J.-C. text") == "GREGORIAN:BC:2000:BC:2000"
    assert excel2xml.find_date_in_string("Text 250 av. J.-C. text") == "GREGORIAN:BC:250:BC:250"
    assert excel2xml.find_date_in_string("Text 33 av. J.-C. text") == "GREGORIAN:BC:33:BC:33"
    assert excel2xml.find_date_in_string("Text 1 av. J.-C. text") == "GREGORIAN:BC:1:BC:1"


def test_find_date_in_string_french_bc_ranges() -> None:
    assert excel2xml.find_date_in_string("Text 99999-1000 av. J.-C. text") == "GREGORIAN:BC:99999:BC:1000"
    assert excel2xml.find_date_in_string("Text 1125-1050 av. J.-C. text") == "GREGORIAN:BC:1125:BC:1050"
    assert excel2xml.find_date_in_string("Text 1234-987 av. J.-C. text") == "GREGORIAN:BC:1234:BC:987"
    assert excel2xml.find_date_in_string("Text 350-340 av. J.-C. text") == "GREGORIAN:BC:350:BC:340"
    assert excel2xml.find_date_in_string("Text 842-98 av. J.-C. text") == "GREGORIAN:BC:842:BC:98"
    assert excel2xml.find_date_in_string("Text 45-26 av. J.-C. text") == "GREGORIAN:BC:45:BC:26"
    assert excel2xml.find_date_in_string("Text 53-7 av. J.-C. text") == "GREGORIAN:BC:53:BC:7"
    assert excel2xml.find_date_in_string("Text 6-5 av. J.-C. text") == "GREGORIAN:BC:6:BC:5"


def test_find_date_in_string_french_bc_orthographical_variants() -> None:
    assert excel2xml.find_date_in_string("Text 1 av. J.-C. text") == "GREGORIAN:BC:1:BC:1"
    assert excel2xml.find_date_in_string("Text 1 av J.-C. text") == "GREGORIAN:BC:1:BC:1"
    assert excel2xml.find_date_in_string("Text 1 av.J.-C. text") == "GREGORIAN:BC:1:BC:1"
    assert excel2xml.find_date_in_string("Text 1 av. J.C. text") == "GREGORIAN:BC:1:BC:1"
    assert excel2xml.find_date_in_string("Text 1 av. J-C text") == "GREGORIAN:BC:1:BC:1"
    assert excel2xml.find_date_in_string("Text 1 av.JC text") == "GREGORIAN:BC:1:BC:1"
    assert excel2xml.find_date_in_string("Text 1 av JC text") == "GREGORIAN:BC:1:BC:1"
    assert excel2xml.find_date_in_string("Text 1 av. J.-C.text") == "GREGORIAN:BC:1:BC:1"


def test_find_date_in_string_french_bc_dash_variants() -> None:
    assert excel2xml.find_date_in_string("Text 2000-1000 av. J.-C. text") == "GREGORIAN:BC:2000:BC:1000"
    assert excel2xml.find_date_in_string("Text 2000- 1000 av. J.-C. text") == "GREGORIAN:BC:2000:BC:1000"
    assert excel2xml.find_date_in_string("Text 2000 -1000 av. J.-C. text") == "GREGORIAN:BC:2000:BC:1000"
    assert excel2xml.find_date_in_string("Text 2000 - 1000 av. J.-C. text") == "GREGORIAN:BC:2000:BC:1000"


def test_find_date_in_string_french_bc_invalid_syntax() -> None:
    assert excel2xml.find_date_in_string("Text12 av. J.-C. text") is None
    assert excel2xml.find_date_in_string("Text 12 av. J.-Ctext") is None
    assert excel2xml.find_date_in_string("Text 1 avJC text") is None


def test_find_date_in_string_french_bc_invalid_range() -> None:
    assert excel2xml.find_date_in_string("Text 12-20 av. J.-C. text") is None


class TestMakeProps(unittest.TestCase):
    def run_test(
        self: unittest.TestCase,
        prop: str,
        method: Callable[..., etree._Element],
        different_values: Sequence[Union[str, int, float, bool]],
        invalid_values: Sequence[Any],
        listname: Optional[str] = None,
    ) -> None:
        """
        XML-properties have always a similar structure,
        and all make_*_prop() methods have some similar things to test.
        This method executes the tests in a parametrized way.

        Args:
            prop: the name of the property
            method: the make_*_prop() method
            different_values: some valid values
            invalid_values: some invalid values
            listname: to check the method make_list_prop, a list name is necessary

        Raises:
            BaseError: if make_list_prop() should be tested, but no listname is provided
        """
        identical_values = [different_values[0]] * 3
        maximum = len(different_values)

        # prepare the test cases of the form (expected_xml, kwargs for the method to generate XML)
        testcases: list[tuple[str, dict[str, Any]]] = []
        # pass every element of different_values separately
        for val in different_values:
            testcases.extend(
                [
                    (
                        f'<{prop}-prop name=":test"><{prop} permissions="prop-default">{val}</{prop}></{prop}-prop>',
                        dict(name=":test", value=val),
                    ),
                    (
                        f'<{prop}-prop name=":test"><{prop} permissions="prop-restricted">{val}</{prop}></{prop}-prop>',
                        dict(name=":test", value=excel2xml.PropertyElement(val, permissions="prop-restricted")),
                    ),
                    (
                        f'<{prop}-prop name=":test"><{prop} permissions="prop-restricted" comment="comment">{val}'
                        f"</{prop}></{prop}-prop>",
                        dict(
                            name=":test",
                            value=excel2xml.PropertyElement(val, permissions="prop-restricted", comment="comment"),
                        ),
                    ),
                ]
            )
        # pass the elements of different_values group-wise
        testcases.extend(
            [
                (
                    f'<{prop}-prop name=":test">'
                    f'<{prop} permissions="prop-default">{identical_values[0]}</{prop}>'
                    f'<{prop} permissions="prop-default">{identical_values[1]}</{prop}>'
                    f'<{prop} permissions="prop-default">{identical_values[2]}</{prop}>'
                    f"</{prop}-prop>",
                    dict(name=":test", value=identical_values),
                ),
                (
                    f'<{prop}-prop name=":test">'
                    f'<{prop} permissions="prop-default">{different_values[0 % maximum]}</{prop}>'
                    f'<{prop} permissions="prop-default">{different_values[1 % maximum]}</{prop}>'
                    f'<{prop} permissions="prop-default">{different_values[2 % maximum]}</{prop}>'
                    f"</{prop}-prop>",
                    dict(
                        name=":test",
                        value=[
                            different_values[0 % maximum],
                            different_values[1 % maximum],
                            different_values[2 % maximum],
                        ],
                    ),
                ),
                (
                    f'<{prop}-prop name=":test">'
                    f'<{prop} permissions="prop-restricted" comment="comment1">{different_values[3 % maximum]}</{prop}>'
                    f'<{prop} permissions="prop-default" comment="comment2">{different_values[4 % maximum]}</{prop}>'
                    f'<{prop} permissions="prop-restricted" comment="comment3">{different_values[5 % maximum]}</{prop}>'
                    f"</{prop}-prop>",
                    dict(
                        name=":test",
                        value=[
                            excel2xml.PropertyElement(
                                different_values[3 % maximum], permissions="prop-restricted", comment="comment1"
                            ),
                            excel2xml.PropertyElement(
                                different_values[4 % maximum], permissions="prop-default", comment="comment2"
                            ),
                            excel2xml.PropertyElement(
                                different_values[5 % maximum], permissions="prop-restricted", comment="comment3"
                            ),
                        ],
                    ),
                ),
            ]
        )

        # run the test cases
        for tc in testcases:
            xml_expected = tc[0]
            kwargs_to_generate_xml = tc[1]
            if prop == "list":
                # a <list-prop> has the additional attribute list="listname"
                xml_expected = regex.sub(r"<list-prop", f'<list-prop list="{listname}"', xml_expected)
                kwargs_to_generate_xml["list_name"] = listname
            elif prop == "text":
                # a <text> has the additional attribute encoding="utf8"
                # (the other encoding, xml, is tested in the caller)
                xml_expected = regex.sub(
                    r"<text (permissions=\".+?\")( comment=\".+?\")?",
                    '<text \\1\\2 encoding="utf8"',
                    xml_expected,
                )
            xml_returned_as_element = method(**kwargs_to_generate_xml)
            xml_returned = etree.tostring(xml_returned_as_element, encoding="unicode")
            xml_returned = regex.sub(
                r" xmlns(:.+?)?=\".+?\"", "", xml_returned
            )  # remove all xml namespace declarations
            self.assertEqual(
                xml_expected, xml_returned, msg=f"Method {method.__name__} failed with kwargs {kwargs_to_generate_xml}"
            )

        # perform illegal actions
        # pass invalid values as param "value"
        for invalid_value in invalid_values:
            kwargs_invalid_value = dict(name=":test", value=invalid_value)
            if prop == "list":
                if not listname:
                    raise BaseError("listname must be set to test make_list_prop()")
                kwargs_invalid_value["list_name"] = listname
            with self.assertWarns(Warning, msg=f"Method {method.__name__} failed with kwargs {kwargs_invalid_value}"):
                method(**kwargs_invalid_value)

    def test_make_color_prop(self) -> None:
        prop = "color"
        method = excel2xml.make_color_prop
        different_values = ["#012345", "#abcdef", "#0B0B0B", "#AAAAAA", "#1a2b3c"]
        invalid_values = ["#0000000", "#00000G"]
        self.run_test(prop, method, different_values, invalid_values)

    def test_make_date_prop(self) -> None:
        prop = "date"
        method = excel2xml.make_date_prop
        different_values = [
            "CE:1849:CE:1850",
            "GREGORIAN:1848-01:1849-02",
            "2022",
            "GREGORIAN:CE:0476-09-04:CE:0476-09-04",
            "GREGORIAN:CE:2014-01-31",
            "JULIAN:BC:1:AD:200",
        ]
        invalid_values = ["GREGORIAN:CE:0476-09-010:CE:0476-09-04"]
        self.run_test(prop, method, different_values, invalid_values)

    def test_make_decimal_prop(self) -> None:
        prop = "decimal"
        method = excel2xml.make_decimal_prop
        different_values: list[Union[str, float, int]] = ["3.14159", 3.14159, "1.3e3", "100", ".1", 100]
        invalid_values = ["string"]
        self.run_test(prop, method, [float(x) for x in different_values], invalid_values)

    def test_make_geometry_prop(self) -> None:
        prop = "geometry"
        method = excel2xml.make_geometry_prop
        different_values = [
            '{"type": "rectangle", "lineColor": "#ff3333", "lineWidth": 2, '
            '"points": [{"x": 0.08, "y": 0.16}, {"x": 0.73, "y": 0.72}], "original_index": 0}',
            '{"type": "rectangle", "lineColor": "#000000", "lineWidth": 1, '
            '"points": [{"x": 0.10, "y": 0.10}, {"x": 0.10, "y": 0.10}], "original_index": 1}',
        ]
        invalid_values = ["100", 100, [0], '{"type": "polygon"}']
        self.run_test(prop, method, different_values, invalid_values)

    def test_make_geoname_prop(self) -> None:
        prop = "geoname"
        method = excel2xml.make_geoname_prop
        different_values: list[Union[int, str]] = [1283416, "1283416", 71, "71", 10000000, "10000000"]
        invalid_values = ["text", 10.0, ["text"]]
        self.run_test(prop, method, different_values, invalid_values)

    def test_make_integer_prop(self) -> None:
        prop = "integer"
        method = excel2xml.make_integer_prop
        different_values: list[Union[int, str, float]] = [1283416, "1283416", 3.14159, " 11 ", 0, "0"]
        invalid_values = [" 10.3 ", "text", ["text"]]
        self.run_test(prop, method, [int(x) for x in different_values], invalid_values)

    def test_make_interval_prop(self) -> None:
        different_values = ["0.1:5", "10:20", "1.5:2.5"]
        for val in different_values:
            output = excel2xml.make_interval_prop("hasSegmentBounds", val)
            self.assertEqual(output[0].text, val)
        invalid_values = ["text", 10.0, ["text"], "10:", ":1", "-.1:5", "-10.0:-5.1"]
        for inv in invalid_values:
            with self.assertWarns(Warning):
                excel2xml.make_interval_prop("hasSegmentBounds", inv)  # type: ignore[arg-type]

    def test_make_list_prop(self) -> None:
        prop = "list"
        method = excel2xml.make_list_prop
        different_values = ["first-node", "second-node", "third-node", "fourth-node", "fifth-node"]
        invalid_values = [10.0]
        self.run_test(prop, method, different_values, invalid_values, ":myList")

    def test_make_resptr_prop(self) -> None:
        prop = "resptr"
        method = excel2xml.make_resptr_prop
        different_values = ["resource_1", "resource_2", "resource_3", "resource_4", "resource_5"]
        invalid_values = [True, 10.0, 5]
        self.run_test(prop, method, different_values, invalid_values)

    def test_make_time_prop(self) -> None:
        prop = "time"
        method = excel2xml.make_time_prop
        different_values = [
            "2019-10-23T13:45:12.01-14:00",
            "2019-10-23T13:45:12-14:00",
            "2019-10-23T13:45:12Z",
            "2019-10-23T13:45:12-13:30",
            "2019-10-23T13:45:12+01:00",
            "2019-10-23T13:45:12.1111111+01:00",
            "2019-10-23T13:45:12.123456789012Z",
        ]
        invalid_values = [
            True,
            10.0,
            5,
            "2019-10-2",
            "CE:1849:CE:1850",
            "2019-10-23T13:45:12.1234567890123Z",
            "2022",
            "GREGORIAN:CE:2014-01-31",
        ]
        self.run_test(prop, method, different_values, invalid_values)

    def test_make_uri_prop(self) -> None:
        prop = "uri"
        method = excel2xml.make_uri_prop
        different_values = [
            "https://www.test-case.ch/",
            "https://reg-exr.com:3000",
            "https://reg-exr.com:3000/path/to/file",
            "https://reg-exr.com:3000/path/to/file#fragment,fragment",
            "https://reg-exr.com:3000/path/to/file?query=test",
            "https://reg-exr.com:3000/path/to/file?query=test#fragment",
            "https://reg-exr.com/path/to/file?query=test#fragment",
            "http://www.168.1.1.0/path",
            "http://www.168.1.1.0:4200/path",
            "http://[2001:0db8:0000:0000:0000:8a2e:0370:7334]:4200/path",
            "https://en.wikipedia.org/wiki/Haiku#/media/File:Basho_Horohoroto.jpg",
        ]
        invalid_values = ["https:", 10.0, 5, "www.test.com"]
        self.run_test(prop, method, different_values, invalid_values)

    @pytest.mark.filterwarnings("ignore::dsp_tools.models.custom_warnings.DspToolsUserWarning")
    def test_make_text_prop(self) -> None:
        prop = "text"
        method = excel2xml.make_text_prop
        different_values = ["text_1", " ", "!", "?", "-", "_", "None"]
        invalid_values = [True, 10.0, 5, ""]
        self.run_test(prop, method, different_values, invalid_values)
        self.assertRaises(
            BaseError,
            lambda: excel2xml.make_text_prop(":test", excel2xml.PropertyElement(value="a", encoding="unicode")),
        )

    def test_make_bitstream_prop_from_string(self) -> None:
        res = excel2xml.make_bitstream_prop("foo/bar/baz.txt")
        assert res.tag.endswith("bitstream")
        assert res.attrib["permissions"] == "prop-default"
        assert res.text == "foo/bar/baz.txt"

    def test_make_bitstream_prop_from_path(self) -> None:
        res = excel2xml.make_bitstream_prop(Path("foo/bar/baz.txt"))
        assert res.tag.endswith("bitstream")
        assert res.attrib["permissions"] == "prop-default"
        assert res.text == "foo/bar/baz.txt"

    def test_make_bitstream_prop_custom_permissions(self) -> None:
        res = excel2xml.make_bitstream_prop("foo/bar/baz.txt", "prop-restricted")
        assert res.tag.endswith("bitstream")
        assert res.attrib["permissions"] == "prop-restricted"
        assert res.text == "foo/bar/baz.txt"

    def test_make_bitstream_prop_valid_file(self) -> None:
        with warnings.catch_warnings():
            warnings.filterwarnings("error", category=UserWarning)
            try:
                res = excel2xml.make_bitstream_prop("testdata/bitstreams/test.jpg", check=True)
            except UserWarning as e:
                raise AssertionError from e
        assert res.tag.endswith("bitstream")
        assert res.attrib["permissions"] == "prop-default"
        assert res.text == "testdata/bitstreams/test.jpg"

    def test_make_bitstream_prop_invalid_file(self) -> None:
        with pytest.warns(DspToolsUserWarning, match=".*Failed validation in bitstream tag.*"):
            res = excel2xml.make_bitstream_prop("foo/bar/baz.txt", check=True)
        assert res.tag.endswith("bitstream")
        assert res.attrib["permissions"] == "prop-default"
        assert res.text == "foo/bar/baz.txt"

    def test_make_boolean_prop(self) -> None:
        # prepare true_values
        true_values_orig: list[Union[bool, str, int]] = [True, "TRue", "TruE", "1", 1, "yes", "YES", "yEs"]
        true_values_as_propelem = [excel2xml.PropertyElement(x) for x in true_values_orig]
        true_values = true_values_orig + true_values_as_propelem

        # prepare false_values
        false_values_orig: list[Union[bool, str, int]] = [False, "false", "False", "falSE", "0", 0, "no", "No", "nO"]
        false_values_as_propelem = [excel2xml.PropertyElement(x) for x in false_values_orig]
        false_values = false_values_orig + false_values_as_propelem

        unsupported_values: list[Any] = [
            np.nan,
            "N/A",
            "NA",
            "na",
            "None",
            "",
            " ",
            "-",
            None,
            [True, False],
            [0, 0, 1],
            ["True", "false"],
        ]

        true_xml_expected = (
            '<boolean-prop name=":test"><boolean permissions="prop-default">true</boolean></boolean-prop>'
        )
        false_xml_expected = (
            '<boolean-prop name=":test"><boolean permissions="prop-default">false</boolean></boolean-prop>'
        )

        for true_value in true_values:
            true_xml = etree.tostring(excel2xml.make_boolean_prop(":test", true_value), encoding="unicode")
            true_xml = regex.sub(r" xmlns(:.+?)?=\".+?\"", "", true_xml)
            self.assertEqual(true_xml, true_xml_expected, msg=f"Failed with '{true_value}'")
        for false_value in false_values:
            false_xml = etree.tostring(excel2xml.make_boolean_prop(":test", false_value), encoding="unicode")
            false_xml = regex.sub(r" xmlns(:.+?)?=\".+?\"", "", false_xml)
            self.assertEqual(false_xml, false_xml_expected, msg=f"Failed with '{false_value}'")
        for unsupported_value in unsupported_values:
            with self.assertRaises(BaseError):
                excel2xml.make_boolean_prop(":test", unsupported_value)

    def test_make_text_prop_utf8_lt_gt_amp(self) -> None:
        original = "1 < 2 & 4 > 3"
        expected = "1 &lt; 2 &amp; 4 &gt; 3"
        returned = etree.tostring(excel2xml.make_text_prop(":test", original), encoding="unicode")
        returned = regex.sub(r"</?text(-prop)?( [^>]+)?>", "", returned)
        assert returned == expected

    def test_make_text_prop_utf8_pseudo_tag(self) -> None:
        original = "txt <txt>txt</txt> txt"
        expected = "txt &lt;txt&gt;txt&lt;/txt&gt; txt"
        returned = etree.tostring(excel2xml.make_text_prop(":test", original), encoding="unicode")
        returned = regex.sub(r"</?text(-prop)?( [^>]+)?>", "", returned)
        assert returned == expected

    def test_make_text_prop_utf8_escape(self) -> None:
        original = "txt &amp; txt"
        expected = "txt &amp;amp; txt"
        returned = etree.tostring(excel2xml.make_text_prop(":test", original), encoding="unicode")
        returned = regex.sub(r"</?text(-prop)?( [^>]+)?>", "", returned)
        assert returned == expected

    def test_make_text_prop_xml_standard_standoff_tag(self) -> None:
        original = "text <strong>and</strong> text"
        expected = "text <strong>and</strong> text"
        returned = etree.tostring(
            excel2xml.make_text_prop(":test", excel2xml.PropertyElement(original, encoding="xml")), encoding="unicode"
        )
        returned = regex.sub(r"</?text(-prop)?( [^>]+)?>", "", returned)
        assert returned == expected

    def test_make_text_prop_xml_unsupported_tag(self) -> None:
        original = "text <unsupported>tag</unsupported> text"
        expected = "text &lt;unsupported&gt;tag&lt;/unsupported&gt; text"
        returned = etree.tostring(
            excel2xml.make_text_prop(":test", excel2xml.PropertyElement(original, encoding="xml")), encoding="unicode"
        )
        returned = regex.sub(r"</?text(-prop)?( [^>]+)?>", "", returned)
        assert returned == expected

    def test_make_text_prop_xml_salsah_link(self) -> None:
        original = 'a <a class="salsah-link" href="IRI:test_thing_0:IRI">link</a> text'
        expected = 'a <a class="salsah-link" href="IRI:test_thing_0:IRI">link</a> text'
        returned = etree.tostring(
            excel2xml.make_text_prop(":test", excel2xml.PropertyElement(original, encoding="xml")), encoding="unicode"
        )
        returned = regex.sub(r"</?text(-prop)?( [^>]+)?>", "", returned)
        assert returned == expected

    def test_make_text_prop_xml_escaped_tag(self) -> None:
        original = "text <strong>and</strong> text"
        expected = "text <strong>and</strong> text"
        returned = etree.tostring(
            excel2xml.make_text_prop(":test", excel2xml.PropertyElement(original, encoding="xml")), encoding="unicode"
        )
        returned = regex.sub(r"</?text(-prop)?( [^>]+)?>", "", returned)
        assert returned == expected

    def test_make_text_prop_xml_lt_gt_amp(self) -> None:
        original = "1 < 2 & 4 > 3"
        expected = "1 &lt; 2 &amp; 4 &gt; 3"
        returned = etree.tostring(
            excel2xml.make_text_prop(":test", excel2xml.PropertyElement(original, encoding="xml")), encoding="unicode"
        )
        returned = regex.sub(r"</?text(-prop)?( [^>]+)?>", "", returned)
        assert returned == expected

    def test_make_text_prop_xml_escape_sequence(self) -> None:
        original = "text &amp; text"
        expected = "text &amp; text"
        returned = etree.tostring(
            excel2xml.make_text_prop(":test", excel2xml.PropertyElement(original, encoding="xml")), encoding="unicode"
        )
        returned = regex.sub(r"</?text(-prop)?( [^>]+)?>", "", returned)
        assert returned == expected

    def test_make_text_prop_special_characters_xml(self) -> None:
        originals = ["'uuas\\. 11` \\a\\ i! 1 ?7", "Rinne   \\Rinne"]
        for orig in originals:
            returned = etree.tostring(
                excel2xml.make_text_prop(":test", excel2xml.PropertyElement(orig, encoding="xml")), encoding="unicode"
            )
            returned = regex.sub(r"</?text(-prop)?( [^>]+)?>", "", returned)
            assert returned == orig

    def test_make_text_prop_special_characters_utf8(self) -> None:
        originals = ["'uuas\\. 11` \\a\\ i! 1 ?7", "Rinne   \\Rinne"]
        for orig in originals:
            returned = etree.tostring(excel2xml.make_text_prop(":test", orig), encoding="unicode")
            returned = regex.sub(r"</?text(-prop)?( [^>]+)?>", "", returned)
            assert returned == orig

    def test_make_text_prop_disallowed_named_char_refs(self) -> None:
        original = "<p>text &nbsp; &auml; &euro; text</p>"
        expected = "<p>text \xa0 ä € text</p>"
        prop = excel2xml.make_text_prop(":test", excel2xml.PropertyElement(original, encoding="xml"))
        returned = etree.tostring(prop, encoding="unicode")
        returned = regex.sub(r"</?text(-prop)?( [^>]+)?>", "", returned)
        assert returned == expected

    def test_make_text_prop_allowed_named_char_refs(self) -> None:
        original = "<p>text &lt; &amp; &gt; text</p>"
        expected = "<p>text &lt; &amp; &gt; text</p>"
        prop = excel2xml.make_text_prop(":test", excel2xml.PropertyElement(original, encoding="xml"))
        returned = etree.tostring(prop, encoding="unicode")
        returned = regex.sub(r"</?text(-prop)?( [^>]+)?>", "", returned)
        assert returned == expected

    def test_make_annotation(self) -> None:
        expected = '<annotation label="label" id="id" permissions="res-default"/>'
        result = _strip_namespace(excel2xml.make_annotation("label", "id"))
        self.assertEqual(expected, result)

    def test_make_annotation_with_permission(self) -> None:
        expected = '<annotation label="label" id="id" permissions="res-restricted"/>'
        result = _strip_namespace(excel2xml.make_annotation("label", "id", "res-restricted"))
        self.assertEqual(expected, result)

    def test_make_annotation_with_ark(self) -> None:
        expected = '<annotation label="label" id="id" permissions="res-default" ark="ark"/>'
        result = _strip_namespace(excel2xml.make_annotation("label", "id", ark="ark"))
        self.assertEqual(expected, result)

    def test_make_annotation_with_iri(self) -> None:
        expected = '<annotation label="label" id="id" permissions="res-default" iri="iri"/>'
        result = _strip_namespace(excel2xml.make_annotation("label", "id", iri="iri"))
        self.assertEqual(expected, result)

    def test_make_annotation_with_creation_date(self) -> None:
        expected = '<annotation label="label" id="id" permissions="res-default" creation_date="2019-10-23T13:45:12Z"/>'
        result = _strip_namespace(excel2xml.make_annotation("label", "id", creation_date="2019-10-23T13:45:12Z"))
        self.assertEqual(expected, result)

    def test_warn_make_annotation_with_iri_and_ark(self) -> None:
        with self.assertWarns(DspToolsUserWarning):
            excel2xml.make_annotation("label", "id", ark="ark", iri="iri")

    def test_fail_annotation_with_invalid_creation_date(self) -> None:
        with self.assertRaisesRegex(BaseError, "invalid creation date"):
            excel2xml.make_annotation("label", "id", creation_date="2019-10-23T13:45:12")

    def test_make_link(self) -> None:
        expected = '<link label="label" id="id" permissions="res-default"/>'
        result = _strip_namespace(excel2xml.make_link("label", "id"))
        self.assertEqual(expected, result)

    def test_make_link_with_permission(self) -> None:
        expected = '<link label="label" id="id" permissions="res-restricted"/>'
        result = _strip_namespace(excel2xml.make_link("label", "id", "res-restricted"))
        self.assertEqual(expected, result)

    def test_make_link_with_ark(self) -> None:
        expected = '<link label="label" id="id" permissions="res-default" ark="ark"/>'
        result = _strip_namespace(excel2xml.make_link("label", "id", ark="ark"))
        self.assertEqual(expected, result)

    def test_make_link_with_iri(self) -> None:
        expected = '<link label="label" id="id" permissions="res-default" iri="iri"/>'
        result = _strip_namespace(excel2xml.make_link("label", "id", iri="iri"))
        self.assertEqual(expected, result)

    def test_make_link_with_creation_date(self) -> None:
        expected = '<link label="label" id="id" permissions="res-default" creation_date="2019-10-23T13:45:12Z"/>'
        result = _strip_namespace(excel2xml.make_link("label", "id", creation_date="2019-10-23T13:45:12Z"))
        self.assertEqual(expected, result)

    def test_warn_make_link_with_iri_and_ark(self) -> None:
        with self.assertWarns(DspToolsUserWarning):
            excel2xml.make_link("label", "id", ark="ark", iri="iri")

    def test_fail_link_with_invalid_creation_date(self) -> None:
        with self.assertRaisesRegex(BaseError, "invalid creation date"):
            excel2xml.make_link("label", "id", creation_date="2019-10-23T13:45:12")

    def test_make_region(self) -> None:
        expected = '<region label="label" id="id" permissions="res-default"/>'
        result = _strip_namespace(excel2xml.make_region("label", "id"))
        self.assertEqual(expected, result)

    def test_make_region_with_permission(self) -> None:
        expected = '<region label="label" id="id" permissions="res-restricted"/>'
        result = _strip_namespace(excel2xml.make_region("label", "id", "res-restricted"))
        self.assertEqual(expected, result)

    def test_make_region_with_ark(self) -> None:
        expected = '<region label="label" id="id" permissions="res-default" ark="ark"/>'
        result = _strip_namespace(excel2xml.make_region("label", "id", ark="ark"))
        self.assertEqual(expected, result)

    def test_make_region_with_iri(self) -> None:
        expected = '<region label="label" id="id" permissions="res-default" iri="iri"/>'
        result = _strip_namespace(excel2xml.make_region("label", "id", iri="iri"))
        self.assertEqual(expected, result)

    def test_make_region_with_creation_date(self) -> None:
        expected = '<region label="label" id="id" permissions="res-default" creation_date="2019-10-23T13:45:12Z"/>'
        result = _strip_namespace(excel2xml.make_region("label", "id", creation_date="2019-10-23T13:45:12Z"))
        self.assertEqual(expected, result)

    def test_warn_make_region_with_iri_and_ark(self) -> None:
        with self.assertWarns(DspToolsUserWarning):
            excel2xml.make_region("label", "id", ark="ark", iri="iri")

    def test_fail_region_with_invalid_creation_date(self) -> None:
        with self.assertRaisesRegex(BaseError, "invalid creation date"):
            excel2xml.make_region("label", "id", creation_date="2019-10-23T13:45:12")

    def test_make_audio_segment(self) -> None:
        expected = '<audio-segment label="label" id="id" permissions="res-default"/>'
        result = _strip_namespace(excel2xml.make_audio_segment("label", "id"))
        self.assertEqual(expected, result)

    def test_make_audio_segment_with_custom_permissions(self) -> None:
        expected = '<audio-segment label="label" id="id" permissions="res-restricted"/>'
        result = _strip_namespace(excel2xml.make_audio_segment("label", "id", "res-restricted"))
        self.assertEqual(expected, result)

    def test_make_video_segment(self) -> None:
        expected = '<video-segment label="label" id="id" permissions="res-default"/>'
        result = _strip_namespace(excel2xml.make_video_segment("label", "id"))
        self.assertEqual(expected, result)

    def test_make_video_segment_with_custom_permissions(self) -> None:
        expected = '<video-segment label="label" id="id" permissions="res-restricted"/>'
        result = _strip_namespace(excel2xml.make_video_segment("label", "id", "res-restricted"))
        self.assertEqual(expected, result)

    def test_make_resource(self) -> None:
        test_cases: list[tuple[Callable[..., etree._Element], str]] = [
            (
                lambda: excel2xml.make_resource("label", "restype", "id"),
                '<resource label="label" restype="restype" id="id" permissions="res-default"/>',
            ),
            (
                lambda: excel2xml.make_resource("label", "restype", "id", "res-restricted"),
                '<resource label="label" restype="restype" id="id" permissions="res-restricted"/>',
            ),
            (
                lambda: excel2xml.make_resource("label", "restype", "id", ark="ark"),
                '<resource label="label" restype="restype" id="id" permissions="res-default" ark="ark"/>',
            ),
            (
                lambda: excel2xml.make_resource("label", "restype", "id", iri="iri"),
                '<resource label="label" restype="restype" id="id" permissions="res-default" iri="iri"/>',
            ),
            (
                lambda: excel2xml.make_resource("label", "restype", "id", creation_date="2019-10-23T13:45:12Z"),
                (
                    '<resource label="label" restype="restype" id="id" permissions="res-default" '
                    'creation_date="2019-10-23T13:45:12Z"/>'
                ),
            ),
        ]

        for method, result in test_cases:
            xml_returned_as_element = method()
            xml_returned = etree.tostring(xml_returned_as_element, encoding="unicode")
            xml_returned = regex.sub(r" xmlns(:.+?)?=\".+?\"", "", xml_returned)
            self.assertEqual(result, xml_returned)

        self.assertWarns(
            DspToolsUserWarning, lambda: excel2xml.make_resource("label", "restype", "id", ark="ark", iri="iri")
        )
        with self.assertRaisesRegex(BaseError, "invalid creation date"):
            excel2xml.make_resource("label", "restype", "id", creation_date="2019-10-23T13:45:12")

    def test_create_json_excel_list_mapping(self) -> None:
        # We start with an Excel column that contains list nodes, but with spelling errors
        excel_column = [
            "  first noude ov testlist  ",
            "sekond noude ov testlist",
            " fierst sobnode , sekond sobnode , Third Node Ov Testliest",  # multiple entries per cell are possible
            "completely wrong spelling variant of 'first subnode' that needs manual correction",
        ]
        corrections = {
            "completely wrong spelling variant of 'first subnode' that needs manual correction": "first subnode"
        }
        testlist_mapping_returned = excel2xml.create_json_excel_list_mapping(
            path_to_json="testdata/json-project/test-project-systematic.json",
            list_name="testlist",
            excel_values=excel_column,
            sep=",",
            corrections=corrections,
        )
        testlist_mapping_expected = {
            "first noude ov testlist": "first node of testlist",
            "sekond noude ov testlist": "second node of testlist",
            "fierst sobnode": "first subnode",
            "sekond sobnode": "second subnode",
            "Third Node Ov Testliest": "third node of testlist",
            "third node ov testliest": "third node of testlist",
            "completely wrong spelling variant of 'first subnode' that needs manual correction": "first subnode",
        }
        self.assertDictEqual(testlist_mapping_returned, testlist_mapping_expected)

    def test_create_json_list_mapping(self) -> None:
        testlist_mapping_returned = excel2xml.create_json_list_mapping(
            path_to_json="testdata/json-project/test-project-systematic.json",
            list_name="testlist",
            language_label="en",
        )
        testlist_mapping_expected = {
            "First node of the Test-List": "first node of testlist",
            "first node of the test-list": "first node of testlist",
            "First Sub-Node": "first subnode",
            "first sub-node": "first subnode",
            "Second Sub-Node": "second subnode",
            "second sub-node": "second subnode",
            "Second node of the Test-List": "second node of testlist",
            "second node of the test-list": "second node of testlist",
            "Third node of the Test-List": "third node of testlist",
            "third node of the test-list": "third node of testlist",
        }
        self.assertDictEqual(testlist_mapping_returned, testlist_mapping_expected)


@pytest.mark.parametrize(
    ("start", "end", "expected"),
    [
        ("0:00:00.1", "0:00:02.345", "0.1:2.345"),
        ("00:00:00", "00:00:01", "0:1"),
        ("00:00:00", "01:00:00", "0:3600"),
        ("01:00:00", "01:00:00", "3600:3600"),
        ("01:30:00", "02:45:00", "5400:9900"),
        ("23:59:58", "23:59:59", "86398:86399"),
    ],
)
def test_create_interval_value_happy_path(start: str, end: str, expected: str) -> None:
    result = create_interval_value(start, end)
    assert result == expected, f"Expected {expected}, got {result}"


@pytest.mark.parametrize(
    ("start", "end"),
    [
        ("01:00", "02:00"),
        ("24:00:00", "23:59:59"),
        ("00:60:00", "02:00:00"),
        ("01:00:00", "02:60:00"),
        ("00:00:60", "01:00:00"),
        ("01:00:00", "02:00:60"),
        ("not:time", "01:00:00"),
        ("01:00:00", "not:time"),
    ],
)
def test_create_interval_value_error_cases(start: str, end: str) -> None:
    with pytest.raises(ValueError):  # noqa: PT011
        create_interval_value(start, end)


class TestEscapedChars:
    def test_single_br(self) -> None:
        test_text = "Text <br/> text after"
        res = _escape_reserved_chars(test_text)
        assert res == test_text

    def test_single_br_with_other(self) -> None:
        test_text = "Text <br/>> text after"
        expected = "Text <br/>&gt; text after"
        res = _escape_reserved_chars(test_text)
        assert res == expected

    def test_wrong_single_br(self) -> None:
        test_text = "Text <br//> text after"
        expected = "Text &lt;br//&gt; text after"
        res = _escape_reserved_chars(test_text)
        assert res == expected

    def test_emphasis(self) -> None:
        test_text = "Text before [<em>emphasis</em>] Text after illegal amp: &"
        expected = "Text before [<em>emphasis</em>] Text after illegal amp: &amp;"
        res = _escape_reserved_chars(test_text)
        assert res == expected

    def test_link(self) -> None:
        test_text = 'Before <a class="salsah-link" href="IRI:link:IRI">link</a> after'
        res = _escape_reserved_chars(test_text)
        assert res == test_text

    def test_illegal_angular(self) -> None:
        test_text = "Before <TagNotKnown>in tags</TagNotKnown> After."
        expected = "Before &lt;TagNotKnown&gt;in tags&lt;/TagNotKnown&gt; After."
        res = _escape_reserved_chars(test_text)
        assert res == expected


def _strip_namespace(element: etree._Element) -> str:
    """Removes the namespace from the XML element."""
    xml = etree.tostring(element, encoding="unicode")
    xml = regex.sub(r" xmlns(:.+?)?=\".+?\"", "", xml)
    return xml


if __name__ == "__main__":
    pytest.main([__file__])
