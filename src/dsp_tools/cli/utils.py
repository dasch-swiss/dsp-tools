import argparse
import subprocess
from pathlib import Path

import regex
import requests
from loguru import logger

from dsp_tools.cli.args import NetworkRequirements
from dsp_tools.cli.args import ProhibitedPaths
from dsp_tools.cli.args import RequiredPaths
from dsp_tools.cli.args import ServerCredentials
from dsp_tools.cli.exceptions import CliUserError
from dsp_tools.cli.exceptions import DockerNotReachableError
from dsp_tools.cli.exceptions import DspApiNotReachableError
from dsp_tools.error.exceptions import UserDirectoryNotFoundError
from dsp_tools.error.exceptions import UserFilepathMustNotExistError
from dsp_tools.error.exceptions import UserFilepathNotFoundError

LOCALHOST_API = "http://0.0.0.0:3333"
LOCALHOST_INGEST = "http://0.0.0.0:3340"


def get_creds(args: argparse.Namespace) -> ServerCredentials:
    return ServerCredentials(
        server=args.server,
        user=args.user,
        password=args.password,
        dsp_ingest_url=args.dsp_ingest_url,
    )


def check_input_dependencies(
    required_paths: RequiredPaths | None = None,
    network_dependencies: NetworkRequirements | None = None,
    prohibited_paths: ProhibitedPaths | None = None,
) -> None:
    if required_paths:
        check_path_dependencies(required_paths)
    if network_dependencies:
        _check_network_health(network_dependencies)
    if prohibited_paths:
        _check_that_files_do_not_exist(prohibited_paths)


def check_path_dependencies(paths: RequiredPaths) -> None:
    for f_path in paths.required_files:
        _check_filepath_exists(f_path)
    for dir_path in paths.required_directories:
        _check_directory_exists(dir_path)


def _check_that_files_do_not_exist(file_paths: ProhibitedPaths) -> None:
    for f_path in file_paths.prohibited_files:
        if f_path.exists():
            raise UserFilepathMustNotExistError(f_path)


def _check_filepath_exists(file_path: Path) -> None:
    if not file_path.exists():
        raise UserFilepathNotFoundError(file_path)


def _check_directory_exists(dir_path: Path) -> None:
    if not dir_path.is_dir():
        raise UserDirectoryNotFoundError(dir_path)


def _check_network_health(network_requirements: NetworkRequirements) -> None:
    if network_requirements.api_url == LOCALHOST_API or network_requirements.always_requires_docker:
        check_docker_health()
    _check_api_health(network_requirements.api_url)


def check_docker_health() -> None:
    if subprocess.run("docker stats --no-stream".split(), check=False, capture_output=True, timeout=3).returncode != 0:
        raise DockerNotReachableError()


def _check_api_health(api_url: str) -> None:
    health_url = f"{api_url}/health"

    try:
        response = requests.get(health_url, timeout=2)
    except requests.exceptions.RequestException:
        logger.exception(f"Failed to connect to DSP-API at {health_url}")
        raise DspApiNotReachableError(is_localhost=api_url == LOCALHOST_API) from None

    if not response.ok:
        error = DspApiNotReachableError(
            is_localhost=bool(api_url == LOCALHOST_API),
            status_code=response.status_code,
            response_text=response.text,
        )
        logger.error(str(error))
        raise error

    logger.debug(f"DSP API health check passed: {health_url}")


def get_canonical_server_and_dsp_ingest_url(
    server: str,
    default_dsp_api_url: str = LOCALHOST_API,
    default_dsp_ingest_url: str = LOCALHOST_INGEST,
) -> tuple[str, str]:
    """
    Based on the DSP server URL passed by the user,
    transform it to its canonical form,
    and derive the ingest server URL from it.

    If the DSP server URL points to port 3333 on localhost,
    the ingest server will point to port 3340 on localhost.

    If the DSP server URL points to a remote server ending in "dasch.swiss",
    modify it (if necessary) to point to the "api" subdomain of that server,
    and add a new "dsp_ingest_url" argument pointing to the "ingest" subdomain of that server.

    Args:
        server: DSP server URL passed by the user
        default_dsp_api_url: default DSP server on localhost
        default_dsp_ingest_url: default ingest server on localhost

    Raises:
        CliUserError: if the DSP server URL passed by the user is invalid

    Returns:
        canonical DSP URL and ingest server URL
    """
    localhost_match = regex.search(r"(0\.0\.0\.0|localhost):3333", server)
    remote_url_match = regex.search(
        r"^(?:https?:\/\/)?(?:admin\.|api\.|ingest\.|app\.)?((?:.+\.)?dasch)\.swiss", server
    )

    if localhost_match:
        server = default_dsp_api_url
        dsp_ingest_url = default_dsp_ingest_url
    elif remote_url_match:
        server = f"https://api.{remote_url_match.group(1)}.swiss"
        dsp_ingest_url = f"https://ingest.{remote_url_match.group(1)}.swiss"
    else:
        logger.error(f"Invalid DSP server URL '{server}'")
        raise CliUserError(f"ERROR: Invalid DSP server URL '{server}'")

    logger.info(f"Using DSP server '{server}' and ingest server '{dsp_ingest_url}'")
    print(f"Using DSP server '{server}' and ingest server '{dsp_ingest_url}'")

    return server, dsp_ingest_url
