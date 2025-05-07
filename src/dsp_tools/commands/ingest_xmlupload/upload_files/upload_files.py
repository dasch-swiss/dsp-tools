from pathlib import Path

from loguru import logger
from lxml import etree
from tqdm import tqdm

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.commands.ingest_xmlupload.bulk_ingest_client import BulkIngestClient
from dsp_tools.commands.ingest_xmlupload.upload_files.filechecker import check_files
from dsp_tools.commands.ingest_xmlupload.upload_files.upload_failures import UploadFailure
from dsp_tools.commands.ingest_xmlupload.upload_files.upload_failures import UploadFailures
from dsp_tools.error.exceptions import InputError
from dsp_tools.utils.xml_parsing.parse_clean_validate_xml import parse_and_clean_xml_file
from src.dsp_tools.clients.openapi_ingest import openapi_client


def upload_files(
    xml_file: Path,
    creds: ServerCredentials,
    imgdir: Path = Path.cwd(),
) -> bool:
    """
    Upload all files referenced in an XML file to the ingest server.
    This involves no processing/ingesting of the files, just uploading them.

    Args:
        xml_file: XML file containing the resources and the references to the files to upload
        creds: credentials to connect to the ingest server
        imgdir: the bitstreams in the XML file are relative to this directory

    Returns:
        success status
    """
    root = parse_and_clean_xml_file(xml_file)
    shortcode = root.attrib["shortcode"]
    paths = _get_validated_paths(root)
    print(f"Found {len(paths)} files to upload onto server {creds.dsp_ingest_url}.")
    logger.info(f"Found {len(paths)} files to upload onto server {creds.dsp_ingest_url}.")

    auth = AuthenticationClientLive(creds.server, creds.user, creds.password)
    configuration = openapi_client.Configuration(
        host=creds.dsp_ingest_url,
        access_token=auth.get_token(),
    )
    api_client = openapi_client.ApiClient(configuration)
    bulk_ingest_api = openapi_client.BulkIngestApi(api_client)
    ingest_client = BulkIngestClient(bulk_ingest_api, shortcode, imgdir)

    failures: list[UploadFailure] = []
    progress_bar = tqdm(paths, desc="Uploading files", unit="file(s)", dynamic_ncols=True)
    for path in progress_bar:
        if res := ingest_client.upload_file(path):
            failures.append(res)
            progress_bar.set_description(f"Uploading files (failed: {len(failures)})")
    if failures:
        aggregated_failures = UploadFailures(failures, len(paths), shortcode, creds.dsp_ingest_url)
        msg = aggregated_failures.execute_error_protocol()
        logger.error(msg)
        print(msg)
        return False
    else:
        msg = f"Uploaded all {len(paths)} files onto server {creds.dsp_ingest_url}."
        logger.info(msg)
        print(msg)
        return True


def _get_validated_paths(root: etree._Element) -> set[Path]:
    paths = {Path(x.text.strip()) for x in root.xpath("//bitstream")}
    if problems := check_files(paths):
        msg = problems.execute_error_protocol()
        raise InputError(msg)
    return paths
