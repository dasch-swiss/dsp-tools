"""unit tests for excel to properties"""

# pylint: disable=missing-class-docstring,missing-function-docstring,protected-access

import json
import os
import re
import shutil
import unittest
from typing import Any, cast

import jsonpath_ng
import jsonpath_ng.ext
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from dsp_tools.commands.excel2json import properties as e2j
from dsp_tools.models.exceptions import InputError, UserError


class TestExcelToProperties(unittest.TestCase):
    outfile = "testdata/tmp/_out_properties.json"

    @classmethod
    def setUpClass(cls) -> None:
        """Is executed once before the methods of this class are run"""
        os.makedirs("testdata/tmp", exist_ok=True)

    @classmethod
    def tearDownClass(cls) -> None:
        """Is executed after the methods of this class have all run through"""
        shutil.rmtree("testdata/tmp", ignore_errors=True)

    def test_excel2properties(self) -> None:
        excelfile = "testdata/excel2json/excel2json_files/test-name (test_label)/properties.xlsx"
        output_from_method, _ = e2j.excel2properties(excelfile, self.outfile)

        # define the expected values from the excel file
        excel_names = [
            "correspondsToGenericAnthroponym",
            "hasAnthroponym",
            "hasGender",
            "isDesignatedAs",
            "hasTitle",
            "hasStatus",
            "hasLifeYearAmount",
            "hasBirthDate",
            "hasRepresentation",
            "hasRemarks",
            "hasTerminusPostQuem",
            "hasGND",
            "hasColor",
            "hasDecimal",
            "hasTime",
            "hasInterval",
            "hasBoolean",
            "hasGeoname",
            "partOfDocument",
            "linkstoRegion",
            "hasLinkToImage",
            "hasLinkToResource",
            "hasLinkToArchiveRepresentation",
            "hasLinkToMovingImageRepesentation",
            "hasLinkToAudioRepesentation",
        ]
        excel_supers = [
            ["hasLinkTo"],
            ["hasValue", "dcterms:creator"],
            ["hasValue"],
            ["hasValue"],
            ["hasLinkTo"],
            ["hasValue"],
            ["hasValue"],
            ["hasValue"],
            ["hasRepresentation"],
            ["hasValue", "dcterms:description"],
            ["hasValue"],
            ["hasValue"],
            ["hasColor"],
            ["hasValue"],
            ["hasValue"],
            ["hasSequenceBounds"],
            ["hasValue"],
            ["hasValue"],
            ["isPartOf"],
            ["hasLinkTo"],
            ["hasLinkTo"],
            ["hasLinkTo"],
            ["hasLinkTo"],
            ["hasLinkTo"],
            ["hasLinkTo"],
        ]
        excel_objects = [
            ":GenericAnthroponym",
            "TextValue",
            "ListValue",
            "ListValue",
            ":Titles",
            "ListValue",
            "IntValue",
            "DateValue",
            "Representation",
            "TextValue",
            "DateValue",
            "UriValue",
            "ColorValue",
            "DecimalValue",
            "TimeValue",
            "IntervalValue",
            "BooleanValue",
            "GeonameValue",
            ":Documents",
            "Region",
            "StillImageRepresentation",
            "Resource",
            "ArchiveRepresentation",
            "MovingImageRepresentation",
            "AudioRepresentation",
        ]

        excel_labels = {
            "de": [
                "",
                "only German",
                "",
                "",
                "",
                "",
                "",
                "",
                "hat eine Multimediadatei",
                "",
                "",
                "GND",
                "Farbe",
                "Dezimalzahl",
                "Zeit",
                "Zeitintervall",
                "Bool'sche Variable",
                "Link zu Geonames",
                "ist Teil eines Dokuments",
                "",
                "",
                "",
                "",
                "",
                "",
            ],
            "it": [
                "",
                "",
                "",
                "only Italian",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "GND",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ],
        }  # there are also labels in other languages, but they are not tested
        excel_comments = {
            "comment_fr": [
                "J'avais déjà examiné plusieurs propriétés quand, un jour, le notaire, qui me "
                "donnait des indications nécessaires pour une de mes explorations, me dit :",
                "Un étrange hasard m'a mis en possession de ce journal.",
                "Je n'en sais rien du tout ; mais si vous voulez la voir, monsieur, voici les "
                "indications précises pour la trouver.",
                "Vous devrez arranger l'affaire avec le curé du village de --.\"",
                "Un étrange hasard m'a mis en possession de ce journal.",
                "",
                "",
                "only French",
                "",
                "",
                "J'avais déjà examiné plusieurs propriétés quand, un jour, le notaire, qui me "
                "donnait des indications nécessaires pour une de mes explorations, me dit :",
                "Gemeinsame Normdatei",
                "",
                "Chiffre décimale",
                "Temps",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ],
            "comment_it": [
                "Avevo già visto diverse proprietà quando un giorno il notaio,",
                "Uno strano caso mi mise in possesso di questo diario.",
                "Non ne so nulla; ma se volete vederla, signore, eccovi le indicazioni precise per trovarla.",
                "Dovrete organizzare l'affare con il curato del villaggio di --\".",
                "Uno strano caso mi mise in possesso di questo diario.",
                "",
                "",
                "",
                "",
                "",
                "Avevo già visto diverse proprietà quando un giorno il notaio,",
                "Gemeinsame Normdatei",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ],
        }  # there are also comments in other languages, but they are not tested
        excel_gui_elements = [
            "Searchbox",
            "Richtext",
            "List",
            "Radio",
            "Searchbox",
            "List",
            "Spinbox",
            "Date",
            "Searchbox",
            "Textarea",
            "Date",
            "SimpleText",
            "Colorpicker",
            "Spinbox",
            "TimeStamp",
            "Interval",
            "Checkbox",
            "Geonames",
            "Searchbox",
            "Searchbox",
            "Searchbox",
            "Searchbox",
            "Searchbox",
            "Searchbox",
            "Searchbox",
        ]

        excel_gui_attributes_hasGender = {"hlist": "gender"}
        excel_gui_attributes_hasGND = {"size": 100}
        excel_gui_attributes_hasDecimal = {"min": 0.0, "max": 100.0}

        # read json file
        with open(self.outfile, encoding="utf-8") as f:
            output_from_file: list[dict[str, Any]] = json.load(f)

        # check that output from file and from method are equal
        self.assertListEqual(output_from_file, output_from_method)

        # extract infos from json file
        json_names = [match.value for match in jsonpath_ng.parse("$[*].name").find(output_from_file)]
        json_supers = [match.value for match in jsonpath_ng.parse("$[*].super").find(output_from_file)]
        json_objects = [match.value for match in jsonpath_ng.parse("$[*].object").find(output_from_file)]

        json_labels_all = [match.value for match in jsonpath_ng.parse("$[*].labels").find(output_from_file)]
        json_labels = {lang: [label.get(lang, "").strip() for label in json_labels_all] for lang in ["de", "it"]}
        json_comments = {
            f"comment_{lang}": [resource.get("comments", {}).get(lang, "").strip() for resource in output_from_file]
            for lang in ["fr", "it"]
        }
        json_gui_elements = [match.value for match in jsonpath_ng.parse("$[*].gui_element").find(output_from_file)]

        json_gui_attributes_hasGender = (
            jsonpath_ng.ext.parse("$[?name='hasGender'].gui_attributes").find(output_from_file)[0].value
        )
        json_gui_attributes_hasGND = (
            jsonpath_ng.ext.parse("$[?name='hasGND'].gui_attributes").find(output_from_file)[0].value
        )
        json_gui_attributes_hasDecimal = (
            jsonpath_ng.ext.parse("$[?name='hasDecimal'].gui_attributes").find(output_from_file)[0].value
        )

        # make checks
        self.assertListEqual(excel_names, json_names)
        self.assertListEqual(excel_supers, json_supers)
        self.assertListEqual(excel_objects, json_objects)
        self.assertDictEqual(excel_labels, json_labels)
        self.assertDictEqual(excel_comments, json_comments)
        self.assertListEqual(excel_gui_elements, json_gui_elements)
        self.assertDictEqual(excel_gui_attributes_hasGND, json_gui_attributes_hasGND)
        self.assertDictEqual(excel_gui_attributes_hasDecimal, json_gui_attributes_hasDecimal)
        self.assertDictEqual(excel_gui_attributes_hasGender, json_gui_attributes_hasGender)

    def test_validate_properties(self) -> None:
        # it is not possible to call the method to be tested directly.
        # So let's make a reference to it, so that it can be found by the usage search
        lambda x: e2j._validate_properties([], "file")  # pylint: disable=expression-not-assigned,protected-access

        testcases = [
            (
                "testdata/invalid-testdata/excel2json/properties-invalid-super.xlsx",
                "did not pass validation.\n"
                "The problematic property is 'hasGeoname' in Excel row 3.\n"
                "The problem is that the column 'super' has an invalid value: "
                "'GeonameValue' is not valid under any of the given schemas",
            ),
            (
                "testdata/invalid-testdata/excel2json/properties-invalid-object.xlsx",
                "did not pass validation.\n"
                "The problematic property is 'hasBoolean' in Excel row 2.\n"
                "The problem is that the column 'object' has an invalid value: "
                "'hasValue' is not valid under any of the given schemas",
            ),
            (
                "testdata/invalid-testdata/excel2json/properties-invalid-gui_element.xlsx",
                "did not pass validation.\n"
                "The problematic property is 'hasInterval' in Excel row 4.\n"
                r"The problem is that the column 'gui_element' has an invalid value: "
                r"'Interval' was expected",
            ),
            (
                "testdata/invalid-testdata/excel2json/properties-invalid-gui_attribute_values.xlsx",
                "did not pass validation.\n"
                "The problematic property is 'hasInteger' in Excel row 4.\n"
                r"The problem is that the column 'gui_attributes' has an invalid value: "
                r"Additional properties are not allowed \('rows' was unexpected\)",
            ),
        ]

        for file, message in testcases:
            with self.assertRaisesRegex(UserError, message):
                e2j.excel2properties(file, self.outfile)

    def test_excel2properties_gui_attrib_problem(self) -> None:
        expected_msg = re.escape(
            (
                "The Excel file 'testdata/invalid-testdata/excel2json/properties-invalid-gui_attribute_format.xlsx' "
                "has invalid content.\n"
                "The expected format is 'attribute: value, attribute: value'\n"
                "\tColumn: gui_attributes\n"
                "\tRow(s):\n"
                "\t- 4\n"
                "\tValue(s):\n"
                "\t- max=10, min=5"
            )
        )
        with pytest.raises(InputError, match=expected_msg):
            e2j.excel2properties(
                "testdata/invalid-testdata/excel2json/properties-invalid-gui_attribute_format.xlsx", ""
            )

    @pytest.mark.filterwarnings("ignore::UserWarning")
    def test_rename_deprecated_lang_cols(self) -> None:
        original_df = pd.DataFrame(
            {"en": [1, 2, 3], "de": [1, 2, 3], "fr": [1, 2, 3], "it": [1, 2, 3], "rm": [1, 2, 3]}
        )
        expected_df = pd.DataFrame(
            {
                "label_en": [1, 2, 3],
                "label_de": [1, 2, 3],
                "label_fr": [1, 2, 3],
                "label_it": [1, 2, 3],
                "label_rm": [1, 2, 3],
            }
        )
        returned_df = e2j._rename_deprecated_lang_cols(df=original_df, excelfile="Test")
        assert_frame_equal(expected_df, returned_df)
        returned_df = e2j._rename_deprecated_lang_cols(df=expected_df, excelfile="Test")
        assert_frame_equal(expected_df, returned_df)

    def test_do_property_excel_compliance_all_good(self) -> None:
        original_df = pd.DataFrame(
            {
                "name": ["name_1", "name_2", "name_3", "name_4", "name_5", "name_6"],
                "label_en": ["label_en_1", "label_en_2", pd.NA, pd.NA, "label_en_5", pd.NA],
                "label_de": ["label_de_1", pd.NA, "label_de_3", pd.NA, pd.NA, pd.NA],
                "label_fr": ["label_fr_1", pd.NA, pd.NA, "label_fr_4", pd.NA, pd.NA],
                "label_it": ["label_it_1", pd.NA, pd.NA, pd.NA, "label_it_5", pd.NA],
                "label_rm": ["label_rm_1", pd.NA, pd.NA, pd.NA, pd.NA, "label_rm_6"],
                "comment_en": ["comment_en_1", "comment_en_2", pd.NA, pd.NA, "comment_en_5", pd.NA],
                "comment_de": ["comment_de_1", pd.NA, "comment_de_3", pd.NA, pd.NA, pd.NA],
                "comment_fr": ["comment_fr_1", pd.NA, pd.NA, "comment_fr_4", pd.NA, pd.NA],
                "comment_it": ["comment_it_1", pd.NA, pd.NA, pd.NA, "comment_it_5", pd.NA],
                "comment_rm": ["comment_rm_1", pd.NA, pd.NA, pd.NA, pd.NA, pd.NA],
                "super": ["super_1", "super_2", "super_3", "super_4.1, super_4.2, super_4.3", "super_5", "super_6"],
                "subject": ["subject_1", "subject_2", "subject_3", "subject_4", "subject_5", "subject_6"],
                "object": ["object_1", "object_2", "object_3", "object_4", "object_5", "object_6"],
                "gui_element": ["Simple", "Searchbox", "Date", "Searchbox", "List", "Searchbox"],
                "gui_attributes": ["size: 32, maxlength: 128", pd.NA, pd.NA, pd.NA, "hlist: languages", pd.NA],
            }
        )

        e2j._do_property_excel_compliance(df=original_df, excelfile="Test")

    def test_do_property_excel_compliance_problems(self) -> None:
        original_df = pd.DataFrame(
            {
                "name": ["name_1", "name_2", "name_3", "name_4", "name_5", "name_6", "name_7", pd.NA],
                "label_en": ["label_en_1", pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA],
                "label_de": [pd.NA, pd.NA, "label_de_3", pd.NA, pd.NA, pd.NA, pd.NA, "label_de_8"],
                "label_fr": [pd.NA, pd.NA, pd.NA, "label_fr_4", pd.NA, pd.NA, pd.NA, pd.NA],
                "label_it": [pd.NA, pd.NA, pd.NA, pd.NA, "label_it_5", pd.NA, pd.NA, pd.NA],
                "label_rm": [pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, "label_rm_6", pd.NA, pd.NA],
                "comment_en": ["comment_en_1", pd.NA, "comment_en_3", pd.NA, pd.NA, pd.NA, pd.NA, pd.NA],
                "comment_de": [pd.NA, pd.NA, pd.NA, "comment_de_4", pd.NA, pd.NA, pd.NA, pd.NA],
                "comment_fr": [pd.NA, pd.NA, pd.NA, pd.NA, "comment_fr_5", pd.NA, pd.NA, pd.NA],
                "comment_it": [pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, "comment_it_6", pd.NA, pd.NA],
                "comment_rm": [pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, "comment_rm_7", pd.NA],
                "super": [
                    pd.NA,
                    "super_2",
                    pd.NA,
                    "super_4.1, super_4.2, super_4.3",
                    "super_5",
                    "super_6",
                    "super_7",
                    pd.NA,
                ],
                "subject": [
                    "subject_1",
                    "subject_2",
                    "subject_3",
                    "subject_4",
                    "subject_5",
                    "subject_6",
                    "subject_7",
                    pd.NA,
                ],
                "object": ["object_1", "object_2", "object_3", pd.NA, "object_5", "object_6", "object_7", pd.NA],
                "gui_element": ["Simple", "Searchbox", "Date", "Date", pd.NA, "List", pd.NA, pd.NA],
                "gui_attributes": ["size: 32, maxlength: 128", pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA],
            }
        )
        expected_msg = re.escape(
            (
                "The excel file 'Test' has some problems:\n"
                "There are missing values in a column that must not be empty:\n"
                "\tColumn: name\n"
                "\tRow(s):\n"
                "\t- 9\n\t\n"
                "There are missing values in a column that must not be empty:\n"
                "\tColumn: super\n"
                "\tRow(s):\n"
                "\t- 2\n"
                "\t- 4\n"
                "\t- 9\n\t\n"
                "There are missing values in a column that must not be empty:\n"
                "\tColumn: object\n"
                "\tRow(s):\n"
                "\t- 5\n"
                "\t- 9\n\t\n"
                "There are missing values in a column that must not be empty:\n"
                "\tColumn: gui_element\n"
                "\tRow(s):\n"
                "\t- 6\n"
                "\t- 8\n"
                "\t- 9\n\t\n"
                "There are missing values in a column that must not be empty:\n"
                "\tColumn: label\n"
                "\tRow(s):\n"
                "\t- 3\n"
                "\t- 8\n\t\n"
                "There are missing values in a column that must not be empty:\n"
                "\tColumn: gui_attributes\n"
                "\tRow(s):\n"
                "\t- 7\n\t"
            )
        )

        with pytest.raises(InputError, match=expected_msg):
            e2j._do_property_excel_compliance(original_df, "Test")

    @pytest.mark.filterwarnings("ignore::UserWarning")
    def test_rename_deprecated_hlist(self) -> None:
        original_df = pd.DataFrame({"hlist": [pd.NA, pd.NA, "languages"]})
        expected_df = pd.DataFrame({"gui_attributes": [pd.NA, pd.NA, "hlist:languages"]})
        returned_df = e2j._rename_deprecated_hlist(df=original_df, excelfile="Test")
        assert_frame_equal(expected_df, returned_df)

        original_df = pd.DataFrame(
            {"hlist": [pd.NA, pd.NA, "languages"], "gui_attributes": [pd.NA, "attribute_1", pd.NA]}
        )
        expected_df = pd.DataFrame({"gui_attributes": [pd.NA, "attribute_1", "hlist:languages"]})
        returned_df = e2j._rename_deprecated_hlist(df=original_df, excelfile="Test")
        assert_frame_equal(expected_df, returned_df)

    def test_unpack_gui_attributes(self) -> None:
        test_dict = {
            "maxlength:1, size:32": {"maxlength": "1", "size": "32"},
            "hlist: languages": {"hlist": "languages"},
        }
        for original, expected in test_dict.items():
            self.assertDictEqual(e2j._unpack_gui_attributes(attribute_str=original), expected)

    def test_search_convert_numbers(self) -> None:
        test_dict = {"1": 1, "string": "string", "1.453": 1.453, "sdf.asdf": "sdf.asdf"}
        for original, expected in test_dict.items():
            self.assertEqual(e2j._search_convert_numbers(value_str=original), expected)

    def test_get_gui_attribute(self) -> None:
        original_df = pd.DataFrame(
            {"gui_attributes": [pd.NA, "max:1.4 / min:1.2", "hlist:", "234345", "hlist: languages,"]}
        )
        self.assertIsNone(e2j._get_gui_attribute(df_row=original_df.loc[0, :], row_num=2, excelfile="Test"))

        res_problem_1 = e2j._get_gui_attribute(df_row=original_df.loc[1, :], row_num=3, excelfile="Test")
        assert res_problem_1.rows == [3]
        assert res_problem_1.values == ["max:1.4 / min:1.2"]

        res_problem_2 = e2j._get_gui_attribute(df_row=original_df.loc[2, :], row_num=4, excelfile="Test")
        assert res_problem_2.rows == [4]
        assert res_problem_2.values == ["hlist:"]

        res_problem_3 = e2j._get_gui_attribute(df_row=original_df.loc[3, :], row_num=5, excelfile="Test")
        assert res_problem_3.rows == [5]
        assert res_problem_3.values == ["234345"]

        expected_dict = {"hlist": "languages"}
        returned_dict = e2j._get_gui_attribute(df_row=original_df.loc[4, :], row_num=6, excelfile="Test")
        self.assertDictEqual(expected_dict, cast(dict[str, str], returned_dict))

    def test_check_compliance_gui_attributes(self) -> None:
        original_df = pd.DataFrame(
            {
                "gui_element": ["Spinbox", "List", "Searchbox", "Date", "Geonames", "Richtext", "TimeStamp"],
                "gui_attributes": ["Spinbox_attr", "List_attr", pd.NA, pd.NA, pd.NA, pd.NA, pd.NA],
            }
        )
        returned_value = e2j._check_compliance_gui_attributes(df=original_df)
        self.assertIsNone(cast(None, returned_value))
        original_df = pd.DataFrame(
            {
                "gui_element": ["Spinbox", "List", "Searchbox", "Date", "Geonames", "Richtext", "TimeStamp"],
                "gui_attributes": ["Spinbox_attr", pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, "TimeStamp_attr"],
            }
        )
        expected_dict = {"gui_attributes": [False, True, False, False, False, False, True]}
        returned_dict = e2j._check_compliance_gui_attributes(df=original_df)
        returned_dict = cast(dict[str, list[pd.Series]], returned_dict)
        casted_dict: dict[str, Any] = {"gui_attributes": list(returned_dict["gui_attributes"])}
        self.assertDictEqual(expected_dict, casted_dict)

    def test_row2prop(self) -> None:
        original_df = pd.DataFrame(
            {
                "name": ["name_1", "name_2", "name_3"],
                "label_en": ["label_en_1", "label_en_2", pd.NA],
                "label_de": ["label_de_1", pd.NA, "label_de_3"],
                "label_fr": ["label_fr_1", pd.NA, pd.NA],
                "label_it": ["label_it_1", pd.NA, pd.NA],
                "label_rm": ["label_rm_1", pd.NA, pd.NA],
                "comment_en": ["comment_en_1", "comment_en_2", pd.NA],
                "comment_de": ["comment_de_1", pd.NA, "comment_de_3"],
                "comment_fr": ["comment_fr_1", pd.NA, pd.NA],
                "comment_it": ["comment_it_1", pd.NA, pd.NA],
                "comment_rm": ["comment_rm_1", pd.NA, pd.NA],
                "super": ["super_1", "super_2.1, super_2.2", "super_3"],
                "subject": ["subject_1", "subject_2", pd.NA],
                "object": ["object_1", "object_2", "object_3"],
                "gui_element": ["Simple", "Date", "List"],
                "gui_attributes": ["size: 32, maxlength: 128", pd.NA, "hlist: languages"],
            }
        )
        returned_dict = e2j._row2prop(df_row=original_df.loc[0, :], row_num=0, excelfile="Test")
        expected_dict = {
            "name": "name_1",
            "object": "object_1",
            "gui_element": "Simple",
            "labels": {
                "en": "label_en_1",
                "de": "label_de_1",
                "fr": "label_fr_1",
                "it": "label_it_1",
                "rm": "label_rm_1",
            },
            "super": ["super_1"],
            "comments": {
                "en": "comment_en_1",
                "de": "comment_de_1",
                "fr": "comment_fr_1",
                "it": "comment_it_1",
                "rm": "comment_rm_1",
            },
            "gui_attributes": {"size": 32, "maxlength": 128},
        }
        self.assertDictEqual(expected_dict, returned_dict)

        returned_dict = e2j._row2prop(df_row=original_df.loc[1, :], row_num=1, excelfile="Test")
        expected_dict = {
            "comments": {"en": "comment_en_2"},
            "gui_element": "Date",
            "labels": {"en": "label_en_2"},
            "name": "name_2",
            "object": "object_2",
            "super": ["super_2.1", "super_2.2"],
        }
        self.assertDictEqual(expected_dict, returned_dict)

        returned_dict = e2j._row2prop(df_row=original_df.loc[2, :], row_num=2, excelfile="Test")
        expected_dict = {
            "comments": {"de": "comment_de_3"},
            "gui_attributes": {"hlist": "languages"},
            "gui_element": "List",
            "labels": {"de": "label_de_3"},
            "name": "name_3",
            "object": "object_3",
            "super": ["super_3"],
        }
        self.assertDictEqual(expected_dict, returned_dict)


if __name__ == "__main__":
    pytest.main([__file__])
