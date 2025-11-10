# mypy: disable-error-code="no-untyped-def"

"""Unit tests for XSD validation of property and resource class names with whitespace."""

from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest
import regex

from dsp_tools.error.exceptions import InputError
from dsp_tools.utils.xml_parsing.parse_clean_validate_xml import parse_and_validate_xml_file


class TestPropertyNameWhitespace:
    """Test that property names with whitespace are rejected by XSD validation."""

    def test_property_name_with_space(self):
        """Property name with space should fail XSD validation."""
        xml_content = """<?xml version='1.0' encoding='utf-8'?>
<knora xmlns="https://dasch.swiss/schema" shortcode="0001" default-ontology="test">
    <resource label="Test Resource" restype="TestResource" id="test_001">
        <text-prop name="has Title">
            <text encoding="utf8">Test</text>
        </text-prop>
    </resource>
</knora>"""
        expected = regex.escape(
            "The XML file cannot be uploaded due to the following validation error(s):\n"
            "    Line 4: Element 'text-prop', attribute 'name': [facet 'pattern'] "
            "The value 'has Title' is not accepted by the pattern '[^\\s]+'."
        )
        with NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write(xml_content)
            f.flush()
            temp_path = Path(f.name)

        try:
            with pytest.raises(InputError, match=expected):
                parse_and_validate_xml_file(input_file=temp_path)
        finally:
            temp_path.unlink()

    def test_property_name_with_tab(self):
        """Property name with tab should fail XSD validation (tab is normalized to space by XML parser)."""
        xml_content = """<?xml version='1.0' encoding='utf-8'?>
<knora xmlns="https://dasch.swiss/schema" shortcode="0001" default-ontology="test">
    <resource label="Test Resource" restype="TestResource" id="test_001">
        <text-prop name="has	Title">
            <text encoding="utf8">Test</text>
        </text-prop>
    </resource>
</knora>"""
        # XML parsers normalize tabs to spaces in attributes
        expected = regex.escape(
            "The XML file cannot be uploaded due to the following validation error(s):\n"
            "    Line 4: Element 'text-prop', attribute 'name': [facet 'pattern'] "
            "The value 'has Title' is not accepted by the pattern '[^\\s]+'."
        )
        with NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write(xml_content)
            f.flush()
            temp_path = Path(f.name)

        try:
            with pytest.raises(InputError, match=expected):
                parse_and_validate_xml_file(input_file=temp_path)
        finally:
            temp_path.unlink()

    def test_property_name_with_newline(self):
        """Property name with newline should fail XSD validation."""
        xml_content = """<?xml version='1.0' encoding='utf-8'?>
<knora xmlns="https://dasch.swiss/schema" shortcode="0001" default-ontology="test">
    <resource label="Test Resource" restype="TestResource" id="test_001">
        <text-prop name="has
Title">
            <text encoding="utf8">Test</text>
        </text-prop>
    </resource>
</knora>"""
        # The pattern should catch the newline in the name
        with NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write(xml_content)
            f.flush()
            temp_path = Path(f.name)

        try:
            with pytest.raises(InputError, match=r"facet 'pattern'.*is not accepted by the pattern"):
                parse_and_validate_xml_file(input_file=temp_path)
        finally:
            temp_path.unlink()

    def test_property_name_with_leading_space(self):
        """Property name with leading space should fail XSD validation."""
        xml_content = """<?xml version='1.0' encoding='utf-8'?>
<knora xmlns="https://dasch.swiss/schema" shortcode="0001" default-ontology="test">
    <resource label="Test Resource" restype="TestResource" id="test_001">
        <text-prop name=" hasTitle">
            <text encoding="utf8">Test</text>
        </text-prop>
    </resource>
</knora>"""
        expected = regex.escape(
            "The XML file cannot be uploaded due to the following validation error(s):\n"
            "    Line 4: Element 'text-prop', attribute 'name': [facet 'pattern'] "
            "The value ' hasTitle' is not accepted by the pattern '[^\\s]+'."
        )
        with NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write(xml_content)
            f.flush()
            temp_path = Path(f.name)

        try:
            with pytest.raises(InputError, match=expected):
                parse_and_validate_xml_file(input_file=temp_path)
        finally:
            temp_path.unlink()

    def test_property_name_with_trailing_space(self):
        """Property name with trailing space should fail XSD validation."""
        xml_content = """<?xml version='1.0' encoding='utf-8'?>
<knora xmlns="https://dasch.swiss/schema" shortcode="0001" default-ontology="test">
    <resource label="Test Resource" restype="TestResource" id="test_001">
        <text-prop name="hasTitle ">
            <text encoding="utf8">Test</text>
        </text-prop>
    </resource>
</knora>"""
        expected = regex.escape(
            "The XML file cannot be uploaded due to the following validation error(s):\n"
            "    Line 4: Element 'text-prop', attribute 'name': [facet 'pattern'] "
            "The value 'hasTitle ' is not accepted by the pattern '[^\\s]+'."
        )
        with NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write(xml_content)
            f.flush()
            temp_path = Path(f.name)

        try:
            with pytest.raises(InputError, match=expected):
                parse_and_validate_xml_file(input_file=temp_path)
        finally:
            temp_path.unlink()


