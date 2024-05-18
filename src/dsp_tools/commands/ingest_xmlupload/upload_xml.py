from __future__ import annotations

from pathlib import Path

from loguru import logger
from lxml import etree

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.ingest_xmlupload.apply_ingest_id import get_mapping_dict_from_file
from dsp_tools.commands.ingest_xmlupload.apply_ingest_id import replace_filepath_with_internal_filename
from dsp_tools.commands.xmlupload.list_client import ListClientLive
from dsp_tools.commands.xmlupload.models.ingest import BulkIngestedAssetClient
from dsp_tools.commands.xmlupload.ontology_client import OntologyClientLive
from dsp_tools.commands.xmlupload.project_client import ProjectClientLive
from dsp_tools.commands.xmlupload.upload_config import UploadConfig
from dsp_tools.commands.xmlupload.xmlupload import UploadClients
from dsp_tools.commands.xmlupload.xmlupload import execute_upload
from dsp_tools.commands.xmlupload.xmlupload import prepare_upload
from dsp_tools.models.exceptions import InputError
from dsp_tools.utils.connection import Connection
from dsp_tools.utils.connection_live import ConnectionLive
from dsp_tools.utils.xml_utils import remove_comments_from_element_tree


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

    Raises:
        InputError: if any media was not uploaded or uploaded media was not referenced.
    """
    xml_tree_orig = etree.parse(xml_file)
    xml_tree_orig = remove_comments_from_element_tree(xml_tree_orig)

    root = xml_tree_orig.getroot()
    shortcode = root.attrib["shortcode"]
    default_ontology = root.attrib["default-ontology"]
    orig_path_2_id_filename = get_mapping_dict_from_file(shortcode)
    xml_tree_replaced, ingest_info = replace_filepath_with_internal_filename(
        xml_tree=xml_tree_orig,
        orig_path_2_id_filename=orig_path_2_id_filename,
    )
    if ok := ingest_info.ok_msg():
        print(ok)
        logger.info(ok)
    else:
        err_msg = ingest_info.execute_error_protocol()
        raise InputError(err_msg)

    con = ConnectionLive(creds.server)
    con.login(creds.user, creds.password)
    config = UploadConfig(media_previously_uploaded=True, interrupt_after=interrupt_after)
    config = config.with_server_info(server=creds.server, shortcode=shortcode)

    ontology_client = OntologyClientLive(con=con, shortcode=shortcode, default_ontology=default_ontology)
    resources, permissions_lookup, stash = prepare_upload(root, ontology_client)

    clients = _get_live_clients(con, config)

    return execute_upload(config, clients, resources, permissions_lookup, stash)


def _get_live_clients(con: Connection, config: UploadConfig) -> UploadClients:
    ingest_client = BulkIngestedAssetClient()
    project_client = ProjectClientLive(con, config.shortcode)
    list_client = ListClientLive(con, project_client.get_project_iri())
    return UploadClients(ingest_client, project_client, list_client)
