from pathlib import Path

from loguru import logger
from lxml import etree

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.ingest_xmlupload.bulk_ingest_client import BulkIngestClient
from dsp_tools.utils.connection import Connection
from dsp_tools.utils.connection_live import ConnectionLive


def upload_files(
    xml_file: Path,
    creds: ServerCredentials,
    imgdir: str = ".",
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
    root = etree.parse(xml_file).getroot()
    for elem in root.iter():
        elem.tag = etree.QName(elem).localname
    shortcode = root.attrib["shortcode"]
    paths = {Path(imgdir) / x.text for x in root.xpath("//bitstream")}
    print(f"Found {len(paths)} files to upload onto server {creds.dsp_ingest_url}.")
    logger.info(f"Found {len(paths)} files to upload onto server {creds.dsp_ingest_url}.")

    con: Connection = ConnectionLive(creds.server)
    con.login(creds.user, creds.password)
    ingest_client = BulkIngestClient(creds.dsp_ingest_url, con.get_token(), shortcode)

    for path in paths:
        ingest_client.upload_file(path)

    print(f"Uploaded all {len(paths)} files onto server {creds.dsp_ingest_url}.")
    logger.info(f"Uploaded all {len(paths)} files onto server {creds.dsp_ingest_url}.")
    return True
