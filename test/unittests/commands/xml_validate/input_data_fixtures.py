import json
from typing import Any

import pytest
from lxml import etree


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
def xml_resptr_prop() -> etree._Element:
    return etree.fromstring("""
        <resptr-prop name=":linkProp">
            <resptr>link-id</resptr>
        </resptr-prop>
    """)


@pytest.fixture
def xml_text_prop() -> etree._Element:
    return etree.fromstring("""
        <text-prop name=":hasSimpleText">
            <text encoding="utf8" permissions="prop-default">text content</text>
            <text encoding="utf8">text content 2</text>
        </text-prop>
    """)


@pytest.fixture
def xml_list_prop() -> etree._Element:
    return etree.fromstring("""
        <list-prop name=":listProp" list="onlyList">
            <list>listNode</list>
        </list-prop>
    """)
