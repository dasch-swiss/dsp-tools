import argparse
import subprocess
from pathlib import Path

import requests
from loguru import logger

from dsp_tools.cli.args import NetworkRequirements
from dsp_tools.cli.args import PathDependencies
from dsp_tools.cli.args import ServerCredentials
from dsp_tools.error.exceptions import DockerNotReachableError
from dsp_tools.error.exceptions import DspApiNotReachableError
from dsp_tools.error.exceptions import UserDirectoryNotFoundError
from dsp_tools.error.exceptions import UserFilepathNotFoundError

LOCALHOST_API = "http://0.0.0.0:3333"


def get_creds(args: argparse.Namespace) -> ServerCredentials:
    return ServerCredentials(
        server=args.server,
        user=args.user,
        password=args.password,
        dsp_ingest_url=args.dsp_ingest_url,
    )


def check_input_dependencies(
    paths: PathDependencies | None = None, network_dependencies: NetworkRequirements | None = None
) -> None:
    if paths:
        check_path_dependencies(paths)
    if network_dependencies:
        _check_network_health(network_dependencies)


def check_path_dependencies(paths: PathDependencies) -> None:
    for f_path in paths.required_files:
        _check_filepath_exists(f_path)
    for dir_path in paths.required_directories:
        _check_directory_exists(dir_path)


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
