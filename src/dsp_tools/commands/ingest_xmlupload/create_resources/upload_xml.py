from __future__ import annotations

from pathlib import Path

from loguru import logger
from lxml import etree

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.ingest_xmlupload.create_resources.apply_ingest_id import get_mapping_dict_from_file
from dsp_tools.commands.ingest_xmlupload.create_resources.apply_ingest_id import replace_filepath_with_internal_filename
from dsp_tools.commands.xmlupload.list_client import ListClientLive
from dsp_tools.commands.xmlupload.models.ingest import BulkIngestedAssetClient
from dsp_tools.commands.xmlupload.models.upload_clients import UploadClients
from dsp_tools.commands.xmlupload.models.upload_state import UploadState
from dsp_tools.commands.xmlupload.ontology_client import OntologyClientLive
from dsp_tools.commands.xmlupload.project_client import ProjectClientLive
from dsp_tools.commands.xmlupload.read_validate_xml_file import validate_and_parse
from dsp_tools.commands.xmlupload.upload_config import UploadConfig
from dsp_tools.commands.xmlupload.xmlupload import execute_upload
from dsp_tools.commands.xmlupload.xmlupload import prepare_upload
from dsp_tools.models.exceptions import InputError
from dsp_tools.utils.authentication_client_live import AuthenticationClientLive
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
    default_ontology, root, shortcode = _parse_xml_and_replace_filepaths(xml_file)

    auth = AuthenticationClientLive(server=creds.server, email=creds.user, password=creds.password)
    con = ConnectionLive(creds.server, auth)

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


def _parse_xml_and_replace_filepaths(xml_file: Path) -> tuple[str, etree._Element, str]:
    """
    Validate and parse an upload XML file.
    The bulk-ingest must already have taken place, and the mapping CSV must be in the CWD.

    Args:
        xml_file: file that will be parsed

    Returns:
        The ontology name, the parsed XML file and the shortcode of the project

    Raises:
        InputError: if replacing file paths with internal asset IDs failed
    """
    root, shortcode, default_ontology = validate_and_parse(xml_file)

    logger.info(f"Validated and parsed the XML. {shortcode=:} and {default_ontology=:}")

    orig_path_2_asset_id = get_mapping_dict_from_file(shortcode)
    root, ingest_info = replace_filepath_with_internal_filename(root, orig_path_2_asset_id)
    if ok := ingest_info.ok_msg():
        print(ok)
        logger.info(ok)
    else:
        err_msg = ingest_info.execute_error_protocol()
        raise InputError(err_msg)
    return default_ontology, root, shortcode


def _get_live_clients(con: Connection, config: UploadConfig) -> UploadClients:
    ingest_client = BulkIngestedAssetClient()
    project_client = ProjectClientLive(con, config.shortcode)
    list_client = ListClientLive(con, project_client.get_project_iri())
    return UploadClients(ingest_client, project_client, list_client)
