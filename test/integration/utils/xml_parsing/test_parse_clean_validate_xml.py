from pathlib import Path

import pytest
import regex
from lxml import etree

from dsp_tools.error.exceptions import InputError
from dsp_tools.utils.xml_parsing.parse_clean_validate_xml import parse_and_clean_xml_file
from dsp_tools.utils.xml_parsing.parse_clean_validate_xml import parse_and_validate_xml_file


@pytest.fixture
def data_systematic_unclean() -> Path:
    return Path("testdata/xml-data/test-data-systematic.xml")


@pytest.fixture
def data_systematic_cleaned(data_systematic_unclean: Path) -> etree._Element:
    return parse_and_clean_xml_file(data_systematic_unclean)


def _clean_resulting_tree(tree: etree._Element) -> str:
    cleaned_str = regex.sub("\n", "", etree.tostring(tree, encoding=str))
    return regex.sub(" +", " ", cleaned_str)


def test_parse_and_clean_xml_file_same_regardless_of_input(data_systematic_unclean: Path) -> None:
    from_tree = parse_and_clean_xml_file(data_systematic_unclean)
    from_file = parse_and_clean_xml_file(Path("testdata/xml-data/test-data-systematic.xml"))
    cleaned_from_file = _clean_resulting_tree(from_file)
    cleaned_from_tree = _clean_resulting_tree(from_tree)
    assert cleaned_from_file == cleaned_from_tree, (
        "The output must be equal, regardless if the input is a path or parsed."
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


def test_validate_xml_data_systematic() -> None:
    assert parse_and_validate_xml_file(input_file="testdata/xml-data/test-data-systematic.xml")


def test_validate_xml_data_minimal() -> None:
    assert parse_and_validate_xml_file(input_file="testdata/xml-data/test-data-minimal.xml")


def test_validate_xml_invalid_resource_tag_line_twelve() -> None:
    expected = regex.escape(
        "The XML file cannot be uploaded due to the following validation error(s):\n"
        "    Line 12: Element 'resource', attribute 'invalidtag': The attribute 'invalidtag' is not allowed."
    )
    with pytest.raises(InputError, match=expected):
        parse_and_validate_xml_file(input_file="testdata/invalid-testdata/xml-data/invalid-resource-tag.xml")


def test_validate_xml_data_duplicate_iri() -> None:
    expected_msg = regex.escape(
        "The XML file cannot be uploaded due to the following validation error(s):\n"
        "    Line 19: Element 'resource': Duplicate key-sequence ['http://rdfh.ch/4123/54SYvWF0QUW6a'] "
        "in unique identity-constraint 'IRI_attribute_of_resource_must_be_unique'."
    )
    with pytest.raises(InputError, match=expected_msg):
        parse_and_validate_xml_file(input_file="testdata/invalid-testdata/xml-data/duplicate-iri.xml")


def test_validate_xml_duplicate_ark() -> None:
    expected_msg = regex.escape(
        "The XML file cannot be uploaded due to the following validation error(s):\n"
        "    Line 19: Element 'resource': Duplicate key-sequence ['ark:/72163/4123-31ec6eab334-a.2022829'] "
        "in unique identity-constraint 'ARK_attribute_of_resource_must_be_unique'."
    )
    with pytest.raises(InputError, match=expected_msg):
        parse_and_validate_xml_file(input_file="testdata/invalid-testdata/xml-data/duplicate-ark.xml")


def test_validate_xml_empty_label() -> None:
    expected_msg = regex.escape(
        "The XML file cannot be uploaded due to the following validation error(s):\n"
        "    Line 11: Element 'resource', attribute 'label': [facet 'minLength'] "
        "The value '' has a length of '0'; this underruns the allowed minimum length of '1'."
    )
    with pytest.raises(InputError, match=expected_msg):
        parse_and_validate_xml_file(input_file="testdata/invalid-testdata/xml-data/empty-label.xml")


def test_beautify_err_msg() -> None:
    _match = (
        r"Line \d+: The resource ID 'res_1' is not valid\. IDs must be unique across the entire file\. "
        r"The function make_xsd_compatible_id\(\) assists you in creating IDs\.\n +"
        r"Line \d+: The resource ID 'res_2' is not valid\. IDs must be unique across the entire file\. "
        r"The function make_xsd_compatible_id\(\) assists you in creating IDs\."
    )
    with pytest.raises(InputError, match=_match):
        parse_and_validate_xml_file("testdata/invalid-testdata/xml-data/duplicate-res-id.xml")


if __name__ == "__main__":
    pytest.main([__file__])
