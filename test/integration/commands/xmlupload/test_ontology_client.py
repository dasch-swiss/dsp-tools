from dataclasses import dataclass
from typing import Any

import pytest
from pytest_unordered import unordered

from dsp_tools.commands.xmlupload.prepare_xml_input.ontology_client import OntologyClientLive
from test.integration.commands.xmlupload.connection_mock import ConnectionMockBase


@dataclass
class ConnectionMock(ConnectionMockBase):
    get_response: dict[Any, Any]

    def get(self, route: str, headers: dict[str, str] | None = None) -> dict[Any, Any]:  # noqa: ARG002 (unused-method-argument)
        return self.get_response


def test_get_ontology_names_from_server() -> None:
    response = {
        "project": {
            "description": [],
            "id": "http://rdfh.ch/projects/yTerZGyxjZVqFMNNKXCDPF",
            "keywords": [],
            "logo": None,
            "longname": "Bernoulli-Euler Online",
            "ontologies": [
                "http://api.dasch.swiss/ontology/0801/biblio/v2",
                "http://api.dasch.swiss/ontology/0801/newton/v2",
                "http://api.dasch.swiss/ontology/0801/leibniz/v2",
                "http://api.dasch.swiss/ontology/0801/beol/v2",
            ],
            "selfjoin": False,
            "shortcode": "0801",
            "shortname": "beol",
            "status": True,
        }
    }
    con = ConnectionMock(response)
    onto_client = OntologyClientLive(con, "0801", "beol")
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
    onto_client = OntologyClientLive(con, "0801", "beol")
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
    onto_client = OntologyClientLive(con, "", "")
    res_graph = onto_client.get_knora_api_ontology_from_server()
    assert unordered(res_graph) == [{"resource_class": ["Information"]}, {"property": ["Information"]}]


if __name__ == "__main__":
    pytest.main([__file__])
