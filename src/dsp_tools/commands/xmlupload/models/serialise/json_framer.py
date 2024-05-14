import json
from typing import Any
from typing import cast

from pyld import jsonld
from rdflib import Graph
from rdflib import URIRef


def frame_json(rdf_graph: Graph, type_: URIRef) -> dict[str, Any]:
    """
    This function makes the serialised json-ld conform to the format expected by the DSP-API.

    Args:
        rdf_graph: graph, this can consist of RESOURCES OR ONLY PROPS??? # TODO:
        type_: type of the resource / property # TODO

    Returns:
        A json-ld
    """
    json_graph = _make_json(rdf_graph)
    json_frame = {
        "@type": str(type_),
        "contains": {"@type": ""},
    }
    framed = jsonld.frame(json_graph, json_frame)
    return json.loads(framed)


def _make_json(rdf_graph: Graph) -> list[dict[str, Any]]:
    graph_str = rdf_graph.serialize(format="json-ld", encoding="utf-8")
    serialised = cast(list[dict[str, Any]], graph_str)
    return serialised
