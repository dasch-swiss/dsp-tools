import json
from typing import Any

from pyld import jsonld
from rdflib import Graph
from rdflib import URIRef


def frame_value(rdf_graph: Graph, type_: URIRef) -> dict[str, Any]:
    """
    This function makes the serialised json-ld conform to the format expected by the DSP-API.
    It returns the information about the property and its value(s).

    Args:
        rdf_graph: rdf graph, the resource type must be part of the graph
        type_: type of the resource

    Returns:
        A json-ld
    """
    json_graph = _make_json(rdf_graph)
    json_frame = {
        str(type_): {},
    }
    framed: dict[str, Any] = jsonld.frame(json_graph, json_frame)
    return framed


def _make_json(rdf_graph: Graph) -> list[dict[str, Any]]:
    graph_bytes = rdf_graph.serialize(format="json-ld", encoding="utf-8")
    json_graph: list[dict[str, Any]] = json.loads(graph_bytes)
    return json_graph
