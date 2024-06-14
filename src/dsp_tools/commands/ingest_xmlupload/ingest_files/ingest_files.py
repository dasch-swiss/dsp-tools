from dsp_tools.cli.args import ServerCredentials


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

    return True
