import json
from typing import Any

from rdflib import Graph


def serialise_json(rdf_graph: Graph) -> list[dict[str, Any]]:
    graph_bytes = rdf_graph.serialize(format="json-ld", encoding="utf-8")
    json_graph: list[dict[str, Any]] = json.loads(graph_bytes)
    return json_graph
