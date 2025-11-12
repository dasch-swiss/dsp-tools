# mypy: disable-error-code="no-untyped-def"

from pathlib import Path

import pytest
from lxml import etree

from dsp_tools.utils.xml_parsing.parse_clean_validate_xml import _parse_xml_file
from dsp_tools.utils.xml_parsing.parse_clean_validate_xml import _reformat_error_message_str
from dsp_tools.utils.xml_parsing.parse_clean_validate_xml import _remove_comments_from_element_tree
from dsp_tools.utils.xml_parsing.parse_clean_validate_xml import _validate_root_get_validation_messages
from dsp_tools.utils.xml_parsing.parse_clean_validate_xml import parse_and_clean_xml_file
from dsp_tools.utils.xml_parsing.parse_clean_validate_xml import parse_and_validate_xml_file


def test_comment_removal() -> None:
    input_file = Path("testdata/xml-data/test-data-systematic-4123.xml")
    data_systematic_uncleaned = etree.parse(input_file)
    data_systematic_cleaned = parse_and_clean_xml_file(input_file)
    comments_before = [e for e in data_systematic_uncleaned.iter() if isinstance(e, etree._Comment)]
    assert len(comments_before) > 0
    comments_after = [e for e in data_systematic_cleaned.iter() if isinstance(e, etree._Comment)]
    assert len(comments_after) == 0, (
        "properties that are commented out would break the the constructor of the class XMLProperty, "
        "if they are not removed in the parsing process"
    )


def test_validate_xml_data_systematic() -> None:
    assert parse_and_validate_xml_file(input_file="testdata/xml-data/test-data-systematic-4123.xml")


def test_validate_xml_data_minimal() -> None:
    assert parse_and_validate_xml_file(input_file="testdata/xml-data/test-data-minimal-4124.xml")


def _prepare_root(input_file: Path) -> etree._Element:
    root = _parse_xml_file(input_file)
    root = _remove_comments_from_element_tree(root)
    return root


def test_validate_xml_invalid_resource_tag_line_twelve() -> None:
    root = _prepare_root(Path("testdata/invalid-testdata/xml-data/invalid-resource-tag-4124.xml"))
    validation_messages = _validate_root_get_validation_messages(root)
    assert validation_messages
    assert len(validation_messages) == 1
    result = validation_messages[0]
    assert result.line_number == 12
    assert result.element == "resource"
    assert result.attribute == "invalidtag"
    assert "The attribute 'invalidtag' is not allowed" in result.message


def test_validate_xml_data_duplicate_iri() -> None:
    root = _prepare_root(Path("testdata/invalid-testdata/xml-data/duplicate-iri-4124.xml"))
    validation_messages = _validate_root_get_validation_messages(root)
    assert validation_messages
    assert len(validation_messages) == 1
    result = validation_messages[0]
    assert result.line_number == 19
    assert result.element == "resource"
    assert result.attribute is None
    assert (
        result.message == "Duplicate key-sequence ['http://rdfh.ch/4123/54SYvWF0QUW6a'] "
        "in unique identity-constraint 'IRI_attribute_of_resource_must_be_unique'."
    )


def test_validate_xml_duplicate_ark() -> None:
    root = _prepare_root(Path("testdata/invalid-testdata/xml-data/duplicate-ark-4124.xml"))
    validation_messages = _validate_root_get_validation_messages(root)
    assert validation_messages
    assert len(validation_messages) == 1
    result = validation_messages[0]
    assert result.line_number == 19
    assert result.element == "resource"
    assert result.attribute is None
    assert (
        result.message == "Duplicate key-sequence ['ark:/72163/4123-31ec6eab334-a.2022829'] "
        "in unique identity-constraint 'ARK_attribute_of_resource_must_be_unique'."
    )


def test_validate_xml_empty_label() -> None:
    root = _prepare_root(Path("testdata/invalid-testdata/xml-data/empty-label-4124.xml"))
    validation_messages = _validate_root_get_validation_messages(root)
    assert validation_messages
    assert len(validation_messages) == 1
    result = validation_messages[0]
    assert result.line_number == 11
    assert result.element == "resource"
    assert result.attribute == "label"
    assert result.message == "The value '' has a length of '0'; this underruns the allowed minimum length of '1'."


def test_validate_xml_invalid_characters_in_resptr() -> None:
    root = _prepare_root(Path("testdata/invalid-testdata/xml-data/invalid-resptr-characters-4124.xml"))
    validation_messages = _validate_root_get_validation_messages(root)
    assert validation_messages
    assert len(validation_messages) == 1
    result = validation_messages[0]
    assert result.line_number == 13
    assert result.element == "resptr"
    assert result.attribute is None
    assert result.message == "The value 'not|allowed|characters' is not accepted by the pattern for this value."


def test_beautify_err_msg() -> None:
    root = _prepare_root(Path("testdata/invalid-testdata/xml-data/duplicate-res-id-4124.xml"))
    validation_messages = _validate_root_get_validation_messages(root)
    assert validation_messages
    assert len(validation_messages) == 2
    result_1 = validation_messages[0]
    result_2 = validation_messages[1]
    assert result_1.element == "audio-segment"
    assert result_2.element == "region"
    assert result_1.attribute == "id"
    assert result_2.attribute == "id"
    expected_msg = "The provided resource id 'res_1' is either not a valid xsd:ID or not unique in the file."
    assert expected_msg in result_1.message
    expected_msg = "The provided resource id 'res_2' is either not a valid xsd:ID or not unique in the file."
    assert expected_msg in result_2.message


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
            "The provided resource id 'res_1' is either not a valid xsd:ID or not unique in the file." in result.message
        )


if __name__ == "__main__":
    pytest.main([__file__])
