from __future__ import annotations

from pathlib import Path

from loguru import logger
from lxml import etree

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.cli.args import ValidateDataConfig
from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.clients.connection import Connection
from dsp_tools.clients.connection_live import ConnectionLive
from dsp_tools.clients.legal_info_client_live import LegalInfoClientLive
from dsp_tools.commands.ingest_xmlupload.create_resources.apply_ingest_id import get_mapping_dict_from_file
from dsp_tools.commands.ingest_xmlupload.create_resources.apply_ingest_id import replace_filepath_with_internal_filename
from dsp_tools.commands.validate_data.validate_data import validate_parsed_resources
from dsp_tools.commands.xmlupload.models.ingest import BulkIngestedAssetClient
from dsp_tools.commands.xmlupload.models.upload_clients import UploadClients
from dsp_tools.commands.xmlupload.models.upload_state import UploadState
from dsp_tools.commands.xmlupload.prepare_xml_input.get_processed_resources import get_processed_resources
from dsp_tools.commands.xmlupload.prepare_xml_input.list_client import ListClientLive
from dsp_tools.commands.xmlupload.prepare_xml_input.prepare_xml_input import get_parsed_resources_and_mappers
from dsp_tools.commands.xmlupload.prepare_xml_input.prepare_xml_input import get_stash_and_upload_order
from dsp_tools.commands.xmlupload.prepare_xml_input.read_validate_xml_file import validate_iiif_uris
from dsp_tools.commands.xmlupload.project_client import ProjectClientLive
from dsp_tools.commands.xmlupload.upload_config import UploadConfig
from dsp_tools.commands.xmlupload.xmlupload import enable_unknown_license_if_any_are_missing
from dsp_tools.commands.xmlupload.xmlupload import execute_upload
from dsp_tools.error.exceptions import InputError
from dsp_tools.utils.data_formats.uri_util import is_prod_like_server
from dsp_tools.utils.xml_parsing.parse_clean_validate_xml import parse_and_clean_xml_file


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
    root = parse_and_clean_xml_file(xml_file)
    shortcode = root.attrib["shortcode"]
    root = _replace_filepaths_with_internal_filename_from_ingest(root, shortcode)

    auth = AuthenticationClientLive(server=creds.server, email=creds.user, password=creds.password)
    con = ConnectionLive(creds.server, auth)
    config = UploadConfig(
        media_previously_uploaded=True,
        interrupt_after=interrupt_after,
    ).with_server_info(
        server=creds.server,
        shortcode=shortcode,
    )
    clients = _get_live_clients(con, config, auth)

    parsed_resources, lookups = get_parsed_resources_and_mappers(root, clients)

    is_on_prod_like_server = is_prod_like_server(creds.server)
    validation_passed = validate_parsed_resources(
        parsed_resources=parsed_resources,
        authorship_lookup=lookups.authorships,
        permission_ids=list(lookups.permissions.keys()),
        shortcode=shortcode,
        config=ValidateDataConfig(
            xml_file,
            save_graph_dir=None,
            severity=config.validation_severity,
            is_on_prod_server=is_on_prod_like_server,
        ),
        auth=auth,
    )
    if not validation_passed:
        return False

    if not config.skip_iiif_validation:
        validate_iiif_uris(root)

    if not is_on_prod_like_server:
        enable_unknown_license_if_any_are_missing(clients.legal_info_client, parsed_resources)

    processed_resources = get_processed_resources(parsed_resources, lookups, is_on_prod_like_server)

    sorted_resources, stash = get_stash_and_upload_order(processed_resources)

    state = UploadState(
        pending_resources=sorted_resources,
        pending_stash=stash,
        config=config,
    )

    return execute_upload(clients, state)


def _replace_filepaths_with_internal_filename_from_ingest(root: etree._Element, shortcode: str) -> etree._Element:
    orig_path_2_asset_id = get_mapping_dict_from_file(shortcode)
    root, ingest_info = replace_filepath_with_internal_filename(root, orig_path_2_asset_id)
    if ok := ingest_info.ok_msg():
        print(ok)
        logger.info(ok)
    else:
        err_msg = ingest_info.execute_error_protocol()
        raise InputError(err_msg)
    return root


def _get_live_clients(con: Connection, config: UploadConfig, auth: AuthenticationClient) -> UploadClients:
    ingest_client = BulkIngestedAssetClient()
    project_client = ProjectClientLive(con, config.shortcode)
    list_client = ListClientLive(con, project_client.get_project_iri())
    legal_info_client = LegalInfoClientLive(config.server, config.shortcode, auth)
    return UploadClients(ingest_client, project_client, list_client, legal_info_client)
