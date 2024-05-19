from __future__ import annotations

from pathlib import Path

from loguru import logger
from lxml import etree

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.ingest_xmlupload.apply_ingest_id import get_mapping_dict_from_file
from dsp_tools.commands.ingest_xmlupload.apply_ingest_id import replace_filepath_with_internal_filename
from dsp_tools.commands.xmlupload.list_client import ListClientLive
from dsp_tools.commands.xmlupload.models.ingest import BulkIngestedAssetClient
from dsp_tools.commands.xmlupload.models.upload_state import UploadState
from dsp_tools.commands.xmlupload.ontology_client import OntologyClientLive
from dsp_tools.commands.xmlupload.project_client import ProjectClientLive
from dsp_tools.commands.xmlupload.read_validate_xml_file import _check_if_link_targets_exist
from dsp_tools.commands.xmlupload.upload_config import UploadConfig
from dsp_tools.commands.xmlupload.xmlupload import UploadClients
from dsp_tools.commands.xmlupload.xmlupload import execute_upload
from dsp_tools.commands.xmlupload.xmlupload import prepare_upload
from dsp_tools.models.exceptions import InputError
from dsp_tools.utils.connection import Connection
from dsp_tools.utils.connection_live import ConnectionLive
from dsp_tools.utils.xml_utils import parse_xml_file
from dsp_tools.utils.xml_utils import remove_comments_from_element_tree
from dsp_tools.utils.xml_utils import remove_qnames_and_transform_special_tags
from dsp_tools.utils.xml_validation import validate_xml


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
    root, shortcode, default_ontology = _parse_xml_for_ingest_upload(xml_file)

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


def _parse_xml_for_ingest_upload(xml_file: Path) -> tuple[etree._Element, str, str]:
    root_orig = parse_xml_file(xml_file)
    root_orig = remove_comments_from_element_tree(root_orig)

    validate_xml(root_orig)
    root = remove_qnames_and_transform_special_tags(root_orig)
    _check_if_link_targets_exist(root)
    shortcode = root.attrib["shortcode"]
    default_ontology = root.attrib["default-ontology"]

    logger.info(f"Validated and parsed the XML. {shortcode=:} and {default_ontology=:}")

    orig_path_2_id_filename = get_mapping_dict_from_file(shortcode)
    root, ingest_info = replace_filepath_with_internal_filename(
        xml_tree=root,
        orig_path_2_id_filename=orig_path_2_id_filename,
    )
    if ok := ingest_info.ok_msg():
        print(ok)
        logger.info(ok)
    else:
        err_msg = ingest_info.execute_error_protocol()
        raise InputError(err_msg)
    return root, shortcode, default_ontology


def _get_live_clients(con: Connection, config: UploadConfig) -> UploadClients:
    ingest_client = BulkIngestedAssetClient()
    project_client = ProjectClientLive(con, config.shortcode)
    list_client = ListClientLive(con, project_client.get_project_iri())
    return UploadClients(ingest_client, project_client, list_client)
