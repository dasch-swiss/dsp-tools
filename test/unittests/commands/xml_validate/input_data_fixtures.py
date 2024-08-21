import json
from typing import Any

import pytest
from lxml import etree

from dsp_tools.commands.xml_validate.models.xml_deserialised import ProjectXML
from dsp_tools.commands.xml_validate.models.xml_deserialised import ResourceXML


@pytest.fixture
def list_from_api() -> dict[str, Any]:
    with open("testdata/xml-validate/from_api/onlyList.json", "r", encoding="utf-8") as file:
        data: dict[str, Any] = json.load(file)
    return data


@pytest.fixture
def parsed_xml() -> etree._Element:
    return etree.fromstring("""
    <knora 
        shortcode="9999"
        default-ontology="onto">

        <permissions id="res-default">
            <allow group="UnknownUser">V</allow>
        </permissions>
        
        <resource label="Label" restype=":Class" id="class-id">
            <text-prop name=":hasSimpleText">
                <text encoding="utf8">Text Content 1</text>
                <text encoding="utf8">Text Content 2</text>
            </text-prop>
            <resptr-prop name=":linkProp">
                <resptr>link-id</resptr>
            </resptr-prop>
        </resource>
    </knora>
    """)


@pytest.fixture
def permission_res_default() -> etree._Element:
    return etree.fromstring("""
        <permissions id="res-default">
            <allow group="UnknownUser">V</allow>
            <allow group="KnownUser">V</allow>
        </permissions>
    """)


@pytest.fixture
def resptr_prop() -> etree._Element:
    return etree.fromstring("""
        <resptr-prop name=":linkProp">
            <resptr>link-id</resptr>
        </resptr-prop>
    """)


@pytest.fixture
def text_prop() -> etree._Element:
    return etree.fromstring("""
        <text-prop name=":hasSimpleText">
            <text encoding="utf8" permissions="prop-default">text content</text>
            <text encoding="utf8" comment="Comment">text content 2</text>
        </text-prop>
    """)


@pytest.fixture
def list_prop() -> etree._Element:
    return etree.fromstring("""
        <list-prop name=":listProp" list="onlyList">
            <list>listNode</list>
        </list-prop>
    """)


@pytest.fixture
def resource_xml(list_prop: etree._Element, text_prop: etree._Element) -> ResourceXML:
    return ResourceXML(
        res_attrib={"label": "Label", "restype": ":Class", "id": "class-id"}, values=[list_prop, text_prop]
    )


@pytest.fixture
def project_xml(resource_xml: ResourceXML) -> ProjectXML:
    return ProjectXML(shortcode="9999", default_onto="onto", xml_resources=[resource_xml])
