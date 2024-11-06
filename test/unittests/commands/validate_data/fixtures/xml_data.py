import pytest
from lxml import etree


@pytest.fixture
def resource_empty() -> etree._Element:
    return etree.fromstring("""
    <resource label="lbl" restype="http://0.0.0.0:3333/ontology/9999/onto/v2#ClassWithEverything" id="one">
    </resource>
    """)


@pytest.fixture
def root_resource_with_props() -> etree._Element:
    return etree.fromstring("""
    <knora>
        <resource label="lbl" restype="http://0.0.0.0:3333/ontology/9999/onto/v2#ClassWithEverything" id="one">
            <boolean-prop name="http://0.0.0.0:3333/ontology/9999/onto/v2#testBoolean">
                <boolean>true</boolean>
            </boolean-prop>
            <color-prop name="http://0.0.0.0:3333/ontology/9999/onto/v2#testColor">
                <color>#00ff00</color>
                <color>#00ff11</color>
            </color-prop>
        </resource>
    </knora>
    """)


@pytest.fixture
def root_resource_region() -> etree._Element:
    return etree.fromstring("""
    <knora>
        <region restype="http://api.knora.org/ontology/knora-api/v2#Region" label="Region" id="region_1">
            <color-prop name="http://api.knora.org/ontology/knora-api/v2#hasColor">
                <color>#5d1f1e</color>
            </color-prop>
            <resptr-prop name="http://api.knora.org/ontology/knora-api/v2#isRegionOf">
                <resptr>image_thing_0</resptr>
            </resptr-prop>
            <geometry-prop name="http://api.knora.org/ontology/knora-api/v2#hasGeometry">
                <geometry>
                    {
                    "status": "active",
                    "type": "polygon",
                    "lineWidth": 5,
                    "points": [{"x": 0.4, "y": 0.6},
                    {"x": 0.5, "y": 0.9},
                    {"x": 0.8, "y": 0.9},
                    {"x": 0.7, "y": 0.6}]
                    }
                </geometry>
            </geometry-prop>
            <text-prop name="http://api.knora.org/ontology/knora-api/v2#hasComment">
                <text encoding="xml">
                    This is a polygon-formed region of interest of an image. It is also displayed as Annotation.
                </text>
            </text-prop>
        </region>
    </knora>
    """)


@pytest.fixture
def boolean_value_corr() -> etree._Element:
    return etree.fromstring("""
        <boolean-prop name="http://0.0.0.0:3333/ontology/9999/onto/v2#testBoolean">
            <boolean>true</boolean>
        </boolean-prop>
    """)


@pytest.fixture
def color_value_corr() -> etree._Element:
    return etree.fromstring("""
        <color-prop name="http://0.0.0.0:3333/ontology/9999/onto/v2#testColor">
            <color>#00ff00</color>
        </color-prop>
        """)


@pytest.fixture
def color_value_corr_several() -> etree._Element:
    return etree.fromstring("""
        <color-prop name="http://0.0.0.0:3333/ontology/9999/onto/v2#testColor">
            <color>#00ff00</color>
            <color>#00ff11</color>
        </color-prop>
        """)


@pytest.fixture
def date_value_corr() -> etree._Element:
    return etree.fromstring("""
        <date-prop name="http://0.0.0.0:3333/ontology/9999/onto/v2#testSubDate1">
            <date>JULIAN:BCE:0700:BCE:0600</date>
        </date-prop>
        """)


@pytest.fixture
def date_value_corr_several() -> etree._Element:
    return etree.fromstring("""
        <date-prop name="http://0.0.0.0:3333/ontology/9999/onto/v2#testSubDate1">
            <date>JULIAN:BCE:0700:BCE:0600</date>
            <date>ISLAMIC:BCE:0700:BCE:0600</date>
        </date-prop>
        """)


