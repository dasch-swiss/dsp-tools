from dataclasses import dataclass
from typing import Any
from typing import cast

from dsp_tools.utils.connection import Connection


@dataclass(frozen=True)
class ResourceCreateClient:
    """client class that creates resources on a DSP server."""

    con: Connection
    project_iri: str
    media_previously_ingested: bool = False

    def create_resource(
        self,
        res_dict: dict[str, Any],
        resource_has_bitstream: bool,
    ) -> str:
        """Creates a resource on the DSP server, and returns its IRI"""
        headers = {"X-Asset-Ingested": "true"} if resource_has_bitstream else None
        res = self.con.post(route="/v2/resources", data=res_dict, headers=headers)
        return cast(str, res["@id"])
