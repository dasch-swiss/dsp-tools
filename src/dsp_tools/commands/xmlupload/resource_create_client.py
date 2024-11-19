from dataclasses import dataclass
from typing import cast

from loguru import logger
from rdflib import Namespace

from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import BitstreamInfo
from dsp_tools.commands.xmlupload.models.serialise.serialise_resource import SerialiseResource
from dsp_tools.utils.connection import Connection

KNORA_API = Namespace("http://api.knora.org/ontology/knora-api/v2#")


@dataclass(frozen=True)
class ResourceCreateClient:
    """client class that creates resources on a DSP server."""

    con: Connection
    project_iri: str
    media_previously_ingested: bool = False

    def create_resource(
        self,
        resource: SerialiseResource,
        bitstream_information: BitstreamInfo | None,
    ) -> str:
        """Creates a resource on the DSP server, and returns its IRI"""
        logger.info(f"Attempting to create resource {resource.res_id} (label: {resource.label})...")
        res_dict = resource.serialise()
        headers = {"X-Asset-Ingested": "true"} if bitstream_information else None
        res = self.con.post(route="/v2/resources", data=res_dict, headers=headers)
        return cast(str, res["@id"])
