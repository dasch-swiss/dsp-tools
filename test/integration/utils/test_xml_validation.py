import pytest
import regex

from dsp_tools.models.custom_warnings import DspToolsUserWarning
from dsp_tools.models.exceptions import InputError
from dsp_tools.utils.xml_validation import validate_xml_file


def test_validate_xml_data_systematic() -> None:
    assert validate_xml_file(input_file="testdata/xml-data/test-data-systematic.xml")


def test_validate_xml_data_minimal() -> None:
    assert validate_xml_file(input_file="testdata/xml-data/test-data-minimal.xml")


def test_validate_xml_invalid_resource_tag_line_twelve() -> None:
    expected = regex.escape(
        "The XML file cannot be uploaded due to the following validation error(s):\n"
        "    Line 12: Element 'resource', attribute 'invalidtag': The attribute 'invalidtag' is not allowed."
    )
    with pytest.raises(InputError, match=expected):
        validate_xml_file(input_file="testdata/invalid-testdata/xml-data/invalid-resource-tag.xml")


def test_validate_xml_invalid_resource_tag_problem() -> None:
    expected_msg = regex.escape(
        "Angular brackets in the format of <text> were found in text properties with encoding=utf8.\n"
        "Please note that these will not be recognised as formatting in the text field, "
        "but will be displayed as-is.\n"
        "The following resources of your XML file contain angular brackets:\n"
        "    - line 13: resource 'the_only_resource', property ':test'\n"
        "    - line 14: resource 'the_only_resource', property ':test'\n"
        "    - line 15: resource 'the_only_resource', property ':test'\n"
        "    - line 16: resource 'the_only_resource', property ':test'",
    )
    with pytest.warns(DspToolsUserWarning, match=expected_msg):
        validate_xml_file(input_file="testdata/invalid-testdata/xml-data/utf8-text-with-xml-tags.xml")


def test_validate_xml_data_duplicate_iri() -> None:
    expected_msg = regex.escape(
        "The XML file cannot be uploaded due to the following validation error(s):\n"
        "    Line 19: Element 'resource': Duplicate key-sequence ['http://rdfh.ch/4123/54SYvWF0QUW6a'] "
        "in unique identity-constraint 'IRI_attribute_of_resource_must_be_unique'."
    )
    with pytest.raises(InputError, match=expected_msg):
        validate_xml_file(input_file="testdata/invalid-testdata/xml-data/duplicate-iri.xml")


def test_validate_xml_duplicate_ark() -> None:
    expected_msg = regex.escape(
        "The XML file cannot be uploaded due to the following validation error(s):\n"
        "    Line 19: Element 'resource': Duplicate key-sequence ['ark:/72163/4123-31ec6eab334-a.2022829'] "
        "in unique identity-constraint 'ARK_attribute_of_resource_must_be_unique'."
    )
    with pytest.raises(InputError, match=expected_msg):
        validate_xml_file(input_file="testdata/invalid-testdata/xml-data/duplicate-ark.xml")


def test_validate_xml_empty_label() -> None:
    expected_msg = regex.escape(
        "The XML file cannot be uploaded due to the following validation error(s):\n"
        "    Line 11: Element 'resource', attribute 'label': [facet 'minLength'] "
        "The value '' has a length of '0'; this underruns the allowed minimum length of '1'."
    )
    with pytest.raises(InputError, match=expected_msg):
        validate_xml_file(input_file="testdata/invalid-testdata/xml-data/empty-label.xml")


if __name__ == "__main__":
    pytest.main([__file__])
