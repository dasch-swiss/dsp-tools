"""unit tests for excel to resource"""
import os
import unittest
import json
import jsonpath_ng
import jsonpath_ng.ext
from typing import Any
from knora.dsplib.utils import excel_to_json_resources as e2j


class TestExcelToResource(unittest.TestCase):

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


    def test_excel2resources(self) -> None:
        excelfile = "testdata/Resources.xlsx"
        outfile = "testdata/tmp/_out_resources.json"
        output_from_method = e2j.excel2resources(excelfile, outfile)

        # define the expected values from the excel file
        excel_names = ["Owner", "Title", "GenericAnthroponym", "FamilyMember", "MentionedPerson", "Alias", "Image",
                       "Video", "Audio", "ZIP", "PDFDocument"]
        excel_supers = [["Resource", "dcterms:fantasy"], ["Resource"], ["Resource"], ["Resource"], ["Resource"],
                        ["Resource"], ["StillImageRepresentation", "dcterms:image"], ["MovingImageRepresentation"],
                        ["AudioRepresentation"], ["ArchiveRepresentation"], ["DocumentRepresentation"]]

        excel_labels = dict()
        excel_labels["en"] = ["Owner", "Title", "Generic anthroponym", "Family member", "Mentioned person", "Alias",
                              "Only English", "", "", "", ""]
        excel_labels["rm"] = ["Rumantsch", "Rumantsch", "Rumantsch", "Rumantsch", "Rumantsch", "Rumantsch", "", "", "",
                              "", "Only Rumantsch"]
        excel_labels_of_image = {"en": "Only English"}

        excel_comments = dict()
        excel_comments["comment_de"] = ["Ein seltsamer Zufall brachte mich in den Besitz dieses Tagebuchs.", "",
                                        "Only German", "", "", "", "Bild", "Video", "Audio", "ZIP", "PDF-Dokument"]
        excel_comments["comment_fr"] = ["Un étrange hasard m'a mis en possession de ce journal.", "", "", "Only French",
                                        "", "", "", "", "", "", ""]
        excel_comments_of_image = {"en": "Image", "de": "Bild"}

        excel_first_class_properties = [":hasAnthroponym", ":isOwnerOf", ":correspondsToGenericAnthroponym", ":hasAlias",
                                        ":hasGender", ":isDesignatedAs", ":hasTitle", ":hasStatus",
                                        ":hasFamilyRelationTo",":hasLifeYearAmount", ":hasBirthDate", ":hasDeathDate",
                                        ":hasBibliography", ":hasRemarks"]
        excel_first_class_cardinalities = ["1", "0-1", "0-n", "1", "0-n", "0-1", "1-n", "0-1", "1-n", "0-1", "0-1",
                                           "0-1", "1-n", "1-n"]

        # read json file
        with open(outfile) as f:
            output_from_file: list[dict[str, Any]] = json.load(f)

        # check that output from file and from method are equal
        self.assertListEqual(output_from_file, output_from_method)
            
        # extract infos from json file
        json_names = [match.value for match in jsonpath_ng.parse("$[*].name").find(output_from_file)]
        json_supers = [match.value for match in jsonpath_ng.parse("$[*].super").find(output_from_file)]

        json_labels_all = [match.value for match in jsonpath_ng.parse("$[*].labels").find(output_from_file)]
        json_labels: dict[str, list[str]] = dict()
        for lang in ["en", "rm"]:
            json_labels[lang] = [label.get(lang, "").strip() for label in json_labels_all]
        json_labels_of_image = jsonpath_ng.ext.parse('$[?name="Image"].labels').find(output_from_file)[0].value

        json_comments: dict[str, list[str]] = dict()
        for lang in ["de", "fr"]:
            # make sure the lists of the json comments contain a blank string even if there is no "comments" section
            # at all in this resource
            json_comments[f"comment_{lang}"] = [resource.get("comments", {}).get(lang, "").strip()
                                               for resource in output_from_file]
        json_comments_of_image = jsonpath_ng.ext.parse('$[?name="Image"].comments').find(output_from_file)[0].value

        json_first_class_properties = [match.value for match in
                                    jsonpath_ng.parse("$[0].cardinalities[*].propname").find(output_from_file)]
        json_first_class_cardinalities = [match.value for match in
                                    jsonpath_ng.parse("$[0].cardinalities[*].cardinality").find(output_from_file)]

        # make checks
        self.assertListEqual(excel_names, json_names)
        self.assertListEqual(excel_supers, json_supers)
        self.assertDictEqual(excel_labels, json_labels)
        self.assertDictEqual(excel_labels_of_image, json_labels_of_image)
        self.assertDictEqual(excel_comments, json_comments)
        self.assertDictEqual(excel_comments_of_image, json_comments_of_image)
        self.assertListEqual(excel_first_class_properties, json_first_class_properties)
        self.assertListEqual(excel_first_class_cardinalities, json_first_class_cardinalities)


if __name__ == "__main__":
    unittest.main()
