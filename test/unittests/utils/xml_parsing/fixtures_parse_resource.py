import pytest
from lxml import etree


@pytest.fixture
def root_no_resources() -> etree._Element:
    return etree.fromstring("""
    <knora shortcode="0000"
       default-ontology="default">
    </knora>
    """)


@pytest.fixture
def minimal_root() -> etree._Element:
    return etree.fromstring("""
    <knora shortcode="0000"
       default-ontology="default">
        <resource label="The only resource"
                  restype=":minimalResource"
                  id="the_only_resource">
        </resource>
        
        <link label="value with permissions" id="value_with_permissions">
            <resptr-prop name="hasLinkTo">
                <resptr permissions="open">target_empty_1</resptr>
            </resptr-prop>
        </link>
    </knora>
    """)


@pytest.fixture
def resource_no_values() -> etree._Element:
    return etree.fromstring("""
    <resource label="lbl" restype=":Class" id="one">
    </resource>
    """)


@pytest.fixture
def resource_empty_permissions() -> etree._Element:
    return etree.fromstring("""
    <resource 
        label="lbl" 
        restype=":Class" 
        id="one"
        permissions="open"
    >
    </resource>
    """)


@pytest.fixture
def resource_with_bitstream() -> etree._Element:
    return etree.fromstring("""
    <resource label="lbl" restype=":Class" id="one">
        <bitstream>
            testdata/bitstreams/test.wav
        </bitstream>
    </resource>
    """)


@pytest.fixture
def resource_with_migration_metadata() -> etree._Element:
    return etree.fromstring("""
    <resource 
        label="lbl" 
        restype=":Class" 
        id="one"
        ark="ark"
        iri="iri"
        creation_date="2019-01-09T15:45:54.502951Z"
    >
    </resource>
    """)


@pytest.fixture
def resource_with_values() -> etree._Element:
    return etree.fromstring("""
        <resource label="lbl" restype=":Class" id="one">
            <boolean-prop name=":hasProp">
                <boolean>true</boolean>
            </boolean-prop>
            <color-prop name=":hasProp">
                <color>#00ff00</color>
                <color>#00ff11</color>
            </color-prop>
        </resource>""")


@pytest.fixture
def resource_region() -> etree._Element:
    return etree.fromstring("""""")


@pytest.fixture
def resource_link() -> etree._Element:
    return etree.fromstring("""""")


@pytest.fixture
def resource_video_segment() -> etree._Element:
    return etree.fromstring("""""")


@pytest.fixture
def resource_audio_segment() -> etree._Element:
    return etree.fromstring("""""")


@pytest.fixture
def boolean_value_with_metadata() -> etree._Element:
    return etree.fromstring("""
        <boolean-prop name=":hasProp">
            <boolean comment="Comment on Value">true</boolean>
             permissions="open"
        </boolean-prop>
    """)


@pytest.fixture
def color_value() -> etree._Element:
    return etree.fromstring("""
        <color-prop name=":hasProp">
            <color>#00ff00</color>
        </color-prop>
        """)


@pytest.fixture
def color_value_several() -> etree._Element:
    return etree.fromstring("""
        <color-prop name=":hasProp">
            <color>#00ff00</color>
            <color>#00ff11</color>
        </color-prop>
        """)


@pytest.fixture
def date_value() -> etree._Element:
    return etree.fromstring("""
        <date-prop name=":hasProp">
            <date>JULIAN:BCE:0700:BCE:0600</date>
        </date-prop>
        """)


@pytest.fixture
def date_value_several() -> etree._Element:
    return etree.fromstring("""
        <date-prop name=":hasProp">
            <date>JULIAN:BCE:0700:BCE:0600</date>
            <date>ISLAMIC:0600:0700</date>
        </date-prop>
        """)


@pytest.fixture
def decimal_value() -> etree._Element:
    return etree.fromstring("""
        <decimal-prop name=":hasProp">
            <decimal>2.71</decimal>
        </decimal-prop>
    """)


@pytest.fixture
def decimal_value_several() -> etree._Element:
    return etree.fromstring("""
        <decimal-prop name=":hasProp">
            <decimal>1.0</decimal>
            <decimal>2.0</decimal>
        </decimal-prop>
    """)


@pytest.fixture
def geometry_value() -> etree._Element:
    return etree.fromstring("""
        <geometry-prop name="hasGeometry">
            <geometry>
                {}
            </geometry>
        </geometry-prop>
    """)


@pytest.fixture
def geoname_value() -> etree._Element:
    return etree.fromstring("""
        <geoname-prop name=":hasProp">
            <geoname>1111111</geoname>
        </geoname-prop>
    """)


@pytest.fixture
def integer_value() -> etree._Element:
    return etree.fromstring("""
        <integer-prop name=":hasProp">
            <integer>1</integer>
        </integer-prop>
    """)


@pytest.fixture
def list_value() -> etree._Element:
    return etree.fromstring("""
        <list-prop list="firstList" name=":hasProp">
            <list>n1</list>
        </list-prop>
    """)


@pytest.fixture
def list_value_several() -> etree._Element:
    return etree.fromstring("""
        <list-prop list="firstList" name=":hasProp">
            <list>n1</list>
            <list>n2</list>
        </list-prop>
    """)


@pytest.fixture
def resptr_value() -> etree._Element:
    return etree.fromstring("""
        <resptr-prop name=":hasProp">
            <resptr>id_1</resptr>
        </resptr-prop>
    """)


@pytest.fixture
def text_richtext_value() -> etree._Element:
    return etree.fromstring("""
        <text-prop name=":hasProp">
            <text encoding="xml"><p>Text</p></text>
        </text-prop>
    """)


@pytest.fixture
def text_simpletext_value() -> etree._Element:
    return etree.fromstring("""
        <text-prop name=":hasProp">
            <text encoding="utf8">Text</text>
        </text-prop>
    """)


@pytest.fixture
def text_simpletext_value_no_text() -> etree._Element:
    return etree.fromstring("""
        <text-prop name=":hasProp">
            <text encoding="utf8"></text>
        </text-prop>
    """)


@pytest.fixture
def time_value() -> etree._Element:
    return etree.fromstring("""
        <time-prop name=":hasProp">
            <time>2019-10-23T13:45:12.01-14:00</time>
        </time-prop>
    """)


@pytest.fixture
def uri_value() -> etree._Element:
    return etree.fromstring("""
        <uri-prop name=":hasProp">
            <uri>https://dasch.swiss</uri>
        </uri-prop>
    """)


@pytest.fixture
def iiif_with_spaces() -> etree._Element:
    return etree.fromstring("""
        <iiif-uri>
            https://iiif.uri/full.jpg
        </iiif-uri>
    """)


@pytest.fixture
def iiif_with_legal_info() -> etree._Element:
    return etree.fromstring("""
        <iiif-uri
         license="license_iri"
                  copyright-holder="copy"
                  authorship-id="auth">
            https://iiif.uri/full.jpg
        </iiif-uri>
    """)


@pytest.fixture
def bitstream_with_spaces() -> etree._Element:
    return etree.fromstring("""
        <bitstream permissions="open">
            this/is/filepath/file.z
        </bitstream>
    """)


@pytest.fixture
def bitstream_with_legal_info() -> etree._Element:
    return etree.fromstring("""
        <bitstream license="http://rdfh.ch/licenses/unknown"
                   copyright-holder="DaSCH"
                   authorship-id="authorship_1"
        >this/is/filepath/file.z</bitstream>
    """)
