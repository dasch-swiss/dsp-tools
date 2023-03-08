"""unit tests for excel to properties"""
import json
import os
import unittest
from typing import Any

import jsonpath_ng
import jsonpath_ng.ext

from dsp_tools.utils import excel_to_json_properties as e2j


class TestExcelToProperties(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        """Is executed before the methods of this class are run"""
        os.makedirs('testdata/tmp', exist_ok=True)

    @classmethod
    def tearDownClass(cls) -> None:
        """Is executed after the methods of this class have all run through"""
        for file in os.listdir('testdata/tmp'):
            os.remove('testdata/tmp/' + file)
        os.rmdir('testdata/tmp')

    def test_excel2properties(self) -> None:
        excelfile = "testdata/excel2json/excel2json_files/test-name (test_label)/properties.xlsx"
        outfile = "testdata/tmp/_out_properties.json"
        output_from_method, _ = e2j.excel2properties(excelfile, outfile)

        # define the expected values from the excel file
        excel_names = ["correspondsToGenericAnthroponym", "hasAnthroponym", "hasGender", "isDesignatedAs", "hasTitle",
                       "hasStatus", "hasLifeYearAmount", "hasBirthDate", "hasRepresentation",
                       "hasRemarks", "hasTerminusPostQuem", "hasGND", "hasColor", "hasDecimal", "hasTime",
                       "hasInterval", "hasBoolean", "hasGeoname", "partOfDocument", "linkstoRegion", "hasLinkToImage",
                       "hasLinkToResource", "hasLinkToArchiveRepresentation", "hasLinkToMovingImageRepesentation",
                       "hasLinkToAudioRepesentation"]
        excel_supers = [["hasLinkTo"], ["hasValue", "dcterms:creator"], ["hasValue"], ["hasValue"], ["hasLinkTo"],
                        ["hasValue"], ["hasValue"], ["hasValue"], ["hasRepresentation"],
                        ["hasValue", "dcterms:description"], ["hasValue"], ["hasValue"], ["hasColor"], ["hasValue"],
                        ["hasValue"], ["hasSequenceBounds"], ["hasValue"], ["hasValue"], ["isPartOf"], ["hasLinkTo"],
                        ["hasLinkTo"], ["hasLinkTo"], ["hasLinkTo"], ["hasLinkTo"], ["hasLinkTo"]]
        excel_objects = [":GenericAnthroponym", "TextValue", "ListValue", "ListValue", ":Titles", "ListValue",
                         "IntValue", "DateValue", "Representation", "TextValue", "DateValue", "UriValue",
                         "ColorValue", "DecimalValue", "TimeValue", "IntervalValue", "BooleanValue", "GeonameValue",
                         ":Documents", "Region", "StillImageRepresentation", "Resource", "ArchiveRepresentation",
                         "MovingImageRepresentation", "AudioRepresentation"]

        excel_labels = dict()
        # there are also labels in other languages, but they are not tested
        excel_labels["de"] = ["", "only German", "", "", "", "", "", "",
                              "hat eine Multimediadatei", "", "", "GND", "Farbe", "Dezimalzahl", "Zeit",
                              "Zeitintervall", "Bool'sche Variable", "Link zu Geonames", "ist Teil eines Dokuments",
                              "", "", "", "", "", ""]
        excel_labels["it"] = ["", "", "", "only Italian", "", "", "", "", "", "", "", "GND", "", "", "", "", "", "", "",
                              "", "", "", "", "", ""]

        excel_comments = dict()
        # there are also comments in other languages, but they are not tested
        excel_comments["comment_fr"] = ["J'avais déjà examiné plusieurs propriétés quand, un jour, le notaire, qui me "
                                "donnait des indications nécessaires pour une de mes explorations, me dit :",
                                "Un étrange hasard m'a mis en possession de ce journal.",
                                "Je n'en sais rien du tout ; mais si vous voulez la voir, monsieur, voici les "
                                "indications précises pour la trouver.",
                                "Vous devrez arranger l'affaire avec le curé du village de --.\"",
                                "Un étrange hasard m'a mis en possession de ce journal.", "", "", "only French", "",
                                "", "J'avais déjà examiné plusieurs propriétés quand, un jour, le notaire, qui me "
                                "donnait des indications nécessaires pour une de mes explorations, me dit :",
                                "Gemeinsame Normdatei", "", "Chiffre décimale", "Temps", "", "", "", "", "", "", "", "",
                                        "", ""]
        excel_comments["comment_it"] = ["Avevo già visto diverse proprietà quando un giorno il notaio,",
                                "Uno strano caso mi mise in possesso di questo diario.",
                                "Non ne so nulla; ma se volete vederla, signore, eccovi le indicazioni precise per trovarla.",
                                "Dovrete organizzare l'affare con il curato del villaggio di --\".",
                                "Uno strano caso mi mise in possesso di questo diario.", "", "", "",
                                "", "", "Avevo già visto diverse proprietà quando un giorno il notaio,",
                                "Gemeinsame Normdatei", "", "", "", "", "", "", "", "", "", "", "", "", ""]

        excel_gui_elements = ["Searchbox", "Richtext", "List", "Radio", "Searchbox", "List", "Spinbox", "Date", 
                              "Searchbox", "Textarea", "Date", "SimpleText", "Colorpicker", "Slider",
                              "TimeStamp", "Interval", "Checkbox", "Geonames", "Searchbox", "Searchbox", "Searchbox",
                              "Searchbox", "Searchbox", "Searchbox", "Searchbox"]

        excel_gui_attributes_hasGender = {"hlist": "gender"}
        excel_gui_attributes_hasGND = {"size": 100}
        excel_gui_attributes_hasDecimal = {"min": 0.0, "max": 100.0}

        # read json file
        with open(outfile) as f:
            output_from_file: list[dict[str, Any]] = json.load(f)

        # check that output from file and from method are equal
        self.assertListEqual(output_from_file, output_from_method)

        # extract infos from json file
        json_names = [match.value for match in jsonpath_ng.parse("$[*].name").find(output_from_file)]
        json_supers = [match.value for match in jsonpath_ng.parse("$[*].super").find(output_from_file)]
        json_objects = [match.value for match in jsonpath_ng.parse("$[*].object").find(output_from_file)]

        json_labels_all = [match.value for match in jsonpath_ng.parse("$[*].labels").find(output_from_file)]
        json_labels: dict[str, list[str]] = dict()
        for lang in ["de", "it"]:
            json_labels[lang] = [label.get(lang, "").strip() for label in json_labels_all]

        json_comments: dict[str, list[str]] = dict()
        for lang in ["fr", "it"]:
            json_comments[f"comment_{lang}"] = [resource.get("comments", {}).get(lang, "").strip()
                                               for resource in output_from_file]

        json_gui_elements = [match.value for match in jsonpath_ng.parse("$[*].gui_element").find(output_from_file)]

        json_gui_attributes_hasGender = jsonpath_ng.ext.parse("$[?name='hasGender'].gui_attributes").find(output_from_file)[0].value
        json_gui_attributes_hasGND = jsonpath_ng.ext.parse("$[?name='hasGND'].gui_attributes").find(output_from_file)[0].value
        json_gui_attributes_hasDecimal = jsonpath_ng.ext.parse("$[?name='hasDecimal'].gui_attributes").find(output_from_file)[0].value

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


if __name__ == "__main__":
    unittest.main()
