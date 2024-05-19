from __future__ import annotations

from pathlib import Path

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.xmlupload.list_client import ListClientLive
from dsp_tools.commands.xmlupload.models.ingest import BulkIngestedAssetClient
from dsp_tools.commands.xmlupload.models.upload_state import UploadState
from dsp_tools.commands.xmlupload.ontology_client import OntologyClientLive
from dsp_tools.commands.xmlupload.project_client import ProjectClientLive
from dsp_tools.commands.xmlupload.read_validate_xml_file import validate_and_parse_xml_file_preprocessing_done
from dsp_tools.commands.xmlupload.upload_config import UploadConfig
from dsp_tools.commands.xmlupload.xmlupload import UploadClients
from dsp_tools.commands.xmlupload.xmlupload import execute_upload
from dsp_tools.commands.xmlupload.xmlupload import prepare_upload
from dsp_tools.utils.connection import Connection
from dsp_tools.utils.connection_live import ConnectionLive


def ingest_xmlupload(
    xml_file: Path,
    creds: ServerCredentials,
    interrupt_after: int | None = None,
) -> bool:
    """
    This function reads an XML file
    and imports the data described in it onto the DSP server,
    using the ingest XML upload method.
    Before using this function,
    the multimedia files must be ingested on the DSP server.
    A mapping file with the internal IDs of the multimedia files must also be provided.

    Args:
        xml_file: path to XML file containing the resources
        creds: credentials to access the DSP server
        interrupt_after: if set, the upload will be interrupted after this number of resources

    Returns:
        True if all resources could be uploaded without errors; False if one of the resources could not be
        uploaded because there is an error in it

    Raises:
        InputError: if any media was not uploaded or uploaded media was not referenced.
    """
    default_ontology, root, shortcode = validate_and_parse_xml_file_preprocessing_done(xml_file)

    con = ConnectionLive(creds.server)
    con.login(creds.user, creds.password)

    config = UploadConfig(
        media_previously_uploaded=True,
        interrupt_after=interrupt_after,
    ).with_server_info(
        server=creds.server,
        shortcode=shortcode,
    )

    ontology_client = OntologyClientLive(con=con, shortcode=shortcode, default_ontology=default_ontology)
    resources, permissions_lookup, stash = prepare_upload(root, ontology_client)

    clients = _get_live_clients(con, config)
    state = UploadState(resources, stash, config, permissions_lookup)

    return execute_upload(clients, state)


def _get_live_clients(con: Connection, config: UploadConfig) -> UploadClients:
    ingest_client = BulkIngestedAssetClient()
    project_client = ProjectClientLive(con, config.shortcode)
    list_client = ListClientLive(con, project_client.get_project_iri())
    return UploadClients(ingest_client, project_client, list_client)
