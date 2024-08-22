from __future__ import annotations

from pathlib import Path

import pytest
import regex
from lxml import etree

from dsp_tools.utils.xml_utils import parse_and_clean_xml_file


@pytest.fixture
def data_systematic_unclean() -> Path:
    return Path("testdata/xml-data/test-data-systematic.xml")


@pytest.fixture
def data_systematic_cleaned() -> etree._Element:
    return parse_and_clean_xml_file(Path("testdata/xml-data/test-data-systematic.xml"))


def clean_resulting_tree(tree: etree._Element) -> str:
    cleaned_str = regex.sub("\n", "", etree.tostring(tree, encoding=str))
    return regex.sub(" +", " ", cleaned_str)


def test_parse_and_clean_xml_file_same_regardless_of_input(data_systematic_unclean: Path) -> None:
    from_tree = parse_and_clean_xml_file(data_systematic_unclean)
    from_file = parse_and_clean_xml_file(Path("testdata/xml-data/test-data-systematic.xml"))
    cleaned_from_file = clean_resulting_tree(from_file)
    cleaned_from_tree = clean_resulting_tree(from_tree)
    assert (
        cleaned_from_file == cleaned_from_tree
    ), "The output must be equal, regardless if the input is a path or parsed."


def test_annotations_regions_links_before(data_systematic_unclean: Path) -> None:
    data = etree.parse(data_systematic_unclean)
    annotations_regions_links_before = [e for e in data.iter() if regex.search("annotation|region|link", str(e.tag))]
    assert len(annotations_regions_links_before) == 5


def test_annotations_regions_links_after(data_systematic_cleaned: etree._Element) -> None:
    annotations_regions_links_after = [
        e for e in data_systematic_cleaned.iter() if regex.search("annotation|region|link", str(e.tag))
    ]
    assert len(annotations_regions_links_after) == 0, (
        "The tags <annotation>, <region>, and <link> must be transformed "
        'to their technically correct form <resource restype="Annotation/Region/LinkObj">'
    )


def test_comment_removal(data_systematic_unclean: Path, data_systematic_cleaned: etree._Element) -> None:
    data = etree.parse(data_systematic_unclean)
    comments_before = [e for e in data.iter() if isinstance(e, etree._Comment)]
    assert len(comments_before) > 0
    comments_after = [e for e in data_systematic_cleaned.iter() if isinstance(e, etree._Comment)]
    assert len(comments_after) == 0, (
        "properties that are commented out would break the the constructor of the class XMLProperty, "
        "if they are not removed in the parsing process"
    )


if __name__ == "__main__":
    pytest.main([__file__])
