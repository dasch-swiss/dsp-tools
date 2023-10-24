"""
This module handles the import of XML data into the DSP platform.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from dsp_tools.models.sipi import Sipi
from dsp_tools.utils.create_logger import get_logger
from dsp_tools.utils.shared import login
from dsp_tools.utils.xmlupload.upload_config import UploadConfig
from dsp_tools.utils.xmlupload.write_diagnostic_info import write_id2iri_mapping
from dsp_tools.xml_upload.domain.service.upload_service import UploadService
from dsp_tools.xml_upload.domain.service.upload_service_live import UploadServiceLive
from dsp_tools.xml_upload.interface.xml_parser import XmlParserLive
from dsp_tools.xml_upload.repo.dsp_upload_repo_live import DspUploadRepoLive

logger = get_logger(__name__)


def xmlupload(
    input_file: Path,
    server: str,
    user: str,
    password: str,
    imgdir: str,
    sipi: str,
    config: UploadConfig = UploadConfig(),
) -> bool:
    """
    This function reads an XML file and imports the data described in it onto the DSP server.

    Args:
        input_file: path to the XML file
        server: the DSP server where the data should be imported
        user: the user (e-mail) with which the data should be imported
        password: the password of the user with which the data should be imported
        imgdir: the image directory
        sipi: the sipi instance to be used
        config: the upload configuration

    Raises:
        BaseError: in case of permanent network or software failure
        UserError: in case of permanent network or software failure, or if the XML file is invalid

    Returns:
        True if all resources could be uploaded without errors; False if one of the resources could not be
        uploaded because there is an error in it
    """
    parser = XmlParserLive.from_file(input_file)
    if not parser:
        return False
    resources = parser.get_resources()
    # XXX: remove circular references

    config = config.with_server_info(
        server=server,
        shortcode=resources.shortcode,
        onto_name=resources.default_ontology,
    )
    connection = login(server=server, user=user, password=password, dump=config.dump)
    sipi_connection = Sipi(sipi, connection.get_token())
    repo = DspUploadRepoLive(connection, sipi_connection)
    upload_service: UploadService = UploadServiceLive(repo, config)

    upload_result = upload_service.upload_resources(resources)

    write_id2iri_mapping(upload_result.id_to_iri_mapping, input_file, config.timestamp_str)
    success = not upload_result.not_uploaded_resources
    if success:
        print("All resources have successfully been uploaded.")
        logger.info("All resources have successfully been uploaded.")
    else:
        print(f"\nWARNING: Could not upload the following resources: {upload_result.not_uploaded_resources}\n")
        logger.warning(f"Could not upload the following resources: {upload_result.not_uploaded_resources}")
    return success
