import pytest
from lxml import etree

from dsp_tools.models.exceptions import InputError
from dsp_tools.utils.xml_validation import validate_xml


def test_validate_xml_data_systematic() -> None:
    assert validate_xml(input_file="testdata/xml-data/test-data-systematic.xml") is True


def test_validate_xml_data_minimal() -> None:
    assert validate_xml(input_file=etree.parse(source="testdata/xml-data/test-data-minimal.xml")) is True


def test_validate_xml_invalid_resource_tag_line_twelve() -> None:
    with pytest.raises(
        InputError,
        match=r"Line 12: Element 'resource', attribute 'invalidtag': The attribute 'invalidtag' is not allowed",
    ):
        validate_xml(input_file="testdata/invalid-testdata/xml-data/invalid-resource-tag.xml")


def test_validate_xml_invalid_resource_tag_problem() -> None:
    with pytest.raises(
        InputError,
        match=r"XML-tags are not allowed in text properties with encoding=utf8\.\n"
        r"The following resources of your XML file violate this rule:\n"
        r"    - line 13: resource 'the_only_resource', property ':test'\n"
        r"    - line 14: resource 'the_only_resource', property ':test'\n"
        r"    - line 15: resource 'the_only_resource', property ':test'\n"
        r"    - line 16: resource 'the_only_resource', property ':test'",
    ):
        validate_xml(input_file="testdata/invalid-testdata/xml-data/utf8-text-with-xml-tags.xml")


def test_validate_xml_data_duplicate_iri() -> None:
    with pytest.raises(
        InputError,
        match="Line 19: Element 'resource': Duplicate key-sequence .+ "
        "in unique identity-constraint 'IRI_attribute_of_resource_must_be_unique'",
    ):
        validate_xml(input_file="testdata/invalid-testdata/xml-data/duplicate-iri.xml")


def test_validate_xml_duplicate_ark() -> None:
    with pytest.raises(
        InputError,
        match="Line 19: Element 'resource': Duplicate key-sequence .+ "
        "in unique identity-constraint 'ARK_attribute_of_resource_must_be_unique'",
    ):
        validate_xml(input_file="testdata/invalid-testdata/xml-data/duplicate-ark.xml")


def test_validate_xml_empty_label() -> None:
    with pytest.raises(
        InputError,
        match="Line 11: Element 'resource', attribute 'label': .+ "
        "The value '' has a length of '0'; this underruns the allowed minimum length of '1'",
    ):
        validate_xml(input_file="testdata/invalid-testdata/xml-data/empty-label.xml")


if __name__ == "__main__":
    pytest.main([__file__])
