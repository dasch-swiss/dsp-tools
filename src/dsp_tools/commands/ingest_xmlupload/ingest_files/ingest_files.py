from dsp_tools.cli.args import ServerCredentials
from dsp_tools.utils.connection import Connection
from dsp_tools.utils.connection_live import ConnectionLive


def ingest_files(creds: ServerCredentials, shortcode: str) -> bool:  # noqa: ARG001
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
    url = "/projects/{shortcode}/bulk-ingest/mapping.csv"
    return True
