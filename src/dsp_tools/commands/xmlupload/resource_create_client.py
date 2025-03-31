from dataclasses import dataclass
from typing import cast

from rdflib import Graph

from dsp_tools.clients.connection import Connection
from dsp_tools.commands.xmlupload.make_rdf_graph.jsonld_utils import serialise_jsonld_for_resource


@dataclass(frozen=True)
class ResourceCreateClient:
    """client class that creates resources on a DSP server."""

    con: Connection

    def create_resource(
        self,
        graph: Graph,
        resource_has_bitstream: bool,
    ) -> str:
        """Creates a resource on the DSP server, and returns its IRI"""
        res_dict = serialise_jsonld_for_resource(graph)
        headers = {"X-Asset-Ingested": "true"} if resource_has_bitstream else None
        res = self.con.post(route="/v2/resources", data=res_dict, headers=headers)
        return cast(str, res["@id"])
