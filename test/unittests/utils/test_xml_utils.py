import pytest
import regex
from lxml import etree

from dsp_tools.utils.xml_utils import parse_and_clean_xml_file


def clean_resulting_tree(tree: etree._Element) -> str:
    cleaned_str = regex.sub("\n", "", etree.tostring(tree, encoding=str))
    return regex.sub(" +", " ", cleaned_str)


def test_parse_and_clean_xml_file_same_regardless_of_input() -> None:
    test_data_systematic_tree = etree.parse("testdata/xml-data/test-data-systematic.xml")
    from_file = parse_and_clean_xml_file("testdata/xml-data/test-data-systematic.xml")
    from_tree = parse_and_clean_xml_file(test_data_systematic_tree)
    cleaned_from_file = clean_resulting_tree(from_file)
    cleaned_from_tree = clean_resulting_tree(from_tree)
    assert (
        cleaned_from_file == cleaned_from_tree
    ), "The output must be equal, regardless if the input is a path or parsed."


def test_annotations_regions_links_before() -> None:
    test_data_systematic_tree = etree.parse("testdata/xml-data/test-data-systematic.xml")
    annotations_regions_links_before = [
        e for e in test_data_systematic_tree.iter() if regex.search("annotation|region|link", str(e.tag))
    ]
    assert len(annotations_regions_links_before) == 5


def test_annotations_regions_links_after() -> None:
    from_file = parse_and_clean_xml_file("testdata/xml-data/test-data-systematic.xml")
    annotations_regions_links_after = [
        e for e in from_file.iter() if regex.search("annotation|region|link", str(e.tag))
    ]
    assert len(annotations_regions_links_after) == 0, (
        "The tags <annotation>, <region>, and <link> must be transformed "
        'to their technically correct form <resource restype="Annotation/Region/LinkObj">'
    )


def test_comment_removal() -> None:
    from_file = parse_and_clean_xml_file("testdata/xml-data/test-data-systematic.xml")
    comments = [e for e in from_file.iter() if isinstance(e, etree._Comment)]
    assert len(comments) == 0, (
        "properties that are commented out would break the the constructor of the class XMLProperty, "
        "if they are not removed in the parsing process"
    )


if __name__ == "__main__":
    pytest.main([__file__])
