"""unit tests for excel to properties"""
import os
import unittest
import json
import jsonpath_ng
import jsonpath_ng.ext

from knora.dsplib.utils import excel_to_json_properties as e2j


class TestExcelToProperties(unittest.TestCase):

    def setUp(self) -> None:
        """Is executed before each test"""
        os.makedirs("testdata/tmp", exist_ok=True)

    def test_excel2json(self) -> None:
        excelfile = "testdata/Properties.xlsx"
        outfile = "testdata/tmp/_out_properties.json"
        e2j.properties_excel2json(excelfile, outfile)

        # define the expected values from the excel file
        excel_names = ["correspondsToGenericAnthroponym", "hasAnthroponym", "hasGender", "isDesignatedAs", "hasTitle",
                       "hasStatus", "hasLifeYearAmount", "hasBirthDate", "hasRepresentation",
                       "hasRemarks", "hasTerminusPostQuem", "hasGND", "hasColor", "hasDecimal", "hasTime",
                       "hasInterval", "hasBoolean", "hasGeoname", "partOfDocument"]
        excel_supers = [["hasLinkTo"], ["hasValue", "dcterms:creator"], ["hasValue"], ["hasValue"], ["hasLinkTo"],
                        ["hasValue"], ["hasValue"], ["hasValue"], ["hasRepresentation"],
                        ["hasValue", "dcterms:description"], ["hasValue"],["hasValue"], ["hasColor"], ["hasValue"],
                        ["hasValue"], ["hasValue"], ["hasValue"], ["hasValue"], ["isPartOf"]]
        excel_objects = [":GenericAnthroponym", "TextValue", "ListValue", "ListValue", ":Titles", "ListValue",
                         "IntValue", "DateValue", "Representation", "TextValue", "DateValue", "UriValue",
                         "ColorValue", "DecimalValue", "TimeValue", "IntervalValue", "BooleanValue", "GeonameValue",
                         ":Documents"]

        excel_labels = dict()
        excel_labels["de"] = ["", "only German", "", "", "", "", "", "",
                              "hat eine Multimediadatei", "", "", "GND", "Farbe", "Dezimalzahl", "Zeit",
                              "Zeitintervall", "Bool'sche Variable", "Link zu Geonames", "ist Teil eines Dokuments"]
        excel_labels["it"] = ["", "", "", "only Italian", "", "", "", "", "", "", "", "GND", "", "", "", "", "", "", ""]

        excel_comments = dict()
        excel_comments["comment_fr"] = ["J'avais déjà examiné plusieurs propriétés quand, un jour, le notaire, qui me "
                                "donnait des indications nécessaires pour une de mes explorations, me dit :",
                                "Un étrange hasard m'a mis en possession de ce journal.",
                                "Je n'en sais rien du tout ; mais si vous voulez la voir, monsieur, voici les "
                                "indications précises pour la trouver.",
                                "Vous devrez arranger l'affaire avec le curé du village de --.\"",
                                "Un étrange hasard m'a mis en possession de ce journal.", "", "", "only French", "",
                                "", "J'avais déjà examiné plusieurs propriétés quand, un jour, le notaire, qui me "
                                "donnait des indications nécessaires pour une de mes explorations, me dit :",
                                "Gemeinsame Normdatei", "", "Chiffre décimale", "Temps", "", "", "", ""]
        excel_comments["comment_it"] = ["Avevo già visto diverse proprietà quando un giorno il notaio,",
                                "Uno strano caso mi mise in possesso di questo diario.",
                                "Non ne so nulla; ma se volete vederla, signore, eccovi le indicazioni precise per trovarla.",
                                "Dovrete organizzare l'affare con il curato del villaggio di --\".",
                                "Uno strano caso mi mise in possesso di questo diario.", "", "", "",
                                "", "", "Avevo già visto diverse proprietà quando un giorno il notaio,",
                                "Gemeinsame Normdatei", "", "", "", "", "", "", ""]

        excel_gui_elements = ["Searchbox", "Richtext", "List", "Radio", "Searchbox", "List", "Spinbox", "Date", 
                              "Searchbox", "Textarea", "Date", "SimpleText", "Colorpicker", "Slider",
                              "TimeStamp", "Interval", "Checkbox", "Geonames", "Searchbox"]

        excel_gui_attributes_hasGender = {"hlist": "gender"}
        excel_gui_attributes_hasGND = {"size": 100}
        excel_gui_attributes_hasDecimal = {"min": 0.0, "max": 100.0}

        # read json file
        with open(outfile) as f:
            json_string = f.read()
            json_string = "{" + json_string + "}"
            json_file = json.loads(json_string)

        # extract infos from json file
        json_names = [match.value for match in jsonpath_ng.parse("$.properties[*].name").find(json_file)]
        json_supers = [match.value for match in jsonpath_ng.parse("$.properties[*].super").find(json_file)]
        json_objects = [match.value for match in jsonpath_ng.parse("$.properties[*].object").find(json_file)]

        json_labels_all = [match.value for match in jsonpath_ng.parse("$.properties[*].labels").find(json_file)]
        json_labels: dict[str, list[str]] = dict()
        for lang in ["de", "it"]:
            json_labels[lang] = [label.get(lang, "").strip() for label in json_labels_all]

        json_comments: dict[str, list[str]] = dict()
        for lang in ["fr", "it"]:
            json_comments[f"comment_{lang}"] = [resource.get("comments", {}).get(lang, "").strip()
                                               for resource in json_file["properties"]]

        json_gui_elements = [match.value for match in jsonpath_ng.parse("$.properties[*].gui_element").find(json_file)]

        json_gui_attributes_hasGender = jsonpath_ng.ext.parse("$.properties[?name='hasGender'].gui_attributes").find(json_file)[0].value
        json_gui_attributes_hasGND = jsonpath_ng.ext.parse("$.properties[?name='hasGND'].gui_attributes").find(json_file)[0].value
        json_gui_attributes_hasDecimal = jsonpath_ng.ext.parse("$.properties[?name='hasDecimal'].gui_attributes").find(json_file)[0].value

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
