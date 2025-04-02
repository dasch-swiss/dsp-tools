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
    <resource label="lbl" restype=":Class" id="resource_no_values">
    </resource>
    """)


@pytest.fixture
def resource_empty_permissions() -> etree._Element:
    return etree.fromstring("""
    <resource 
        label="lbl" 
        restype=":Class" 
        id="resource_empty_permissions"
        permissions="open"
    >
    </resource>
    """)


@pytest.fixture
def resource_with_file_values() -> etree._Element:
    return etree.fromstring("""
    <resource label="lbl" restype=":Class" id="resource_with_file_values">
        <bitstream>testdata/bitstreams/test.wav</bitstream>
    </resource>
    """)


@pytest.fixture
def resource_with_iiif() -> etree._Element:
    return etree.fromstring("""
    <resource label="lbl" restype=":Class" id="resource_with_iiif">
        <iiif-uri>https://iiif.uri/full.jpg</iiif-uri>
    </resource>
    """)


@pytest.fixture
def resource_with_migration_metadata() -> etree._Element:
    return etree.fromstring("""
    <resource 
        label="lbl" 
        restype=":Class" 
        id="resource_with_migration_metadata"
        ark="ark"
        iri="iri"
        creation_date="2019-01-09T15:45:54.502951Z"
    >
    </resource>
    """)


@pytest.fixture
def resource_with_values() -> etree._Element:
    return etree.fromstring("""
        <resource label="lbl" restype=":Class" id="resource_with_values">
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
    return etree.fromstring("""
    <region label="lbl" id="resource_region">
        <color-prop name="hasColor">
            <color>#5d1f1e</color>
        </color-prop>
        <resptr-prop name="isRegionOf">
            <resptr>target_region_of</resptr>
        </resptr-prop>
        <geometry-prop name="hasGeometry">
            <geometry>
                {}
            </geometry>
        </geometry-prop>
        <text-prop name="hasComment">
            <text encoding="xml">Comment</text>
        </text-prop>
    </region>
    """)


@pytest.fixture
def resource_link() -> etree._Element:
    return etree.fromstring("""
    <link label="lbl" id="resource_link">
        <resptr-prop name="hasLinkTo">
            <resptr permissions="open">target</resptr>
        </resptr-prop>
    </link>
    """)


@pytest.fixture
def resource_video_segment() -> etree._Element:
    return etree.fromstring("""
    <video-segment label="lbl" id="resource_video_segment">
        <isSegmentOf>target_empty_movie</isSegmentOf>
        <hasSegmentBounds segment_start="0.1" segment_end="0.234"/>
        <hasTitle>Title</hasTitle>
        <hasComment>Comment</hasComment>
        <hasDescription><Description</hasDescription>
        <hasKeyword>Keyword 1</hasKeyword>
        <hasKeyword>Keyword 2</hasKeyword>
        <relatesTo>relates_to_id</relatesTo>
    </video-segment>
    """)


@pytest.fixture
def resource_audio_segment() -> etree._Element:
    return etree.fromstring("""
    <audio-segment label="lbl" id="resource_audio_segment">
        <isSegmentOf>target_empty_movie</isSegmentOf>
        <hasSegmentBounds segment_start="0.1" segment_end="0.234"/>
        <hasTitle>Title</hasTitle>
        <hasComment>Comment</hasComment>
        <hasDescription><Description 1</hasDescription>
        <hasDescription><Description 2</hasDescription>
        <hasKeyword>Keyword 1</hasKeyword>
        <relatesTo>relates_to_id</relatesTo>
    </audio-segment>
    """)
