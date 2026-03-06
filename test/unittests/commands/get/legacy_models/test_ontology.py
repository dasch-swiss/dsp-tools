from typing import Any

import pytest

from dsp_tools.commands.get.legacy_models.ontology import create_all_ontologies_from_json
from dsp_tools.commands.get.legacy_models.ontology import create_ontology_from_json
from dsp_tools.error.exceptions import BaseError


def _make_minimal_ontology_json() -> dict[str, Any]:
    return {
        "@id": "http://0.0.0.0:3333/ontology/0001/myonto/v2",
        "@context": {
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "owl": "http://www.w3.org/2002/07/owl#",
            "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
        },
        "rdfs:label": "My Ontology",
        "knora-api:attachedToProject": {"@id": "http://rdfh.ch/projects/0001"},
    }


class TestCreateOntologyFromJson:
    """Tests for the create_ontology_from_json factory function."""

    def test_missing_iri_raises(self) -> None:
        json_obj = _make_minimal_ontology_json()
        del json_obj["@id"]
        with pytest.raises(BaseError, match="iri is missing"):
            create_ontology_from_json(json_obj)

    def test_missing_label_raises(self) -> None:
        json_obj = _make_minimal_ontology_json()
        del json_obj["rdfs:label"]
        with pytest.raises(BaseError, match="label is missing"):
            create_ontology_from_json(json_obj)

    def test_missing_project_attachment_raises(self) -> None:
        json_obj = _make_minimal_ontology_json()
        del json_obj["knora-api:attachedToProject"]
        with pytest.raises(BaseError, match="not attached to a project"):
            create_ontology_from_json(json_obj)

    def test_valid_minimal_ontology(self) -> None:
        json_obj = _make_minimal_ontology_json()
        onto = create_ontology_from_json(json_obj)
        assert onto.iri == "http://0.0.0.0:3333/ontology/0001/myonto/v2"
        assert onto.name == "myonto"
        assert onto.label == "My Ontology"
        assert onto.resource_classes == ()
        assert onto.property_classes == ()

    def test_extracts_resource_classes_from_graph(self) -> None:
        json_obj = _make_minimal_ontology_json()
        json_obj["@graph"] = [
            {
                "@id": "myonto:MyResource",
                "knora-api:isResourceClass": True,
                "rdfs:label": [{"@language": "en", "@value": "My Resource"}],
            }
        ]
        onto = create_ontology_from_json(json_obj)
        assert len(onto.resource_classes) == 1
        assert onto.resource_classes[0].name == "MyResource"

    def test_extracts_property_classes_from_graph(self) -> None:
        json_obj = _make_minimal_ontology_json()
        json_obj["@graph"] = [
            {
                "@id": "myonto:hasTitle",
                "knora-api:isResourceProperty": True,
                "rdfs:label": [{"@language": "en", "@value": "Title"}],
            }
        ]
        onto = create_ontology_from_json(json_obj)
        assert len(onto.property_classes) == 1
        assert onto.property_classes[0].name == "hasTitle"

    def test_filters_link_value_properties(self) -> None:
        # Properties with objectType LinkValue should be filtered out
        json_obj = _make_minimal_ontology_json()
        json_obj["@graph"] = [
            {
                "@id": "myonto:hasLinkValue",
                "knora-api:isResourceProperty": True,
                "knora-api:objectType": {"@id": "knora-api:LinkValue"},
            },
            {
                "@id": "myonto:hasTitle",
                "knora-api:isResourceProperty": True,
            },
        ]
        onto = create_ontology_from_json(json_obj)
        # Only hasTitle should be included
        assert len(onto.property_classes) == 1
        assert onto.property_classes[0].name == "hasTitle"


class TestCreateAllOntologiesFromJson:
    """Tests for the create_all_ontologies_from_json factory function."""

    def test_single_ontology_without_graph(self) -> None:
        json_obj = {
            "@context": {
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "owl": "http://www.w3.org/2002/07/owl#",
                "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
            },
            "@type": "owl:Ontology",
            "@id": "http://0.0.0.0:3333/ontology/0001/myonto/v2",
            "rdfs:label": "My Ontology",
            "knora-api:attachedToProject": {"@id": "http://rdfh.ch/projects/0001"},
        }
        ontos = create_all_ontologies_from_json(json_obj)
        assert len(ontos) == 1
        assert ontos[0].name == "myonto"

    def test_multiple_ontologies_in_graph(self) -> None:
        json_obj = {
            "@context": {
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "owl": "http://www.w3.org/2002/07/owl#",
                "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
            },
            "@graph": [
                {
                    "@type": "owl:Ontology",
                    "@id": "http://0.0.0.0:3333/ontology/0001/onto1/v2",
                    "rdfs:label": "Ontology 1",
                    "knora-api:attachedToProject": {"@id": "http://rdfh.ch/projects/0001"},
                },
                {
                    "@type": "owl:Ontology",
                    "@id": "http://0.0.0.0:3333/ontology/0001/onto2/v2",
                    "rdfs:label": "Ontology 2",
                    "knora-api:attachedToProject": {"@id": "http://rdfh.ch/projects/0001"},
                },
            ],
        }
        ontos = create_all_ontologies_from_json(json_obj)
        assert len(ontos) == 2
        names = {o.name for o in ontos}
        assert names == {"onto1", "onto2"}

    def test_filters_non_ontology_types(self) -> None:
        # Only owl:Ontology types should be included
        json_obj = {
            "@context": {
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "owl": "http://www.w3.org/2002/07/owl#",
                "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
            },
            "@graph": [
                {
                    "@type": "owl:Ontology",
                    "@id": "http://0.0.0.0:3333/ontology/0001/myonto/v2",
                    "rdfs:label": "My Ontology",
                    "knora-api:attachedToProject": {"@id": "http://rdfh.ch/projects/0001"},
                },
                {
                    "@type": "owl:Class",
                    "@id": "http://example.org/SomeClass",
                },
            ],
        }
        ontos = create_all_ontologies_from_json(json_obj)
        assert len(ontos) == 1
