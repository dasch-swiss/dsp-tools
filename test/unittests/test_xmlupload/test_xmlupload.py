"""Unit tests for xmlupload"""

# pylint: disable=missing-class-docstring,missing-function-docstring

import unittest

import pytest
import regex
from lxml import etree

from dsp_tools.models.exceptions import BaseError
from dsp_tools.utils.xml_utils import parse_and_clean_xml_file
from dsp_tools.utils.xmlupload.ark2iri import convert_ark_v0_to_resource_iri
from dsp_tools.utils.xmlupload.write_diagnostic_info import (
    _transform_server_url_to_foldername,
    determine_save_location_of_diagnostic_info,
)


class TestXMLUpload(unittest.TestCase):
    def test_transform_server_url_to_foldername(self) -> None:
        testcases: list[tuple[str, str]] = [
            ("https://api.test.dasch.swiss/", "test.dasch.swiss"),
            ("http://api.082e-test-server.dasch.swiss/", "082e-test-server.dasch.swiss"),
            ("http://0.0.0.0:12345", "localhost"),
            ("https://0.0.0.0:80/", "localhost"),
        ]
        for _input, expected_output in testcases:
            actual_output = _transform_server_url_to_foldername(_input)
            self.assertEqual(actual_output, expected_output)

    def test_determine_save_location_of_logs(self) -> None:
        shortcode = "082E"
        onto_name = "rosetta"
        testcases: list[tuple[str, str]] = [
            (
                "https://api.test.dasch.swiss/",
                f"/.dsp-tools/xmluploads/test.dasch.swiss/{shortcode}/{onto_name}",
            ),
            (
                "http://api.082e-test-server.dasch.swiss/",
                f"/.dsp-tools/xmluploads/082e-test-server.dasch.swiss/{shortcode}/{onto_name}",
            ),
        ]
        for server, expected_path in testcases:
            save_location, _, _ = determine_save_location_of_diagnostic_info(
                server=server,
                proj_shortcode=shortcode,
                onto_name=onto_name,
            )
            self.assertTrue(str(save_location).endswith(expected_path))
            self.assertTrue(save_location.is_dir())
            try:
                save_location.rmdir()
                save_location.parent.rmdir()
                save_location.parent.parent.rmdir()
            except OSError:
                # there was already stuff in the folder before this test: do nothing
                pass

    def test_parse_xml_file(self) -> None:
        test_data_systematic_tree = etree.parse("testdata/xml-data/test-data-systematic.xml")
        output1 = parse_and_clean_xml_file("testdata/xml-data/test-data-systematic.xml")
        output2 = parse_and_clean_xml_file(test_data_systematic_tree)
        result1 = regex.sub("\n", "", etree.tostring(output1, encoding=str))
        result1 = regex.sub(" +", " ", result1)
        result2 = regex.sub("\n", "", etree.tostring(output2, encoding=str))
        result2 = regex.sub(" +", " ", result2)
        self.assertEqual(result1, result2, msg="The output must be equal, regardless if the input is a path or parsed.")

        annotations_regions_links_before = [
            e for e in test_data_systematic_tree.iter() if regex.search("annotation|region|link", str(e.tag))
        ]
        annotations_regions_links_after = [
            e for e in output1.iter() if regex.search("annotation|region|link", str(e.tag))
        ]
        self.assertGreater(len(annotations_regions_links_before), 0)
        self.assertEqual(
            len(annotations_regions_links_after),
            0,
            msg="The tags <annotation>, <region>, and <link> must be transformed to their technically correct form "
            '<resource restype="Annotation/Region/LinkObj">',
        )

        comments = [e for e in output1.iter() if isinstance(e, etree._Comment)]  # pylint: disable=protected-access
        self.assertEqual(
            len(comments),
            0,
            msg="properties that are commented out would break the the constructor of the class XMLProperty, "
            "if they are not removed in the parsing process",
        )

    def test_convert_ark_v0_to_resource_iri(self) -> None:
        ark = "ark:/72163/080c-779b9990a0c3f-6e"
        iri = convert_ark_v0_to_resource_iri(ark)
        self.assertEqual("http://rdfh.ch/080C/Ef9heHjPWDS7dMR_gGax2Q", iri)

        with self.assertRaisesRegex(
            BaseError, r"converting ARK 'ark:/72163/080c-779b999-0a0c3f-6e'\. The ARK seems to be invalid"
        ):
            convert_ark_v0_to_resource_iri("ark:/72163/080c-779b999-0a0c3f-6e")

        with self.assertRaisesRegex(
            BaseError, r"converting ARK 'ark:/72163/080X-779b9990a0c3f-6e'\. Invalid project shortcode '080X'"
        ):
            convert_ark_v0_to_resource_iri("ark:/72163/080X-779b9990a0c3f-6e")

        with self.assertRaisesRegex(
            BaseError, r"converting ARK 'ark:/72163/080c1-779b9990a0c3f-6e'\. Invalid project shortcode '080C1'"
        ):
            convert_ark_v0_to_resource_iri("ark:/72163/080c1-779b9990a0c3f-6e")

        with self.assertRaisesRegex(
            BaseError, r"converting ARK 'ark:/72163/080c-779b99\+90a0c3f-6e'\. Invalid Salsah ID '779b99\+90a0c3f'"
        ):
            convert_ark_v0_to_resource_iri("ark:/72163/080c-779b99+90a0c3f-6e")

    # TODO: fix this test # pylint: disable=fixme
    # def test_remove_circular_references(self) -> None:
    #     # create a list of XMLResources from the test data file
    #     root = parse_and_clean_xml_file("testdata/xml-data/test-data-systematic.xml")
    #     resources = [XMLResource(x, "testonto") for x in root if x.tag == "resource"]

    #     # get the purged resources and the stashes from the function to be tested
    #     resources, stashed_xml_texts_original, stashed_resptr_props_original = remove_circular_references(
    #         resources=resources,
    #         verbose=False,
    #     )

    #     # make a list of all hashes from the stashed xml texts
    #     stashed_xml_texts_hashes = list()
    #     for res, propdict in stashed_xml_texts_original.items():
    #         for elem in propdict.values():
    #             for _hash in elem:
    #                 stashed_xml_texts_hashes.append(_hash)

    #     # make a version of the stashes with the IDs from the XML file instead of the Python objects
    #     stashed_xml_texts = {
    #         res.id: {prop.name: [str(x) for x in d.values()] for prop, d in _dict.items()}
    #         for res, _dict in stashed_xml_texts_original.items()
    #     }
    #     stashed_resptr_props = {
    #         res.id: {prop.name: l for prop, l in _dict.items()} for res, _dict in stashed_resptr_props_original.items()
    #     }

    #     # hardcode the expected values
    #     stashed_xml_texts_expected = {
    #         "test_thing_1": {
    #             "testonto:hasRichtext": [
    #                 "This text contains links to all resources: "
    #                 '<a class="salsah-link" href="IRI:test_thing_0:IRI">test_thing_0</a> '
    #                 '<a class="salsah-link" href="IRI:test_thing_1:IRI">test_thing_1</a> '
    #                 '<a class="salsah-link" href="IRI:image_thing_0:IRI">image_thing_0</a> '
    #                 '<a class="salsah-link" href="IRI:compound_thing_0:IRI">compound_thing_0</a> '
    #                 '<a class="salsah-link" href="IRI:partof_thing_1:IRI">partof_thing_1</a> '
    #                 '<a class="salsah-link" href="IRI:partof_thing_2:IRI">partof_thing_2</a> '
    #                 '<a class="salsah-link" href="IRI:partof_thing_3:IRI">partof_thing_3</a> '
    #                 '<a class="salsah-link" href="IRI:document_thing_1:IRI">document_thing_1</a> '
    #                 '<a class="salsah-link" href="IRI:text_thing_1:IRI">text_thing_1</a> '
    #                 '<a class="salsah-link" href="IRI:zip_thing_1:IRI">zip_thing_1</a> '
    #                 '<a class="salsah-link" href="IRI:audio_thing_1:IRI">audio_thing_1</a> '
    #                 '<a class="salsah-link" href="IRI:test_thing_2:IRI">test_thing_2</a> '
    #                 '<a class="salsah-link" href="http://rdfh.ch/4123/DiAmYQzQSzC7cdTo6OJMYA">test_thing_with_iri_1</a>'
    #             ]
    #         },
    #         "test_thing_2": {
    #             "testonto:hasRichtext": [
    #                 "This text contains links to all resources: "
    #                 '<a class="salsah-link" href="IRI:test_thing_0:IRI">test_thing_0</a> '
    #                 '<a class="salsah-link" href="IRI:test_thing_1:IRI">test_thing_1</a> '
    #                 '<a class="salsah-link" href="IRI:image_thing_0:IRI">image_thing_0</a> '
    #                 '<a class="salsah-link" href="IRI:compound_thing_0:IRI">compound_thing_0</a> '
    #                 '<a class="salsah-link" href="IRI:partof_thing_1:IRI">partof_thing_1</a> '
    #                 '<a class="salsah-link" href="IRI:partof_thing_2:IRI">partof_thing_2</a> '
    #                 '<a class="salsah-link" href="IRI:partof_thing_3:IRI">partof_thing_3</a> '
    #                 '<a class="salsah-link" href="IRI:document_thing_1:IRI">document_thing_1</a> '
    #                 '<a class="salsah-link" href="IRI:text_thing_1:IRI">text_thing_1</a> '
    #                 '<a class="salsah-link" href="IRI:zip_thing_1:IRI">zip_thing_1</a> '
    #                 '<a class="salsah-link" href="IRI:audio_thing_1:IRI">audio_thing_1</a> '
    #                 '<a class="salsah-link" href="IRI:test_thing_2:IRI">test_thing_2</a>'
    #             ]
    #         },
    #     }
    #     stashed_resptr_props_expected = {
    #         "test_thing_0": {"testonto:hasTestThing": ["test_thing_1"]},
    #         "test_thing_1": {"testonto:hasResource": ["test_thing_2", "link_obj_1"]},
    #     }

    #     # check if the stashes are equal to the expected stashes
    #     self.assertDictEqual(stashed_resptr_props, stashed_resptr_props_expected)
    #     self.assertDictEqual(stashed_xml_texts, stashed_xml_texts_expected)

    #     # check if the stashed hashes can also be found at the correct position in the purged resources
    #     for res, propdict in stashed_xml_texts_original.items():
    #         for prop, hashdict in propdict.items():
    #             stashed_hashes = list(hashdict.keys())
    #             purged_res = resources[resources.index(res)]
    #             purged_prop = purged_res.properties[purged_res.properties.index(prop)]
    #             purged_hashes = [
    #                 str(val.value) for val in purged_prop.values if str(val.value) in stashed_xml_texts_hashes
    #             ]
    #             self.assertListEqual(stashed_hashes, purged_hashes)


if __name__ == "__main__":
    pytest.main([__file__])
