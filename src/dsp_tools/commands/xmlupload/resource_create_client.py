from dataclasses import dataclass
from typing import cast

from loguru import logger
from rdflib import Namespace

from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import BitstreamInfo
from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import XMLResource
from dsp_tools.commands.xmlupload.models.namespace_context import JSONLDContext
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.utils.connection import Connection

KNORA_API = Namespace("http://api.knora.org/ontology/knora-api/v2#")


@dataclass(frozen=True)
class ResourceCreateClient:
    """client class that creates resources on a DSP server."""

    con: Connection
    project_iri: str
    iri_resolver: IriResolver
    permissions_lookup: dict[str, Permissions]
    listnode_lookup: dict[str, str]
    jsonld_context: JSONLDContext
    namespaces: dict[str, Namespace]
    media_previously_ingested: bool = False

    def create_resource(
        self,
        resource: XMLResource,
        bitstream_information: BitstreamInfo | None,
    ) -> str:
        """Creates a resource on the DSP server, and returns its IRI"""
        logger.info(
            f"Attempting to create resource {resource.res_id} (label: {resource.label}, iri: {resource.iri})..."
        )
        resource_dict = self._make_resource_with_values(resource, bitstream_information)
        headers = {"X-Asset-Ingested": "true"} if bitstream_information else None
        res = self.con.post(route="/v2/resources", data=resource_dict, headers=headers)
        return cast(str, res["@id"])
