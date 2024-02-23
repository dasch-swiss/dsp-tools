import unittest

import regex
from lxml import etree

from dsp_tools.utils.xml_utils import parse_and_clean_xml_file

# ruff: noqa: PT009 (pytest-unittest-assertion) (remove this line when pytest is used instead of unittest)


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
