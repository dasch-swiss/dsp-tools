import importlib.resources
import re
import shutil
import subprocess
import time
from pathlib import Path
from typing import Optional

import requests

from dsp_tools.models.exceptions import BaseError

docker_path_of_user = Path.home() / Path(".dsp-tools/start-stack")
docker_path_of_user.mkdir(parents=True, exist_ok=True)


def start_stack(
    max_file_size: Optional[int] = None,
    enforce_docker_system_prune: bool = False,
    suppress_docker_system_prune: bool = False
) -> bool:
    """
    Start the Docker containers of DSP-API and DSP-APP, and load some basic data models and data. After startup, ask
    user if Docker should be pruned or not.

    Args:
        max_file_size: max. multimedia file size allowed by SIPI, in MB (max: 100'000)
        enforce_docker_system_prune: if True, prune Docker without asking the user
        suppress_docker_system_prune: if True, don't prune Docker (and don't ask)

    Raises:
        BaseError if the stack cannot be started with the parameters passed by the user

    Returns:
        True if everything went well, False otherwise
    """
    # validate input
    if max_file_size is not None:
        if not 1 <= max_file_size <= 100_000:
            raise BaseError("max_file_size must be between 1 and 100000")
    if enforce_docker_system_prune and suppress_docker_system_prune:
        raise BaseError('The arguments "--prune" and "--no-prune" are mutually exclusive')

    # copy contents of src/dsp_tools/resources/start-stack to ~/.dsp-tools/start-stack
    docker_path_of_distribution = importlib.resources.files("dsp_tools").joinpath("resources/start-stack")
    for file in docker_path_of_distribution.iterdir():
        with importlib.resources.as_file(file) as f:
            file_path = Path(f)
        shutil.copy(file_path, docker_path_of_user / file.name)

    # get sipi.docker-config.lua
    commit_of_used_api_version = "d6bae7ff5e6b6a635982c14f21ca4e69e298a312"      # gitleaks:allow
    url_prefix = f"https://github.com/dasch-swiss/dsp-api/raw/{commit_of_used_api_version}/"
    docker_config_lua_text = requests.get(f"{url_prefix}sipi/config/sipi.docker-config.lua", timeout=5).text
    if max_file_size:
        max_post_size_regex = r"max_post_size ?= ?[\'\"]\d+M[\'\"]"
        if not re.search(max_post_size_regex, docker_config_lua_text):
            raise BaseError("Unable to set max_file_size. Please try again without this flag.")
        docker_config_lua_text = re.sub(max_post_size_regex, f"max_post_size = '{max_file_size}M'", docker_config_lua_text)
    with open(docker_path_of_user / "sipi.docker-config.lua", "w", encoding="utf-8") as f:
        f.write(docker_config_lua_text)

    # start up the fuseki database
    completed_process = subprocess.run("docker compose up db -d", shell=True, cwd=docker_path_of_user, check=False)
    if not completed_process or completed_process.returncode != 0:
        raise BaseError("Cannot start the API: Error while executing 'docker compose up db -d'")

    # wait until fuseki is up (same behaviour as dsp-api/webapi/scripts/wait-for-db.sh)
    for _ in range(360):
        try:
            response = requests.get(url="http://0.0.0.0:3030/$/server", auth=("admin", "test"), timeout=5)
            if response.ok:
                break
        except Exception:  # pylint: disable=broad-exception-caught
            time.sleep(1)
        time.sleep(1)

    # inside fuseki, create the "knora-test" repository
    # (same behaviour as dsp-api/webapi/target/docker/stage/opt/docker/scripts/fuseki-init-knora-test.sh)
    repo_template = requests.get(f"{url_prefix}webapi/scripts/fuseki-repository-config.ttl.template", timeout=5).text
    repo_template = repo_template.replace("@REPOSITORY@", "knora-test")
    response = requests.post(
        url="http://0.0.0.0:3030/$/datasets",
        files={"file": ("file.ttl", repo_template, "text/turtle; charset=utf8")},
        auth=("admin", "test"),
        timeout=5
    )
    if not response.ok:
        raise BaseError("Cannot start DSP-API: Error when creating the 'knora-test' repository. Is DSP-API perhaps "
                        "running already?")

    # load some basic ontos and data into the repository
    # (same behaviour as dsp-api/webapi/target/docker/stage/opt/docker/scripts/fuseki-init-knora-test.sh)
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
        ("test_data/all_data/anything-data.ttl", "http://www.knora.org/data/0001/anything")
    ]
    for ttl_file, graph in ttl_files:
        ttl_text = requests.get(url_prefix + ttl_file, timeout=5).text
        response = requests.post(
            url=graph_prefix + graph,
            files={"file": ("file.ttl", ttl_text, "text/turtle; charset: utf-8")},
            auth=("admin", "test"),
            timeout=5
        )
        if not response.ok:
            raise BaseError(f"Cannot start DSP-API: Error when creating graph '{graph}'")

    # startup all other components
    subprocess.run("docker compose up -d", shell=True, cwd=docker_path_of_user, check=True)
    print("DSP-API is now running on http://0.0.0.0:3333/ and DSP-APP on http://0.0.0.0:4200/")

    # docker system prune
    if enforce_docker_system_prune:
        prune_docker = "y"
    elif suppress_docker_system_prune:
        prune_docker = "n"
    else:
        prune_docker = None
        while prune_docker not in ["y", "n"]:
            prune_docker = input("Allow dsp-tools to execute 'docker system prune'? This is necessary to keep your "
                                 "Docker clean. If you are unsure what that means, just type y and press Enter. [y/n]")
    if prune_docker == "y":
        subprocess.run("docker system prune -f", shell=True, cwd=docker_path_of_user, check=False)

    return True


def stop_stack() -> bool:
    """
    Shut down the Docker containers of your local DSP stack and delete all data that is in it.

    Returns:
        True if everything went well, False otherwise
    """
    subprocess.run("docker compose down --volumes", shell=True, cwd=docker_path_of_user, check=True)
    return True
