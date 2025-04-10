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
def root_with_2_resources() -> etree._Element:
    return etree.fromstring("""
    <knora shortcode="0000"
       default-ontology="default">
        <resource label="The only resource"
                  restype=":minimalResource"
                  id="the_only_resource">
        </resource>
        
        <link label="a link object" id="link_obj">
            <resptr-prop name="hasLinkTo">
                <resptr permissions="open">the_only_resource</resptr>
            </resptr-prop>
        </link>
    </knora>
    """)


@pytest.fixture
def resource_no_values() -> etree._Element:
    return etree.fromstring('<resource label="lbl" restype=":Class" id="resource_no_values"/>')


@pytest.fixture
def resource_empty_with_permission() -> etree._Element:
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
def resource_with_file_value() -> etree._Element:
    return etree.fromstring("""
    <resource label="lbl" restype=":Class" id="resource_with_file_value">
        <bitstream>
            testdata/bitstreams/test.wav    
        </bitstream>
    </resource>
    """)


@pytest.fixture
def resource_with_iiif() -> etree._Element:
    return etree.fromstring("""
    <resource label="lbl" restype=":Class" id="resource_with_iiif">
        <iiif-uri>
            https://iiif.uri/full.jpg
        </iiif-uri>
    </resource>
    """)


@pytest.fixture
def resource_with_migration_data() -> etree._Element:
    return etree.fromstring("""
    <resource 
        label="lbl" 
        restype=":Class" 
        id="resource_with_migration_data"
        ark="ark"
        iri="iri"
        creation_date="2019-01-09T15:45:54.502951Z"
    >
    </resource>
    """)


@pytest.fixture
def resource_with_value() -> etree._Element:
    return etree.fromstring("""
        <resource label="lbl" restype=":Class" id="resource_with_value">
            <boolean-prop name=":hasProp">
                <boolean>true</boolean>
            </boolean-prop>
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
            <text encoding="xml"> Comment</text>
        </text-prop>
    </region>
    """)


@pytest.fixture
def resource_link() -> etree._Element:
    return etree.fromstring("""
    <link label="lbl" id="resource_link">
        <resptr-prop name="hasLinkTo">
            <resptr permissions="open"> target</resptr>
        </resptr-prop>
    </link>
    """)


@pytest.fixture
def resource_video_segment() -> etree._Element:
    return etree.fromstring("""
    <video-segment label="lbl" id="resource_video_segment">
        <isSegmentOf>target</isSegmentOf>
        <hasSegmentBounds segment_start="0.1" segment_end="0.234"/>
        <hasTitle>Title</hasTitle>
        <hasComment>Comment</hasComment>
        <hasDescription> Description</hasDescription>
        <hasKeyword>Keyword 1</hasKeyword>
        <hasKeyword>Keyword 2</hasKeyword>
        <relatesTo>relates_to_id</relatesTo>
    </video-segment>
    """)


@pytest.fixture
def resource_audio_segment() -> etree._Element:
    return etree.fromstring("""
    <audio-segment label="lbl" id="resource_audio_segment">
        <isSegmentOf>target</isSegmentOf>
        <hasSegmentBounds permissions="open" segment_start="0.1" segment_end="0.234"/>
        <hasTitle comment="Cmt"> Title</hasTitle>
        <hasComment><p>Comment</p></hasComment>
        <hasDescription> <p>Description 1</p></hasDescription>
        <hasDescription>Description 2</hasDescription>
        <hasKeyword>Keyword </hasKeyword>
        <relatesTo>relates_to_id</relatesTo>
    </audio-segment>
    """)
