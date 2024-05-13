import json
from dataclasses import dataclass
from typing import Any

from pyld import jsonld
from rdflib import Graph
from rdflib import URIRef


@dataclass(frozen=True)
class JSONFramer:
    """
    This class is used to frame the json-ld graph to make it conform to DSP-API requirements.
    """

    rdf_graph: Graph
    type: URIRef

    def frame(self) -> dict[str, Any]:
        json_graph = self._make_json()
        return self._frame_json(json_graph)

    def _make_json(self) -> list[dict[str, Any]]:
        graph_str = self.rdf_graph.serialize(format="json-ld", encoding="utf-8")
        return json.loads(graph_str)

    def _frame_json(self, json_graph: list[dict[str, Any]]) -> dict[str, Any]:
        json_frame = {
            "@type": str(self.type),
            "contains": {"@type": ""},
        }
        return jsonld.frame(json_graph, json_frame)
