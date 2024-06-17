from pathlib import Path
from time import sleep
from typing import Any

import requests
from loguru import logger

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.models.exceptions import UserError
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
    _kick_off_ingest(con.get_token(), creds, shortcode)

    success = False
    while not success:
        success = _try_download(con.get_token(), creds, shortcode)
        sleep(10)
    return True


def _kick_off_ingest(token: str, creds: ServerCredentials, shortcode: str) -> None:
    url = f"{creds.dsp_ingest_url}/projects/{shortcode}/bulk-ingest"
    try:
        res: dict[str, Any] = requests.post(url, headers={"Authorization": f"Bearer {token}"}, timeout=5).json()
    except Exception:  # TODO: catch a specific error  # noqa: BLE001
        print("Ingest process is already running. Wait until it completes...")
        logger.error("Ingest process is already running. Wait until it completes...")
        return
    if res.get("id") != shortcode:
        raise UserError("Failed to kick off the ingest process.")
    print("Kicked off the ingest process on the server. Wait until it completes...")
    logger.info("Kicked off the ingest process on the server. Wait until it completes...")


def _try_download(token: str, creds: ServerCredentials, shortcode: str) -> bool:
    url = f"{creds.dsp_ingest_url}/projects/{shortcode}/bulk-ingest/mapping.csv"
    res = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=5)
    if res.status_code == 409:
        print("Ingest process is still running. Wait until it completes...")
        logger.info("Ingest process is still running. Wait until it completes...")
        return False
    elif not res.ok:
        print("Dubious error")
        logger.error("Dubious error")
        return False
    print("Ingest process completed.")
    logger.info("Ingest process completed.")
    _save_mapping(res.text, shortcode)
    return True


def _save_mapping(mapping: str, shortcode: str) -> None:
    filepath = Path(f"mapping-{shortcode}.csv")
    filepath.write_text(mapping)
    print(f"Saved mapping CSV to '{filepath}'")
    logger.info(f"Saved mapping CSV to '{filepath}'")
