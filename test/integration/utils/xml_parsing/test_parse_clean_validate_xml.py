# mypy: disable-error-code="no-untyped-def"

from pathlib import Path

import pytest
import regex
from lxml import etree

from dsp_tools.error.exceptions import InputError
from dsp_tools.utils.xml_parsing.parse_clean_validate_xml import _reformat_error_message_str
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


def test_validate_xml_invalid_characters_in_resptr() -> None:
    expected_msg = regex.escape(
        "The XML file cannot be uploaded due to the following validation error(s):\n"
        "    Line 13: Element 'resptr': [facet 'pattern'] The value 'not|allowed|characters' "
        "is not accepted by the pattern "
    )
    with pytest.raises(InputError, match=expected_msg):
        parse_and_validate_xml_file(input_file="testdata/invalid-testdata/xml-data/invalid-resptr-characters.xml")


def test_beautify_err_msg() -> None:
    _match = (
        r"Line \d+: The resource ID 'res_1' is not valid\. IDs must be unique across the entire file\. "
        r"The function make_xsd_compatible_id\(\) assists you in creating IDs\.\n +"
        r"Line \d+: The resource ID 'res_2' is not valid\. IDs must be unique across the entire file\. "
        r"The function make_xsd_compatible_id\(\) assists you in creating IDs\."
    )
    with pytest.raises(InputError, match=_match):
        parse_and_validate_xml_file("testdata/invalid-testdata/xml-data/duplicate-res-id.xml")


class TestReformatErrorMessage:
    def test_empty_label(self):
        in_msg = (
            "Element '{https://dasch.swiss/schema}resource', attribute 'label': [facet 'minLength'] "
            "The value '' has a length of '0'; this underruns the allowed minimum length of '1'."
        )
        result = _reformat_error_message_str(in_msg, line_number=1)
        assert result.line_number == 1
        assert result.element == "resource"
        assert result.attribute == "label"
        assert result.message == "The value '' has a length of '0'; this underruns the allowed minimum length of '1'."

    def test_pattern_resource_id(self):
        in_msg = (
            "Element '{https://dasch.swiss/schema}resptr': [facet 'pattern'] "
            "The value 'not|allowed|characters' is not accepted by the pattern "
            "'([a-zA-Zçéàèöäüòôûâêñ_][a-zA-Zçéàèöäüòôûâêñ_]*)'."
        )
        result = _reformat_error_message_str(in_msg, line_number=1)
        assert result.line_number == 1
        assert result.element == "resptr"
        assert result.attribute is None
        assert result.message == "The value 'not|allowed|characters' is not accepted by the pattern for this value."

    def test_invalid_tag(self):
        in_msg = (
            "Element '{https://dasch.swiss/schema}resource', attribute 'invalidattrib': "
            "The attribute 'invalidattrib' is not allowed."
        )
        result = _reformat_error_message_str(in_msg, line_number=1)
        assert result.line_number == 1
        assert result.element == "resource"
        assert result.attribute == "invalidattrib"
        assert result.message == "The attribute 'invalidattrib' is not allowed."

    def test_duplicate_iri(self):
        in_msg = (
            "Element '{https://dasch.swiss/schema}resource': "
            "Duplicate key-sequence ['http://rdfh.ch/4123/54SYvWF0QUW6a'] in unique identity-constraint "
            "'{https://dasch.swiss/schema}IRI_attribute_of_resource_must_be_unique'."
        )
        result = _reformat_error_message_str(in_msg, line_number=1)
        assert result.line_number == 1
        assert result.element == "resource"
        assert result.attribute is None
        assert (
            result.message == "Duplicate key-sequence ['http://rdfh.ch/4123/54SYvWF0QUW6a'] "
            "in unique identity-constraint 'IRI_attribute_of_resource_must_be_unique'."
        )

    def test_duplicate_ark(self):
        in_msg = (
            "Element '{https://dasch.swiss/schema}resource': Duplicate key-sequence "
            "['ark:/72163/4123-31ec6eab334-a.2022829'] in unique identity-constraint "
            "'{https://dasch.swiss/schema}ARK_attribute_of_resource_must_be_unique'."
        )
        result = _reformat_error_message_str(in_msg, line_number=1)
        assert result.line_number == 1
        assert result.element == "resource"
        assert result.attribute is None
        assert (
            result.message == "Duplicate key-sequence ['ark:/72163/4123-31ec6eab334-a.2022829'] "
            "in unique identity-constraint 'ARK_attribute_of_resource_must_be_unique'."
        )

    def test_resource_id_problem(self):
        in_msg = (
            "Element '{https://dasch.swiss/schema}audio-segment', attribute 'id': "
            "'res_1' is not a valid value of the atomic type 'xs:ID'."
        )
        result = _reformat_error_message_str(in_msg, line_number=1)
        assert result.line_number == 1
        assert result.element == "audio-segment"
        assert result.attribute == "id"
        assert (
            result.message == "The provided resource id 'res_1' is either not a valid xsd:ID or not unique in the file."
        )


if __name__ == "__main__":
    pytest.main([__file__])
