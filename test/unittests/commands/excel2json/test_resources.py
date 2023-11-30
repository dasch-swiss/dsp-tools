"""unit tests for excel to resource"""

# pylint: disable=missing-class-docstring,missing-function-docstring

import re
import unittest

import jsonpath_ng
import jsonpath_ng.ext
import pytest
from pytest_unordered import unordered

from dsp_tools.commands.excel2json import resources as e2j
from dsp_tools.models.exceptions import BaseError

excelfile = "testdata/excel2json/excel2json_files/test-name (test_label)/resources.xlsx"
output_from_method, _ = e2j.excel2resources(excelfile, None)


class TestExcelToResource(unittest.TestCase):
    def test_names(self) -> None:
        # make checks
        expected_names = [
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
        res_names = [match.value for match in jsonpath_ng.parse("$[*].name").find(output_from_method)]
        assert unordered(res_names) == expected_names

    def test_supers(self) -> None:
        expected_supers = [
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
        res_supers = [match.value for match in jsonpath_ng.parse("$[*].super").find(output_from_method)]
        assert unordered(res_supers) == expected_supers

    def test_labels(self) -> None:
        expected_labels = {
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
        res_labels_all = [match.value for match in jsonpath_ng.parse("$[*].labels").find(output_from_method)]
        res_labels = {lang: [label.get(lang, "").strip() for label in res_labels_all] for lang in ["en", "rm"]}
        self.assertDictEqual(res_labels, expected_labels)

    def test_image_labels(self) -> None:
        expected_labels_of_image = {"en": "Only English"}
        res_labels_of_image = jsonpath_ng.ext.parse('$[?name="Image"].labels').find(output_from_method)[0].value
        self.assertDictEqual(res_labels_of_image, expected_labels_of_image)

    def test_comments(self) -> None:
        expected_comments = {
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
        # make sure the lists of the json comments contain a blank string,
        # even if there is no "comments" section at all in this resource
        res_comments = {
            f"comment_{lang}": [resource.get("comments", {}).get(lang, "").strip() for resource in output_from_method]
            for lang in ["de", "fr"]
        }
        self.assertDictEqual(res_comments, expected_comments)

    def test_image_comments(self) -> None:
        expected_comments_of_image = {"en": "Image", "de": "Bild"}
        res_comments_of_image = jsonpath_ng.ext.parse('$[?name="Image"].comments').find(output_from_method)[0].value
        self.assertDictEqual(expected_comments_of_image, res_comments_of_image)

    def test_first_class_properties(self) -> None:
        expected_first_class_properties = [
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
        res_first_class_properties = [
            match.value for match in jsonpath_ng.parse("$[0].cardinalities[*].propname").find(output_from_method)
        ]
        assert unordered(res_first_class_properties) == expected_first_class_properties

    def test_cardinalities(self) -> None:
        expected_first_class_cardinalities = [
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
        res_first_class_cardinalities = [
            match.value for match in jsonpath_ng.parse("$[0].cardinalities[*].cardinality").find(output_from_method)
        ]
        assert unordered(res_first_class_cardinalities) == expected_first_class_cardinalities


class TestValidateWithSchema:
    # it is not possible to call the method to be tested directly.
    # So let's make a reference to it, so that it can be found by the usage search
    lambda x: e2j._validate_resources([], "file")  # pylint: disable=expression-not-assigned,protected-access

    def test_invalid_super(self) -> None:
        expected_msg = re.escape(
            (
                "did not pass validation. The problem is that the Excel sheet 'classes' contains an invalid value "
                "for resource 'Title', in row 3, column 'super': 'fantasy' is not valid under any of the given schemas"
            )
        )
        with pytest.raises(BaseError, match=expected_msg):
            e2j.excel2resources("testdata/invalid-testdata/excel2json/resources-invalid-super.xlsx", "")

    def test_missing_sheet(self) -> None:
        expected_msg = re.escape("Worksheet named 'GenericAnthroponym' not found")
        with pytest.raises(BaseError, match=expected_msg):
            e2j.excel2resources("testdata/invalid-testdata/excel2json/resources-invalid-missing-sheet.xlsx", "")

    def test_sheet_invalid_cardinality(self) -> None:
        expected_msg = re.escape(
            (
                "did not pass validation. The problem is that the Excel sheet 'Owner' contains an invalid value "
                "in row 3, column 'Cardinality': '0-2' is not one of"
            )
        )
        with pytest.raises(BaseError, match=expected_msg):
            e2j.excel2resources("testdata/invalid-testdata/excel2json/resources-invalid-cardinality.xlsx", "")

    def test_invalid_property(self) -> None:
        expected_msg = re.escape(
            (
                "did not pass validation. The problem is that the Excel sheet 'FamilyMember' contains an invalid value "
                "in row 7, column 'Property': ':fan:ta:sy' does not match "
            )
        )
        with pytest.raises(BaseError, match=expected_msg):
            e2j.excel2resources("testdata/invalid-testdata/excel2json/resources-invalid-property.xlsx", "")

    def test_duplicate_name(self) -> None:
        expected_msg = re.escape(
            (
                "Resource names must be unique inside every ontology, but your Excel file "
                "'testdata/invalid-testdata/excel2json/resources-duplicate-name.xlsx' contains duplicates:\n"
                " - Row 3: MentionedPerson\n"
                " - Row 4: MentionedPerson"
            )
        )
        with pytest.raises(BaseError, match=expected_msg):
            e2j.excel2resources("testdata/invalid-testdata/excel2json/resources-duplicate-name.xlsx", "")


if __name__ == "__main__":
    pytest.main([__file__])
