import json
from dataclasses import dataclass
from typing import Any
from typing import cast

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
        res_dict = self._make_json(graph)
        headers = {"X-Asset-Ingested": "true"} if resource_has_bitstream else None
        res = self.con.post(route="/v2/resources", data=res_dict, headers=headers)
        return cast(str, res["@id"])

    def _make_json(self, rdf_graph: Graph) -> list[dict[str, Any]]:
        graph_bytes = rdf_graph.serialize(format="json-ld", encoding="utf-8")
        json_graph: list[dict[str, Any]] = json.loads(graph_bytes)
        return json_graph
