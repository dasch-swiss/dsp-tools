import pytest
from rdflib import Graph
from rdflib import URIRef

from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.make_rdf_graph.make_resource_and_values import create_resource_with_values
from dsp_tools.commands.xmlupload.models.intermediary.resource import IntermediaryResource
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryBoolean
from dsp_tools.commands.xmlupload.models.lookup_models import IRILookups
from dsp_tools.commands.xmlupload.models.lookup_models import JSONLDContext
from dsp_tools.commands.xmlupload.resource_create_client import _make_json


@pytest.fixture
def resource_graph() -> Graph:
    lookups = IRILookups(
        project_iri=URIRef("http://rdfh.ch/9999/project"),
        id_to_iri=IriResolver({"res_one": "http://rdfh.ch/9999/res_one"}),
        jsonld_context=JSONLDContext({}),
    )
    res = IntermediaryResource(
        res_id="resource_id",
        type_iri="http://0.0.0.0:3333/ontology/9999/onto/v2#TestResource",
        label="Resource Label",
        permissions=None,
        values=[IntermediaryBoolean(True, "http://0.0.0.0:3333/ontology/9999/onto/v2#isTrueOrFalse", None, None)],
        file_value=None,
        iiif_uri=None,
        migration_metadata=None,
    )
    return create_resource_with_values(res, None, lookups)


def test_frame_json(resource_graph: Graph) -> None:
    result_json = _make_json(resource_graph)
    expected = {}
    assert result_json == expected
