import pytest
from lxml import etree

@pytest.fixture
def old_xml() -> etree._Element:
    return etree.fromstring(""" 
    <knora>
        <resource label="lbl" restype=":type" id="res_1">
            <bitstream>
                testdata/bitstreams/test.jpg
            </bitstream>
            <text-prop name=":hasAuthorship">
                <text encoding="utf8">Maurice et Pierre Chuzeville</text>
            </text-prop>
            <text-prop name=":hasCopyright">
                <text encoding="utf8">© Musée du Louvre, Dist. GrandPalaisRmn</text>
            </text-prop>
            <text-prop name=":hasLicense">
                <text encoding="utf8">CC BY</text>
            </text-prop>
        </resource>
    </knora>
    """)


@pytest.fixture
def expected_xml() -> etree._Element:
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

def test_convert_legal() -> None:
    pass