@pytest.fixture
def decimal_value_corr() -> etree._Element:
    return etree.fromstring("""
        <decimal-prop name="http://0.0.0.0:3333/ontology/9999/onto/v2#testDecimalSimpleText">
            <decimal>2.71</decimal>
        </decimal-prop>
    """)


@pytest.fixture
def decimal_value_corr_several() -> etree._Element:
    return etree.fromstring("""
        <decimal-prop name="http://0.0.0.0:3333/ontology/9999/onto/v2#testDecimalSimpleText">
            <decimal>1.0</decimal>
            <decimal>2.0</decimal>
        </decimal-prop>
    """)


@pytest.fixture
def geometry_value_corr() -> etree._Element:
    return etree.fromstring("""
        <geometry-prop name="hasGeometry">
            <geometry>
                {
                    "status": "active",
                    "type": "polygon",
                    "lineWidth": 5,
                    "points": [{"x": 0.4, "y": 0.6},
                               {"x": 0.5, "y": 0.9},
                               {"x": 0.8, "y": 0.9},
                               {"x": 0.7, "y": 0.6}]
                }
            </geometry>
        </geometry-prop>
    """)


@pytest.fixture
def geometry_value_wrong() -> etree._Element:
    return etree.fromstring("""
        <geometry-prop name="hasGeometry">
            <geometry></geometry>
        </geometry-prop>
    """)


@pytest.fixture
def geoname_value_corr() -> etree._Element:
    return etree.fromstring("""
        <geoname-prop name="http://0.0.0.0:3333/ontology/9999/onto/v2#testGeoname">
            <geoname>1111111</geoname>
        </geoname-prop>
    """)


@pytest.fixture
def geoname_value_corr_several() -> etree._Element:
    return etree.fromstring("""
        <geoname-prop name="http://0.0.0.0:3333/ontology/9999/onto/v2#testGeoname">
            <geoname>1111111</geoname>
            <geoname>2222222</geoname>
        </geoname-prop>
    """)


@pytest.fixture
def integer_value_corr() -> etree._Element:
    return etree.fromstring("""
        <integer-prop name="http://0.0.0.0:3333/ontology/9999/onto/v2#testIntegerSimpleText">
            <integer>1</integer>
        </integer-prop>
    """)


@pytest.fixture
def integer_value_corr_several() -> etree._Element:
    return etree.fromstring("""
        <integer-prop name="http://0.0.0.0:3333/ontology/9999/onto/v2#testIntegerSimpleText">
            <integer>1</integer>
            <integer>2</integer>
        </integer-prop>
    """)


@pytest.fixture
def list_value_corr() -> etree._Element:
    return etree.fromstring("""
        <list-prop list="firstList" name="http://0.0.0.0:3333/ontology/9999/onto/v2#testListProp">
            <list>n1</list>
        </list-prop>
    """)


@pytest.fixture
def list_value_corr_several() -> etree._Element:
    return etree.fromstring("""
        <list-prop list="firstList" name="http://0.0.0.0:3333/ontology/9999/onto/v2#testListProp">
            <list>n1</list>
            <list>n2</list>
        </list-prop>
    """)


@pytest.fixture
def list_value_wrong_node() -> etree._Element:
    return etree.fromstring("""
        <list-prop list="firstList" name="http://0.0.0.0:3333/ontology/9999/onto/v2#testListProp">
            <list>other</list>
        </list-prop>
    """)


@pytest.fixture
def list_value_wrong_list() -> etree._Element:
    return etree.fromstring("""
        <list-prop list="other" name="http://0.0.0.0:3333/ontology/9999/onto/v2#testListProp">
            <list>n1</list>
        </list-prop>
    """)


@pytest.fixture
def resptr_value_corr() -> etree._Element:
    return etree.fromstring("""
        <resptr-prop name="http://0.0.0.0:3333/ontology/9999/onto/v2#testHasLinkTo">
            <resptr>id_1</resptr>
        </resptr-prop>
    """)


