from pathlib import Path

import pandas as pd
import pytest
from lxml import etree

from dsp_tools.commands.update_legal.core import _update_xml_tree
from dsp_tools.commands.update_legal.csv_operations import is_fixme_value
from dsp_tools.commands.update_legal.csv_operations import read_corrections_csv
from dsp_tools.commands.update_legal.csv_operations import write_problems_to_csv
from dsp_tools.commands.update_legal.models import Authorships
from dsp_tools.commands.update_legal.models import LegalMetadata
from dsp_tools.commands.update_legal.models import LegalMetadataDefaults
from dsp_tools.commands.update_legal.models import LegalProperties
from dsp_tools.commands.update_legal.models import Problem

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
            <text-prop name="{COPY_PROP}"><text encoding="utf8">Musée du Louvre</text></text-prop>
            <text-prop name="{LICENSE_PROP}"><text encoding="utf8">License is: CC BY</text></text-prop>
        </resource>
        <resource label="lbl" restype=":type" id="res_2">
            <iiif-uri>https://iiif.example.org/image/file_1.JP2/full/1338/0/default.jpg</iiif-uri>
            <text-prop name="{AUTH_PROP}"><text encoding="utf8">  Maurice Chuzeville  </text></text-prop>
            <text-prop name="{COPY_PROP}"><text encoding="utf8">Musée du Louvre</text></text-prop>
            <text-prop name="{LICENSE_PROP}"><text encoding="utf8">License is: CC BY</text></text-prop>
        </resource>
    </knora>
    """)


def test_simple_good(one_bitstream_one_iiif: etree._Element) -> None:
    properties = LegalProperties(authorship_prop=AUTH_PROP, copyright_prop=COPY_PROP, license_prop=LICENSE_PROP)
    defaults = LegalMetadataDefaults()
    root_returned, counter, problems = _update_xml_tree(
        one_bitstream_one_iiif, properties=properties, defaults=defaults
    )

    assert len(problems) == 0

    assert counter.resources_updated == 2
    assert counter.licenses_set == 2
    assert counter.copyrights_set == 2
    assert counter.authorships_set == 2

    assert len(root_returned) == 3
    auth_def = root_returned[0]
    resource_1 = root_returned[1]
    resource_2 = root_returned[2]

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


def test_incomplete() -> None:
    """Test that when some fields are missing, problems are generated and resources are left unchanged."""
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
    root_returned, counter, problems = _update_xml_tree(orig, properties=properties, defaults=defaults)

    assert counter.resources_updated == 0
    assert counter.licenses_set == 0
    assert counter.copyrights_set == 0
    assert counter.authorships_set == 0

    assert len(problems) == 3
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

    # Verify that problematic resources still have their text properties (not removed)
    for res in root_returned.iterchildren(tag="resource"):
        text_props = res.xpath("text-prop")
        assert len(text_props) == 1, "Problematic resources should still have their text properties"


def test_everything_is_missing() -> None:
    orig = etree.fromstring("""
    <knora>
        <resource label="lbl" restype=":type" id="res_1">
            <bitstream>test/file.jpg</bitstream>
        </resource>
    </knora>
    """)
    properties = LegalProperties(authorship_prop=AUTH_PROP, copyright_prop=COPY_PROP, license_prop=LICENSE_PROP)
    defaults = LegalMetadataDefaults()
    root_returned, counter, problems = _update_xml_tree(orig, properties=properties, defaults=defaults)

    assert root_returned == orig

    assert counter.resources_updated == 0
    assert counter.licenses_set == 0
    assert counter.copyrights_set == 0
    assert counter.authorships_set == 0

    assert len(problems) == 1
    assert problems[0].res_id == "res_1"
    assert "FIXME:" in problems[0].license
    assert "FIXME:" in problems[0].copyright
    assert "FIXME:" in problems[0].authorships[0]


def test_different_authors() -> None:
    orig = etree.fromstring(f"""
    <knora>
        <resource label="lbl" restype=":type" id="res_1">
            <bitstream>test/file.jpg</bitstream>
            <text-prop name="{AUTH_PROP}"><text encoding="utf8">Chuzeville, Maurice</text></text-prop>
            <text-prop name="{COPY_PROP}"><text encoding="utf8">Musée du Louvre</text></text-prop>
            <text-prop name="{LICENSE_PROP}"><text encoding="utf8">License is: CC BY</text></text-prop>
        </resource>
        <resource label="lbl" restype=":type" id="res_2">
            <bitstream>test/file.jpg</bitstream>
            <text-prop name="{AUTH_PROP}"><text encoding="utf8">Maillard, Pierre</text></text-prop>
            <text-prop name="{COPY_PROP}"><text encoding="utf8">Musée du Louvre</text></text-prop>
            <text-prop name="{LICENSE_PROP}"><text encoding="utf8">License is: CC BY</text></text-prop>
        </resource>
        <resource label="lbl" restype=":type" id="res_3">
            <bitstream>test/file.jpg</bitstream>
            <text-prop name="{AUTH_PROP}"><text encoding="utf8">Chuzeville, Maurice</text></text-prop>
            <text-prop name="{COPY_PROP}"><text encoding="utf8">Musée du Louvre</text></text-prop>
            <text-prop name="{LICENSE_PROP}"><text encoding="utf8">License is: CC BY</text></text-prop>
        </resource>
    </knora>
    """)
    properties = LegalProperties(authorship_prop=AUTH_PROP, copyright_prop=COPY_PROP, license_prop=LICENSE_PROP)
    defaults = LegalMetadataDefaults()
    root_returned, counter, problems = _update_xml_tree(orig, properties=properties, defaults=defaults)

    assert len(problems) == 0
    assert counter.resources_updated == 3
    assert counter.authorships_set == 3
    assert counter.copyrights_set == 3
    assert counter.licenses_set == 3

    assert len(root_returned) == 5  # 3 resources + 2 authorship definitions

    auth_def_0 = root_returned[0]
    assert auth_def_0.tag == "authorship"
    assert auth_def_0.attrib["id"] == "authorship_0"
    assert auth_def_0[0].tag == "author"
    assert auth_def_0[0].text == "Chuzeville, Maurice"

    auth_def_1 = root_returned[1]
    assert auth_def_1.tag == "authorship"
    assert auth_def_1.attrib["id"] == "authorship_1"
    assert auth_def_1[0].tag == "author"
    assert auth_def_1[0].text == "Maillard, Pierre"

    res_1 = root_returned[2]
    assert len(res_1) == 1
    assert res_1[0].attrib["authorship-id"] == "authorship_0"
    assert res_1[0].attrib["license"] == "http://rdfh.ch/licenses/cc-by-4.0"
    assert res_1[0].attrib["copyright-holder"] == "Musée du Louvre"

    res_2 = root_returned[3]
    assert len(res_2) == 1
    assert res_2[0].attrib["authorship-id"] == "authorship_1"
    assert res_2[0].attrib["license"] == "http://rdfh.ch/licenses/cc-by-4.0"
    assert res_2[0].attrib["copyright-holder"] == "Musée du Louvre"

    res_3 = root_returned[4]
    assert len(res_3) == 1
    assert res_3[0].attrib["authorship-id"] == "authorship_0"
    assert res_3[0].attrib["license"] == "http://rdfh.ch/licenses/cc-by-4.0"
    assert res_3[0].attrib["copyright-holder"] == "Musée du Louvre"


def test_no_props(one_bitstream_one_iiif: etree._Element) -> None:
    """Test that when no properties are provided, problems are generated."""
    properties = LegalProperties(authorship_prop="", copyright_prop="", license_prop="")
    defaults = LegalMetadataDefaults()
    _, counter, problems = _update_xml_tree(one_bitstream_one_iiif, properties=properties, defaults=defaults)
    assert len(problems) == 2
    assert counter.resources_updated == 0

    properties_empty = LegalProperties()
    _, counter2, problems2 = _update_xml_tree(one_bitstream_one_iiif, properties=properties_empty, defaults=defaults)
    assert len(problems2) == 2
    assert counter2.resources_updated == 0


def test_empty_author() -> None:
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
    _, counter, problems = _update_xml_tree(empty, properties=properties, defaults=defaults)

    assert counter.resources_updated == 0
    assert len(problems) == 1
    assert "FIXME:" in problems[0].authorships[0]


def test_empty_copy() -> None:
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
    _, counter, problems = _update_xml_tree(empty, properties=properties, defaults=defaults)

    assert counter.resources_updated == 0
    assert len(problems) == 1
    assert "FIXME:" in problems[0].copyright


def test_empty_license() -> None:
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
    _, counter, problems = _update_xml_tree(empty, properties=properties, defaults=defaults)

    assert counter.resources_updated == 0
    assert len(problems) == 1
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
    _, counter, problems = _update_xml_tree(empty, properties=properties, defaults=defaults)

    assert counter.resources_updated == 0
    assert len(problems) == 1
    assert "FIXME: Invalid license: CC FO BA 4.0" in problems[0].license


def test_defaults_all_applied() -> None:
    """Test that default values are applied when XML properties are missing."""
    xml = etree.fromstring("""
    <knora>
        <resource label="lbl" restype=":type" id="res_1">
            <bitstream>test/file.jpg</bitstream>
        </resource>
    </knora>
    """)
    properties = LegalProperties(authorship_prop=AUTH_PROP, copyright_prop=COPY_PROP, license_prop=LICENSE_PROP)
    defaults = LegalMetadataDefaults(
        authorship_default="Default Author",
        copyright_default="Default Copyright Holder",
        license_default="CC BY 4.0",
    )
    root_returned, counter, problems = _update_xml_tree(xml, properties=properties, defaults=defaults)

    assert len(problems) == 0

    assert counter.resources_updated == 1
    assert counter.licenses_set == 1
    assert counter.copyrights_set == 1
    assert counter.authorships_set == 1

    auth_def = root_returned[0]
    assert auth_def[0].text == "Default Author"

    resource = root_returned[1]
    bitstream = resource[0]
    assert bitstream.attrib["license"] == "http://rdfh.ch/licenses/cc-by-4.0"
    assert bitstream.attrib["copyright-holder"] == "Default Copyright Holder"
    assert bitstream.attrib["authorship-id"] == "authorship_0"


def test_defaults_partial() -> None:
    """Test that defaults are only applied for missing fields, not overriding XML values."""
    xml = etree.fromstring(f"""
    <knora>
        <resource label="lbl" restype=":type" id="res_1">
            <bitstream>test/file.jpg</bitstream>
            <text-prop name="{AUTH_PROP}"><text encoding="utf8">XML Author</text></text-prop>
        </resource>
    </knora>
    """)
    properties = LegalProperties(authorship_prop=AUTH_PROP, copyright_prop=COPY_PROP, license_prop=LICENSE_PROP)
    defaults = LegalMetadataDefaults(
        authorship_default="Default Author",
        copyright_default="Default Copyright",
        license_default="CC BY 4.0",
    )
    root_returned, counter, problems = _update_xml_tree(xml, properties=properties, defaults=defaults)

    assert len(problems) == 0

    assert counter.resources_updated == 1
    assert counter.licenses_set == 1
    assert counter.copyrights_set == 1
    assert counter.authorships_set == 1

    auth_def = root_returned[0]
    assert auth_def[0].text == "XML Author"

    resource = root_returned[1]
    bitstream = resource[0]
    assert bitstream.attrib["license"] == "http://rdfh.ch/licenses/cc-by-4.0"
    assert bitstream.attrib["copyright-holder"] == "Default Copyright"
    assert bitstream.attrib["authorship-id"] == "authorship_0"


def test_multiple_licenses() -> None:
    """Test that multiple license values generate a FIXME problem with license text."""
    xml = etree.fromstring(f"""
    <knora>
        <resource label="lbl" restype=":type" id="res_1">
            <bitstream>test/file.jpg</bitstream>
            <text-prop name="{LICENSE_PROP}">
                <text encoding="utf8">CC BY 4.0</text>
                <text encoding="utf8">CC BY-SA 4.0</text>
            </text-prop>
        </resource>
    </knora>
    """)
    properties = LegalProperties(license_prop=LICENSE_PROP)
    defaults = LegalMetadataDefaults()
    _, counter, problems = _update_xml_tree(xml, properties=properties, defaults=defaults)

    assert len(problems) == 1
    assert counter.resources_updated == 0
    assert problems[0].license == "FIXME: Multiple licenses found. Choose one: CC BY 4.0, CC BY-SA 4.0"


def test_multiple_copyrights() -> None:
    """Test that multiple copyright values generate a FIXME problem with copyright text."""
    xml = etree.fromstring(f"""
    <knora>
        <resource label="lbl" restype=":type" id="res_1">
            <bitstream>test/file.jpg</bitstream>
            <text-prop name="{COPY_PROP}">
                <text encoding="utf8">Copyright Holder 1</text>
                <text encoding="utf8">Copyright Holder 2</text>
            </text-prop>
        </resource>
    </knora>
    """)
    properties = LegalProperties(copyright_prop=COPY_PROP)
    defaults = LegalMetadataDefaults()
    _, counter, problems = _update_xml_tree(xml, properties=properties, defaults=defaults)

    assert len(problems) == 1
    assert counter.resources_updated == 0
    expected_copyright = "FIXME: Multiple copyrights found. Choose one: Copyright Holder 1, Copyright Holder 2"
    assert problems[0].copyright == expected_copyright


def test_multiple_authorships_per_resource() -> None:
    """Test that multiple authorship text elements are collected and combined."""
    xml = etree.fromstring(f"""
    <knora>
        <resource label="lbl" restype=":type" id="res_1">
            <bitstream>test/file.jpg</bitstream>
            <text-prop name="{AUTH_PROP}">
                <text encoding="utf8">Surname 1, Given Name 1</text>
                <text encoding="utf8">Surname 2, Given Name 2</text>
                <text encoding="utf8">Surname 3, Given Name 3</text>
            </text-prop>
        </resource>
    </knora>
    """)
    properties = LegalProperties(authorship_prop=AUTH_PROP, copyright_prop=COPY_PROP, license_prop=LICENSE_PROP)
    defaults = LegalMetadataDefaults(copyright_default="Default Copy", license_default="CC BY 4.0")
    root_returned, counter, problems = _update_xml_tree(xml, properties=properties, defaults=defaults)

    assert len(problems) == 0

    assert counter.resources_updated == 1
    assert counter.licenses_set == 1
    assert counter.copyrights_set == 1
    assert counter.authorships_set == 1

    auth_def = root_returned[0]
    assert auth_def.tag == "authorship"
    assert auth_def.attrib["id"] == "authorship_0"
    assert {x.text for x in auth_def} == {
        "Surname 1, Given Name 1",
        "Surname 2, Given Name 2",
        "Surname 3, Given Name 3",
    }

    resource = root_returned[1]
    bitstream = resource[0]
    assert bitstream.attrib["authorship-id"] == "authorship_0"


def test_resources_without_media_skipped() -> None:
    xml = etree.fromstring(f"""
    <knora>
        <resource label="lbl" restype=":type" id="res_1">
            <text-prop name="{AUTH_PROP}"><text encoding="utf8">Keep this authorship property</text></text-prop>
            <text-prop name="{COPY_PROP}"><text encoding="utf8">Keep this copyright property</text></text-prop>
            <text-prop name="{LICENSE_PROP}"><text encoding="utf8">Keep this license property</text></text-prop>
        </resource>
        <resource label="lbl" restype=":type" id="res_2">
            <bitstream>file1.jpg</bitstream>
            <text-prop name="{AUTH_PROP}"><text encoding="utf8">Author C</text></text-prop>
            <text-prop name="{COPY_PROP}"><text encoding="utf8">Copyright C</text></text-prop>
            <text-prop name="{LICENSE_PROP}"><text encoding="utf8">CC BY-NC</text></text-prop>
        </resource>
        <resource label="lbl" restype=":type" id="res_3">
            <text-prop name="{AUTH_PROP}"><text encoding="utf8">Keep this authorship property</text></text-prop>
            <text-prop name="{COPY_PROP}"><text encoding="utf8">Keep this copyright property</text></text-prop>
            <text-prop name="{LICENSE_PROP}"><text encoding="utf8">Keep this license property</text></text-prop>
        </resource>
    </knora>
    """)
    properties = LegalProperties(authorship_prop=AUTH_PROP, copyright_prop=COPY_PROP, license_prop=LICENSE_PROP)
    defaults = LegalMetadataDefaults()
    root_returned, counter, problems = _update_xml_tree(xml, properties=properties, defaults=defaults)

    assert len(problems) == 0

    assert counter.resources_updated == 1
    assert counter.licenses_set == 1
    assert counter.copyrights_set == 1
    assert counter.authorships_set == 1

    res_1 = root_returned[1]
    assert [x.text for x in res_1.xpath("text-prop/text")] == [
        "Keep this authorship property",
        "Keep this copyright property",
        "Keep this license property",
    ]

    res_2 = root_returned[2]
    assert len(res_2) == 1
    assert res_2[0].tag == "bitstream"

    res_3 = root_returned[3]
    assert [x.text for x in res_3.xpath("text-prop/text")] == [
        "Keep this authorship property",
        "Keep this copyright property",
        "Keep this license property",
    ]


def test_is_fixme_value() -> None:
    assert is_fixme_value("FIXME: Multiple copyrights found. Choose one: DaSCH, Louvre")
    assert is_fixme_value("FIXME: Copyright missing")
    assert is_fixme_value("FIXME: License missing")
    assert is_fixme_value("FIXME: Invalid license: Courtesy of DaSCH")
    assert is_fixme_value("FIXME: Multiple licenses found. Choose one: CC-BY, CC-BY-SA")
    assert not is_fixme_value(None)
    assert not is_fixme_value("CC BY 4.0")
    assert not is_fixme_value("John Doe")
    assert not is_fixme_value("unknown")
    assert not is_fixme_value("")
    assert not is_fixme_value("  ")


def test_write_problems_to_csv(tmp_path: Path) -> None:
    xml_file = tmp_path / "test.xml"
    xml_file.write_text("<knora></knora>")

    problems = [
        Problem(
            file_or_iiif_uri="file1.jpg",
            res_id="res_1",
            license="FIXME: Missing license",
            copyright="Copyright Holder",
            authorships=["Author One"],
        ),
        Problem(
            file_or_iiif_uri="file2.jpg",
            res_id="res_2",
            license="http://rdfh.ch/licenses/cc-by-4.0",
            copyright="FIXME: Missing copyright",
            authorships=["Author Two", "Author Three"],
        ),
    ]

    write_problems_to_csv(xml_file, problems)

    csv_file = tmp_path / "test_legal_errors.csv"
    assert csv_file.exists()

    df = pd.read_csv(csv_file)
    assert len(df) == 2
    assert "resource_id" in df.columns
    assert "file" in df.columns
    assert "license" in df.columns
    assert "copyright" in df.columns
    assert "authorship_1" in df.columns
    assert "authorship_2" in df.columns

    assert df.iloc[0]["resource_id"] == "res_1"
    assert df.iloc[0]["license"] == "FIXME: Missing license"
    assert df.iloc[0]["authorship_1"] == "Author One"

    assert df.iloc[1]["resource_id"] == "res_2"
    assert df.iloc[1]["authorship_1"] == "Author Two"
    assert df.iloc[1]["authorship_2"] == "Author Three"


def test_write_problems_to_csv_file_exists(tmp_path: Path) -> None:
    xml_file = tmp_path / "test.xml"
    xml_file.write_text("<knora></knora>")

    csv_file = tmp_path / "test_legal_errors.csv"
    csv_file.write_text("existing content")

    problems = [
        Problem(
            file_or_iiif_uri="file1.jpg",
            res_id="res_1",
            license="FIXME: Missing",
            copyright="Copyright",
            authorships=["Author"],
        )
    ]

    write_problems_to_csv(xml_file, problems)

    csv_file_1 = tmp_path / "test_legal_errors_1.csv"
    assert csv_file_1.exists()
    assert csv_file.exists()

    df = pd.read_csv(csv_file_1)
    assert len(df) == 1
    assert df.iloc[0]["resource_id"] == "res_1"


def test_read_corrections_csv(tmp_path: Path) -> None:
    csv_file = tmp_path / "corrections.csv"
    csv_content = """resource_id,file,license,copyright,authorship_1,authorship_2
