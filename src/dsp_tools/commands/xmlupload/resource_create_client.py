import json
from dataclasses import dataclass
from typing import Any
from typing import cast

from pyld import jsonld
from rdflib import Graph

from dsp_tools.utils.connection import Connection


@dataclass(frozen=True)
class ResourceCreateClient:
    """client class that creates resources on a DSP server."""

    con: Connection
    media_previously_ingested: bool = False

    def create_resource(
        self,
        graph: Graph,
        resource_has_bitstream: bool,
    ) -> str:
        """Creates a resource on the DSP server, and returns its IRI"""
        res_dict = _make_json(graph)
        headers = {"X-Asset-Ingested": "true"} if resource_has_bitstream else None
        res = self.con.post(route="/v2/resources", data=res_dict, headers=headers)
        return cast(str, res["@id"])


def _make_json(rdf_graph: Graph) -> dict[str, Any]:
    graph_bytes = rdf_graph.serialize(format="json-ld", encoding="utf-8")
    json_graph: list[dict[str, Any]] = json.loads(graph_bytes)
    return _frame_graph(json_graph)


def _frame_graph(serialised_json: list[dict[str, Any]]) -> dict[str, Any]:
    json_frame: dict[str, Any] = {"http://api.knora.org/ontology/knora-api/v2#attachedToProject": {}}
    framed: dict[str, Any] = jsonld.frame(serialised_json, json_frame)
    return framed
