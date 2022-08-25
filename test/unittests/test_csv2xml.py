import random
import unittest
import re
from typing import Callable, Sequence, Union

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
    invalid_values: Sequence[Union[str, int, float, bool]]
) -> None:
    """
    XML-properties have always a similar structure, and all make_*_prop() methods have some similar things to test. This
    method executes the tests in a parametrized way.

    Args:
        prop: the name of the property
        method: the make_*_prop() method
        different_values: some valid values
        invalid_values: some invalid values
    """
    identical_values = [different_values[0]] * 3
    max = len(different_values)
    testcases = [
        (
            f'<{prop}-prop name=":test"><{prop} permissions="prop-default">{different_values[0 % max]}</{prop}></{prop}-prop>',
            method(":test", value=different_values[0 % max])
        ),
        (
            f'<{prop}-prop name=":test"><{prop} permissions="prop-restricted">{different_values[1 % max]}</{prop}></{prop}-prop>',
            method(":test", value=c2x.PropertyElement(different_values[1 % max], permissions="prop-restricted"))
        ),
        (
            f'<{prop}-prop name=":test"><{prop} permissions="prop-default" comment="comment">{different_values[2 % max]}</{prop}></{prop}-prop>',
            method(":test", value=c2x.PropertyElement(different_values[2 % max], comment="comment"))
        ),
        (
            f'<{prop}-prop name=":test"><{prop} permissions="prop-default">{identical_values[0]}</{prop}></{prop}-prop>',
            method(":test", value=identical_values)
        ),
        (
            f'<{prop}-prop name=":test">'
            f'<{prop} permissions="prop-default">{identical_values[0]}</{prop}>'
            f'<{prop} permissions="prop-default">{identical_values[0]}</{prop}>'
            f'<{prop} permissions="prop-default">{identical_values[0]}</{prop}>'
            f'</{prop}-prop>',
            method(":test", values=identical_values)
        ),
        (
            f'<{prop}-prop name=":test">'
            f'<{prop} permissions="prop-default">{different_values[3 % max]}</{prop}>'
            f'<{prop} permissions="prop-default">{different_values[4 % max]}</{prop}>'
            f'<{prop} permissions="prop-default">{different_values[5 % max]}</{prop}>'
            f'</{prop}-prop>',
            method(":test", values=[different_values[3 % max], different_values[4 % max], different_values[5 % max]])
        )
    ]

    for i, tc in enumerate(testcases):
        xml_received = etree.tostring(tc[1], encoding="unicode")
        xml_received = re.sub(r" xmlns(:.+?)?=\".+?\"", "", xml_received)
        testcase.assertEqual(tc[0], xml_received, msg=f"Failed testcase: testcases[{i}]")

    for inv in invalid_values:
        with testcase.assertRaises(BaseError, msg=f"Failed with value '{inv}'"):
            method(":test", inv)
    testcase.assertRaises(BaseError, lambda: method(":test", different_values))



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
            {"type": "rectangle", "lineColor": "#ff3333", "lineWidth": 2, "points": [{"x": 0.08, "y": 0.16}, {"x": 0.73, "y": 0.72}], "original_index": 0}
        ]
        invalid_values = ["100", 100, [0], {"type": "polygon"}]
        run_test(self, prop, method, different_values, invalid_values)


if __name__ == "__main__":
    unittest.main()
