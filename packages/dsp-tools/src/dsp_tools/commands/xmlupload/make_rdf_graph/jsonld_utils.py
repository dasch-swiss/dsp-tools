import json
from typing import Any

from pyld import jsonld
from rdflib import Graph


def serialise_jsonld_for_resource(rdf_graph: Graph) -> dict[str, Any]:
    json_graph = _serialise_json(rdf_graph)
    return _frame_graph_for_resource(json_graph)


def _frame_graph_for_resource(serialised_json: list[dict[str, Any]]) -> dict[str, Any]:
    """
    The result of the serialisation is a list.
    Although the API would accept that, our connection has the payload typed as `dict[str, Any]`.
    If the typing of the connection was changed or a different class was used, this step can be removed.

    Args:
        serialised_json: graph serialised as json-ld

    Returns:
        graph in a specific json-ld format
    """
    json_frame: dict[str, Any] = {"http://api.knora.org/ontology/knora-api/v2#attachedToProject": {}}
    framed: dict[str, Any] = jsonld.frame(serialised_json, json_frame)
    return framed


def serialise_jsonld_for_value(rdf_graph: Graph, resource_iri_str: str) -> dict[str, Any]:
    json_graph = _serialise_json(rdf_graph)
    return _frame_graph_for_value(json_graph, resource_iri_str)


def _frame_graph_for_value(serialised_json: list[dict[str, Any]], resource_iri_str: str) -> dict[str, Any]:
    json_frame = {"@id": resource_iri_str}
    framed: dict[str, Any] = jsonld.frame(serialised_json, json_frame)
    return framed


def _serialise_json(rdf_graph: Graph) -> list[dict[str, Any]]:
    graph_bytes = rdf_graph.serialize(format="json-ld", encoding="utf-8")
    json_graph: list[dict[str, Any]] = json.loads(graph_bytes)
    return json_graph
