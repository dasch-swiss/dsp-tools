import pytest
from lxml import etree

from dsp_tools.commands.convert_legal import _convert
from dsp_tools.error.exceptions import InputError

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
                © Musée du Louvre
            </text></text-prop>
            <text-prop name="{LICENSE_PROP}"><text encoding="utf8">License is: CC BY</text></text-prop>
        </resource>
        <resource label="lbl" restype=":type" id="res_2">
            <iiif-uri>https://iiif.example.org/image/file_1.JP2/full/1338/0/default.jpg</iiif-uri>
            <text-prop name="{AUTH_PROP}"><text encoding="utf8">  Maurice Chuzeville  </text></text-prop>
            <text-prop name="{COPY_PROP}"><text encoding="utf8">
                © Musée du Louvre
            </text></text-prop>
            <text-prop name="{LICENSE_PROP}"><text encoding="utf8">License is: CC BY</text></text-prop>
        </resource>
    </knora>
    """)


def test_simple_good(one_bitstream_one_iiif: etree._Element) -> None:
    result = _convert(one_bitstream_one_iiif, auth_prop=AUTH_PROP, copy_prop=COPY_PROP, license_prop=LICENSE_PROP)
    assert len(result) == 3
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
    assert resource_1[0].attrib["copyright-holder"] == "© Musée du Louvre"
    assert resource_1[0].attrib["authorship-id"] == "authorship_0"
    assert str(resource_1[0].text).strip() == "test/file.jpg"

    assert resource_2.tag == "resource"
    assert len(resource_2) == 1
    assert resource_2[0].tag == "iiif-uri"
    assert resource_2[0].attrib["license"] == "http://rdfh.ch/licenses/cc-by-4.0"
    assert resource_2[0].attrib["copyright-holder"] == "© Musée du Louvre"
    assert resource_2[0].attrib["authorship-id"] == "authorship_0"
    assert str(resource_2[0].text).strip() == "https://iiif.example.org/image/file_1.JP2/full/1338/0/default.jpg"


def test_incomplete_legal() -> None:
    orig = etree.fromstring(f""" 
    <knora>
        <resource label="lbl" restype=":type" id="res_1">
            <bitstream>test/file.jpg</bitstream>
            <text-prop name="{AUTH_PROP}"><text encoding="utf8">Maurice Chuzeville</text></text-prop>
        </resource>
        <resource label="lbl" restype=":type" id="res_2">
            <bitstream>test/file.jpg</bitstream>
            <text-prop name="{COPY_PROP}"><text encoding="utf8">© Musée du Louvre</text></text-prop>
        </resource>
        <resource label="lbl" restype=":type" id="res_3">
            <bitstream>test/file.jpg</bitstream>
            <text-prop name="{LICENSE_PROP}"><text encoding="utf8">CC BY</text></text-prop>
        </resource>
    </knora>
    """)
    result = _convert(orig, auth_prop=AUTH_PROP, copy_prop=COPY_PROP, license_prop=LICENSE_PROP)
    assert len(result) == 4
    auth_def_0 = result[0]
    resource_1 = result[1]
    resource_2 = result[2]
    resource_3 = result[3]

    assert auth_def_0.tag == "authorship"
    assert auth_def_0.attrib["id"] == "authorship_0"
    assert auth_def_0[0].tag == "author"
    assert auth_def_0[0].text == "Maurice Chuzeville"

    assert resource_1.tag == "resource"
    assert len(resource_1) == 1
    assert resource_1[0].tag == "bitstream"
    assert resource_1[0].attrib["authorship-id"] == "authorship_0"
    assert str(resource_1[0].text).strip() == "test/file.jpg"

    assert resource_2.tag == "resource"
    assert len(resource_2) == 1
    assert resource_2[0].tag == "bitstream"
    assert resource_2[0].attrib["copyright-holder"] == "© Musée du Louvre"
    assert str(resource_2[0].text).strip() == "test/file.jpg"

    assert resource_3.tag == "resource"
    assert len(resource_3) == 1
    assert resource_3[0].tag == "bitstream"
    assert resource_3[0].attrib["license"] == "http://rdfh.ch/licenses/cc-by-4.0"
    assert str(resource_3[0].text).strip() == "test/file.jpg"


def test_missing_legal() -> None:
    orig = etree.fromstring("""
    <knora>
        <resource label="lbl" restype=":type" id="res_1">
            <bitstream>test/file.jpg</bitstream>
        </resource>
    </knora>
    """)
    result = _convert(orig, auth_prop=AUTH_PROP, copy_prop=COPY_PROP, license_prop=LICENSE_PROP)
    assert len(result) == 1
    resource_1 = result[0]

    assert resource_1.tag == "resource"
    assert len(resource_1) == 1
    assert resource_1[0].tag == "bitstream"
    assert not resource_1[0].attrib


def test_different_authors() -> None:
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
    result = _convert(orig, auth_prop=AUTH_PROP)
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

    assert auth_def_1.tag == "authorship"
    assert auth_def_1.attrib["id"] == "authorship_1"
    assert auth_def_1[0].tag == "author"
    assert auth_def_1[0].text == "Pierre Maillard"

    assert resource_1.tag == "resource"
    assert len(resource_1) == 1
    assert resource_1[0].tag == "bitstream"
    assert resource_1[0].attrib["authorship-id"] == "authorship_0"
    assert str(resource_1[0].text).strip() == "test/file.jpg"

    assert resource_2.tag == "resource"
    assert len(resource_2) == 1
    assert resource_2[0].tag == "bitstream"
    assert resource_2[0].attrib["authorship-id"] == "authorship_1"
    assert str(resource_2[0].text).strip() == "test/file.jpg"

    assert resource_3.tag == "resource"
    assert len(resource_3) == 1
    assert resource_3[0].tag == "bitstream"
    assert resource_3[0].attrib["authorship-id"] == "authorship_0"
    assert str(resource_3[0].text).strip() == "test/file.jpg"


def test_no_props(one_bitstream_one_iiif: etree._Element) -> None:
    with pytest.raises(InputError):
        _convert(one_bitstream_one_iiif, auth_prop="", copy_prop="", license_prop="")
    with pytest.raises(InputError):
        _convert(one_bitstream_one_iiif)
