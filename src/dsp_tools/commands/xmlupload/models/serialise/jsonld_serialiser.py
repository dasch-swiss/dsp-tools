import json
from typing import Any

from pyld import jsonld
from rdflib import Graph


def serialise_property(rdf_graph: Graph, prop_name: str) -> dict[str, Any]:
    """
    This function makes the serialised json-ld conform to the format expected by the DSP-API.
    It returns the information about the property and its value(s).

    Args:
        rdf_graph: rdf graph
        prop_name: property name

    Returns:
        A json-ld
    """
    json_graph = _make_json(rdf_graph)
    return _frame_property(json_graph, prop_name)


def _frame_property(serialised_json: list[dict[str, Any]], prop_name: str) -> dict[str, Any]:
    json_frame: dict[str, Any] = {
        str(prop_name): {},
    }
    framed: dict[str, Any] = jsonld.frame(serialised_json, json_frame)
    return framed


def _make_json(rdf_graph: Graph) -> list[dict[str, Any]]:
    graph_bytes = rdf_graph.serialize(format="json-ld", encoding="utf-8")
    json_graph: list[dict[str, Any]] = json.loads(graph_bytes)
    return json_graph
