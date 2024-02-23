import unittest

import pytest
import regex
from lxml import etree

from dsp_tools.commands.xmlupload.ark2iri import convert_ark_v0_to_resource_iri
from dsp_tools.models.exceptions import BaseError
from dsp_tools.utils.xml_utils import parse_and_clean_xml_file

# ruff: noqa: PT009 (pytest-unittest-assertion) (remove this line when pytest is used instead of unittest)
# ruff: noqa: PT027 (pytest-unittest-raises-assertion) (remove this line when pytest is used instead of unittest)


def clean_resulting_tree(tree: etree._Element) -> str:
    cleaned_str = regex.sub("\n", "", etree.tostring(tree, encoding=str))
    return regex.sub(" +", " ", cleaned_str)


class TestParseAndCleanXML(unittest.TestCase):
    def test_parse_and_clean_xml_file_same_regardless_of_input(self) -> None:
        test_data_systematic_tree = etree.parse("testdata/xml-data/test-data-systematic.xml")
        from_file = parse_and_clean_xml_file("testdata/xml-data/test-data-systematic.xml")
        from_tree = parse_and_clean_xml_file(test_data_systematic_tree)
        cleaned_from_file = clean_resulting_tree(from_file)
        cleaned_from_tree = clean_resulting_tree(from_tree)
        self.assertEqual(
            cleaned_from_file,
            cleaned_from_tree,
            msg="The output must be equal, regardless if the input is a path or parsed.",
        )

    def test_annotations_regions_links_before(self) -> None:
        test_data_systematic_tree = etree.parse("testdata/xml-data/test-data-systematic.xml")
        annotations_regions_links_before = [
            e for e in test_data_systematic_tree.iter() if regex.search("annotation|region|link", str(e.tag))
        ]
        self.assertGreater(len(annotations_regions_links_before), 0)

    def test_annotations_regions_links_after(self) -> None:
        from_file = parse_and_clean_xml_file("testdata/xml-data/test-data-systematic.xml")
        annotations_regions_links_after = [
            e for e in from_file.iter() if regex.search("annotation|region|link", str(e.tag))
        ]
        self.assertEqual(
            len(annotations_regions_links_after),
            0,
            msg="The tags <annotation>, <region>, and <link> must be transformed to their technically correct form "
            '<resource restype="Annotation/Region/LinkObj">',
        )

    def test_comment_removal(self) -> None:
        from_file = parse_and_clean_xml_file("testdata/xml-data/test-data-systematic.xml")
        comments = [e for e in from_file.iter() if isinstance(e, etree._Comment)]
        self.assertEqual(
            len(comments),
            0,
            msg="properties that are commented out would break the the constructor of the class XMLProperty, "
            "if they are not removed in the parsing process",
        )


class TestConvertArkToResourceIRI(unittest.TestCase):
    def test_good(self) -> None:
        ark = "ark:/72163/080c-779b9990a0c3f-6e"
        iri = convert_ark_v0_to_resource_iri(ark)
        self.assertEqual("http://rdfh.ch/080C/Ef9heHjPWDS7dMR_gGax2Q", iri)

    def test_invalid_ark(self) -> None:
        with self.assertRaisesRegex(
            BaseError, r"converting ARK 'ark:/72163/080c-779b999-0a0c3f-6e'\. The ARK seems to be invalid"
        ):
            convert_ark_v0_to_resource_iri("ark:/72163/080c-779b999-0a0c3f-6e")

    def test_invalid_shortcode(self) -> None:
        with self.assertRaisesRegex(
            BaseError, r"converting ARK 'ark:/72163/080X-779b9990a0c3f-6e'\. Invalid project shortcode '080X'"
        ):
            convert_ark_v0_to_resource_iri("ark:/72163/080X-779b9990a0c3f-6e")

    def test_invalid_shortcode_long(self) -> None:
        with self.assertRaisesRegex(
            BaseError, r"converting ARK 'ark:/72163/080c1-779b9990a0c3f-6e'\. Invalid project shortcode '080C1'"
        ):
            convert_ark_v0_to_resource_iri("ark:/72163/080c1-779b9990a0c3f-6e")

    def test_invalid_salsah_id(self) -> None:
        with self.assertRaisesRegex(
            BaseError, r"converting ARK 'ark:/72163/080c-779b99\+90a0c3f-6e'\. Invalid Salsah ID '779b99\+90a0c3f'"
        ):
            convert_ark_v0_to_resource_iri("ark:/72163/080c-779b99+90a0c3f-6e")


if __name__ == "__main__":
    pytest.main([__file__])
