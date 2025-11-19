import unittest
import warnings
from collections.abc import Callable
from collections.abc import Sequence
from pathlib import Path
from typing import Any
from typing import Optional
from typing import Union

import numpy as np
import pandas as pd
import pytest
import regex
from lxml import etree

from dsp_tools.commands import excel2xml
from dsp_tools.error.custom_warnings import DspToolsUserWarning
from dsp_tools.error.exceptions import BaseError

# ruff: noqa: PT009 (pytest-unittest-assertion) (remove this line when pytest is used instead of unittest)
# ruff: noqa: PT027 (pytest-unittest-raises-assertion) (remove this line when pytest is used instead of unittest)


class TestPropsGeneral(unittest.TestCase):
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
                        f'<{prop}-prop name=":test"><{prop} permissions="public">{val}</{prop}></{prop}-prop>',
                        dict(name=":test", value=val),
                    ),
                    (
                        f'<{prop}-prop name=":test"><{prop} permissions="private">{val}</{prop}></{prop}-prop>',
                        dict(name=":test", value=excel2xml.PropertyElement(val, permissions="private")),
                    ),
                    (
                        f'<{prop}-prop name=":test"><{prop} permissions="private" comment="comment">{val}'
                        f"</{prop}></{prop}-prop>",
                        dict(
                            name=":test",
                            value=excel2xml.PropertyElement(val, permissions="private", comment="comment"),
                        ),
                    ),
                ]
            )
        # pass the elements of different_values group-wise
        testcases.extend(
            [
                (
                    f'<{prop}-prop name=":test">'
                    f'<{prop} permissions="public">{identical_values[0]}</{prop}>'
                    f'<{prop} permissions="public">{identical_values[1]}</{prop}>'
                    f'<{prop} permissions="public">{identical_values[2]}</{prop}>'
                    f"</{prop}-prop>",
                    dict(name=":test", value=identical_values),
                ),
                (
                    f'<{prop}-prop name=":test">'
                    f'<{prop} permissions="public">{different_values[0 % maximum]}</{prop}>'
                    f'<{prop} permissions="public">{different_values[1 % maximum]}</{prop}>'
                    f'<{prop} permissions="public">{different_values[2 % maximum]}</{prop}>'
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
                    f'<{prop} permissions="private" comment="comment1">{different_values[3 % maximum]}</{prop}>'
                    f'<{prop} permissions="public" comment="comment2">{different_values[4 % maximum]}</{prop}>'
                    f'<{prop} permissions="private" comment="comment3">{different_values[5 % maximum]}</{prop}>'
                    f"</{prop}-prop>",
                    dict(
                        name=":test",
                        value=[
                            excel2xml.PropertyElement(
                                different_values[3 % maximum], permissions="private", comment="comment1"
                            ),
                            excel2xml.PropertyElement(
                                different_values[4 % maximum], permissions="public", comment="comment2"
                            ),
                            excel2xml.PropertyElement(
                                different_values[5 % maximum], permissions="private", comment="comment3"
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
            '{"type": "rectangle", "lineWidth": 2, '
            '"points": [{"x": 0.08, "y": 0.16}, {"x": 0.73, "y": 0.72}], "original_index": 0}',
            '{"type": "rectangle", "lineWidth": 1, '
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

    def test_make_text_prop(self) -> None:
        prop = "text"
        method = excel2xml.make_text_prop
        different_values = ["text_1", " ", "!", "?", "-", "_", "None"]
        invalid_values = [True, 10.0, 5, ""]
        with warnings.catch_warnings(record=True) as caught_warnings:
            self.run_test(prop, method, different_values, invalid_values)
            assert len(caught_warnings) == 3
        self.assertRaises(
            BaseError,
            lambda: excel2xml.make_text_prop(":test", excel2xml.PropertyElement(value="a", encoding="unicode")),
        )

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
            pd.NA,
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

        true_xml_expected = '<boolean-prop name=":test"><boolean permissions="public">true</boolean></boolean-prop>'
        false_xml_expected = '<boolean-prop name=":test"><boolean permissions="public">false</boolean></boolean-prop>'

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


class TestTextProp:
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
        # the following will be displayed as "ä €" in the XML and in DSP-APP  # noqa: RUF003 (ambiguous character)
        original = "<p>text &auml;&nbsp;&euro; text</p>"
        expected = "<p>text ä\xa0€ text</p>"
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


class TestBitstreamProp:
    def test_make_bitstream_prop_from_string(self) -> None:
        res = excel2xml.make_bitstream_prop("foo/bar/baz.txt")
        assert str(res.tag).endswith("bitstream")
        assert res.attrib["permissions"] == "public"
        assert res.text == "foo/bar/baz.txt"

    def test_make_bitstream_prop_from_path(self) -> None:
        res = excel2xml.make_bitstream_prop(Path("foo/bar/baz.txt"))
        assert str(res.tag).endswith("bitstream")
        assert res.attrib["permissions"] == "public"
        assert res.text == "foo/bar/baz.txt"

    def test_make_bitstream_prop_custom_permissions(self) -> None:
        res = excel2xml.make_bitstream_prop("foo/bar/baz.txt", "private")
        assert str(res.tag).endswith("bitstream")
        assert res.attrib["permissions"] == "private"
        assert res.text == "foo/bar/baz.txt"

    def test_make_bitstream_prop_valid_file(self) -> None:
        with warnings.catch_warnings():
            warnings.filterwarnings("error", category=UserWarning)
            try:
                res = excel2xml.make_bitstream_prop("testdata/bitstreams/test.jpg", check=True)
            except UserWarning as e:
                raise AssertionError from e
        assert str(res.tag).endswith("bitstream")
        assert res.attrib["permissions"] == "public"
        assert res.text == "testdata/bitstreams/test.jpg"

    def test_make_bitstream_prop_invalid_file(self) -> None:
        with pytest.warns(DspToolsUserWarning, match=regex.escape("Failed validation in bitstream tag")):
            res = excel2xml.make_bitstream_prop("foo/bar/baz.txt", check=True)
        assert str(res.tag).endswith("bitstream")
        assert res.attrib["permissions"] == "public"
        assert res.text == "foo/bar/baz.txt"


@pytest.mark.parametrize(
    ("tag", "func"),
    [("isSegmentOf", excel2xml.make_isSegmentOf_prop), ("relatesTo", excel2xml.make_relatesTo_prop)],
)
class Test_isSegmentOf_and_relatesTo_Prop:
    def test_defaults(self, tag: str, func: Callable[..., etree._Element]) -> None:
        res = func("target_id")
        assert str(res.tag).endswith(tag)
        assert res.attrib["permissions"] == "public"
        assert "comment" not in res.attrib
        assert res.text == "target_id"

    def test_custom_params(self, tag: str, func: Callable[..., etree._Element]) -> None:
        res = func("target_id", "private", "my comment")
        assert str(res.tag).endswith(tag)
        assert res.attrib["permissions"] == "private"
        assert res.attrib["comment"] == "my comment"
        assert res.text == "target_id"

    def test_invalid(self, tag: str, func: Callable[..., etree._Element]) -> None:
        with pytest.warns(DspToolsUserWarning):
            res = func("<NA>")
        assert str(res.tag).endswith(tag)
        assert res.attrib["permissions"] == "public"
        assert "comment" not in res.attrib
        assert res.text == "<NA>"


class Test_hasSegmentBounds_Prop:
    def test_defaults(self) -> None:
        res = excel2xml.make_hasSegmentBounds_prop(100, 200)
        assert str(res.tag).endswith("hasSegmentBounds")
        assert res.attrib["permissions"] == "public"
        assert "comment" not in res.attrib
        assert res.attrib["segment_start"] == "100"
        assert res.attrib["segment_end"] == "200"
        assert res.text is None

    def test_custom_params(self) -> None:
        res = excel2xml.make_hasSegmentBounds_prop(10, 20, "private", "my comment")
        assert str(res.tag).endswith("hasSegmentBounds")
        assert res.attrib["permissions"] == "private"
        assert res.attrib["comment"] == "my comment"
        assert res.attrib["segment_start"] == "10"
        assert res.attrib["segment_end"] == "20"
        assert res.text is None

    def test_floats(self) -> None:
        res = excel2xml.make_hasSegmentBounds_prop(1.2, 3.4)
        assert str(res.tag).endswith("hasSegmentBounds")
        assert res.attrib["permissions"] == "public"
        assert "comment" not in res.attrib
        assert res.attrib["segment_start"] == "1.2"
        assert res.attrib["segment_end"] == "3.4"
        assert res.text is None

    def test_nums_as_strings(self) -> None:
        res = excel2xml.make_hasSegmentBounds_prop("1.2", "3")  # type: ignore[arg-type]
        assert str(res.tag).endswith("hasSegmentBounds")
        assert res.attrib["permissions"] == "public"
        assert "comment" not in res.attrib
        assert res.attrib["segment_start"] == "1.2"
        assert res.attrib["segment_end"] == "3.0"  # silent conversion to float is okay, since the db stores it that way
        assert res.text is None

    def test_start_less_than_end(self) -> None:
        with pytest.warns(DspToolsUserWarning, match=regex.escape("must be less than")):
            res = excel2xml.make_hasSegmentBounds_prop(5, 3)
        assert str(res.tag).endswith("hasSegmentBounds")
        assert res.attrib["permissions"] == "public"
        assert "comment" not in res.attrib
        assert res.attrib["segment_start"] == "5"
        assert res.attrib["segment_end"] == "3"
        assert res.text is None

    def test_not_a_number(self) -> None:
        with pytest.warns(DspToolsUserWarning, match=regex.escape("must be integers or floats")):
            res = excel2xml.make_hasSegmentBounds_prop(segment_start="foo", segment_end=2)  # type: ignore[arg-type]
        assert str(res.tag).endswith("hasSegmentBounds")
        assert res.attrib["permissions"] == "public"
        assert "comment" not in res.attrib
        assert res.attrib["segment_start"] == "foo"
        assert res.attrib["segment_end"] == "2"
        assert res.text is None


@pytest.mark.parametrize(
    ("tag", "func"),
    [("hasTitle", excel2xml.make_hasTitle_prop), ("hasKeyword", excel2xml.make_hasKeyword_prop)],
)
class Test_hasTitle_hasKeyword:
    def test_defaults(self, tag: str, func: Callable[..., etree._Element]) -> None:
        res = func("my text ...")
        assert str(res.tag).endswith(tag)
        assert res.attrib["permissions"] == "public"
        assert "comment" not in res.attrib
        assert res.text == "my text ..."

    def test_custom_params(self, tag: str, func: Callable[..., etree._Element]) -> None:
        res = func("my text ...", "private", "my comment")
        assert str(res.tag).endswith(tag)
        assert res.attrib["permissions"] == "private"
        assert res.attrib["comment"] == "my comment"
        assert res.text == "my text ..."

    def test_invalid(self, tag: str, func: Callable[..., etree._Element]) -> None:
        with pytest.warns(DspToolsUserWarning):
            res = func("<NA>")
        assert str(res.tag).endswith(tag)
        assert res.attrib["permissions"] == "public"
        assert "comment" not in res.attrib
        assert res.text == "<NA>"


@pytest.mark.parametrize(
    ("tag", "func"),
    [("hasComment", excel2xml.make_hasComment_prop), ("hasDescription", excel2xml.make_hasDescription_prop)],
)
class Test_hasComment_hasDescription:
    def test_defaults(self, tag: str, func: Callable[..., etree._Element]) -> None:
        res = func("my text ...")
        assert str(res.tag).endswith(tag)
        assert res.attrib["permissions"] == "public"
        assert "comment" not in res.attrib
        assert res.text == "my text ..."

    def test_custom_params(self, tag: str, func: Callable[..., etree._Element]) -> None:
        res = func("my text ...", "private", "my comment")
        assert str(res.tag).endswith(tag)
        assert res.attrib["permissions"] == "private"
        assert res.attrib["comment"] == "my comment"
        assert res.text == "my text ..."

    def test_invalid(self, tag: str, func: Callable[..., etree._Element]) -> None:
        with pytest.warns(DspToolsUserWarning):
            res = func("<NA>")
        assert str(res.tag).endswith(tag)
        assert res.attrib["permissions"] == "public"
        assert "comment" not in res.attrib
        assert res.text == "<NA>"

    def test_richtext(self, tag: str, func: Callable[..., etree._Element]) -> None:
        text = "<p>my <strong>bold <em>and italiziced</em></strong> text ...</p>"
        res = func(text)
        assert str(res.tag).endswith(tag)
        assert res.attrib["permissions"] == "public"
        assert "comment" not in res.attrib
        serialized_text = regex.sub(rf"<ns0:{tag} .+?>|</ns0:{tag}>", "", etree.tostring(res, encoding="unicode"))
        assert serialized_text == text

    def test_invalid_richtext(self, tag: str, func: Callable[..., etree._Element]) -> None:  # noqa: ARG002 (unused arg)
        text = "<p> my <pseudo> & xml </>"
        with pytest.raises(BaseError, match=regex.escape("must be well-formed")):
            func(text)
