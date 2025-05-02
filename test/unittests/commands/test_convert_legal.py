import pytest
from lxml import etree

from dsp_tools.commands.convert_legal import _convert

AUTH_PROP = ":hasAuthorship"
COPY_PROP = ":hasCopyright"
LICENSE_PROP = ":hasLicense"


@pytest.fixture
def _1_res_with_bitstream() -> etree._Element:
    return etree.fromstring(f""" 
    <knora>
        <resource label="lbl" restype=":type" id="res_1">
            <bitstream>test/file.jpg</bitstream>
            <text-prop name="{AUTH_PROP}"><text encoding="utf8">Maurice Chuzeville</text></text-prop>
            <text-prop name="{COPY_PROP}"><text encoding="utf8">© Musée du Louvre</text></text-prop>
            <text-prop name="{LICENSE_PROP}"><text encoding="utf8">CC BY</text></text-prop>
        </resource>
    </knora>
    """)


@pytest.fixture
def _3_res_with_iiif_and_2_different_authors() -> etree._Element:
    return etree.fromstring(f""" 
    <knora>
        <resource label="lbl" restype=":type" id="res_1">
            <iiif-uri>https://iiif.example.org/image/file_1.JP2/full/1338/0/default.jpg</iiif-uri>
            <text-prop name="{AUTH_PROP}"><text encoding="utf8">Maurice Chuzeville</text></text-prop>
            <text-prop name="{COPY_PROP}"><text encoding="utf8">© Musée du Louvre</text></text-prop>
            <text-prop name="{LICENSE_PROP}"><text encoding="utf8">CC BY</text></text-prop>
        </resource>
        <resource label="lbl" restype=":type" id="res_2">
            <iiif-uri>https://iiif.example.org/image/file_2.JP2/full/1338/0/default.jpg</iiif-uri>
            <text-prop name="{AUTH_PROP}"><text encoding="utf8">Pierre Chuzeville</text></text-prop>
            <text-prop name="{COPY_PROP}"><text encoding="utf8">© Musée du Louvre</text></text-prop>
            <text-prop name="{LICENSE_PROP}"><text encoding="utf8">CC BY</text></text-prop>
        </resource>
        <resource label="lbl" restype=":type" id="res_3">
            <bitstream>test/file.jpg</bitstream>
            <text-prop name="{AUTH_PROP}"><text encoding="utf8">Maurice Chuzeville</text></text-prop>
            <text-prop name="{COPY_PROP}"><text encoding="utf8">© Musée du Louvre</text></text-prop>
            <text-prop name="{LICENSE_PROP}"><text encoding="utf8">CC BY</text></text-prop>
        </resource>
    </knora>
    """)


def test_simple_good(_1_res_with_bitstream: etree._Element) -> None:
    result = _convert(_1_res_with_bitstream, auth_prop=AUTH_PROP, copy_prop=COPY_PROP, license_prop=LICENSE_PROP)
    assert len(result) == 2
    auth_def = result[0]
    resource = result[1]

    assert auth_def.tag == "authorship"
    assert auth_def.attrib["id"] == "authorship_0"
    assert auth_def[0].tag == "author"
    assert auth_def[0].text == "Maurice Chuzeville"

    assert resource.tag == "resource"
    assert len(resource) == 1
    assert resource[0].tag == "bitstream"
    assert resource[0].attrib["license"] == "http://rdfh.ch/licenses/cc-by-4.0"
    assert resource[0].attrib["copyright-holder"] == "© Musée du Louvre"
    assert resource[0].attrib["authorship-id"] == "authorship_0"
    assert str(resource[0].text).strip() == "test/file.jpg"


def test_complex_good(_3_res_with_iiif_and_2_different_authors: etree._Element) -> None:
    result = _convert(
        _3_res_with_iiif_and_2_different_authors, auth_prop=AUTH_PROP, copy_prop=COPY_PROP, license_prop=LICENSE_PROP
    )
    assert len(result) == 5
    auth_def_0 = result[0]
    auth_def_1 = result[1]
    resource_1 = result[2]
    resource_2 = result[3]
    resource_3 = result[4]

    assert auth_def_0.tag == "authorship"
    assert auth_def_0.attrib["id"] == "authorship_0"
    assert auth_def_0[0].tag == "author"
    assert auth_def_0[0].text == "Maurice Chuzeville"
