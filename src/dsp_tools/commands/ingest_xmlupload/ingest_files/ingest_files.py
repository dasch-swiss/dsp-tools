from datetime import datetime
from pathlib import Path
from time import sleep

from loguru import logger

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.ingest_xmlupload.bulk_ingest_client import BulkIngestClient
from dsp_tools.utils.connection import Connection
from dsp_tools.utils.connection_live import ConnectionLive


def ingest_files(creds: ServerCredentials, shortcode: str) -> bool:
    """
    Kick off the ingest process on the server, and wait until it has finished.
    Then, retrieve the mapping CSV from the server and save it in the CWD.

    Args:
        creds: credentials to log in on the server
        shortcode: shortcode of the project

    Returns:
        success status
    """
    con: Connection = ConnectionLive(creds.server)
    con.login(creds.user, creds.password)
    mass_ingest_client = BulkIngestClient(creds.dsp_ingest_url, con.get_token(), shortcode)
    mass_ingest_client.kick_off_ingest()

    while not (mapping := mass_ingest_client.retrieve_mapping()):
        sleep(10)
    _save_mapping(mapping, shortcode)
    return True


def _save_mapping(mapping: str, shortcode: str) -> None:
    filepath = Path(f"mapping-{shortcode}.csv")
    if filepath.exists():
        timestamp = datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
        filepath = filepath.with_name(f"{filepath.stem}-{timestamp}.csv")
    filepath.write_text(mapping)
    print(f"Saved mapping CSV to '{filepath}'")
    logger.info(f"Saved mapping CSV to '{filepath}'")
