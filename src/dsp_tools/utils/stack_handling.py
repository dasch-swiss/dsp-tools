import importlib.resources
import re
import shutil
import subprocess
import time
from pathlib import Path
from typing import Optional

import requests
import yaml

from dsp_tools.models.exceptions import UserError
from dsp_tools.utils.logging import get_logger

logger = get_logger(__name__)

docker_path_of_user = Path.home() / Path(".dsp-tools/start-stack")
docker_path_of_user.mkdir(parents=True, exist_ok=True)


def _validate_input(
    max_file_size: Optional[int],
    enforce_docker_system_prune: bool,
    suppress_docker_system_prune: bool,
) -> None:
    """
    Validate the input parameters passed by the user.
    Raises a UserError if one of the parameters is invalid.
    """
    if max_file_size is not None:
        if not 1 <= max_file_size <= 100_000:
            raise UserError("max_file_size must be between 1 and 100000")
    if enforce_docker_system_prune and suppress_docker_system_prune:
        raise UserError('The arguments "--prune" and "--no-prune" are mutually exclusive')


def _get_url_prefix() -> str:
    """
    The start-stack command needs some files from the DSP-API repository.
    By default, start-stack starts the latest deployed version of DSP-API.
    Since the last deployment, the DSP-API repository may have been updated.
    For this reason, we need to know the commit hash of the DSP-API version that is currently deployed,
    so that the files can be retrieved from the correct commit.

    This function reads the commit hash of DSP-API
    that is configured in start-stack-config.yml,
    and constructs the URL prefix necessary to retrieve the files from the DSP-API repository.

    If something goes wrong,
    the URL prefix falls back to pointing to the main branch of the DSP-API repository.

    Returns:
        URL prefix used to retrieve files from the DSP-API repository
    """
    url_prefix_base = "https://github.com/dasch-swiss/dsp-api/raw/"
    config_file = Path("src/dsp_tools/resources/start-stack/start-stack-config.yml")
    if not config_file.is_file():
        return url_prefix_base + "main/"

    with open("src/dsp_tools/resources/start-stack/start-stack-config.yml", "r", encoding="utf-8") as f:
        try:
            start_stack_config = yaml.safe_load(f)
        except yaml.YAMLError:
            start_stack_config = {}
    commit_of_used_api_version = start_stack_config.get("DSP-API commit", "main")
    url_prefix = f"https://github.com/dasch-swiss/dsp-api/raw/{commit_of_used_api_version}/"
    return url_prefix


def _copy_resources_to_home_dir() -> None:
    """
    On most systems, Docker is not allowed to access files outside of the user's home directory.
    For this reason, copy the contents of src/dsp_tools/resources/start-stack to ~/.dsp-tools/start-stack.
    """
    docker_path_of_distribution = importlib.resources.files("dsp_tools").joinpath("resources/start-stack")
    for file in docker_path_of_distribution.iterdir():
        with importlib.resources.as_file(file) as f:
            file_path = Path(f)
        shutil.copy(file_path, docker_path_of_user / file.name)


def _get_sipi_docker_config_lua(
    max_file_size: Optional[int],
    url_prefix: str,
) -> None:
    """
    Retrieve the config file sipi.docker-config.lua from the DSP-API repository,
    and set the max_file_size parameter if necessary.

    Args:
        max_file_size: new value for max_file_size to inject into sipi.docker-config.lua
        url_prefix: URL prefix used to retrieve file

    Raises:
        UserError: if max_file_size is set but cannot be injected into sipi.docker-config.lua
    """
    docker_config_lua_text = requests.get(f"{url_prefix}sipi/config/sipi.docker-config.lua", timeout=5).text
    if max_file_size:
        max_post_size_regex = r"max_post_size ?= ?[\'\"]\d+M[\'\"]"
        if not re.search(max_post_size_regex, docker_config_lua_text):
            raise UserError("Unable to set max_file_size. Please try again without this flag.")
        docker_config_lua_text = re.sub(
            max_post_size_regex,
            f"max_post_size = '{max_file_size}M'",
            docker_config_lua_text,
        )
    with open(docker_path_of_user / "sipi.docker-config.lua", "w", encoding="utf-8") as f:
        f.write(docker_config_lua_text)


