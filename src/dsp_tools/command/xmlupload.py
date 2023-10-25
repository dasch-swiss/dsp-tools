"""
This module handles the import of XML data into the DSP platform.
"""
from __future__ import annotations

from pathlib import Path

from lxml import etree

from dsp_tools.command.xml_upload.service.upload_service import UploadService
from dsp_tools.command.xml_upload.service.upload_service_live import UploadServiceLive
from dsp_tools.command.xml_upload.upload_api_client.api_client_live import DspUploadRepoLive
from dsp_tools.command.xml_upload.xml_parser.xml_parser import XmlParser
from dsp_tools.command.xml_upload.xml_parser.xml_parser_live import XmlParserLive
from dsp_tools.models.sipi import Sipi
from dsp_tools.utils.create_logger import get_logger
from dsp_tools.utils.shared import login
from dsp_tools.utils.xmlupload.upload_config import Credentials, UploadConfig
from dsp_tools.utils.xmlupload.write_diagnostic_info import write_id2iri_mapping

logger = get_logger(__name__)


def xmlupload(
    input_file: Path,
    credentials: Credentials,
    imgdir: str,
    config: UploadConfig = UploadConfig(),
) -> bool:
    """
    This function reads an XML file and imports the data described in it onto the DSP server.

    Args:
        input_file: path to the XML file
        credentials: the credentials to use for logging in
        imgdir: the image directory
        config: the upload configuration

    Raises:
        BaseError: in case of permanent network or software failure
        UserError: in case of permanent network or software failure, or if the XML file is invalid

    Returns:
        True if all resources could be uploaded without errors; False if one of the resources could not be
        uploaded because there is an error in it
    """
    parser = XmlParserLive.from_file(input_file, imgdir)
    if not parser:
        return False
    config = config.with_server_info(shortcode=parser.shortcode, onto_name=parser.default_ontology)
    return _upload(parser, config, credentials)


def xmlupload_without_image_processing(
    root: etree._Element,
    config: UploadConfig,
    credentials: Credentials,
) -> bool:
    parser = XmlParserLive.make(root)
    if not parser:
        return False
    return _upload(parser, config, credentials)


def _upload(parser: XmlParser, config: UploadConfig, credentials: Credentials) -> bool:
    resources = parser.get_resources()
    # XXX: remove circular references
    connection = login(server=config.server, credentials=credentials, dump=config.dump)
    sipi_connection = Sipi(config.sipi, connection.get_token())
    repo = DspUploadRepoLive(connection, sipi_connection)
    upload_service: UploadService = UploadServiceLive(repo, config)

    upload_result = upload_service.upload_resources(resources)

    write_id2iri_mapping(upload_result.id_to_iri_mapping, config.input_file_name, config.timestamp_str)
    success = not upload_result.not_uploaded_resources
    if success:
        print("All resources have successfully been uploaded.")
        logger.info("All resources have successfully been uploaded.")
    else:
        print(f"\nWARNING: Could not upload the following resources: {upload_result.not_uploaded_resources}\n")
        logger.warning(f"Could not upload the following resources: {upload_result.not_uploaded_resources}")
    return success
