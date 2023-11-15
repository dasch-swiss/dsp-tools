from dataclasses import dataclass
from test.unittests.commands.xmlupload.connection_mock import ConnectionMockBase
from typing import Any

from dsp_tools.commands.xmlupload.ontology_client import (
    _get_all_classes_from_graph,
    _get_all_properties_from_graph,
    format_ontology,
)

# pylint: disable=missing-class-docstring,missing-function-docstring,unused-argument,redefined-outer-name


@dataclass
class ConnectionMock(ConnectionMockBase):
    get_responses: dict[str, Any]

    def get(self, route: str, headers: dict[str, str] | None = None) -> dict[str, Any]:
        return self.get_responses


def test_get_all_classes_from_graph() -> None:
    test_graph = [
        {
            "knora-api:isResourceClass": True,
            "rdfs:label": "Sequenz einer Audio-Ressource",
            "knora-api:canBeInstantiated": True,
            "rdfs:subClassOf": [
                {"@id": "knora-api:Resource"},
                {"@type": "owl:Restriction", "owl:onProperty": {"@id": "testonto:hasBounds"}, "owl:cardinality": 1},
                {
                    "@type": "owl:Restriction",
                    "owl:onProperty": {"@id": "testonto:sequenceOfAudio"},
                    "owl:cardinality": 1,
                },
            ],
            "@type": "owl:Class",
            "@id": "testonto:AudioSequence",
        },
    ]
    res_cls = _get_all_classes_from_graph(test_graph)
    assert res_cls == ["testonto:AudioSequence"]


def test_get_all_classes_from_graph_property() -> None:
    test_graph = [
        {
            "rdfs:label": "URI",
            "rdfs:subPropertyOf": {"@id": "knora-api:hasValue"},
            "knora-api:isEditable": True,
            "knora-api:isResourceProperty": True,
            "@type": "owl:ObjectProperty",
            "salsah-gui:guiAttribute": ["maxlength=255", "size=80"],
            "knora-api:objectType": {"@id": "knora-api:UriValue"},
            "salsah-gui:guiElement": {"@id": "salsah-gui:SimpleText"},
            "@id": "testonto:hasUri",
        },
    ]
    res_cls = _get_all_classes_from_graph(test_graph)
    assert not res_cls


def test_get_all_properties_from_graph_hasLinkTo() -> None:
    test_graph = [
        {
            "rdfs:label": "hasResource",
            "rdfs:subPropertyOf": {"@id": "knora-api:hasLinkTo"},
            "knora-api:isEditable": True,
            "knora-api:isResourceProperty": True,
            "knora-api:isLinkProperty": True,
            "@type": "owl:ObjectProperty",
            "knora-api:objectType": {"@id": "knora-api:Resource"},
            "salsah-gui:guiElement": {"@id": "salsah-gui:Searchbox"},
            "@id": "testonto:hasResource",
        },
        {
            "knora-api:isLinkValueProperty": True,
            "rdfs:label": "hasResource",
            "rdfs:subPropertyOf": {"@id": "knora-api:hasLinkToValue"},
            "knora-api:isEditable": True,
            "knora-api:isResourceProperty": True,
            "@type": "owl:ObjectProperty",
            "knora-api:objectType": {"@id": "knora-api:LinkValue"},
            "salsah-gui:guiElement": {"@id": "salsah-gui:Searchbox"},
            "@id": "testonto:hasResourceValue",
        },
    ]
    res_prop = _get_all_properties_from_graph(test_graph)
    assert res_prop == ["testonto:hasResource", "testonto:hasResourceValue"]


def test_get_all_properties_from_graph_resources_and_properties() -> None:
    test_graph = [
        {
            "knora-api:isResourceClass": True,
            "rdfs:label": "Sequenz einer Audio-Ressource",
            "knora-api:canBeInstantiated": True,
            "rdfs:subClassOf": [
                {"@id": "knora-api:Resource"},
                {"@type": "owl:Restriction", "owl:onProperty": {"@id": "testonto:hasBounds"}, "owl:cardinality": 1},
                {
                    "@type": "owl:Restriction",
                    "owl:onProperty": {"@id": "testonto:sequenceOfAudio"},
                    "owl:cardinality": 1,
                },
            ],
            "@type": "owl:Class",
            "@id": "testonto:AudioSequence",
        },
        {
            "rdfs:label": "URI",
            "rdfs:subPropertyOf": {"@id": "knora-api:hasValue"},
            "knora-api:isEditable": True,
            "knora-api:isResourceProperty": True,
            "@type": "owl:ObjectProperty",
            "salsah-gui:guiAttribute": ["maxlength=255", "size=80"],
            "knora-api:objectType": {"@id": "knora-api:UriValue"},
            "salsah-gui:guiElement": {"@id": "salsah-gui:SimpleText"},
            "@id": "testonto:hasUri",
        },
    ]
    res_prop = _get_all_properties_from_graph(test_graph)
    assert res_prop == ["testonto:hasUri"]


def test_get_all_classes_from_graph_from_graph_resources_and_properties() -> None:
    test_graph = [
        {
            "knora-api:isResourceClass": True,
            "rdfs:label": "Sequenz einer Audio-Ressource",
            "knora-api:canBeInstantiated": True,
            "rdfs:subClassOf": [
                {"@id": "knora-api:Resource"},
                {"@type": "owl:Restriction", "owl:onProperty": {"@id": "testonto:hasBounds"}, "owl:cardinality": 1},
                {
                    "@type": "owl:Restriction",
                    "owl:onProperty": {"@id": "testonto:sequenceOfAudio"},
                    "owl:cardinality": 1,
                },
            ],
            "@type": "owl:Class",
            "@id": "testonto:AudioSequence",
        },
        {
            "rdfs:label": "URI",
            "rdfs:subPropertyOf": {"@id": "knora-api:hasValue"},
            "knora-api:isEditable": True,
            "knora-api:isResourceProperty": True,
            "@type": "owl:ObjectProperty",
            "salsah-gui:guiAttribute": ["maxlength=255", "size=80"],
            "knora-api:objectType": {"@id": "knora-api:UriValue"},
            "salsah-gui:guiElement": {"@id": "salsah-gui:SimpleText"},
            "@id": "testonto:hasUri",
        },
    ]
    res_cls = _get_all_classes_from_graph(test_graph)
    assert res_cls == ["testonto:AudioSequence"]


def test_format_ontology() -> None:
    test_graph = [
        {
            "knora-api:isResourceClass": True,
            "rdfs:label": "Annotation",
            "knora-api:canBeInstantiated": True,
            "rdfs:subClassOf": [
                {"@id": "knora-api:Resource"},
            ],
            "rdfs:comment": "A generic class for representing annotations",
            "@type": "owl:Class",
            "@id": "knora-api:Annotation",
        },
        {
            "rdfs:label": "has Link to",
            "rdfs:subPropertyOf": {"@id": "knora-api:resourceProperty"},
            "knora-api:isEditable": True,
            "knora-api:isResourceProperty": True,
            "@type": "owl:ObjectProperty",
            "knora-api:objectType": {"@id": "knora-api:Resource"},
            "@id": "knora-api:hasLinkTo",
            "knora-api:subjectType": {"@id": "knora-api:Resource"},
            "knora-api:isLinkProperty": True,
            "rdfs:comment": "Represents a direct connection between two resources",
        },
    ]
    res_onto = format_ontology(test_graph)
    assert res_onto.classes == ["knora-api:Annotation"]
    assert res_onto.properties == ["knora-api:hasLinkTo"]