def _start_up_fuseki() -> None:
    """
    Start up the Docker container of the fuseki database.

    Raises:
        UserError: if the database cannot be started
    """
    completed_process = subprocess.run("docker compose up db -d", shell=True, cwd=docker_path_of_user, check=False)
    if not completed_process or completed_process.returncode != 0:
        msg = "Cannot start the API: Error while executing 'docker compose up db -d'"
        logger.error(f"{msg}. completed_process = '{completed_process}'")
        raise UserError(msg)


def _wait_for_fuseki() -> None:
    """
    Wait up to 6 minutes, until the fuseki database is up and running.
    This function imitates the behaviour of the script dsp-api/webapi/scripts/wait-for-db.sh.
    """
    for _ in range(6 * 60):
        try:
            response = requests.get(url="http://0.0.0.0:3030/$/server", auth=("admin", "test"), timeout=5)
            if response.ok:
                break
        except Exception:  # pylint: disable=broad-exception-caught
            time.sleep(1)
        time.sleep(1)


def _create_knora_test_repo(url_prefix: str) -> None:
    """
    Inside fuseki, create the "knora-test" repository.
    This function imitates the behaviour of the script dsp-api/webapi/scripts/fuseki-init-knora-test.sh.

    Args:
        url_prefix: URL prefix used to retrieve the file from the DSP-API repository

    Raises:
        UserError: in case of failure
    """
    repo_template = requests.get(f"{url_prefix}webapi/scripts/fuseki-repository-config.ttl.template", timeout=5).text
    repo_template = repo_template.replace("@REPOSITORY@", "knora-test")
    response = requests.post(
        url="http://0.0.0.0:3030/$/datasets",
        files={"file": ("file.ttl", repo_template, "text/turtle; charset=utf8")},
        auth=("admin", "test"),
        timeout=5,
    )
    if not response.ok:
        msg = (
            "Cannot start DSP-API: Error when creating the 'knora-test' repository. "
            "Is DSP-API perhaps running already?"
        )
        logger.error(f"{msg}. response = {response}")
        raise UserError(msg)


def _load_data_into_repo(url_prefix: str) -> None:
    """
    Load some basic ontologies and data into the repository.
    This function imitates the behaviour of the script
    dsp-api/webapi/target/docker/stage/opt/docker/scripts/fuseki-init-knora-test.sh.

    Args:
        url_prefix: URL prefix used to retrieve the files from the DSP-API repository

    Raises:
        UserError: if one of the graphs cannot be created
    """
    graph_prefix = "http://0.0.0.0:3030/knora-test/data?graph="
    ttl_files = [
        ("knora-ontologies/knora-admin.ttl", "http://www.knora.org/ontology/knora-admin"),
        ("knora-ontologies/knora-base.ttl", "http://www.knora.org/ontology/knora-base"),
        ("knora-ontologies/standoff-onto.ttl", "http://www.knora.org/ontology/standoff"),
        ("knora-ontologies/standoff-data.ttl", "http://www.knora.org/data/standoff"),
        ("knora-ontologies/salsah-gui.ttl", "http://www.knora.org/ontology/salsah-gui"),
        ("test_data/all_data/admin-data.ttl", "http://www.knora.org/data/admin"),
        ("test_data/all_data/permissions-data.ttl", "http://www.knora.org/data/permissions"),
        ("test_data/ontologies/anything-onto.ttl", "http://www.knora.org/ontology/0001/anything"),
        ("test_data/all_data/anything-data.ttl", "http://www.knora.org/data/0001/anything"),
    ]
    for ttl_file, graph in ttl_files:
        ttl_text = requests.get(url_prefix + ttl_file, timeout=5).text
        response = requests.post(
            url=graph_prefix + graph,
            files={"file": ("file.ttl", ttl_text, "text/turtle; charset: utf-8")},
            auth=("admin", "test"),
            timeout=5,
        )
        if not response.ok:
            logger.error(f"Cannot start DSP-API: Error when creating graph '{graph}'. response = {response}")
            raise UserError(f"Cannot start DSP-API: Error when creating graph '{graph}'")


