"""unit tests for excel to resource"""
import os
import unittest
import json
import jsonpath_ng
import jsonpath_ng.ext
import pandas as pd
import numpy as np

from knora.dsplib.utils import excel_to_json_resources as e2j


class TestExcelToResource(unittest.TestCase):

    def setUp(self) -> None:
        """Is executed before each test"""
        os.makedirs("testdata/tmp", exist_ok=True)

    def test_prepare_dataframe(self) -> None:
        original_df = pd.DataFrame({
             "  TitLE of Column 1 ": ["1",  " 0-1 ", "1-n ", pd.NA,  "    ", " ",    "",     " 0-n ", np.nan],
             " Title of Column 2 ":  [None, "1",     1,      "text", "text", "text", "text", "text",  "text"],
             "Title of Column 3":    ["",   pd.NA,   None,   "text", "text", "text", "text", np.nan,  "text"]
        })
        expected_df = pd.DataFrame({
            "title of column 1":     [      "0-1", "1-n",                                  "0-n"],
            "title of column 2":     [      "1",   "1",                                    "text"],
            "title of column 3":     [      "",    "",                                     ""]
        })
        returned_df = e2j.prepare_dataframe(
            df=original_df,
            required_columns=["  TitLE of Column 1 ", " Title of Column 2 "],
            location_of_sheet=''
        )
        for expected, returned in zip(expected_df.iterrows(), returned_df.iterrows()):
            _, expected_row = expected
            _, returned_row = returned
            self.assertListEqual(list(expected_row), list(returned_row))

    def test_excel2json(self) -> None:
        excelfile = "testdata/Resources.xlsx"
        outfile = "testdata/tmp/_out_res.json"
        e2j.resources_excel2json(excelfile, outfile)

        # define the expected values from the excel file
        excel_names = ["Owner", "Title", "GenericAnthroponym", "FamilyMember", "MentionedPerson", "Alias", "Image",
                       "Video", "Audio", "ZIP", "PDFDocument", "Annotation", "LinkObject", "RegionOfImage"]
        excel_supers = [["Resource", "dcterms:fantasy"], ["Resource"], ["Resource"], ["Resource"], ["Resource"],
                        ["Resource"], ["StillImageRepresentation", "dcterms:image"], ["MovingImageRepresentation"],
                        ["AudioRepresentation"], ["ArchiveRepresentation"], ["DocumentRepresentation"], ["Annotation"],
                        ["LinkObj"], ["Region"]]

        excel_labels = dict()
        excel_labels["en"] = ["Owner", "Title", "Generic anthroponym", "Family member", "Mentioned person", "Alias",
                              "Only English", "", "", "", "", "Annotation", "Link Object", "Region of an image"]
        excel_labels["rm"] = ["Rumantsch", "Rumantsch", "Rumantsch", "Rumantsch", "Rumantsch", "Rumantsch", "", "", "",
                              "", "Only Rumantsch", "", "", ""]
        excel_labels_of_Image = {"en": "Only English"}

        excel_comments = dict()
        excel_comments["comment_de"] = ["Ein seltsamer Zufall brachte mich in den Besitz dieses Tagebuchs.", "",
                                        "Only German", "", "", "", "Bild", "Video", "Audio", "ZIP", "PDF-Dokument",
                                        "Annotation", "Linkobjekt", ""]
        excel_comments["comment_fr"] = ["Un étrange hasard m'a mis en possession de ce journal.", "", "", "Only French",
                                        "", "", "", "", "", "", "", "", "", ""]
        excel_comments_of_Image = {"en": "Image", "de": "Bild"}

        excel_first_class_properties = [":hasAnthroponym", ":isOwnerOf", ":correspondsToGenericAnthroponym", ":hasAlias",
                                        ":hasGender", ":isDesignatedAs", ":hasTitle", ":hasStatus",
                                        ":hasFamilyRelationTo",":hasLifeYearAmount", ":hasBirthDate", ":hasDeathDate",
                                        ":hasBibliography", ":hasRemarks"]
        excel_first_class_cardinalities = ["1", "0-1", "0-n", "1", "0-n", "0-1", "1-n", "0-1", "1-n", "0-1", "0-1",
                                           "0-1", "1-n", "1-n"]

        # read json file
        with open(outfile) as f:
            json_string = f.read()
            json_string = "{" + json_string + "}"
            json_file = json.loads(json_string)

        # extract infos from json file
        json_names = [match.value for match in jsonpath_ng.parse("$.resources[*].name").find(json_file)]
        json_supers = [match.value for match in jsonpath_ng.parse("$.resources[*].super").find(json_file)]

        json_labels_all = [match.value for match in jsonpath_ng.parse("$.resources[*].labels").find(json_file)]
        json_labels: dict[str, list[str]] = dict()
        for lang in ["en", "rm"]:
            json_labels[lang] = [label.get(lang, "").strip() for label in json_labels_all]
        json_labels_of_Image = jsonpath_ng.ext.parse('$.resources[?name="Image"].labels').find(json_file)[0].value

        json_comments: dict[str, list[str]] = dict()
        for lang in ["de", "fr"]:
            # make sure the lists of the json comments contain a blank string even if there is no "comments" section
            # at all in this resource
            json_comments[f"comment_{lang}"] = [resource.get("comments", {}).get(lang, "").strip()
                                               for resource in json_file["resources"]]
        json_comments_of_Image = jsonpath_ng.ext.parse('$.resources[?name="Image"].comments').find(json_file)[0].value

        json_first_class_properties = [match.value for match in
                                    jsonpath_ng.parse("$.resources[0].cardinalities[*].propname").find(json_file)]
        json_first_class_cardinalities = [match.value for match in
                                    jsonpath_ng.parse("$.resources[0].cardinalities[*].cardinality").find(json_file)]

        # make checks
        self.assertListEqual(excel_names, json_names)
        self.assertListEqual(excel_supers, json_supers)
        self.assertDictEqual(excel_labels, json_labels)
        self.assertDictEqual(excel_labels_of_Image, json_labels_of_Image)
        self.assertDictEqual(excel_comments, json_comments)
        self.assertDictEqual(excel_comments_of_Image, json_comments_of_Image)
        self.assertListEqual(excel_first_class_properties, json_first_class_properties)
        self.assertListEqual(excel_first_class_cardinalities, json_first_class_cardinalities)


if __name__ == "__main__":
    unittest.main()
