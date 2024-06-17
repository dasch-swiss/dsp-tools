from pathlib import Path
from time import sleep
from typing import Any

from dsp_tools.cli.args import ServerCredentials
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
    _kick_off_ingest(con, creds, shortcode)

    success = False
    while not success:
        success = _try_download(con, creds, shortcode)
        sleep(10)
    return True


def _kick_off_ingest(con: Connection, creds: ServerCredentials, shortcode: str) -> None:
    kickoff_url = f"{creds.dsp_ingest_url}/projects/{shortcode}/bulk-ingest"
    try:
        con.post(kickoff_url)
        print("Kicked off the ingest process on the server. Wait until it completes...")
    except Exception:  # TODO: catch a specific error
        print("Ingest process is already running. Wait until it completes...")


def _try_download(con: Connection, creds: ServerCredentials, shortcode: str) -> bool:
    url = f"{creds.dsp_ingest_url}/projects/{shortcode}/bulk-ingest/mapping.csv"
    try:
        mapping = con.get(url)
        print("Ingest process completed.")
        _save_mapping(mapping, shortcode)
        return True
    except Exception:  # catch only 409 Conflict error
        print("Ingest process is still running. Wait until it completes...")
        return False


def _save_mapping(mapping: dict[str, Any], shortcode: str) -> None:
    filepath = Path(f"mapping-{shortcode}.csv")
    filepath.write_text(mapping["csv"])
    print(f"Saved mapping CSV to {filepath}")