res_1,file1.jpg,http://rdfh.ch/licenses/cc-by-4.0,Copyright Holder,Author One,
res_2,file2.jpg,http://rdfh.ch/licenses/cc0-1.0,Another Copyright,Author Two,Author Three
"""
    csv_file.write_text(csv_content)

    corrections = read_corrections_csv(csv_file)

    assert len(corrections) == 2
    assert "res_1" in corrections
    assert "res_2" in corrections

    res1_metadata = corrections["res_1"]
    assert res1_metadata.license == "http://rdfh.ch/licenses/cc-by-4.0"
    assert res1_metadata.copyright == "Copyright Holder"
    assert res1_metadata.authorships.elems == {"Author One"}

    res2_metadata = corrections["res_2"]
    assert res2_metadata.license == "http://rdfh.ch/licenses/cc0-1.0"
    assert res2_metadata.copyright == "Another Copyright"
    assert res2_metadata.authorships.elems == {"Author Two", "Author Three"}


def test_read_corrections_csv_with_fixme_values(tmp_path: Path) -> None:
    csv_file = tmp_path / "corrections.csv"
    csv_content = """resource_id,file,license,copyright,authorship_1
res_1,file1.jpg,FIXME: Choose one,Real Copyright,Real Author
"""
    csv_file.write_text(csv_content)

    corrections = read_corrections_csv(csv_file)

    res1_metadata = corrections["res_1"]
    assert res1_metadata.license is None
    assert res1_metadata.copyright == "Real Copyright"
    assert res1_metadata.authorships.elems == {"Real Author"}


def test_csv_corrections_override_xml() -> None:
    xml = etree.fromstring(f"""
    <knora>
        <resource label="lbl" restype=":type" id="res_1">
            <bitstream>file1.jpg</bitstream>
            <text-prop name="{AUTH_PROP}"><text encoding="utf8">XML Author</text></text-prop>
            <text-prop name="{COPY_PROP}"><text encoding="utf8">XML Copyright</text></text-prop>
            <text-prop name="{LICENSE_PROP}"><text encoding="utf8">CC BY</text></text-prop>
        </resource>
    </knora>
    """)

    csv_metadata = {
        "res_1": LegalMetadata(
            license="http://rdfh.ch/licenses/cc0-1.0",
            copyright="CSV Copyright",
            authorships=Authorships.from_iterable({"CSV Author"}),
        )
    }

    properties = LegalProperties(authorship_prop=AUTH_PROP, copyright_prop=COPY_PROP, license_prop=LICENSE_PROP)
    defaults = LegalMetadataDefaults(
        authorship_default="Default Author",
        copyright_default="Default Copyright",
        license_default="CC BY-SA 4.0",
    )

    root_returned, counter, problems = _update_xml_tree(
        xml, properties=properties, defaults=defaults, csv_corrections=csv_metadata
    )

    assert len(problems) == 0

    assert counter.resources_updated == 1
    assert counter.licenses_set == 1
    assert counter.copyrights_set == 1
    assert counter.authorships_set == 1

    auth_def = root_returned[0]
    assert auth_def[0].text == "CSV Author"

    resource = root_returned[1]
    bitstream = resource[0]
    assert bitstream.attrib["license"] == "http://rdfh.ch/licenses/cc0-1.0"
    assert bitstream.attrib["copyright-holder"] == "CSV Copyright"


def test_partial_update_mixed_resources() -> None:
    xml = etree.fromstring(f"""
    <knora>
        <resource label="lbl" restype=":type" id="res_good">
            <bitstream>file_good.jpg</bitstream>
            <text-prop name="{AUTH_PROP}"><text encoding="utf8">Surname 1, Given Name 1</text></text-prop>
            <text-prop name="{COPY_PROP}"><text encoding="utf8">Good Copyright</text></text-prop>
            <text-prop name="{LICENSE_PROP}"><text encoding="utf8">CC BY</text></text-prop>
        </resource>
        <resource label="lbl" restype=":type" id="res_bad">
            <bitstream>file_bad.jpg</bitstream>
            <text-prop name="{AUTH_PROP}"><text encoding="utf8">Surname 2, Given Name 2</text></text-prop>
        </resource>
        <resource label="lbl" restype=":type" id="res_good2">
            <bitstream>file_good2.jpg</bitstream>
            <text-prop name="{AUTH_PROP}"><text encoding="utf8">Surname 3, Given Name 3</text></text-prop>
            <text-prop name="{COPY_PROP}"><text encoding="utf8">Good Copyright 2</text></text-prop>
            <text-prop name="{LICENSE_PROP}"><text encoding="utf8">CC BY-SA</text></text-prop>
        </resource>
    </knora>
    """)

    properties = LegalProperties(authorship_prop=AUTH_PROP, copyright_prop=COPY_PROP, license_prop=LICENSE_PROP)
    defaults = LegalMetadataDefaults()
    root_returned, counter, problems = _update_xml_tree(xml, properties=properties, defaults=defaults)

    assert len(problems) == 1
    assert problems[0].res_id == "res_bad"

    assert counter.resources_updated == 2
    assert counter.licenses_set == 2
    assert counter.copyrights_set == 2
    assert counter.authorships_set == 2

    res_good = root_returned.xpath('//resource[@id="res_good"]')[0]
    assert len(res_good.xpath("text-prop")) == 0
    assert res_good[0].attrib["license"] == "http://rdfh.ch/licenses/cc-by-4.0"
    assert res_good[0].attrib["copyright-holder"] == "Good Copyright"

    res_good2 = root_returned.xpath('//resource[@id="res_good2"]')[0]
    assert len(res_good2.xpath("text-prop")) == 0
    assert res_good2[0].attrib["license"] == "http://rdfh.ch/licenses/cc-by-sa-4.0"

    res_bad = root_returned.xpath('//resource[@id="res_bad"]')[0]
    assert len(res_bad.xpath("text-prop")) == 1
    assert "license" not in res_bad[0].attrib
    assert "copyright-holder" not in res_bad[0].attrib

    auth_defs = root_returned.xpath("//authorship")
    assert len(auth_defs) == 2


def test_treat_invalid_licenses_as_unknown_flag() -> None:
    """Test that the flag converts invalid licenses to 'unknown'."""
    xml = etree.fromstring(f"""
    <knora>
        <resource label="lbl" restype=":type" id="res_1">
            <bitstream>file1.jpg</bitstream>
            <text-prop name="{LICENSE_PROP}"><text encoding="utf8">CC FO BA 4.0</text></text-prop>
            <text-prop name="{AUTH_PROP}"><text encoding="utf8">Author</text></text-prop>
            <text-prop name="{COPY_PROP}"><text encoding="utf8">Copyright</text></text-prop>
        </resource>
    </knora>
    """)
    properties = LegalProperties(authorship_prop=AUTH_PROP, copyright_prop=COPY_PROP, license_prop=LICENSE_PROP)
    defaults = LegalMetadataDefaults()
    root_returned, counter, problems = _update_xml_tree(
        xml, properties=properties, defaults=defaults, treat_invalid_licenses_as_unknown=True
    )

    assert len(problems) == 0
    assert counter.resources_updated == 1
    assert counter.invalid_licenses_replaced == 1

    resource = root_returned[1]
    bitstream = resource[0]
    assert bitstream.attrib["license"] == "http://rdfh.ch/licenses/unknown"
    assert bitstream.attrib["copyright-holder"] == "Copyright"


def test_csv_overrides_treat_invalid_flag() -> None:
    """Test that CSV corrections take priority over the flag."""
    xml = etree.fromstring(f"""
    <knora>
        <resource label="lbl" restype=":type" id="res_1">
            <bitstream>file1.jpg</bitstream>
            <text-prop name="{LICENSE_PROP}"><text encoding="utf8">Invalid License</text></text-prop>
            <text-prop name="{AUTH_PROP}"><text encoding="utf8">Author</text></text-prop>
            <text-prop name="{COPY_PROP}"><text encoding="utf8">Copyright</text></text-prop>
        </resource>
    </knora>
    """)

    csv_metadata = {
        "res_1": LegalMetadata(
            license="http://rdfh.ch/licenses/cc-by-4.0",
            copyright="CSV Copyright",
            authorships=Authorships.from_iterable({"CSV Author"}),
        )
    }

    properties = LegalProperties(authorship_prop=AUTH_PROP, copyright_prop=COPY_PROP, license_prop=LICENSE_PROP)
    defaults = LegalMetadataDefaults()
    root_returned, counter, problems = _update_xml_tree(
        xml,
        properties=properties,
        defaults=defaults,
        csv_corrections=csv_metadata,
        treat_invalid_licenses_as_unknown=True,
    )

    assert len(problems) == 0
    assert counter.resources_updated == 1
    assert counter.invalid_licenses_replaced == 0

    resource = root_returned[1]
    bitstream = resource[0]
    assert bitstream.attrib["license"] == "http://rdfh.ch/licenses/cc-by-4.0"
    assert bitstream.attrib["copyright-holder"] == "CSV Copyright"


def test_multiple_licenses_still_fixme_with_flag() -> None:
    """Test that multiple licenses still create FIXME even with the flag enabled."""
    xml = etree.fromstring(f"""
    <knora>
        <resource label="lbl" restype=":type" id="res_1">
            <bitstream>file1.jpg</bitstream>
            <text-prop name="{LICENSE_PROP}">
                <text encoding="utf8">CC BY 4.0</text>
                <text encoding="utf8">CC BY-SA 4.0</text>
            </text-prop>
            <text-prop name="{AUTH_PROP}"><text encoding="utf8">Author</text></text-prop>
            <text-prop name="{COPY_PROP}"><text encoding="utf8">Copyright</text></text-prop>
        </resource>
    </knora>
    """)
    properties = LegalProperties(authorship_prop=AUTH_PROP, copyright_prop=COPY_PROP, license_prop=LICENSE_PROP)
    defaults = LegalMetadataDefaults()
    _, counter, problems = _update_xml_tree(
        xml, properties=properties, defaults=defaults, treat_invalid_licenses_as_unknown=True
    )

    assert len(problems) == 1
    assert counter.resources_updated == 0
    assert counter.invalid_licenses_replaced == 0
    assert problems[0].license == "FIXME: Multiple licenses found. Choose one: CC BY 4.0, CC BY-SA 4.0"


def test_treat_invalid_mixed_resources() -> None:
    """Test mixed valid/invalid/multiple licenses with the flag."""
    xml = etree.fromstring(f"""
    <knora>
        <resource label="lbl" restype=":type" id="res_valid">
            <bitstream>file_valid.jpg</bitstream>
            <text-prop name="{LICENSE_PROP}"><text encoding="utf8">CC BY</text></text-prop>
            <text-prop name="{AUTH_PROP}"><text encoding="utf8">Author Valid</text></text-prop>
            <text-prop name="{COPY_PROP}"><text encoding="utf8">Copyright Valid</text></text-prop>
        </resource>
        <resource label="lbl" restype=":type" id="res_invalid">
            <bitstream>file_invalid.jpg</bitstream>
            <text-prop name="{LICENSE_PROP}"><text encoding="utf8">Invalid License</text></text-prop>
            <text-prop name="{AUTH_PROP}"><text encoding="utf8">Author Invalid</text></text-prop>
            <text-prop name="{COPY_PROP}"><text encoding="utf8">Copyright Invalid</text></text-prop>
        </resource>
        <resource label="lbl" restype=":type" id="res_multiple">
            <bitstream>file_multiple.jpg</bitstream>
            <text-prop name="{LICENSE_PROP}">
                <text encoding="utf8">CC BY</text>
                <text encoding="utf8">CC BY-SA</text>
            </text-prop>
            <text-prop name="{AUTH_PROP}"><text encoding="utf8">Author Multiple</text></text-prop>
            <text-prop name="{COPY_PROP}"><text encoding="utf8">Copyright Multiple</text></text-prop>
        </resource>
    </knora>
    """)
    properties = LegalProperties(authorship_prop=AUTH_PROP, copyright_prop=COPY_PROP, license_prop=LICENSE_PROP)
    defaults = LegalMetadataDefaults()
    root_returned, counter, problems = _update_xml_tree(
        xml, properties=properties, defaults=defaults, treat_invalid_licenses_as_unknown=True
    )

    assert len(problems) == 1
    assert problems[0].res_id == "res_multiple"
    assert counter.resources_updated == 2
    assert counter.invalid_licenses_replaced == 1

    res_valid = root_returned.xpath('//resource[@id="res_valid"]')[0]
    assert res_valid[0].attrib["license"] == "http://rdfh.ch/licenses/cc-by-4.0"

    res_invalid = root_returned.xpath('//resource[@id="res_invalid"]')[0]
    assert res_invalid[0].attrib["license"] == "http://rdfh.ch/licenses/unknown"

    res_multiple = root_returned.xpath('//resource[@id="res_multiple"]')[0]
    assert "license" not in res_multiple[0].attrib