class TestResourceTypeWhitespace:
    """Test that resource type names with whitespace are rejected by XSD validation."""

    def test_restype_with_space(self):
        """Resource type with space should fail XSD validation."""
        xml_content = """<?xml version='1.0' encoding='utf-8'?>
<knora xmlns="https://dasch.swiss/schema" shortcode="0001" default-ontology="test">
    <resource label="Test Resource" restype="Test Resource" id="test_001">
        <text-prop name="hasTitle">
            <text encoding="utf8">Test</text>
        </text-prop>
    </resource>
</knora>"""
        expected = regex.escape(
            "The XML file cannot be uploaded due to the following validation error(s):\n"
            "    Line 3: Element 'resource', attribute 'restype': [facet 'pattern'] "
            "The value 'Test Resource' is not accepted by the pattern '[^\\s]+'."
        )
        with NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write(xml_content)
            f.flush()
            temp_path = Path(f.name)

        try:
            with pytest.raises(InputError, match=expected):
                parse_and_validate_xml_file(input_file=temp_path)
        finally:
            temp_path.unlink()

    def test_restype_with_tab(self):
        """Resource type with tab should fail XSD validation (tab is normalized to space by XML parser)."""
        xml_content = """<?xml version='1.0' encoding='utf-8'?>
<knora xmlns="https://dasch.swiss/schema" shortcode="0001" default-ontology="test">
    <resource label="Test Resource" restype="Test	Resource" id="test_001">
        <text-prop name="hasTitle">
            <text encoding="utf8">Test</text>
        </text-prop>
    </resource>
</knora>"""
        # XML parsers normalize tabs to spaces in attributes
        expected = regex.escape(
            "The XML file cannot be uploaded due to the following validation error(s):\n"
            "    Line 3: Element 'resource', attribute 'restype': [facet 'pattern'] "
            "The value 'Test Resource' is not accepted by the pattern '[^\\s]+'."
        )
        with NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write(xml_content)
            f.flush()
            temp_path = Path(f.name)

        try:
            with pytest.raises(InputError, match=expected):
                parse_and_validate_xml_file(input_file=temp_path)
        finally:
            temp_path.unlink()

    def test_restype_with_leading_trailing_space(self):
        """Resource type with leading and trailing space should fail XSD validation."""
        xml_content = """<?xml version='1.0' encoding='utf-8'?>
<knora xmlns="https://dasch.swiss/schema" shortcode="0001" default-ontology="test">
    <resource label="Test Resource" restype=" TestResource " id="test_001">
        <text-prop name="hasTitle">
            <text encoding="utf8">Test</text>
        </text-prop>
    </resource>
</knora>"""
        expected = regex.escape(
            "The XML file cannot be uploaded due to the following validation error(s):\n"
            "    Line 3: Element 'resource', attribute 'restype': [facet 'pattern'] "
            "The value ' TestResource ' is not accepted by the pattern '[^\\s]+'."
        )
        with NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write(xml_content)
            f.flush()
            temp_path = Path(f.name)

        try:
            with pytest.raises(InputError, match=expected):
                parse_and_validate_xml_file(input_file=temp_path)
        finally:
            temp_path.unlink()


