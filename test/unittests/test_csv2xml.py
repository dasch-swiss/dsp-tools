import random
import unittest
import re
from typing import Callable, Sequence, Union, Optional, Any

import pandas as pd
import numpy as np
from lxml import etree

from knora import csv2xml as c2x
from knora.dsplib.models.helpers import BaseError


def run_test(
    testcase: unittest.TestCase,
    prop: str,
    method: Callable[..., etree._Element],
    different_values: Sequence[Union[str, int, float, bool]],
    invalid_values: Sequence[Union[str, int, float, bool]],
    listname: Optional[str] = None
) -> None:
    """
    XML-properties have always a similar structure, and all make_*_prop() methods have some similar things to test. This
    method executes the tests in a parametrized way.

    Args:
        testcase: the object of the unittest class
        prop: the name of the property
        method: the make_*_prop() method
        different_values: some valid values
        invalid_values: some invalid values
        listname: to check the method make_list_prop, a list name is necessary
    """
    identical_values = [different_values[0]] * 3
    max = len(different_values)

    # prepare the test cases of the form (expected_xml, kwargs for the method to generate XML)
    testcases: list[tuple[str, dict[str, Any]]] = [
        (
            f'<{prop}-prop name=":test"><{prop} permissions="prop-default">{different_values[0 % max]}'
            f'</{prop}></{prop}-prop>',
            dict(name=":test", value=different_values[0 % max])
        ),
        (
            f'<{prop}-prop name=":test"><{prop} permissions="prop-restricted">{different_values[1 % max]}'
            f'</{prop}></{prop}-prop>',
            dict(name=":test", value=c2x.PropertyElement(different_values[1 % max], permissions="prop-restricted"))
        ),
        (
            f'<{prop}-prop name=":test"><{prop} permissions="prop-default" comment="comment">{different_values[2 % max]}'
            f'</{prop}></{prop}-prop>',
            dict(name=":test", value=c2x.PropertyElement(different_values[2 % max], comment="comment"))
        ),
        (
            f'<{prop}-prop name=":test"><{prop} permissions="prop-default">{identical_values[0]}</{prop}></{prop}-prop>',
            dict(name=":test", value=identical_values)
        ),
        (
            f'<{prop}-prop name=":test">'
            f'<{prop} permissions="prop-default">{identical_values[0]}</{prop}>'
            f'<{prop} permissions="prop-default">{identical_values[0]}</{prop}>'
            f'<{prop} permissions="prop-default">{identical_values[0]}</{prop}>'
            f'</{prop}-prop>',
            dict(name=":test", values=identical_values)
        ),
        (
            f'<{prop}-prop name=":test">'
            f'<{prop} permissions="prop-default">{different_values[3 % max]}</{prop}>'
            f'<{prop} permissions="prop-default">{different_values[4 % max]}</{prop}>'
            f'<{prop} permissions="prop-default">{different_values[5 % max]}</{prop}>'
            f'</{prop}-prop>',
            dict(name=":test", values=[different_values[3 % max], different_values[4 % max], different_values[5 % max]])
        ),
        (
            f'<{prop}-prop name=":test">'
            f'<{prop} permissions="prop-restricted" comment="comment1">{different_values[6 % max]}</{prop}>'
            f'<{prop} permissions="prop-default" comment="comment2">{different_values[7 % max]}</{prop}>'
            f'<{prop} permissions="prop-restricted" comment="comment3">{different_values[8 % max]}</{prop}>'
            f'</{prop}-prop>',
            dict(name=":test", values=[
                c2x.PropertyElement(different_values[6 % max], permissions="prop-restricted", comment="comment1"),
                c2x.PropertyElement(different_values[7 % max], permissions="prop-default", comment="comment2"),
                c2x.PropertyElement(different_values[8 % max], permissions="prop-restricted", comment="comment3")
            ])
        )
    ]

    # run the test cases
    for tc in testcases:
        xml_expected = tc[0]
        kwargs_to_generate_xml = tc[1]
        if prop == "list":
            # a <list-prop> has the additional attribute list="listname"
            xml_expected = re.sub(r"<list-prop", f"<list-prop list=\"{listname}\"", xml_expected)
            kwargs_to_generate_xml["list_name"] = listname
        elif prop == "text":
            # a <text> has the additional attribute encoding="utf8" (the other encoding, xml, is tested in the caller)
            xml_expected = re.sub(r"<text (permissions=\".+?\")( comment=\".+?\")?", "<text \\1\\2 encoding=\"utf8\"",
                                  xml_expected)
        xml_received = method(**kwargs_to_generate_xml)
        xml_received = etree.tostring(xml_received, encoding="unicode")
        xml_received = re.sub(r" xmlns(:.+?)?=\".+?\"", "", xml_received)
        testcase.assertEqual(xml_expected, xml_received,
                             msg=f"Method {method.__name__} failed with kwargs {kwargs_to_generate_xml}")

    # perform illegal actions
    # pass iterable of different values as param "value" (instead of iterable of identical values, which would be legal)
    kwargs_value_with_different_values = dict(name=":test", value=different_values)
    if prop == "list":
        kwargs_value_with_different_values["list_name"] = listname
    with testcase.assertRaises(BaseError, msg=f"Method {method.__name__} failed with kwargs "
                                              f"{kwargs_value_with_different_values}"):
        method(**kwargs_value_with_different_values)

    # pass invalid values as param "value"
    for invalid_value in invalid_values:
        kwargs_invalid_value = dict(name=":test", value=invalid_value)
        if prop == "list":
            kwargs_invalid_value["list_name"] = listname
        with testcase.assertRaises(BaseError, msg=f"Method {method.__name__} failed with kwargs {kwargs_invalid_value}"):
            method(**kwargs_invalid_value)



