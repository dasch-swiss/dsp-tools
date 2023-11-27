# ruff: noqa: D101 (undocumented-public-class)
# ruff: noqa: D102 (undocumented-public-method)

import unittest

import pytest
import regex
from lxml import etree

from dsp_tools.commands.xmlupload.ark2iri import convert_ark_v0_to_resource_iri
from dsp_tools.models.exceptions import BaseError
from dsp_tools.utils.xml_utils import parse_and_clean_xml_file


class TestXMLUpload(unittest.TestCase):
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

        comments = [e for e in output1.iter() if isinstance(e, etree._Comment)]
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


if __name__ == "__main__":
    pytest.main([__file__])
