from pathlib import Path

from loguru import logger
from lxml import etree
from tqdm import tqdm

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.ingest_xmlupload.bulk_ingest_client import BulkIngestClient
from dsp_tools.commands.ingest_xmlupload.upload_files.filechecker import FileChecker
from dsp_tools.commands.ingest_xmlupload.upload_files.upload_failures import UploadFailure
from dsp_tools.commands.ingest_xmlupload.upload_files.upload_failures import UploadFailures
from dsp_tools.models.exceptions import InputError
from dsp_tools.utils.connection import Connection
from dsp_tools.utils.connection_live import ConnectionLive
from dsp_tools.utils.xml_utils import remove_comments_from_element_tree


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
    root = _parse_xml(xml_file)
    shortcode = root.attrib["shortcode"]
    paths = _get_validated_paths(root)
    print(f"Found {len(paths)} files to upload onto server {creds.dsp_ingest_url}.")
    logger.info(f"Found {len(paths)} files to upload onto server {creds.dsp_ingest_url}.")

    con: Connection = ConnectionLive(creds.server)
    con.login(creds.user, creds.password)
    ingest_client = BulkIngestClient(creds.dsp_ingest_url, con.get_token(), shortcode, imgdir)

    failures: list[UploadFailure] = []
    progress_bar = tqdm(sorted(paths), desc="Uploading files", unit="file")  # sorting is for testability
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


def _parse_xml(xml_file: Path) -> etree._Element:
    root = etree.parse(xml_file).getroot()
    root = remove_comments_from_element_tree(root)
    for elem in root.iter():
        elem.tag = etree.QName(elem).localname
    return root


def _get_validated_paths(root: etree._Element) -> set[Path]:
    paths = {Path(x.text) for x in root.xpath("//bitstream")}
    if problems := FileChecker(paths).validate():
        msg = problems.execute_error_protocol()
        raise InputError(msg)
    return paths