class TestCsv2xml(unittest.TestCase):

    def test_make_xsd_id_compatible(self) -> None:
        teststring = "0aüZ/_-äöü1234567890?`^':.;+*ç%&/()=±“#Ç[]|{}≠"

        # test that the results are distinct from each other
        results = {c2x.make_xsd_id_compatible(teststring) for _ in range(10)}
        self.assertTrue(len(results) == 10)

        # test that the results are valid xsd:ids
        for result in results:
            self.assertTrue(re.search(r"^[a-zA-Z_][\w.-]*$", result))

        # test that invalid inputs lead to an error
        self.assertRaises(BaseError, c2x.make_xsd_id_compatible, 0)
        self.assertRaises(BaseError, c2x.make_xsd_id_compatible, "n/a")
        self.assertRaises(BaseError, c2x.make_xsd_id_compatible, None)
        self.assertRaises(BaseError, c2x.make_xsd_id_compatible, "")
        self.assertRaises(BaseError, c2x.make_xsd_id_compatible, " ")
        self.assertRaises(BaseError, c2x.make_xsd_id_compatible, ".")


    def test_check_notna(self) -> None:
        na_values = [None, pd.NA, np.nan, "", "  ", "-", ",", ".", "*", "!", " \n\t ", "N/A", "n/a", "<NA>", ["a", "b"],
                     pd.array(["a", "b"]), np.array([0, 1])]
        for na_value in na_values:
            self.assertFalse(c2x.check_notna(na_value), msg=f"Failed na_value: {na_value}")

        notna_values = [1, 0.1, True, False, "True", "False", r" \n\t ", "0", "_"]
        notna_values.extend([c2x.PropertyElement(x) for x in notna_values])
        for notna_value in notna_values:
            self.assertTrue(c2x.check_notna(notna_value), msg=f"Failed notna_value: {notna_value}")


    def test_find_date_in_string(self) -> None:

        # template: 2021-01-01 | 2015_01_02
        self.assertEqual(c2x.find_date_in_string("text 1492-10-12, text"), "GREGORIAN:CE:1492-10-12:CE:1492-10-12")
        self.assertEqual(c2x.find_date_in_string("Text 0476-09-04. text"), "GREGORIAN:CE:0476-09-04:CE:0476-09-04")
        self.assertEqual(c2x.find_date_in_string("Text (0476-09-04) text"), "GREGORIAN:CE:0476-09-04:CE:0476-09-04")
        self.assertWarns(UserWarning, lambda: c2x.find_date_in_string("Text [1492-10-32?] text"))

        # template: 31.4.2021 | 5/11/2021
        self.assertEqual(c2x.find_date_in_string("Text (30.4.2021) text"), "GREGORIAN:CE:2021-04-30:CE:2021-04-30")
        self.assertEqual(c2x.find_date_in_string("Text (5/11/2021) text"), "GREGORIAN:CE:2021-11-05:CE:2021-11-05")

        # template: 26.2.-24.3.1948
        self.assertEqual(c2x.find_date_in_string("Text ...2193_01_26... text"), "GREGORIAN:CE:2193-01-26:CE:2193-01-26")
        self.assertEqual(c2x.find_date_in_string("Text -2193_01_26- text"), "GREGORIAN:CE:2193-01-26:CE:2193-01-26")
        self.assertWarns(UserWarning, lambda: c2x.find_date_in_string("Text 2193_02_30 text"))

        # template: 27.-28.1.1900
        self.assertEqual(c2x.find_date_in_string("Text _1.3. - 25.4.2022_ text"), "GREGORIAN:CE:2022-03-01:CE:2022-04-25")
        self.assertEqual(c2x.find_date_in_string("Text (01.03. - 25.04.2022) text"), "GREGORIAN:CE:2022-03-01:CE:2022-04-25")
        self.assertEqual(c2x.find_date_in_string("Text 28.2.-1.12.1515 text"), "GREGORIAN:CE:1515-02-28:CE:1515-12-01")
        self.assertEqual(c2x.find_date_in_string("Text 28.2.-1.12.1515 text"), "GREGORIAN:CE:1515-02-28:CE:1515-12-01")
        self.assertWarns(UserWarning, lambda: c2x.find_date_in_string("Text 28.2.-26.2.1515 text"))

        # template: 1.12.1973 - 6.1.1974
        self.assertEqual(c2x.find_date_in_string("Text 25.-26.2.0800 text"), "GREGORIAN:CE:0800-02-25:CE:0800-02-26")
        self.assertEqual(c2x.find_date_in_string("Text 25. - 26.2.0800 text"), "GREGORIAN:CE:0800-02-25:CE:0800-02-26")
        self.assertEqual(c2x.find_date_in_string("Text 25. - 26.2.0800 text"), "GREGORIAN:CE:0800-02-25:CE:0800-02-26")
        self.assertWarns(UserWarning, lambda: c2x.find_date_in_string("Text 25.-24.2.0800 text"))

        # template: 31.4.2021 | 5/11/2021
        self.assertEqual(c2x.find_date_in_string("Text 1.9.2022-3.1.2024 text"), "GREGORIAN:CE:2022-09-01:CE:2024-01-03")
        self.assertEqual(c2x.find_date_in_string("Text 25.12.2022 - 3.1.2024 text"), "GREGORIAN:CE:2022-12-25:CE:2024-01-03")
        self.assertWarns(UserWarning, lambda: c2x.find_date_in_string("Text 25.12.2022-03.01.2022 text"))
        self.assertEqual(c2x.find_date_in_string("Text 25/12/2022-03/01/2024 text"), "GREGORIAN:CE:2022-12-25:CE:2024-01-03")
        self.assertEqual(c2x.find_date_in_string("Text 25/12/2022 - 3/1/2024 text"), "GREGORIAN:CE:2022-12-25:CE:2024-01-03")
        self.assertWarns(UserWarning, lambda: c2x.find_date_in_string("Text 25/12/2022-03/01/2022 text"))

        # template: February 9, 1908 | Dec 5,1908
        self.assertEqual(c2x.find_date_in_string("Text Jan 26, 1993 text"), "GREGORIAN:CE:1993-01-26:CE:1993-01-26")
        self.assertEqual(c2x.find_date_in_string("Text February26,2051 text"), "GREGORIAN:CE:2051-02-26:CE:2051-02-26")
        self.assertEqual(c2x.find_date_in_string("Text Sept 1, 1000 text"), "GREGORIAN:CE:1000-09-01:CE:1000-09-01")
        self.assertEqual(c2x.find_date_in_string("Text October 01, 1000 text"), "GREGORIAN:CE:1000-10-01:CE:1000-10-01")
        self.assertEqual(c2x.find_date_in_string("Text Nov 6,1000 text"), "GREGORIAN:CE:1000-11-06:CE:1000-11-06")
        self.assertEqual(c2x.find_date_in_string("Text Nov 6,1000 text"), "GREGORIAN:CE:1000-11-06:CE:1000-11-06")

        # template: 1907
        self.assertEqual(c2x.find_date_in_string("Text 1848 text"), "GREGORIAN:CE:1848:CE:1848")

        # template: 1849/50 | 1845-50 | 1849/1850
        self.assertEqual(c2x.find_date_in_string("Text 1849/1850? text"), "GREGORIAN:CE:1849:CE:1850")
        self.assertEqual(c2x.find_date_in_string("Text 1845-1850, text"), "GREGORIAN:CE:1845:CE:1850")
        self.assertEqual(c2x.find_date_in_string("Text 1849/50. text"), "GREGORIAN:CE:1849:CE:1850")
        self.assertEqual(c2x.find_date_in_string("Text (1845-50) text"), "GREGORIAN:CE:1845:CE:1850")
        self.assertEqual(c2x.find_date_in_string("Text [1849/1850] text"), "GREGORIAN:CE:1849:CE:1850")


    def test_check_and_prepare_values(self) -> None:
        identical_values = ["Test", "Test", "Test"]
        different_values: list[Union[str, int, float]] = [1, 1.0, "1", "1.0", " 1 "]
        values_with_nas: list[Union[str, int, float]] = ["test", "", 1, np.nan, 0]

        values_output = c2x._check_and_prepare_values(value=identical_values,
                                                      values=None,
                                                      name="")
        self.assertEqual([x.value for x in values_output], list(set(identical_values)))

        values_output = c2x._check_and_prepare_values(value=[c2x.PropertyElement(x) for x in identical_values],
                                                      values=None,
                                                      name="")
        self.assertEqual([x.value for x in values_output], list(set(identical_values)))

        values_output = c2x._check_and_prepare_values(value=None,
                                                      values=identical_values,
                                                      name="")
        self.assertEqual([x.value for x in values_output], identical_values)

        values_output = c2x._check_and_prepare_values(value=None,
                                                      values=[c2x.PropertyElement(x) for x in identical_values],
                                                      name="")
        self.assertEqual([x.value for x in values_output], identical_values)

        values_output = c2x._check_and_prepare_values(value=None,
                                                      values=different_values,
                                                      name="")
        self.assertEqual([x.value for x in values_output], different_values)

        values_output = c2x._check_and_prepare_values(value=None,
                                                      values=[c2x.PropertyElement(x) for x in different_values],
                                                      name="")
        self.assertEqual([x.value for x in values_output], different_values)

        values_output = c2x._check_and_prepare_values(value=None,
                                                      values=values_with_nas,
                                                      name="")
        self.assertEqual([x.value for x in values_output], ["test", 1, 0])

        self.assertRaises(BaseError, lambda: c2x._check_and_prepare_values(value=different_values,
                                                                           values=None,
                                                                           name=""))
        self.assertRaises(BaseError, lambda: c2x._check_and_prepare_values(value=[c2x.PropertyElement(x) for x in different_values],
                                                                           values=None,
                                                                           name=""))

        self.assertRaises(BaseError, lambda: c2x._check_and_prepare_values(value=1,
                                                                           values=[1],
                                                                           name=""))
        self.assertRaises(BaseError, lambda: c2x._check_and_prepare_values(value=np.nan,
                                                                           values=[np.nan],
                                                                           name=""))


    def test_make_boolean_prop(self) -> None:
        true_values = [True, "true", "True", "1", 1, "yes", "Yes"]
        len_of_base_values = len(true_values)
        true_values.extend([c2x.PropertyElement(x) for x in true_values])
        for _iterable in [tuple, list, set]:
            # randomly choose 3 elements among the base values
            equivalent_values = [true_values[i] for i in random.choices(range(len_of_base_values), k=3)]
            equivalent_propelems = [c2x.PropertyElement(x) for x in equivalent_values]
            true_values.append(_iterable(equivalent_values))
            true_values.append(_iterable(equivalent_propelems))

        false_values = [False, "false", "False", "0", 0, "no", "No"]
        len_of_base_values = len(false_values)
        false_values.extend([c2x.PropertyElement(x) for x in false_values])
        for _iterable in [tuple, list, set]:
            # randomly choose 3 elements among the base values
            equivalent_values = [false_values[i] for i in random.choices(range(len_of_base_values), k=3)]
            equivalent_propelems = [c2x.PropertyElement(x) for x in equivalent_values]
            false_values.append(_iterable(equivalent_values))
            false_values.append(_iterable(equivalent_propelems))

        unsupported_values = [np.nan, "N/A", "NA", "na", "None", "", " ", "-", None,
                              [True, False], [0, 0, 1], ["True", "false"]]

        true_xml_expected = '<boolean-prop name=":test"><boolean permissions="prop-default">true</boolean></boolean-prop>'
        false_xml_expected = '<boolean-prop name=":test"><boolean permissions="prop-default">false</boolean></boolean-prop>'

        for true_value in true_values:
            true_xml = etree.tostring(c2x.make_boolean_prop(":test", true_value), encoding="unicode")
            true_xml = re.sub(r" xmlns(:.+?)?=\".+?\"", "", true_xml)
            self.assertEqual(true_xml, true_xml_expected, msg=f"Failed with '{true_value}'")
        for false_value in false_values:
            false_xml = etree.tostring(c2x.make_boolean_prop(":test", false_value), encoding="unicode")
            false_xml = re.sub(r" xmlns(:.+?)?=\".+?\"", "", false_xml)
            self.assertEqual(false_xml, false_xml_expected, msg=f"Failed with '{false_value}'")
        for unsupported_value in unsupported_values:
            self.assertRaises(BaseError, lambda: c2x.make_boolean_prop(":test", unsupported_value))


    def test_make_color_prop(self) -> None:
        prop = "color"
        method = c2x.make_color_prop
        different_values = ["#012345", "#abcdef", "#0B0B0B", "#AAAAAA", "#1a2b3c"]
        invalid_values = ["#0000000", "#00000G"]
        run_test(self, prop, method, different_values, invalid_values)


    def test_make_date_prop(self) -> None:
        prop = "date"
        method = c2x.make_date_prop
        different_values = ["CE:1849:CE:1850", "GREGORIAN:1848-01:1849-02", "2022",
                            "GREGORIAN:CE:0476-09-04:CE:0476-09-04", "GREGORIAN:CE:2014-01-31"]
        invalid_values = ["GREGORIAN:CE:0476-09-04:CE:09-04", "GREGORIAN:CE:0476-09-010:CE:0476-09-04"]
        run_test(self, prop, method, different_values, invalid_values)


    def test_make_decimal_prop(self) -> None:
        prop = "decimal"
        method = c2x.make_decimal_prop
        different_values = ["3.14159", 3.14159, .1, 100.0, "100.0"]
        invalid_values = ["100", ".1", 100]
        run_test(self, prop, method, different_values, invalid_values)


    def test_make_geometry_prop(self) -> None:
        prop = "geometry"
        method = c2x.make_geometry_prop
        different_values = [
            '{"type": "rectangle", "lineColor": "#ff3333", "lineWidth": 2, "points": [{"x": 0.08, "y": 0.16}, {"x": 0.73, "y": 0.72}], "original_index": 0}',
            '{"type": "rectangle", "lineColor": "#000000", "lineWidth": 1, "points": [{"x": 0.10, "y": 0.10}, {"x": 0.10, "y": 0.10}], "original_index": 1}',
        ]
        invalid_values = ["100", 100, [0], '{"type": "polygon"}']
        run_test(self, prop, method, different_values, invalid_values)


    def test_make_geoname_prop(self) -> None:
        prop = "geoname"
        method = c2x.make_geoname_prop
        different_values = [1283416, "1283416", 71, "71", 10000000, "10000000"]
        invalid_values = ["text", 10.0, ["text"]]
        run_test(self, prop, method, different_values, invalid_values)


    def test_make_integer_prop(self) -> None:
        prop = "integer"
        method = c2x.make_integer_prop
        different_values = [1283416, "1283416", 71, "71", 0, "0"]
        invalid_values = ["text", 10.0, ["text"]]
        run_test(self, prop, method, different_values, invalid_values)


    def test_make_interval_prop(self) -> None:
        prop = "interval"
        method = c2x.make_interval_prop
        different_values = ["+.1:+.9", "10:20", "1.5:2.5", "-.1:5", "-10.0:-5.1"]
        invalid_values = ["text", 10.0, ["text"], "10:", ":1"]
        run_test(self, prop, method, different_values, invalid_values)


    def test_make_list_prop(self) -> None:
        prop = "list"
        method = c2x.make_list_prop
        different_values = ["first-node", "second-node", "third-node", "fourth-node", "fifth-node"]
        invalid_values = [10.0]
        run_test(self, prop, method, different_values, invalid_values, ":myList")


    def test_make_resptr_prop(self) -> None:
        prop = "resptr"
        method = c2x.make_resptr_prop
        different_values = ["resource_1", "resource_2", "resource_3", "resource_4", "resource_5"]
        invalid_values = [True, 10.0, 5]
        run_test(self, prop, method, different_values, invalid_values)


    def test_make_text_prop(self) -> None:
        prop = "text"
        method = c2x.make_text_prop
        different_values = ["text_1", "text_2", "text_3", "text_4", "text_5"]
        invalid_values = [True, 10.0, 5]
        run_test(self, prop, method, different_values, invalid_values)

        # test encoding="xml"
        xml_expected_1 = '<text-prop name=":test"><text permissions="prop-default" encoding="xml">a</text></text-prop>'
        xml_received_1 = c2x.make_text_prop(":test", c2x.PropertyElement(value="a", encoding="xml"))
        xml_received_1 = etree.tostring(xml_received_1, encoding="unicode")
        xml_received_1 = re.sub(r" xmlns(:.+?)?=\".+?\"", "", xml_received_1)
        self.assertEqual(xml_expected_1, xml_received_1)

        # encoding="unicode" must raise an error
        self.assertRaises(BaseError, lambda: c2x.make_text_prop(":test", c2x.PropertyElement(value="a", encoding="unicode")))


    def test_make_time_prop(self) -> None:
        prop = "time"
        method = c2x.make_time_prop
        different_values = [
            "2019-10-23T13:45:12.01-14:00",
            "2019-10-23T13:45:12-14:00",
            "2019-10-23T13:45:12Z",
            "2019-10-23T13:45:12-13:30",
            "2019-10-23T13:45:12+01:00",
            "2019-10-23T13:45:12.1111111+01:00",
            "2019-10-23T13:45:12.123456789012Z",
        ]
        invalid_values = [True, 10.0, 5, "2019-10-2", "CE:1849:CE:1850", "2019-10-23T13:45:12.1234567890123Z", "2022",
                          "GREGORIAN:CE:2014-01-31"]
        run_test(self, prop, method, different_values, invalid_values)


    def test_make_uri_prop(self) -> None:
        prop = "uri"
        method = c2x.make_uri_prop
        different_values = [
            "https://www.test-case.ch/",
            "https://reg-exr.com:3000",
            "https://reg-exr.com:3000/path/to/file",
            "https://reg-exr.com:3000/path/to/file#fragment",
            "https://reg-exr.com:3000/path/to/file?query=test",
            "https://reg-exr.com:3000/path/to/file?query=test#fragment",
            "https://reg-exr.com/path/to/file?query=test#fragment",
            "http://www.168.1.1.0/path",
            "http://www.168.1.1.0:4200/path",
            "http://[2001:0db8:0000:0000:0000:8a2e:0370:7334]:4200/path",
            "https://en.wikipedia.org/wiki/Haiku#/media/File:Basho_Horohoroto.jpg"
        ]
        invalid_values = ["https:", 10.0, 5, "www.test.com"]
        run_test(self, prop, method, different_values, invalid_values)


if __name__ == "__main__":
    unittest.main()
