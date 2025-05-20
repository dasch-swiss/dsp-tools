# mypy: disable-error-code="method-assign,no-untyped-def"

from uuid import uuid4

import pytest
from rdflib import Graph
from rdflib import Namespace
from rdflib import URIRef

from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.make_rdf_graph.jsonld_utils import serialise_jsonld_for_resource
from dsp_tools.commands.xmlupload.make_rdf_graph.jsonld_utils import serialise_jsonld_for_value
from dsp_tools.commands.xmlupload.make_rdf_graph.make_resource_and_values import create_resource_with_values
from dsp_tools.commands.xmlupload.models.lookup_models import IRILookups
from dsp_tools.commands.xmlupload.models.processed.res import ProcessedResource
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedBoolean
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedLink
from dsp_tools.commands.xmlupload.stash.stash_models import LinkValueStashItem
from dsp_tools.commands.xmlupload.stash.upload_stashed_resptr_props import _make_link_value_create_graph

ONTO_STR = "http://0.0.0.0:3333/ontology/9999/onto/v2#"

ONTO = Namespace(ONTO_STR)
RES_IRI_STR = "http://rdfh.ch/9999/res_one"
TARGET_IRI_STR = "http://rdfh.ch/9999/target_resource"
RES_IRI = URIRef(RES_IRI_STR)
RES_TYPE = ONTO.Resource


@pytest.fixture
def resource_graph() -> Graph:
    lookups = IRILookups(
        project_iri=URIRef("http://rdfh.ch/9999/project"),
        id_to_iri=IriResolver({"res_one": "http://rdfh.ch/9999/res_one"}),
    )
    res = ProcessedResource(
        res_id="resource_id",
        type_iri="http://0.0.0.0:3333/ontology/9999/onto/v2#TestResource",
        label="Special Characters: äöüéèà",
        permissions=None,
        values=[ProcessedBoolean(True, "http://0.0.0.0:3333/ontology/9999/onto/v2#isTrueOrFalse", None, None)],
        file_value=None,
        iiif_uri=None,
        migration_metadata=None,
    )
    return create_resource_with_values(res, None, lookups)


def test_serialise_jsonld_for_resource(resource_graph: Graph) -> None:
    result_json = serialise_jsonld_for_resource(resource_graph)
    expected = {
        "@type": "http://0.0.0.0:3333/ontology/9999/onto/v2#TestResource",
        "http://0.0.0.0:3333/ontology/9999/onto/v2#isTrueOrFalse": {
            "@type": "http://api.knora.org/ontology/knora-api/v2#BooleanValue",
            "http://api.knora.org/ontology/knora-api/v2#booleanValueAsBoolean": {
                "@type": "http://www.w3.org/2001/XMLSchema#boolean",
                "@value": True,
            },
        },
        "http://api.knora.org/ontology/knora-api/v2#attachedToProject": {"@id": "http://rdfh.ch/9999/project"},
        "http://www.w3.org/2000/01/rdf-schema#label": {
            "@type": "http://www.w3.org/2001/XMLSchema#string",
            "@value": "Special Characters: äöüéèà",
        },
    }
    assert result_json == expected


def test_serialise_jsonld_for_value():
    link_stash = LinkValueStashItem(
        res_id=RES_IRI_STR,
        res_type=RES_TYPE,
        value=ProcessedLink("target_resource_id", ONTO.hasLink, None, None, str(uuid4())),
    )
    graph = _make_link_value_create_graph(link_stash, RES_IRI_STR, TARGET_IRI_STR)
    expected = {
        "@id": "http://rdfh.ch/9999/res_one",
        "@type": "http://0.0.0.0:3333/ontology/9999/onto/v2#Resource",
        "http://0.0.0.0:3333/ontology/9999/onto/v2#hasLinkValue": {
            "@type": "http://api.knora.org/ontology/knora-api/v2#LinkValue",
            "http://api.knora.org/ontology/knora-api/v2#linkValueHasTargetIri": {
                "@id": "http://rdfh.ch/9999/target_resource"
            },
        },
    }
    result = serialise_jsonld_for_value(graph, RES_IRI_STR)
    assert result == expected
