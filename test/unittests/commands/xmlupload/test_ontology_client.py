from dataclasses import dataclass
from test.unittests.commands.xmlupload.connection_mock import ConnectionMockBase
from typing import Any

from pytest_unordered import unordered

from dsp_tools.commands.xmlupload.ontology_client import (
    OntologyClientLive,
    _get_all_classes_from_graph,
    _get_all_properties_from_graph,
    _remove_prefixes,
    format_ontology,
)

# pylint: disable=missing-class-docstring,missing-function-docstring,unused-argument,redefined-outer-name,protected-access


@dataclass
class ConnectionMock(ConnectionMockBase):
    get_responses: dict[Any, Any]

    def get(self, route: str, headers: dict[str, str] | None = None) -> dict[Any, Any]:
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


def test_get_all_properties_from_graph_haslinkto() -> None:
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
    assert res_onto.classes == ["Annotation"]
    assert res_onto.properties == ["hasLinkTo"]


def test_get_ontology_names_from_server() -> None:
    response = {
        "project": {
            "description": [],
            "id": "http://rdfh.ch/projects/yTerZGyxjZVqFMNNKXCDPF",
            "keywords": [],
            "logo": None,
            "longname": "Bernoulli-Euler Online",
            "ontologies": [
                "http://www.knora.org/ontology/0801/biblio",
                "http://www.knora.org/ontology/0801/newton",
                "http://www.knora.org/ontology/0801/leibniz",
                "http://www.knora.org/ontology/0801/beol",
            ],
            "selfjoin": False,
            "shortcode": "0801",
            "shortname": "beol",
            "status": True,
        }
    }
    con = ConnectionMock(response)
    onto_cli = OntologyClientLive(con, "0801", "beol")
    onto_cli._get_ontology_names_from_server()
    assert unordered(onto_cli.ontology_names) == ["biblio", "newton", "leibniz", "beol"]


def test_get_ontology_from_server() -> None:
    response = {
        "knora-api:lastModificationDate": {"@value": "2022-04-27T08:47:20.815147225Z", "@type": "xsd:dateTimeStamp"},
        "rdfs:label": "The BEOL ontology",
        "@graph": [
            {"resource_class": ["Information"]},
            {"property": ["Information"]},
        ],
        "knora-api:attachedToProject": {"@id": "http://rdfh.ch/projects/yTerZGyxjZVqFMNNKXCDPF"},
        "@type": "owl:Ontology",
        "@id": "http://api.dasch.swiss/ontology/0801/beol/v2",
        "@context": {
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "standoff": "http://api.knora.org/ontology/standoff/v2#",
            "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
            "owl": "http://www.w3.org/2002/07/owl#",
            "salsah-gui": "http://api.knora.org/ontology/salsah-gui/v2#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "beol": "http://api.dasch.swiss/ontology/0801/beol/v2#",
            "xsd": "http://www.w3.org/2001/XMLSchema#",
            "biblio": "http://api.dasch.swiss/ontology/0801/biblio/v2#",
        },
    }
    con = ConnectionMock(response)
    onto_cli = OntologyClientLive(con, "0801", "beol")
    res_graph = onto_cli._get_ontology_from_server("beol")
    assert unordered(res_graph) == [{"resource_class": ["Information"]}, {"property": ["Information"]}]


def test_get_knora_api_from_server() -> None:
    response = {
        "rdfs:label": "The knora-api ontology in the complex schema",
        "@graph": [
            {"resource_class": ["Information"]},
            {"property": ["Information"]},
        ],
        "knora-api:attachedToProject": {"@id": "http://www.knora.org/ontology/knora-admin#SystemProject"},
        "knora-api:isBuiltIn": True,
        "@type": "owl:Ontology",
        "@id": "http://api.knora.org/ontology/knora-api/v2",
        "@context": {
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
            "owl": "http://www.w3.org/2002/07/owl#",
            "salsah-gui": "http://api.knora.org/ontology/salsah-gui/v2#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "xsd": "http://www.w3.org/2001/XMLSchema#",
        },
    }
    con = ConnectionMock(response)
    onto_cli = OntologyClientLive(con, "", "")
    res_graph = onto_cli._get_knora_api_from_server()
    assert unordered(res_graph) == [{"resource_class": ["Information"]}, {"property": ["Information"]}]


def test_remove_prefixes_knora_classes() -> None:
    test_elements = ["knora-api:Annotation", "knora-api:ArchiveFileValue", "knora-api:ArchiveRepresentation"]
    res = _remove_prefixes(test_elements)
    assert unordered(res) == ["Annotation", "ArchiveFileValue", "ArchiveRepresentation"]


def test_remove_prefixes_knora_properties() -> None:
    test_elements = ["knora-api:attachedToUser", "knora-api:deletedBy"]
    res = _remove_prefixes(test_elements)
    assert unordered(res) == ["attachedToUser", "deletedBy"]