@pytest.fixture
def resptr_value_corr_several() -> etree._Element:
    return etree.fromstring("""
        <resptr-prop name="http://0.0.0.0:3333/ontology/9999/onto/v2#testHasLinkTo">
            <resptr>id_1</resptr>
            <resptr>id_2</resptr>
        </resptr-prop>
    """)


@pytest.fixture
def resptr_value_wrong() -> etree._Element:
    return etree.fromstring("""
        <resptr-prop name="http://0.0.0.0:3333/ontology/9999/onto/v2#testHasLinkTo">
            <resptr></resptr>
        </resptr-prop>
    """)


@pytest.fixture
def text_richtext_value_corr() -> etree._Element:
    return etree.fromstring("""
        <text-prop name="http://0.0.0.0:3333/ontology/9999/onto/v2#testRichtext">
            <text encoding="xml"><p>Text</p></text>
        </text-prop>
    """)


@pytest.fixture
def text_richtext_value_corr_several() -> etree._Element:
    return etree.fromstring("""
        <text-prop name="http://0.0.0.0:3333/ontology/9999/onto/v2#testRichtext">
            <text encoding="xml">Text 1</text>
            <text encoding="xml">Text 2</text>
        </text-prop>
    """)


@pytest.fixture
def text_richtext_value_wrong() -> etree._Element:
    return etree.fromstring("""
        <text-prop name="http://0.0.0.0:3333/ontology/9999/onto/v2#testRichtext">
            <text encoding="xml"></text>
        </text-prop>
    """)


@pytest.fixture
def text_simpletext_value_corr() -> etree._Element:
    return etree.fromstring("""
        <text-prop name="http://0.0.0.0:3333/ontology/9999/onto/v2#testTextarea">
            <text encoding="utf8">Text</text>
        </text-prop>
    """)


@pytest.fixture
def text_simpletext_value_corr_several() -> etree._Element:
    return etree.fromstring("""
        <text-prop name="http://0.0.0.0:3333/ontology/9999/onto/v2#testSimpleText">
            <text encoding="utf8">Text 1</text>
            <text encoding="utf8">Text 2</text>
        </text-prop>
    """)


@pytest.fixture
def text_simpletext_value_wrong() -> etree._Element:
    return etree.fromstring("""
        <text-prop name="http://0.0.0.0:3333/ontology/9999/onto/v2#testSimpleText">
            <text encoding="utf8"></text>
        </text-prop>
    """)


@pytest.fixture
def time_value_corr() -> etree._Element:
    return etree.fromstring("""
        <time-prop name="http://0.0.0.0:3333/ontology/9999/onto/v2#testTimeValue">
            <time>2019-10-23T13:45:12.01-14:00</time>
        </time-prop>
    """)


@pytest.fixture
def time_value_corr_several() -> etree._Element:
    return etree.fromstring("""
        <time-prop name="http://0.0.0.0:3333/ontology/9999/onto/v2#testTimeValue">
            <time>2019-10-23T13:45:12.01-14:00</time>
            <time>2019-10-23T13:45:12.01-08:00</time>
        </time-prop>
    """)


@pytest.fixture
def uri_value_corr() -> etree._Element:
    return etree.fromstring("""
        <uri-prop name="http://0.0.0.0:3333/ontology/9999/onto/v2#testUriValue">
            <uri>https://dasch.swiss</uri>
        </uri-prop>
    """)


@pytest.fixture
def uri_value_corr_several() -> etree._Element:
    return etree.fromstring("""
        <uri-prop name="http://0.0.0.0:3333/ontology/9999/onto/v2#testUriValue">
            <uri>https://dasch.swiss</uri>
            <uri>https://app.dasch.swiss</uri>
        </uri-prop>
    """)


@pytest.fixture
def uri_value_wrong() -> etree._Element:
    return etree.fromstring("""
        <uri-prop name="http://0.0.0.0:3333/ontology/9999/onto/v2#testUriValue">
            <uri>oth er</uri>
        </uri-prop>
    """)
