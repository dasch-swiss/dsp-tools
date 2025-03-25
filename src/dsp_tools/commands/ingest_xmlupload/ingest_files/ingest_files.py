from datetime import datetime
from pathlib import Path
from time import sleep
from typing import cast

from loguru import logger
from tqdm import tqdm

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.commands.ingest_xmlupload.bulk_ingest_client import BulkIngestClient


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
    auth = AuthenticationClientLive(creds.server, creds.user, creds.password)
    bulk_ingest_client = BulkIngestClient(creds.dsp_ingest_url, auth, shortcode)
    bulk_ingest_client.trigger_ingest_process()
    sleep(5)
    mapping = _retrieve_mapping(bulk_ingest_client)
    _save_mapping(mapping, shortcode)
    return True


def _retrieve_mapping(bulk_ingest_client: BulkIngestClient) -> str:
    sleeping_time = 60
    desc = f"Wait until mapping CSV is ready. Ask server every {sleeping_time} seconds "
    progress_bar = tqdm(
        bulk_ingest_client.retrieve_mapping_generator(), desc=desc, bar_format="{desc}{elapsed}", dynamic_ncols=True
    )
    num_of_attempts = 0
    num_of_server_errors = 0
    for result in progress_bar:
        if result is False:
            num_of_attempts += 1
            num_of_server_errors += 1
        elif result is True:
            num_of_attempts += 1
        elif isinstance(result, str):
            break
        progress_bar.set_description(f"{desc}(attempts: {num_of_attempts}, server errors: {num_of_server_errors})")
        sleep(sleeping_time)
    return cast(str, result)


def _save_mapping(mapping: str, shortcode: str) -> None:
    filepath = Path(f"mapping-{shortcode}.csv")
    if filepath.exists():
        timestamp = datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
        filepath = filepath.with_name(f"{filepath.stem}-{timestamp}.csv")
    filepath.write_text(mapping)
    print(f"Saved mapping CSV to '{filepath}'")
    logger.info(f"Saved mapping CSV to '{filepath}'")
