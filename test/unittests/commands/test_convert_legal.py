import pytest
from lxml import etree

from dsp_tools.commands.update_legal.core import _update_xml_tree
from dsp_tools.commands.update_legal.models import LegalMetadataDefaults
from dsp_tools.commands.update_legal.models import LegalProperties

AUTH_PROP = ":hasAuthorship"
COPY_PROP = ":hasCopyright"
LICENSE_PROP = ":hasLicense"


@pytest.fixture
def one_bitstream_one_iiif() -> etree._Element:
    return etree.fromstring(f""" 
    <knora>
        <resource label="lbl" restype=":type" id="res_1">
            <bitstream>test/file.jpg</bitstream>
            <text-prop name="{AUTH_PROP}"><text encoding="utf8">  Maurice Chuzeville  </text></text-prop>
            <text-prop name="{COPY_PROP}"><text encoding="utf8">
                Musée du Louvre
            </text></text-prop>
            <text-prop name="{LICENSE_PROP}"><text encoding="utf8">License is: CC BY</text></text-prop>
        </resource>
        <resource label="lbl" restype=":type" id="res_2">
            <iiif-uri>https://iiif.example.org/image/file_1.JP2/full/1338/0/default.jpg</iiif-uri>
            <text-prop name="{AUTH_PROP}"><text encoding="utf8">  Maurice Chuzeville  </text></text-prop>
            <text-prop name="{COPY_PROP}"><text encoding="utf8">
                Musée du Louvre
            </text></text-prop>
            <text-prop name="{LICENSE_PROP}"><text encoding="utf8">License is: CC BY</text></text-prop>
        </resource>
    </knora>
    """)


def test_simple_good(one_bitstream_one_iiif: etree._Element) -> None:
    properties = LegalProperties(authorship_prop=AUTH_PROP, copyright_prop=COPY_PROP, license_prop=LICENSE_PROP)
    defaults = LegalMetadataDefaults()
    result, counter, problems = _update_xml_tree(one_bitstream_one_iiif, properties=properties, defaults=defaults)
    assert result is not None
    assert counter is not None
    assert len(result) == 3
    assert len(problems) == 0  # No problems expected
    assert counter.resources_updated == 2
    auth_def = result[0]
    resource_1 = result[1]
    resource_2 = result[2]

    assert auth_def.tag == "authorship"
    assert auth_def.attrib["id"] == "authorship_0"
    assert auth_def[0].tag == "author"
    assert auth_def[0].text == "Maurice Chuzeville"

    assert resource_1.tag == "resource"
    assert len(resource_1) == 1
    assert resource_1[0].tag == "bitstream"
    assert resource_1[0].attrib["license"] == "http://rdfh.ch/licenses/cc-by-4.0"
    assert resource_1[0].attrib["copyright-holder"] == "Musée du Louvre"
    assert resource_1[0].attrib["authorship-id"] == "authorship_0"
    assert str(resource_1[0].text).strip() == "test/file.jpg"

    assert resource_2.tag == "resource"
    assert len(resource_2) == 1
    assert resource_2[0].tag == "iiif-uri"
    assert resource_2[0].attrib["license"] == "http://rdfh.ch/licenses/cc-by-4.0"
    assert resource_2[0].attrib["copyright-holder"] == "Musée du Louvre"
    assert resource_2[0].attrib["authorship-id"] == "authorship_0"
    assert str(resource_2[0].text).strip() == "https://iiif.example.org/image/file_1.JP2/full/1338/0/default.jpg"


