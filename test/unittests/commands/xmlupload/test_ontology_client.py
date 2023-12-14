from dataclasses import dataclass
from pathlib import Path
from test.unittests.commands.xmlupload.connection_mock import ConnectionMockBase
from typing import Any

from pytest_unordered import unordered

from dsp_tools.commands.xmlupload.ontology_client import (
    OntologyClientLive,
    _get_all_classes_from_graph,
    _get_all_properties_from_graph,
    _remove_prefixes,
    deserialize_ontology,
)


@dataclass
class ConnectionMock(ConnectionMockBase):
    get_response: dict[Any, Any]

    def get(
        self,
        route: str,  # noqa: ARG002 (unused-method-argument)
        headers: dict[str, str] | None = None,  # noqa: ARG002 (unused-method-argument)
        timeout: int = 20,  # noqa: ARG002 (unused-method-argument)
    ) -> dict[Any, Any]:
        return self.get_response


class TestGetAllClassesFromGraph:
    @staticmethod
    def test_single_class() -> None:
        test_graph = [
            {
                "knora-api:isResourceClass": True,
                "rdfs:label": "Sequenz einer Audio-Ressource",
                "knora-api:canBeInstantiated": True,
                "rdfs:subClassOf": [],
                "@type": "owl:Class",
                "@id": "testonto:AudioSequence",
            },
        ]
        res_cls = _get_all_classes_from_graph(test_graph)
        assert res_cls == ["testonto:AudioSequence"]

    @staticmethod
    def test_property() -> None:
        test_graph = [
            {
                "rdfs:label": "URI",
                "rdfs:subPropertyOf": {},
                "knora-api:isEditable": True,
                "knora-api:isResourceProperty": True,
                "@type": "owl:ObjectProperty",
                "salsah-gui:guiAttribute": [],
                "knora-api:objectType": {},
                "salsah-gui:guiElement": {},
                "@id": "testonto:hasUri",
            },
        ]
        res_cls = _get_all_classes_from_graph(test_graph)
        assert not res_cls

    @staticmethod
    def test_from_graph_resources_and_properties() -> None:
        test_graph = [
            {
                "knora-api:isResourceClass": True,
                "rdfs:label": "Sequenz einer Audio-Ressource",
                "knora-api:canBeInstantiated": True,
                "rdfs:subClassOf": [],
                "@type": "owl:Class",
                "@id": "testonto:AudioSequence",
            },
            {
                "rdfs:label": "URI",
                "rdfs:subPropertyOf": {},
                "knora-api:isEditable": True,
                "knora-api:isResourceProperty": True,
                "@type": "owl:ObjectProperty",
                "salsah-gui:guiAttribute": [],
                "knora-api:objectType": {},
                "salsah-gui:guiElement": {},
                "@id": "testonto:hasUri",
            },
        ]
        res_cls = _get_all_classes_from_graph(test_graph)
        assert res_cls == ["testonto:AudioSequence"]


def test_get_all_properties_from_graph_haslinkto() -> None:
    test_graph = [
        {
            "rdfs:label": "hasResource",
            "rdfs:subPropertyOf": {},
            "knora-api:isEditable": True,
            "knora-api:isResourceProperty": True,
            "knora-api:isLinkProperty": True,
            "@type": "owl:ObjectProperty",
            "knora-api:objectType": {},
            "salsah-gui:guiElement": {},
            "@id": "testonto:hasResource",
        },
        {
            "knora-api:isLinkValueProperty": True,
            "rdfs:label": "hasResource",
            "rdfs:subPropertyOf": {},
            "knora-api:isEditable": True,
            "knora-api:isResourceProperty": True,
            "@type": "owl:ObjectProperty",
            "knora-api:objectType": {},
            "salsah-gui:guiElement": {},
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
            "rdfs:subClassOf": [],
            "@type": "owl:Class",
            "@id": "testonto:AudioSequence",
        },
        {
            "rdfs:label": "URI",
            "rdfs:subPropertyOf": {},
            "knora-api:isEditable": True,
            "knora-api:isResourceProperty": True,
            "@type": "owl:ObjectProperty",
            "salsah-gui:guiAttribute": [],
            "knora-api:objectType": {},
            "salsah-gui:guiElement": {},
            "@id": "testonto:hasUri",
        },
    ]
    res_prop = _get_all_properties_from_graph(test_graph)
    assert res_prop == ["testonto:hasUri"]


def test_deserialize_ontology() -> None:
    test_graph = [
        {
            "knora-api:isResourceClass": True,
            "rdfs:label": "Annotation",
            "knora-api:canBeInstantiated": True,
            "rdfs:subClassOf": [],
            "rdfs:comment": "A generic class for representing annotations",
            "@type": "owl:Class",
            "@id": "knora-api:Annotation",
        },
        {
            "rdfs:label": "has Link to",
            "rdfs:subPropertyOf": {},
            "knora-api:isEditable": True,
            "knora-api:isResourceProperty": True,
            "@type": "owl:ObjectProperty",
            "knora-api:objectType": {},
            "@id": "knora-api:hasLinkTo",
            "knora-api:subjectType": {},
            "knora-api:isLinkProperty": True,
            "rdfs:comment": "Represents a direct connection between two resources",
        },
    ]
    res_onto = deserialize_ontology(test_graph)
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
    onto_client = OntologyClientLive(con, "0801", "beol", Path(""))
    onto_client._get_ontology_names_from_server()
    assert unordered(onto_client.ontology_names) == ["biblio", "newton", "leibniz", "beol"]


def test_get_ontology_from_server() -> None:
    response = {
        "knora-api:lastModificationDate": {},
        "rdfs:label": "The BEOL ontology",
        "@graph": [
            {"resource_class": ["Information"]},
            {"property": ["Information"]},
        ],
        "knora-api:attachedToProject": {},
        "@type": "owl:Ontology",
        "@id": "http://api.dasch.swiss/ontology/0801/beol/v2",
        "@context": {},
    }
    con = ConnectionMock(response)
    onto_client = OntologyClientLive(con, "0801", "beol", Path(""))
    res_graph = onto_client._get_ontology_from_server("beol")
    assert unordered(res_graph) == [{"resource_class": ["Information"]}, {"property": ["Information"]}]


def test_get_knora_api_from_server() -> None:
    response = {
        "rdfs:label": "The knora-api ontology in the complex schema",
        "@graph": [
            {"resource_class": ["Information"]},
            {"property": ["Information"]},
        ],
        "knora-api:attachedToProject": {},
        "knora-api:isBuiltIn": True,
        "@type": "owl:Ontology",
        "@id": "http://api.knora.org/ontology/knora-api/v2",
        "@context": {},
    }
    con = ConnectionMock(response)
    onto_client = OntologyClientLive(con, "", "", Path(""))
    res_graph = onto_client._get_knora_api_ontology_from_server()
    assert unordered(res_graph) == [{"resource_class": ["Information"]}, {"property": ["Information"]}]


def test_remove_prefixes_knora_classes() -> None:
    test_elements = ["knora-api:Annotation", "knora-api:ArchiveFileValue", "knora-api:ArchiveRepresentation"]
    res = _remove_prefixes(test_elements)
    assert unordered(res) == ["Annotation", "ArchiveFileValue", "ArchiveRepresentation"]


def test_remove_prefixes_knora_properties() -> None:
    test_elements = ["knora-api:attachedToUser", "knora-api:deletedBy"]
    res = _remove_prefixes(test_elements)
    assert unordered(res) == ["attachedToUser", "deletedBy"]