class TestValidNames:
    """Test that valid names without whitespace pass XSD validation."""

    def test_valid_property_name_simple(self):
        """Simple property name without whitespace should pass."""
        xml_content = """<?xml version='1.0' encoding='utf-8'?>
<knora xmlns="https://dasch.swiss/schema" shortcode="0001" default-ontology="test">
    <resource label="Test Resource" restype="TestResource" id="test_001">
        <text-prop name="hasTitle">
            <text encoding="utf8">Test</text>
        </text-prop>
    </resource>
</knora>"""
        with NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write(xml_content)
            f.flush()
            temp_path = Path(f.name)

        try:
            # Should not raise an exception
            assert parse_and_validate_xml_file(input_file=temp_path)
        finally:
            temp_path.unlink()

    def test_valid_property_name_with_colon(self):
        """Property name with colon (namespace prefix) should pass."""
        xml_content = """<?xml version='1.0' encoding='utf-8'?>
<knora xmlns="https://dasch.swiss/schema" shortcode="0001" default-ontology="test">
    <resource label="Test Resource" restype="TestResource" id="test_001">
        <text-prop name=":hasTitle">
            <text encoding="utf8">Test</text>
        </text-prop>
    </resource>
</knora>"""
        with NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write(xml_content)
            f.flush()
            temp_path = Path(f.name)

        try:
            # Should not raise an exception
            assert parse_and_validate_xml_file(input_file=temp_path)
        finally:
            temp_path.unlink()

    def test_valid_property_name_with_underscore_and_numbers(self):
        """Property name with underscores and numbers should pass."""
        xml_content = """<?xml version='1.0' encoding='utf-8'?>
<knora xmlns="https://dasch.swiss/schema" shortcode="0001" default-ontology="test">
    <resource label="Test Resource" restype="TestResource" id="test_001">
        <text-prop name="has_Title_123">
            <text encoding="utf8">Test</text>
        </text-prop>
    </resource>
</knora>"""
        with NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write(xml_content)
            f.flush()
            temp_path = Path(f.name)

        try:
            # Should not raise an exception
            assert parse_and_validate_xml_file(input_file=temp_path)
        finally:
            temp_path.unlink()

    def test_valid_restype_camelcase(self):
        """CamelCase resource type should pass."""
        xml_content = """<?xml version='1.0' encoding='utf-8'?>
<knora xmlns="https://dasch.swiss/schema" shortcode="0001" default-ontology="test">
    <resource label="Test Resource" restype="TestResourceType" id="test_001">
        <text-prop name="hasTitle">
            <text encoding="utf8">Test</text>
        </text-prop>
    </resource>
</knora>"""
        with NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write(xml_content)
            f.flush()
            temp_path = Path(f.name)

        try:
            # Should not raise an exception
            assert parse_and_validate_xml_file(input_file=temp_path)
        finally:
            temp_path.unlink()

    def test_valid_restype_with_colon(self):
        """Resource type with colon (namespace prefix) should pass."""
        xml_content = """<?xml version='1.0' encoding='utf-8'?>
<knora xmlns="https://dasch.swiss/schema" shortcode="0001" default-ontology="test">
    <resource label="Test Resource" restype=":TestResource" id="test_001">
        <text-prop name="hasTitle">
            <text encoding="utf8">Test</text>
        </text-prop>
    </resource>
</knora>"""
        with NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write(xml_content)
            f.flush()
            temp_path = Path(f.name)

        try:
            # Should not raise an exception
            assert parse_and_validate_xml_file(input_file=temp_path)
        finally:
            temp_path.unlink()


if __name__ == "__main__":
    pytest.main([__file__])
