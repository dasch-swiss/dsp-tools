import pytest
from lxml import etree

from dsp_tools.commands.convert_legal import _convert

AUTH_PROP = ":hasAuthorship"
COPY_PROP = ":hasCopyright"
LICENSE_PROP = ":hasLicense"


@pytest.fixture
def one_res_with_bitstream() -> etree._Element:
    return etree.fromstring(f""" 
    <knora>
        <resource label="lbl" restype=":type" id="res_1">
            <bitstream>
                testdata/bitstreams/test.jpg
            </bitstream>
            <text-prop name="{AUTH_PROP}">
                <text encoding="utf8">Maurice et Pierre Chuzeville</text>
            </text-prop>
            <text-prop name="{COPY_PROP}">
                <text encoding="utf8">© Musée du Louvre, Dist. GrandPalaisRmn</text>
            </text-prop>
            <text-prop name="{LICENSE_PROP}">
                <text encoding="utf8">CC BY</text>
            </text-prop>
        </resource>
    </knora>
    """)


def test_convert_legal(one_res_with_bitstream: etree._Element) -> None:
    result = _convert(one_res_with_bitstream, auth_prop=AUTH_PROP, copy_prop=COPY_PROP, license_prop=LICENSE_PROP)
    assert len(result) == 2
    auth_def = result[0]
    resource = result[1]

    assert auth_def.tag == "authorship"
    assert auth_def.attrib["id"] == "authorship_0"
    assert auth_def[0].tag == "author"
    assert auth_def[0].text == "Maurice et Pierre Chuzeville"

    assert resource.tag == "resource"
    assert len(resource) == 1
    assert resource[0].tag == "bitstream"
    assert resource[0].attrib["license"] == "http://rdfh.ch/licenses/cc-by-4.0"
    assert resource[0].attrib["copyright-holder"] == "© Musée du Louvre, Dist. GrandPalaisRmn"
    assert resource[0].attrib["authorship-id"] == "authorship_0"
    assert str(resource[0].text).strip() == "testdata/bitstreams/test.jpg"
