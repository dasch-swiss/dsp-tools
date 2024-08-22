import json
from typing import Any

import pytest
from lxml import etree

from dsp_tools.commands.xml_validate.models.project_deserialised import ListDeserialised


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


@pytest.fixture
def onto_json() -> list[dict[str, Any]]:
    with open("testdata/xml-validate/from_api/onto.jsonld", "r", encoding="utf-8") as file:
        f: list[dict[str, Any]] = json.load(file)["@graph"]
        return f


@pytest.fixture
def list_deserialised() -> ListDeserialised:
    return ListDeserialised(
        list_name="onlyList", iri="http://rdfh.ch/lists/9999/trTKqD1uTPe7VSswMcaLSQ", nodes=["n1", "n1.1", "n1.1.1"]
    )


@pytest.fixture
def subclass_dict() -> dict[str, set[str]]:
    return {
        "onto:CardOneResource": {"onto:CardOneResource", "onto:SubClass"},
        "onto:NormalClass": {"onto:NormalClass"},
        "onto:SubClass": {"onto:CardOneResource"},
        "knora-api:Resource": {"onto:CardOneResource", "onto:SubClass", "onto:NormalClass"},
    }


@pytest.fixture
def one_res_class(onto_json: list[dict[str, Any]]) -> dict[str, Any]:
    return next(x for x in onto_json if x.get("@id") == "onto:SubClass")


@pytest.fixture
def list_prop(onto_json: list[dict[str, Any]]) -> dict[str, Any]:
    return next(x for x in onto_json if x.get("@id") == "onto:listProp")


@pytest.fixture
def link_prop(onto_json: list[dict[str, Any]]) -> dict[str, Any]:
    return next(x for x in onto_json if x.get("@id") == "onto:linkProp")


@pytest.fixture
def simpletext_prop(onto_json: list[dict[str, Any]]) -> dict[str, Any]:
    return next(x for x in onto_json if x.get("@id") == "onto:hasSimpleText")
