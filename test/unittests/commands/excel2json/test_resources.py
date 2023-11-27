"""unit tests for excel to resource"""

# ruff: noqa: D101 (undocumented-public-class)
# ruff: noqa: D102 (undocumented-public-method)

import json
import os
import shutil
import unittest
from typing import Any

import jsonpath_ng
import jsonpath_ng.ext
import pytest

from dsp_tools.commands.excel2json import resources as e2j
from dsp_tools.models.exceptions import BaseError


class TestExcelToResource(unittest.TestCase):
    outfile = "testdata/tmp/_out_resources.json"

    @classmethod
    def setUpClass(cls) -> None:
        """Is executed once before the methods of this class are run"""
        os.makedirs("testdata/tmp", exist_ok=True)

    @classmethod
    def tearDownClass(cls) -> None:
        """Is executed after the methods of this class have all run through"""
        shutil.rmtree("testdata/tmp", ignore_errors=True)

    def test_excel2resources(self) -> None:
        excelfile = "testdata/excel2json/excel2json_files/test-name (test_label)/resources.xlsx"
        output_from_method, _ = e2j.excel2resources(excelfile, self.outfile)

        # define the expected values from the excel file
        excel_names = [
            "Owner",
            "Title",
            "GenericAnthroponym",
            "FamilyMember",
            "MentionedPerson",
            "Alias",
            "Image",
            "Video",
            "Audio",
            "ZIP",
            "PDFDocument",
        ]
        excel_supers = [
            ["Resource", "dcterms:fantasy"],
            ["Resource"],
            ["Resource"],
            ["Resource"],
            ["Resource"],
            ["Resource"],
            ["StillImageRepresentation", "dcterms:image"],
            ["MovingImageRepresentation"],
            ["AudioRepresentation"],
            ["ArchiveRepresentation"],
            ["DocumentRepresentation"],
        ]

        excel_labels = {
            "en": [
                "Owner",
                "Title",
                "Generic anthroponym",
                "Family member",
                "Mentioned person",
                "Alias",
                "Only English",
                "",
                "",
                "",
                "",
            ],
            "rm": [
                "Rumantsch",
                "Rumantsch",
                "Rumantsch",
                "Rumantsch",
                "Rumantsch",
                "Rumantsch",
                "",
                "",
                "",
                "",
                "Only Rumantsch",
            ],
        }
        excel_labels_of_image = {"en": "Only English"}

        excel_comments = {
            "comment_de": [
                "Ein seltsamer Zufall brachte mich in den Besitz dieses Tagebuchs.",
                "",
                "Only German",
                "",
                "",
                "",
                "Bild",
                "Video",
                "Audio",
                "ZIP",
                "PDF-Dokument",
            ],
            "comment_fr": [
                "Un étrange hasard m'a mis en possession de ce journal.",
                "",
                "",
                "Only French",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ],
        }
        excel_comments_of_image = {"en": "Image", "de": "Bild"}

        excel_first_class_properties = [
            ":hasAnthroponym",
            ":isOwnerOf",
            ":correspondsToGenericAnthroponym",
            ":hasAlias",
            ":hasGender",
            ":isDesignatedAs",
            ":hasTitle",
            ":hasStatus",
            ":hasFamilyRelationTo",
            ":hasLifeYearAmount",
            ":hasBirthDate",
            ":hasDeathDate",
            ":hasBibliography",
            ":hasRemarks",
        ]
        excel_first_class_cardinalities = [
            "1",
            "0-1",
            "0-n",
            "1",
            "0-n",
            "0-1",
            "1-n",
            "0-1",
            "1-n",
            "0-1",
            "0-1",
            "0-1",
            "1-n",
            "1-n",
        ]

        # read json file
        with open(self.outfile, encoding="utf-8") as f:
            output_from_file: list[dict[str, Any]] = json.load(f)

        # check that output from file and from method are equal
        self.assertListEqual(output_from_file, output_from_method)

        # extract infos from json file
        json_names = [match.value for match in jsonpath_ng.parse("$[*].name").find(output_from_file)]
        json_supers = [match.value for match in jsonpath_ng.parse("$[*].super").find(output_from_file)]

        json_labels_all = [match.value for match in jsonpath_ng.parse("$[*].labels").find(output_from_file)]
        json_labels = {lang: [label.get(lang, "").strip() for label in json_labels_all] for lang in ["en", "rm"]}
        json_labels_of_image = jsonpath_ng.ext.parse('$[?name="Image"].labels').find(output_from_file)[0].value

        # make sure the lists of the json comments contain a blank string,
        # even if there is no "comments" section at all in this resource
        json_comments = {
            f"comment_{lang}": [resource.get("comments", {}).get(lang, "").strip() for resource in output_from_file]
            for lang in ["de", "fr"]
        }
        json_comments_of_image = jsonpath_ng.ext.parse('$[?name="Image"].comments').find(output_from_file)[0].value

        json_first_class_properties = [
            match.value for match in jsonpath_ng.parse("$[0].cardinalities[*].propname").find(output_from_file)
        ]
        json_first_class_cardinalities = [
            match.value for match in jsonpath_ng.parse("$[0].cardinalities[*].cardinality").find(output_from_file)
        ]

        # make checks
        self.assertListEqual(excel_names, json_names)
        self.assertListEqual(excel_supers, json_supers)
        self.assertDictEqual(excel_labels, json_labels)
        self.assertDictEqual(excel_labels_of_image, json_labels_of_image)
        self.assertDictEqual(excel_comments, json_comments)
        self.assertDictEqual(excel_comments_of_image, json_comments_of_image)
        self.assertListEqual(excel_first_class_properties, json_first_class_properties)
        self.assertListEqual(excel_first_class_cardinalities, json_first_class_cardinalities)

    def test_validate_resources_with_schema(self) -> None:
        # it is not possible to call the method to be tested directly.
        # So let's make a reference to it, so that it can be found by the usage search
        lambda x: e2j._validate_resources([], "file")  # pylint: disable=expression-not-assigned

        testcases = [
            (
                "testdata/invalid-testdata/excel2json/resources-invalid-super.xlsx",
                "did not pass validation. The problem is that the Excel sheet 'classes' contains an invalid value "
                "for resource 'Title', in row 3, column 'super': 'fantasy' is not valid under any of the given schemas",
            ),
            (
                "testdata/invalid-testdata/excel2json/resources-invalid-missing-sheet.xlsx",
                "Worksheet named 'GenericAnthroponym' not found",
            ),
            (
                "testdata/invalid-testdata/excel2json/resources-invalid-cardinality.xlsx",
                "did not pass validation. The problem is that the Excel sheet 'Owner' contains an invalid value "
                "in row 3, column 'Cardinality': '0-2' is not one of",
            ),
            (
                "testdata/invalid-testdata/excel2json/resources-invalid-property.xlsx",
                "did not pass validation. The problem is that the Excel sheet 'FamilyMember' contains an invalid value "
                "in row 7, column 'Property': ':fan:ta:sy' does not match ",
            ),
            (
                "testdata/invalid-testdata/excel2json/resources-duplicate-name.xlsx",
                "Resource names must be unique inside every ontology, but your Excel file '.+' contains duplicates:\n"
                r" - Row 3: MentionedPerson\n - Row 4: MentionedPerson",
            ),
        ]

        for file, message in testcases:
            with self.assertRaisesRegex(BaseError, message):
                e2j.excel2resources(file, self.outfile)


if __name__ == "__main__":
    pytest.main([__file__])
