import os
import re
import time
import unittest
from typing import Callable, Sequence, Union, Optional, Any

import numpy as np
import pytest
from lxml import etree

from src import excel2xml
from src.dsp_tools.models.helpers import BaseError


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
    testcases: list[tuple[str, dict[str, Any]]] = list()
    # pass every element of different_values separately
    for val in different_values:
        testcases.extend(
            [
                (
                    f'<{prop}-prop name=":test"><{prop} permissions="prop-default">{val}'
                    f'</{prop}></{prop}-prop>',
                    dict(name=":test", value=val)
                ),
                (
                    f'<{prop}-prop name=":test"><{prop} permissions="prop-restricted">{val}'
                    f'</{prop}></{prop}-prop>',
                    dict(name=":test", value=excel2xml.PropertyElement(val, permissions="prop-restricted"))
                ),
                (
                    f'<{prop}-prop name=":test"><{prop} permissions="prop-restricted" comment="comment">{val}'
                    f'</{prop}></{prop}-prop>',
                    dict(name=":test", value=excel2xml.PropertyElement(val, permissions="prop-restricted", comment="comment"))
                )
            ]
        )
    # pass the elements of different_values group-wise
    testcases.extend([
        (
            f'<{prop}-prop name=":test">'
            f'<{prop} permissions="prop-default">{identical_values[0]}</{prop}>'
            f'<{prop} permissions="prop-default">{identical_values[1]}</{prop}>'
            f'<{prop} permissions="prop-default">{identical_values[2]}</{prop}>'
            f'</{prop}-prop>',
            dict(name=":test", value=identical_values)
        ),
        (
            f'<{prop}-prop name=":test">'
            f'<{prop} permissions="prop-default">{different_values[0 % max]}</{prop}>'
            f'<{prop} permissions="prop-default">{different_values[1 % max]}</{prop}>'
            f'<{prop} permissions="prop-default">{different_values[2 % max]}</{prop}>'
            f'</{prop}-prop>',
            dict(name=":test", value=[different_values[0 % max], different_values[1 % max], different_values[2 % max]])
        ),
        (
            f'<{prop}-prop name=":test">'
            f'<{prop} permissions="prop-restricted" comment="comment1">{different_values[3 % max]}</{prop}>'
            f'<{prop} permissions="prop-default" comment="comment2">{different_values[4 % max]}</{prop}>'
            f'<{prop} permissions="prop-restricted" comment="comment3">{different_values[5 % max]}</{prop}>'
            f'</{prop}-prop>',
            dict(name=":test", value=[
                excel2xml.PropertyElement(different_values[3 % max], permissions="prop-restricted", comment="comment1"),
                excel2xml.PropertyElement(different_values[4 % max], permissions="prop-default", comment="comment2"),
                excel2xml.PropertyElement(different_values[5 % max], permissions="prop-restricted", comment="comment3")
            ])
        )
    ])

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
        xml_returned = method(**kwargs_to_generate_xml)
        xml_returned = etree.tostring(xml_returned, encoding="unicode")
        xml_returned = re.sub(r" xmlns(:.+?)?=\".+?\"", "", xml_returned)  # remove all xml namespace declarations
        xml_returned = xml_returned.replace("&lt;", "<")
        xml_returned = xml_returned.replace("&gt;", ">")
        testcase.assertEqual(xml_expected, xml_returned,
                             msg=f"Method {method.__name__} failed with kwargs {kwargs_to_generate_xml}")

    # perform illegal actions
    # pass invalid values as param "value"
    for invalid_value in invalid_values:
        kwargs_invalid_value = dict(name=":test", value=invalid_value)
        if prop == "list":
            kwargs_invalid_value["list_name"] = listname
        with testcase.assertRaises(BaseError, msg=f"Method {method.__name__} failed with kwargs {kwargs_invalid_value}"):
            method(**kwargs_invalid_value)



