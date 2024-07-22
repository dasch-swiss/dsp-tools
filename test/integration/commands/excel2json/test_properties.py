import unittest

import jsonpath_ng
import pytest
import regex

from dsp_tools.commands.excel2json import properties as e2j
from dsp_tools.models.exceptions import InputError

excelfile = "testdata/excel2json/excel2json_files/test-name (test_label)/properties.xlsx"
output_from_method, _ = e2j.excel2properties(excelfile, None)


# ruff: noqa: PT009 (pytest-unittest-assertion) (remove this line when pytest is used instead of unittest)
class TestValidateProperties:
    # it is not possible to call the method to be tested directly.
    # So let's make a reference to it, so that it can be found by the usage search
    lambda _: e2j._validate_properties_section_in_json([])

    def test_invalid_super(self) -> None:
        expected_msg = (
            "The Excel file 'properties.xlsx' contains the following problems:\n\n\n"
            "    Section of the problem: 'Properties'\n"
            "    Problematic property: 'hasGeoname'\n"
            "    Located at: Column 'super' | Row 3\n"
            "    Original Error Message: 'GeonameValue' is not valid under any of the given schemas"
        )
        with pytest.raises(InputError, match=expected_msg):
            e2j.excel2properties(
                excelfile="testdata/invalid-testdata/excel2json/properties-invalid-super.xlsx", path_to_output_file=""
            )

    def test_invalid_object(self) -> None:
        expected_msg = regex.escape(
            "The Excel file 'properties.xlsx' contains the following problems:\n\n\n"
            "    Section of the problem: 'Properties'\n"
            "    Problematic property: 'hasBoolean'\n"
            "    Located at: Column 'object' | Row 2\n"
            "    Original Error Message: 'hasValue' is not valid under any of the given schemas"
        )
        with pytest.raises(InputError, match=expected_msg):
            e2j.excel2properties(
                excelfile="testdata/invalid-testdata/excel2json/properties-invalid-object.xlsx", path_to_output_file=""
            )

    def test_invalid_gui_element(self) -> None:
        expected_msg = regex.escape(
            "The Excel file 'properties.xlsx' contains the following problems:\n\n\n"
            "    Section of the problem: 'Properties'\n"
            "    Problematic property: 'hasGeoname'\n"
            "    Located at: Column 'gui_element' | Row 3\n"
            "    Original Error Message: 'Geonames' was expected"
        )
        with pytest.raises(InputError, match=expected_msg):
            e2j.excel2properties(
                excelfile="testdata/invalid-testdata/excel2json/properties-invalid-gui_element.xlsx",
                path_to_output_file="",
            )

    def test_invalid_gui_attrib_values(self) -> None:
        expected_msg = regex.escape(
            "The Excel file 'properties.xlsx' contains the following problems:\n\n\n"
            "    Section of the problem: 'Properties'\n"
            "    Problematic property: 'hasInteger'\n"
            "    Located at: Column 'gui_attributes' | Row 4\n"
            "    Original Error Message: Additional properties are not allowed ('rows' was unexpected)"
        )
        with pytest.raises(InputError, match=expected_msg):
            e2j.excel2properties(
                excelfile="testdata/invalid-testdata/excel2json/properties-invalid-gui_attribute_values.xlsx",
                path_to_output_file="",
            )


def test_excel2properties_invalid_gui_attrib_format() -> None:
    expected_msg = regex.escape(
        "The Excel file 'properties.xlsx' contains the following problems:\n\n"
        "The property 'hasInteger' has the following problem(s):\n"
        "There is invalid content in the excel.\n"
        "Located at: Column 'gui_attributes' | Row 4\n"
        "Expected Content: attribute: value, attribute: value\n"
        "Actual Content: max=10, min=5"
    )
    with pytest.raises(InputError, match=expected_msg):
        e2j.excel2properties("testdata/invalid-testdata/excel2json/properties-invalid-gui_attribute_format.xlsx", "")


class TestExcelToProperties(unittest.TestCase):
    def test_names(self) -> None:
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
        json_names = [match.value for match in jsonpath_ng.parse("$[*].name").find(output_from_method)]
        self.assertListEqual(excel_names, json_names)

    def test_supers(self) -> None:
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
        json_supers = [match.value for match in jsonpath_ng.parse("$[*].super").find(output_from_method)]
        self.assertListEqual(excel_supers, json_supers)

    def test_objects(self) -> None:
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
        json_objects = [match.value for match in jsonpath_ng.parse("$[*].object").find(output_from_method)]
        self.assertListEqual(excel_objects, json_objects)

    def test_labels(self) -> None:
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
            ],
        }  # there are also labels in other languages, but they are not tested
        json_labels_all = [match.value for match in jsonpath_ng.parse("$[*].labels").find(output_from_method)]
        json_labels = {lang: [label.get(lang, "").strip() for label in json_labels_all] for lang in ["de", "it"]}
        self.assertDictEqual(excel_labels, json_labels)

    def test_comments(self) -> None:
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
            ],
        }  # there are also comments in other languages, but they are not tested
        json_comments = {
            f"comment_{lang}": [resource.get("comments", {}).get(lang, "").strip() for resource in output_from_method]
            for lang in ["fr", "it"]
        }
        self.assertDictEqual(excel_comments, json_comments)

    def test_gui_elements(self) -> None:
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

        json_gui_elements = [match.value for match in jsonpath_ng.parse("$[*].gui_element").find(output_from_method)]
        self.assertListEqual(excel_gui_elements, json_gui_elements)

    def test_gui_attributes_hasGender(self) -> None:
        excel_gui_attributes_hasGender = {"hlist": "gender"}
        json_gui_attributes_hasGender = (
            jsonpath_ng.ext.parse("$[?name='hasGender'].gui_attributes").find(output_from_method)[0].value
        )
        self.assertDictEqual(excel_gui_attributes_hasGender, json_gui_attributes_hasGender)

    def test_gui_attributes_hasGND(self) -> None:
        excel_gui_attributes_hasGND = {"size": 100}
        json_gui_attributes_hasGND = (
            jsonpath_ng.ext.parse("$[?name='hasGND'].gui_attributes").find(output_from_method)[0].value
        )
        self.assertDictEqual(excel_gui_attributes_hasGND, json_gui_attributes_hasGND)

    def test_gui_attributes_hasDecimal(self) -> None:
        excel_gui_attributes_hasDecimal = {"min": 0.0, "max": 100.0}
        json_gui_attributes_hasDecimal = (
            jsonpath_ng.ext.parse("$[?name='hasDecimal'].gui_attributes").find(output_from_method)[0].value
        )
        self.assertDictEqual(excel_gui_attributes_hasDecimal, json_gui_attributes_hasDecimal)


if __name__ == "__main__":
    pytest.main([__file__])