def test_incomplete_legal() -> None:
    """Test that when some fields are missing, problems are generated but values that exist are still applied."""
    orig = etree.fromstring(f"""
    <knora>
        <resource label="lbl" restype=":type" id="res_1">
            <bitstream>test/file.jpg</bitstream>
            <text-prop name="{AUTH_PROP}"><text encoding="utf8">Maurice Chuzeville</text></text-prop>
        </resource>
        <resource label="lbl" restype=":type" id="res_2">
            <bitstream>test/file.jpg</bitstream>
            <text-prop name="{COPY_PROP}"><text encoding="utf8">Musée du Louvre</text></text-prop>
        </resource>
        <resource label="lbl" restype=":type" id="res_3">
            <bitstream>test/file.jpg</bitstream>
            <text-prop name="{LICENSE_PROP}"><text encoding="utf8">CC BY</text></text-prop>
        </resource>
    </knora>
    """)
    properties = LegalProperties(authorship_prop=AUTH_PROP, copyright_prop=COPY_PROP, license_prop=LICENSE_PROP)
    defaults = LegalMetadataDefaults()
    result, counter, problems = _update_xml_tree(orig, properties=properties, defaults=defaults)

    # Should have 3 problems (one for each resource with missing fields)
    assert len(problems) == 3
    assert result is None
    assert counter is None

    # Check the problems contain FIXME markers
    assert problems[0].res_id == "res_1"
    assert "FIXME:" in problems[0].license
    assert "FIXME:" in problems[0].copyright
    assert problems[0].authorships[0] == "Maurice Chuzeville"

    assert problems[1].res_id == "res_2"
    assert "FIXME:" in problems[1].license
    assert "FIXME:" in problems[1].authorships[0]
    assert problems[1].copyright == "Musée du Louvre"

    assert problems[2].res_id == "res_3"
    assert "FIXME:" in problems[2].authorships[0]
    assert "FIXME:" in problems[2].copyright
    assert problems[2].license == "http://rdfh.ch/licenses/cc-by-4.0"


def test_missing_legal() -> None:
    """Test that when all legal metadata is missing, problems are generated."""
    orig = etree.fromstring("""
    <knora>
        <resource label="lbl" restype=":type" id="res_1">
            <bitstream>test/file.jpg</bitstream>
        </resource>
    </knora>
    """)
    properties = LegalProperties(authorship_prop=AUTH_PROP, copyright_prop=COPY_PROP, license_prop=LICENSE_PROP)
    defaults = LegalMetadataDefaults()
    result, counter, problems = _update_xml_tree(orig, properties=properties, defaults=defaults)

    # Should have 1 problem for the resource with all fields missing
    assert len(problems) == 1
    assert result is None
    assert counter is None
    assert problems[0].res_id == "res_1"
    assert "FIXME:" in problems[0].license
    assert "FIXME:" in problems[0].copyright
    assert "FIXME:" in problems[0].authorships[0]


def test_different_authors() -> None:
    """Test that multiple different authors are handled correctly."""
    orig = etree.fromstring(f"""
    <knora>
        <resource label="lbl" restype=":type" id="res_1">
            <bitstream>test/file.jpg</bitstream>
            <text-prop name="{AUTH_PROP}"><text encoding="utf8">Maurice Chuzeville</text></text-prop>
        </resource>
        <resource label="lbl" restype=":type" id="res_2">
            <bitstream>test/file.jpg</bitstream>
            <text-prop name="{AUTH_PROP}"><text encoding="utf8">Pierre Maillard</text></text-prop>
        </resource>
        <resource label="lbl" restype=":type" id="res_3">
            <bitstream>test/file.jpg</bitstream>
            <text-prop name="{AUTH_PROP}"><text encoding="utf8">Maurice Chuzeville</text></text-prop>
        </resource>
    </knora>
    """)
    properties = LegalProperties(authorship_prop=AUTH_PROP)
    defaults = LegalMetadataDefaults()
    result, counter, problems = _update_xml_tree(orig, properties=properties, defaults=defaults)

    # Should have problems because license and copyright are missing
    assert len(problems) == 3
    assert result is None
    assert counter is None