class TestExcel2xml(unittest.TestCase):

    def test_make_xsd_id_compatible(self) -> None:
        teststring = "0aüZ/_-äöü1234567890?`^':.;+*ç%&/()=±“#Ç[]|{}≠"

        # test that the results are distinct from each other
        results = {excel2xml.make_xsd_id_compatible(teststring) for _ in range(10)}
        self.assertTrue(len(results) == 10)

        # test that the results are valid xsd:ids
        for result in results:
            self.assertTrue(re.search(r"^[a-zA-Z_][\w.-]*$", result))

        # test that invalid inputs lead to an error
        self.assertRaises(BaseError, excel2xml.make_xsd_id_compatible, 0)
        self.assertRaises(BaseError, excel2xml.make_xsd_id_compatible, "n/a")
        self.assertRaises(BaseError, excel2xml.make_xsd_id_compatible, None)
        self.assertRaises(BaseError, excel2xml.make_xsd_id_compatible, "")
        self.assertRaises(BaseError, excel2xml.make_xsd_id_compatible, " ")
        self.assertRaises(BaseError, excel2xml.make_xsd_id_compatible, ".")


    def test_derandomize_xsd_id(self) -> None:
        teststring = "0aüZ/_-äöü1234567890?`^':.;+*ç%&/()=±“#Ç[]|{}≠"
        id_1 = excel2xml.make_xsd_id_compatible(teststring)
        time.sleep(1)
        id_2 = excel2xml.make_xsd_id_compatible(teststring)
        id_1_derandom = excel2xml._derandomize_xsd_id(id_1)
        id_2_derandom = excel2xml._derandomize_xsd_id(id_2)

        # test single occurrence
        self.assertEqual(id_1_derandom, id_2_derandom)

        # test multiple occurrence
        multiple_ids = f"{id_1}----{id_2}----{id_1}----{id_2}"
        multiple_ids_derandom = excel2xml._derandomize_xsd_id(multiple_ids, multiple_occurrences=True)
        self.assertListEqual(multiple_ids_derandom.split("----"), [id_1_derandom] * 4)


    def test_find_date_in_string(self) -> None:

        # template: 2021-01-01 | 2015_01_02
        self.assertEqual(excel2xml.find_date_in_string("text 1492-10-12, text"), "GREGORIAN:CE:1492-10-12:CE:1492-10-12")
        self.assertEqual(excel2xml.find_date_in_string("Text 0476-09-04. text"), "GREGORIAN:CE:0476-09-04:CE:0476-09-04")
        self.assertEqual(excel2xml.find_date_in_string("Text (0476-09-04) text"), "GREGORIAN:CE:0476-09-04:CE:0476-09-04")
        self.assertIsNone(excel2xml.find_date_in_string("Text [1492-10-32?] text"))

        # template: 31.4.2021 | 5/11/2021
        self.assertEqual(excel2xml.find_date_in_string("Text (30.4.2021) text"), "GREGORIAN:CE:2021-04-30:CE:2021-04-30")
        self.assertEqual(excel2xml.find_date_in_string("Text (5/11/2021) text"), "GREGORIAN:CE:2021-11-05:CE:2021-11-05")

        # template: 26.2.-24.3.1948
        self.assertEqual(excel2xml.find_date_in_string("Text ...2193_01_26... text"), "GREGORIAN:CE:2193-01-26:CE:2193-01-26")
        self.assertEqual(excel2xml.find_date_in_string("Text -2193_01_26- text"), "GREGORIAN:CE:2193-01-26:CE:2193-01-26")
        self.assertIsNone(excel2xml.find_date_in_string("Text 2193_02_30 text"))

        # template: 27.-28.1.1900
        self.assertEqual(excel2xml.find_date_in_string("Text _1.3. - 25.4.2022_ text"), "GREGORIAN:CE:2022-03-01:CE:2022-04-25")
        self.assertEqual(excel2xml.find_date_in_string("Text (01.03. - 25.04.2022) text"), "GREGORIAN:CE:2022-03-01:CE:2022-04-25")
        self.assertEqual(excel2xml.find_date_in_string("Text 28.2.-1.12.1515 text"), "GREGORIAN:CE:1515-02-28:CE:1515-12-01")
        self.assertEqual(excel2xml.find_date_in_string("Text 28.2.-1.12.1515 text"), "GREGORIAN:CE:1515-02-28:CE:1515-12-01")
        self.assertIsNone(excel2xml.find_date_in_string("Text 28.2.-26.2.1515 text"))

        # template: 1.12.1973 - 6.1.1974
        self.assertEqual(excel2xml.find_date_in_string("Text 25.-26.2.0800 text"), "GREGORIAN:CE:0800-02-25:CE:0800-02-26")
        self.assertEqual(excel2xml.find_date_in_string("Text 25. - 26.2.0800 text"), "GREGORIAN:CE:0800-02-25:CE:0800-02-26")
        self.assertEqual(excel2xml.find_date_in_string("Text 25. - 26.2.0800 text"), "GREGORIAN:CE:0800-02-25:CE:0800-02-26")
        self.assertIsNone(excel2xml.find_date_in_string("Text 25.-24.2.0800 text"))

        # template: 31.4.2021 | 5/11/2021
        self.assertEqual(excel2xml.find_date_in_string("Text 1.9.2022-3.1.2024 text"), "GREGORIAN:CE:2022-09-01:CE:2024-01-03")
        self.assertEqual(excel2xml.find_date_in_string("Text 25.12.2022 - 3.1.2024 text"), "GREGORIAN:CE:2022-12-25:CE:2024-01-03")
        self.assertIsNone(excel2xml.find_date_in_string("Text 25.12.2022-03.01.2022 text"))
        self.assertEqual(excel2xml.find_date_in_string("Text 25/12/2022-03/01/2024 text"), "GREGORIAN:CE:2022-12-25:CE:2024-01-03")
        self.assertEqual(excel2xml.find_date_in_string("Text 25/12/2022 - 3/1/2024 text"), "GREGORIAN:CE:2022-12-25:CE:2024-01-03")
        self.assertIsNone(excel2xml.find_date_in_string("Text 25/12/2022-03/01/2022 text"))

        # template: February 9, 1908 | Dec 5,1908
        self.assertEqual(excel2xml.find_date_in_string("Text Jan 26, 1993 text"), "GREGORIAN:CE:1993-01-26:CE:1993-01-26")
        self.assertEqual(excel2xml.find_date_in_string("Text February26,2051 text"), "GREGORIAN:CE:2051-02-26:CE:2051-02-26")
        self.assertEqual(excel2xml.find_date_in_string("Text Sept 1, 1000 text"), "GREGORIAN:CE:1000-09-01:CE:1000-09-01")
        self.assertEqual(excel2xml.find_date_in_string("Text October 01, 1000 text"), "GREGORIAN:CE:1000-10-01:CE:1000-10-01")
        self.assertEqual(excel2xml.find_date_in_string("Text Nov 6,1000 text"), "GREGORIAN:CE:1000-11-06:CE:1000-11-06")
        self.assertEqual(excel2xml.find_date_in_string("Text Nov 6,1000 text"), "GREGORIAN:CE:1000-11-06:CE:1000-11-06")

        # template: 1907
        self.assertEqual(excel2xml.find_date_in_string("Text 1848 text"), "GREGORIAN:CE:1848:CE:1848")

        # template: 1849/50 | 1845-50 | 1849/1850
        self.assertEqual(excel2xml.find_date_in_string("Text 1849/1850? text"), "GREGORIAN:CE:1849:CE:1850")
        self.assertEqual(excel2xml.find_date_in_string("Text 1845-1850, text"), "GREGORIAN:CE:1845:CE:1850")
        self.assertEqual(excel2xml.find_date_in_string("Text 1849/50. text"), "GREGORIAN:CE:1849:CE:1850")
        self.assertEqual(excel2xml.find_date_in_string("Text (1845-50) text"), "GREGORIAN:CE:1845:CE:1850")
        self.assertEqual(excel2xml.find_date_in_string("Text [1849/1850] text"), "GREGORIAN:CE:1849:CE:1850")


    def test_prepare_value(self) -> None:
        identical_values = ["Test", "Test", "Test"]
        different_values: list[Union[str, int, float]] = [1, 1.0, "1", "1.0", " 1 "]
        values_with_nas: list[Union[str, int, float]] = ["test", "", 1, np.nan, 0]

        for val in different_values:
            values_output = excel2xml.prepare_value(val)
            self.assertEqual([x.value for x in values_output], [val, ])

            values_output = excel2xml.prepare_value(excel2xml.PropertyElement(val))
            self.assertEqual([x.value for x in values_output], [val, ])

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


    def test_make_boolean_prop(self) -> None:
        # prepare true_values
        true_values = [True, "TRue", "TruE", "1", 1, "yes", "YES", "yEs"]
        true_values.extend([excel2xml.PropertyElement(x) for x in true_values])

        # prepare false_values
        false_values = [False, "false", "False", "falSE", "0", 0, "no", "No", "nO"]
        false_values.extend([excel2xml.PropertyElement(x) for x in false_values])

        unsupported_values = [np.nan, "N/A", "NA", "na", "None", "", " ", "-", None,
                              [True, False], [0, 0, 1], ["True", "false"]]

        true_xml_expected = '<boolean-prop name=":test"><boolean permissions="prop-default">true</boolean></boolean-prop>'
        false_xml_expected = '<boolean-prop name=":test"><boolean permissions="prop-default">false</boolean></boolean-prop>'

        for true_value in true_values:
            true_xml = etree.tostring(excel2xml.make_boolean_prop(":test", true_value), encoding="unicode")
            true_xml = re.sub(r" xmlns(:.+?)?=\".+?\"", "", true_xml)
            self.assertEqual(true_xml, true_xml_expected, msg=f"Failed with '{true_value}'")
        for false_value in false_values:
            false_xml = etree.tostring(excel2xml.make_boolean_prop(":test", false_value), encoding="unicode")
            false_xml = re.sub(r" xmlns(:.+?)?=\".+?\"", "", false_xml)
            self.assertEqual(false_xml, false_xml_expected, msg=f"Failed with '{false_value}'")
        for unsupported_value in unsupported_values:
            self.assertRaises(BaseError, lambda: excel2xml.make_boolean_prop(":test", unsupported_value))


    def test_make_color_prop(self) -> None:
        prop = "color"
        method = excel2xml.make_color_prop
        different_values = ["#012345", "#abcdef", "#0B0B0B", "#AAAAAA", "#1a2b3c"]
        invalid_values = ["#0000000", "#00000G"]
        run_test(self, prop, method, different_values, invalid_values)


    def test_make_date_prop(self) -> None:
        prop = "date"
        method = excel2xml.make_date_prop
        different_values = ["CE:1849:CE:1850", "GREGORIAN:1848-01:1849-02", "2022",
                            "GREGORIAN:CE:0476-09-04:CE:0476-09-04", "GREGORIAN:CE:2014-01-31"]
        invalid_values = ["GREGORIAN:CE:0476-09-04:CE:09-04", "GREGORIAN:CE:0476-09-010:CE:0476-09-04"]
        run_test(self, prop, method, different_values, invalid_values)


    def test_make_decimal_prop(self) -> None:
        prop = "decimal"
        method = excel2xml.make_decimal_prop
        different_values = ["3.14159", 3.14159, "1.3e3", "100", ".1", 100]
        invalid_values = ["string"]
        run_test(self, prop, method, [float(x) for x in different_values], invalid_values)


    def test_make_geometry_prop(self) -> None:
        prop = "geometry"
        method = excel2xml.make_geometry_prop
        different_values = [
            '{"type": "rectangle", "lineColor": "#ff3333", "lineWidth": 2, "points": [{"x": 0.08, "y": 0.16}, {"x": 0.73, "y": 0.72}], "original_index": 0}',
            '{"type": "rectangle", "lineColor": "#000000", "lineWidth": 1, "points": [{"x": 0.10, "y": 0.10}, {"x": 0.10, "y": 0.10}], "original_index": 1}',
        ]
        invalid_values = ["100", 100, [0], '{"type": "polygon"}']
        run_test(self, prop, method, different_values, invalid_values)


    def test_make_geoname_prop(self) -> None:
        prop = "geoname"
        method = excel2xml.make_geoname_prop
        different_values = [1283416, "1283416", 71, "71", 10000000, "10000000"]
        invalid_values = ["text", 10.0, ["text"]]
        run_test(self, prop, method, different_values, invalid_values)


    def test_make_integer_prop(self) -> None:
        prop = "integer"
        method = excel2xml.make_integer_prop
        different_values = [1283416, "1283416", 3.14159, " 11 ", 0, "0"]
        invalid_values = [" 10.3 ", "text", ["text"]]
        run_test(self, prop, method, [int(x) for x in different_values], invalid_values)


    def test_make_interval_prop(self) -> None:
        prop = "interval"
        method = excel2xml.make_interval_prop
        different_values = ["+.1:+.9", "10:20", "1.5:2.5", "-.1:5", "-10.0:-5.1"]
        invalid_values = ["text", 10.0, ["text"], "10:", ":1"]
        run_test(self, prop, method, different_values, invalid_values)


    def test_make_list_prop(self) -> None:
        prop = "list"
        method = excel2xml.make_list_prop
        different_values = ["first-node", "second-node", "third-node", "fourth-node", "fifth-node"]
        invalid_values = [10.0]
        run_test(self, prop, method, different_values, invalid_values, ":myList")


    def test_make_resptr_prop(self) -> None:
        prop = "resptr"
        method = excel2xml.make_resptr_prop
        different_values = ["resource_1", "resource_2", "resource_3", "resource_4", "resource_5"]
        invalid_values = [True, 10.0, 5]
        run_test(self, prop, method, different_values, invalid_values)


    @pytest.mark.filterwarnings("ignore")
    def test_make_text_prop(self) -> None:
        prop = "text"
        method = excel2xml.make_text_prop
        different_values = ["text_1", " ", "!", "?", "-", "_", "None", "<NA>"]
        invalid_values = [True, 10.0, 5, ""]
        run_test(self, prop, method, different_values, invalid_values)

        # test encoding="xml"
        xml_expected_1 = '<text-prop name=":test"><text permissions="prop-default" encoding="xml">A text with ' \
                         '<b>formatting</b> and a <a class="salsah-link" href="IRI:test_thing_0:IRI">Link</a></text></text-prop>'
        xml_returned_1 = excel2xml.make_text_prop(":test", excel2xml.PropertyElement(
            value='A text with <b>formatting</b> and a <a class="salsah-link" href="IRI:test_thing_0:IRI">Link</a>', encoding="xml"))
        xml_returned_1 = etree.tostring(xml_returned_1, encoding="unicode")
        xml_returned_1 = re.sub(r" xmlns(:.+?)?=\".+?\"", "", xml_returned_1)
        xml_returned_1 = xml_returned_1.replace("&lt;", "<")
        xml_returned_1 = xml_returned_1.replace("&gt;", ">")
        self.assertEqual(xml_expected_1, xml_returned_1)

        # encoding="unicode" must raise an error
        self.assertRaises(BaseError, lambda: excel2xml.make_text_prop(":test", excel2xml.PropertyElement(value="a", encoding="unicode")))


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
        invalid_values = [True, 10.0, 5, "2019-10-2", "CE:1849:CE:1850", "2019-10-23T13:45:12.1234567890123Z", "2022",
                          "GREGORIAN:CE:2014-01-31"]
        run_test(self, prop, method, different_values, invalid_values)


    def test_make_uri_prop(self) -> None:
        prop = "uri"
        method = excel2xml.make_uri_prop
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


    def test_make_annotation_link_region(self) -> None:
        """
        This method tests 3 methods at the same time: make_annotation(), make_link(), and make_region().
        """
        for method, tagname in [
            (excel2xml.make_annotation, "annotation"),
            (excel2xml.make_link, "link"),
            (excel2xml.make_region, "region"),
        ]:
            test_cases = [
                (lambda: method("label", "id"),
                 f'<{tagname} label="label" id="id" permissions="res-default"/>'),
                (lambda: method("label", "id", "res-restricted"),
                 f'<{tagname} label="label" id="id" permissions="res-restricted"/>'),
                (lambda: method("label", "id", ark="ark"),
                 f'<{tagname} label="label" id="id" permissions="res-default" ark="ark"/>'),
                (lambda: method("label", "id", iri="iri"),
                 f'<{tagname} label="label" id="id" permissions="res-default" iri="iri"/>'),
                (lambda: method("label", "id", creation_date="2019-10-23T13:45:12Z"),
                 f'<{tagname} label="label" id="id" permissions="res-default" creation_date="2019-10-23T13:45:12Z"/>')
            ]
            for _method, result in test_cases:
                xml_returned = _method()
                xml_returned = etree.tostring(xml_returned, encoding="unicode")
                xml_returned = re.sub(r" xmlns(:.+?)?=\".+?\"", "", xml_returned)
                self.assertEqual(result, xml_returned)

            self.assertWarns(UserWarning, lambda: method("label", "id", ark="ark", iri="iri"))
            with self.assertRaisesRegex(BaseError, "invalid creation date"):
                method("label", "restype", "id", creation_date="2019-10-23T13:45:12")


    def test_make_resource(self) -> None:
        test_cases = [
            (lambda: excel2xml.make_resource("label", "restype", "id"),
             '<resource label="label" restype="restype" id="id" permissions="res-default"/>'),
            (lambda: excel2xml.make_resource("label", "restype", "id", "res-restricted"),
             '<resource label="label" restype="restype" id="id" permissions="res-restricted"/>'),
            (lambda: excel2xml.make_resource("label", "restype", "id", ark="ark"),
             '<resource label="label" restype="restype" id="id" permissions="res-default" ark="ark"/>'),
            (lambda: excel2xml.make_resource("label", "restype", "id", iri="iri"),
             '<resource label="label" restype="restype" id="id" permissions="res-default" iri="iri"/>'),
            (lambda: excel2xml.make_resource("label", "restype", "id", creation_date="2019-10-23T13:45:12Z"),
             '<resource label="label" restype="restype" id="id" permissions="res-default" creation_date="2019-10-23T13:45:12Z"/>')
        ]

        for method, result in test_cases:
            xml_returned = method()
            xml_returned = etree.tostring(xml_returned, encoding="unicode")
            xml_returned = re.sub(r" xmlns(:.+?)?=\".+?\"", "", xml_returned)
            self.assertEqual(result, xml_returned)

        self.assertWarns(UserWarning, lambda: excel2xml.make_resource("label", "restype", "id", ark="ark", iri="iri"))
        with self.assertRaisesRegex(BaseError, "invalid creation date"):
            excel2xml.make_resource("label", "restype", "id", creation_date="2019-10-23T13:45:12")


    def test_create_json_excel_list_mapping(self) -> None:
        # We start with an Excel column that contains list nodes, but with spelling errors
        excel_column = [
            "  first noude ov testlist  ",
            "sekond noude ov testlist",
            " fierst sobnode , sekond sobnode , Third Node Ov Testliest",  # multiple entries per cell are possible
            "completely wrong spelling variant of 'first subnode' that needs manual correction"
        ]
        corrections = {"completely wrong spelling variant of 'first subnode' that needs manual correction": "first subnode"}
        testlist_mapping_returned = excel2xml.create_json_excel_list_mapping(
            path_to_json="testdata/test-project-systematic.json",
            list_name="testlist",
            excel_values=excel_column,
            sep=",",
            corrections=corrections
        )
        testlist_mapping_expected = {
            "first noude ov testlist": "first node of testlist",
            "sekond noude ov testlist": "second node of testlist",
            "fierst sobnode": "first subnode",
            "sekond sobnode": "second subnode",
            "Third Node Ov Testliest": "third node of testlist",
            "third node ov testliest": "third node of testlist",
            "completely wrong spelling variant of 'first subnode' that needs manual correction": "first subnode"
        }
        self.assertDictEqual(testlist_mapping_returned, testlist_mapping_expected)


    def test_create_json_list_mapping(self) -> None:
        testlist_mapping_returned = excel2xml.create_json_list_mapping(
            path_to_json="testdata/test-project-systematic.json",
            list_name="testlist",
            language_label="en"
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
            "third node of the test-list": "third node of testlist"
        }
        self.assertDictEqual(testlist_mapping_returned, testlist_mapping_expected)


    @pytest.mark.filterwarnings("ignore")
    def test_excel2xml(self) -> None:
        # test the valid files, 3 times identical, but in the three formats XLSX, XLS, and CSV
        with open("testdata/excel2xml-expected-output.xml") as f:
            expected = f.read()
        for ext in ["xlsx", "xls", "csv"]:
            excel2xml.excel2xml(f"testdata/excel2xml-testdata.{ext}", "1234", "excel2xml-output")
            with open("excel2xml-output-data.xml") as f:
                returned = f.read()
                self.assertEqual(returned, expected, msg=f"Failed with extension {ext}")
        if os.path.isfile("excel2xml-output-data.xml"):
            os.remove("excel2xml-output-data.xml")

        # test the invalid files
        invalid_prefix = "testdata/invalid_testdata/excel2xml-testdata-invalid"
        invalid_cases = [
            (f"{invalid_prefix}-boolean-prop-two-values.xlsx",           "A <boolean-prop> can only have a single value"),
            (f"{invalid_prefix}-empty-property.xlsx",                    "At least one value per property is required"),
            (f"{invalid_prefix}-id-propname-both.xlsx",                  "Exactly 1 of the 2 columns 'id' and 'prop name' must have an entry"),
            (f"{invalid_prefix}-id-propname-none.xlsx",                  "Exactly 1 of the 2 columns 'id' and 'prop name' must have an entry"),
            (f"{invalid_prefix}-missing-prop-permissions.xlsx",          "Missing permissions for value .+ of property"),
            (f"{invalid_prefix}-missing-resource-label.xlsx",            "Missing label for resource"),
            (f"{invalid_prefix}-missing-resource-permissions.xlsx",      "Missing permissions for resource"),
            (f"{invalid_prefix}-missing-restype.xlsx",                   "Missing restype"),
            (f"{invalid_prefix}-no-bitstream-permissions.xlsx",          "'file permissions' missing"),
            (f"{invalid_prefix}-nonexisting-proptype.xlsx",              "Invalid prop type"),
            (f"{invalid_prefix}-single-invalid-value-for-property.xlsx", "has an entry in column \\d+_permissions, but not in \\d+_value")
        ]
        for file, _regex in invalid_cases:
            with self.assertRaisesRegex(BaseError, _regex, msg=f"Failed with file '{file}'"):
                excel2xml.excel2xml(file, "1234", f"excel2xml-invalid")


if __name__ == "__main__":
    unittest.main()
