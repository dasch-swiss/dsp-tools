import pytest
from lxml import etree

from dsp_tools.commands.convert_legal import _convert

AUTH_PROP = ":hasAuthorship"
COPY_PROP = ":hasCopyright"
LICENSE_PROP = ":hasLicense"


@pytest.fixture
def original() -> etree._Element:
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


@pytest.fixture
def expected() -> etree._Element:
    return etree.fromstring(""" 
    <knora>
        <authorship id="authorship_1">
            <author>Maurice et Pierre Chuzeville</author>
        </authorship>

        <resource label="lbl" restype=":type" id="res_1">
            <bitstream 
                license="http://rdfh.ch/licenses/cc-by-4.0" 
                copyright-holder="© Musée du Louvre, Dist. GrandPalaisRmn" 
                authorship-id="authorship_1">
                    testdata/bitstreams/test.jpg
            </bitstream>
        </resource>
    </knora>
    """)


def test_convert_legal(original: etree._Element, expected: etree._Element) -> None:
    result = _convert(original, auth_prop=AUTH_PROP, copy_prop=COPY_PROP, license_prop=LICENSE_PROP)
    assert result == expected