def test_no_props(one_bitstream_one_iiif: etree._Element) -> None:
    """Test that when no properties are provided, the function returns None and counter is None with problems."""
    properties = LegalProperties(authorship_prop="", copyright_prop="", license_prop="")
    defaults = LegalMetadataDefaults()
    result, counter, problems = _update_xml_tree(one_bitstream_one_iiif, properties=properties, defaults=defaults)
    assert len(problems) == 2
    assert result is None
    assert counter is None

    properties_empty = LegalProperties()
    result2, counter2, problems2 = _update_xml_tree(
        one_bitstream_one_iiif, properties=properties_empty, defaults=defaults
    )
    assert len(problems2) == 2
    assert result2 is None
    assert counter2 is None


def test_empty_author() -> None:
    """Test that empty authorship creates a problem with FIXME marker."""
    empty = etree.fromstring(f"""
    <knora>
        <resource label="lbl" restype=":type" id="res_1">
            <bitstream>test/file.jpg</bitstream>
            <text-prop name="{AUTH_PROP}"><text encoding="utf8"> </text></text-prop>
        </resource>
    </knora>
    """)
    properties = LegalProperties(authorship_prop=AUTH_PROP)
    defaults = LegalMetadataDefaults()
    result, counter, problems = _update_xml_tree(empty, properties=properties, defaults=defaults)

    # Should have 1 problem for empty authorship
    assert len(problems) == 1
    assert result is None
    assert counter is None
    assert problems[0].res_id == "res_1"
    assert "FIXME:" in problems[0].authorships[0]


def test_empty_copy() -> None:
    """Test that empty copyright creates a problem with FIXME marker."""
    empty = etree.fromstring(f"""
    <knora>
        <resource label="lbl" restype=":type" id="res_1">
            <bitstream>test/file.jpg</bitstream>
            <text-prop name="{COPY_PROP}"><text encoding="utf8"> </text></text-prop>
        </resource>
    </knora>
    """)
    properties = LegalProperties(copyright_prop=COPY_PROP)
    defaults = LegalMetadataDefaults()
    result, counter, problems = _update_xml_tree(empty, properties=properties, defaults=defaults)

    # Should have 1 problem for empty copyright
    assert len(problems) == 1
    assert result is None
    assert counter is None
    assert problems[0].res_id == "res_1"
    assert "FIXME:" in problems[0].copyright


def test_empty_license() -> None:
    """Test that empty license creates a problem with FIXME marker."""
    empty = etree.fromstring(f"""
    <knora>
        <resource label="lbl" restype=":type" id="res_1">
            <bitstream>test/file.jpg</bitstream>
            <text-prop name="{LICENSE_PROP}"><text encoding="utf8"> </text></text-prop>
        </resource>
    </knora>
    """)
    properties = LegalProperties(license_prop=LICENSE_PROP)
    defaults = LegalMetadataDefaults()
    result, counter, problems = _update_xml_tree(empty, properties=properties, defaults=defaults)

    # Should have 1 problem for empty license
    assert len(problems) == 1
    assert result is None
    assert counter is None
    assert problems[0].res_id == "res_1"
    assert "FIXME:" in problems[0].license


def test_unknown_license() -> None:
    """Test that unknown license creates a problem with FIXME marker containing the original text."""
    empty = etree.fromstring(f"""
    <knora>
        <resource label="lbl" restype=":type" id="res_1">
            <bitstream>test/file.jpg</bitstream>
            <text-prop name="{LICENSE_PROP}"><text encoding="utf8">CC FO BA 4.0</text></text-prop>
        </resource>
    </knora>
    """)
    properties = LegalProperties(license_prop=LICENSE_PROP)
    defaults = LegalMetadataDefaults()
    result, counter, problems = _update_xml_tree(empty, properties=properties, defaults=defaults)

    # Should have 1 problem for unknown license
    assert len(problems) == 1
    assert result is None
    assert counter is None
    assert problems[0].res_id == "res_1"
    assert "FIXME: Invalid license: CC FO BA 4.0" in problems[0].license
