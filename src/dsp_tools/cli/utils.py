import argparse
import subprocess
from pathlib import Path

import requests
from loguru import logger

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.error.exceptions import DockerNotReachableError
from dsp_tools.error.exceptions import DspApiNotReachableError
from dsp_tools.error.exceptions import UserDirectoryNotFoundError
from dsp_tools.error.exceptions import UserFilepathNotFoundError

LOCALHOST_API = "http://0.0.0.0:3333"


def _check_docker_health() -> None:
    if subprocess.run("docker stats --no-stream".split(), check=False, capture_output=True).returncode != 0:
        raise DockerNotReachableError()


def _check_api_health(api_url: str) -> None:
    health_url = f"{api_url}/health"
    msg = (
        "The DSP-API could not be reached. Please check if your stack is healthy "
        "or start a stack with 'dsp-tools start-stack' if none is running."
    )
    try:
        response = requests.get(health_url, timeout=2)
        if not response.ok:
            if api_url != LOCALHOST_API:
                msg = (
                    f"The DSP-API could not be reached (returned status {response.status_code}). "
                    f"Please contact the DaSCH engineering team for help."
                )
            logger.error(msg)
            raise DspApiNotReachableError(msg)
        logger.debug(f"DSP API health check passed: {health_url}")
    except requests.exceptions.RequestException as e:
        logger.error(e)
        if api_url != LOCALHOST_API:
            msg = "The DSP-API responded with a request exception. Please contact the DaSCH engineering team for help."
        logger.error(msg)
        raise DspApiNotReachableError(msg) from None


def _check_filepath_exists(file_path: Path) -> None:
    if not file_path.exists():
        raise UserFilepathNotFoundError(file_path)


def _check_directory_exists(dir_path: Path) -> None:
    if not dir_path.is_dir():
        raise UserDirectoryNotFoundError(dir_path)


def _get_creds(args: argparse.Namespace) -> ServerCredentials:
    return ServerCredentials(
        server=args.server,
        user=args.user,
        password=args.password,
        dsp_ingest_url=args.dsp_ingest_url,
    )


def _check_health_with_docker_on_localhost(api_url: str) -> None:
    if api_url == LOCALHOST_API:
        _check_docker_health()
    _check_api_health(api_url)


def _check_health_with_docker(api_url: str) -> None:
    # validate always needs docker running
    _check_docker_health()
    _check_api_health(api_url)
