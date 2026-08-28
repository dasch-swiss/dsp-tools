from pathlib import Path
from time import sleep
from typing import cast

from loguru import logger

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.commands.ingest_xmlupload.bulk_ingest_client import BulkIngestClient
from dsp_tools.error.exceptions import UnreachableCodeError
from dsp_tools.utils.spinners import get_green_bouncy_ball_spinner

MAPPING_RETRIEVAL_SLEEP = 60


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
    status_start_text = "Wait until mapping CSV is ready."
    sp = get_green_bouncy_ball_spinner("Wait until mapping CSV is ready.")
    logger.debug(status_start_text)

    mapping_generator = bulk_ingest_client.retrieve_mapping_generator()
    num_of_attempts = 0
    with sp:
        for result in mapping_generator:
            match result:
                case True:
                    logger.debug(f"Attempt {num_of_attempts}: in progress")
                    num_of_attempts += 1
                case False:
                    logger.warning(f"Attempt {num_of_attempts}: server error")
                    num_of_attempts += 1
                case str():
                    sp.ok("✔")
                    break
                case _:
                    raise UnreachableCodeError()
            sleep(MAPPING_RETRIEVAL_SLEEP)
        return cast(str, result)


def _save_mapping(mapping: str, shortcode: str) -> None:
    filepath = Path(f"mapping-{shortcode}.csv")
    if filepath.exists():
        i = 1
        while (new_name_for_existing := Path(f"mapping-{shortcode}-{i}.csv")).exists():
            i += 1
        filepath.rename(new_name_for_existing)
    filepath.write_text(mapping, encoding="utf-8")
    print(f"Saved mapping CSV to '{filepath}'")
    logger.info(f"Saved mapping CSV to '{filepath}'")