def _initialize_fuseki(url_prefix: str) -> None:
    """
    Create the "knora-test" repository and load some basic ontologies and data into it.

    Args:
        url_prefix: URL prefix used to retrieve the files from the DSP-API repository
    """
    _create_knora_test_repo(url_prefix=url_prefix)
    _load_data_into_repo(url_prefix=url_prefix)


def _start_remaining_docker_containers() -> None:
    """
    Start the other Docker containers that are not running yet.
    (Fuseki is already running at this point.)
    """
    subprocess.run("docker compose up -d", shell=True, cwd=docker_path_of_user, check=True)
    print("DSP-API is now running on http://0.0.0.0:3333/ and DSP-APP on http://0.0.0.0:4200/")


def _execute_docker_system_prune(
    enforce_docker_system_prune: bool,
    suppress_docker_system_prune: bool,
) -> None:
    """
    Depending on the CLI parameters or the user's input,
    execute "docker system prune" or not.

    Args:
        enforce_docker_system_prune: parameter received from CLI
        suppress_docker_system_prune: parameter received from CLI
    """
    if enforce_docker_system_prune:
        prune_docker = "y"
    elif suppress_docker_system_prune:
        prune_docker = "n"
    else:
        prune_docker = None
        while prune_docker not in ["y", "n"]:
            prune_docker = input(
                "Allow dsp-tools to execute 'docker system prune'? This is necessary to keep your Docker clean. "
                "If you are unsure what that means, just type y and press Enter. [y/n]"
            )
    if prune_docker == "y":
        subprocess.run("docker system prune -f", shell=True, cwd=docker_path_of_user, check=False)


def start_stack(
    max_file_size: Optional[int] = None,
    enforce_docker_system_prune: bool = False,
    suppress_docker_system_prune: bool = False,
) -> bool:
    """
    Start the Docker containers of DSP-API and DSP-APP, and load some basic data models and data. After startup, ask
    user if Docker should be pruned or not.

    Args:
        max_file_size: max. multimedia file size allowed by SIPI, in MB (max: 100'000)
        enforce_docker_system_prune: if True, prune Docker without asking the user
        suppress_docker_system_prune: if True, don't prune Docker (and don't ask)

    Raises:
        UserError if the stack cannot be started with the parameters passed by the user

    Returns:
        True if everything went well, False otherwise
    """
    _validate_input(
        max_file_size=max_file_size,
        enforce_docker_system_prune=enforce_docker_system_prune,
        suppress_docker_system_prune=suppress_docker_system_prune,
    )

    url_prefix = _get_url_prefix()

    _copy_resources_to_home_dir()

    _get_sipi_docker_config_lua(
        max_file_size=max_file_size,
        url_prefix=url_prefix,
    )

    _start_up_fuseki()
    _wait_for_fuseki()
    _initialize_fuseki(url_prefix=url_prefix)

    _start_remaining_docker_containers()

    _execute_docker_system_prune(
        enforce_docker_system_prune=enforce_docker_system_prune,
        suppress_docker_system_prune=suppress_docker_system_prune,
    )

    return True


def stop_stack() -> bool:
    """
    Shut down the Docker containers of your local DSP stack and delete all data that is in it.

    Returns:
        True if everything went well, False otherwise
    """
    subprocess.run("docker compose down --volumes", shell=True, cwd=docker_path_of_user, check=True)
    return True
