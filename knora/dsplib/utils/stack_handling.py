import json
import re
import subprocess
import time
from typing import Optional

import requests

from knora.dsplib.models.helpers import BaseError


def start_stack(
    max_file_size: Optional[int] = None,
    enforce_docker_system_prune: bool = False
) -> None:
    """
    Start the Docker containers of DSP-API and DSP-APP, and load some basic data models and data. After startup, ask
    user if Docker should be pruned or not.

    Args:
        max_file_size: max. multimedia file size allowed by SIPI, in MB (max: 100'000)
        enforce_docker_system_prune: if True, prune Docker without asking the user
    """
    # get sipi.docker-config.lua
    latest_release = json.loads(requests.get("https://api.github.com/repos/dasch-swiss/dsp-api/releases").text)[0]
    url_prefix = f"https://github.com/dasch-swiss/dsp-api/raw/{latest_release['target_commitish']}/"
    docker_config_lua_text = requests.get(f"{url_prefix}sipi/config/sipi.docker-config.lua").text
    if max_file_size is not None:
        if not 1 <= max_file_size <= 100_000:
            raise BaseError("max_file_size must be between 1 and 100000")
        max_post_size_regex = r"max_post_size ?= ?[\'\"]\d+M[\'\"]"
        if not re.search(max_post_size_regex, docker_config_lua_text):
            raise BaseError("sipi.docker-config.lua doesn't contain a variable max_post_size that could be replaced")
        docker_config_lua_text = re.sub(max_post_size_regex, f"max_post_size = '{max_file_size}M'", docker_config_lua_text)
    with open("knora/dsplib/docker/sipi.docker-config.lua", "w") as f:
        f.write(docker_config_lua_text)

    # start up the fuseki database
    completed_process = subprocess.run("docker compose up db -d", shell=True, cwd="knora/dsplib/docker")
    if not completed_process or completed_process.returncode != 0:
        raise BaseError("Cannot start the API: Error while executing 'docker compose up db -d'")

    # wait until fuseki is up (same behaviour as dsp-api/webapi/scripts/wait-for-db.sh)
    for i in range(360):
        try:
            response = requests.get(url="http://0.0.0.0:3030/$/server", auth=("admin", "test"))
            if response.ok:
                break
        except:
            time.sleep(1)
        time.sleep(1)

    # inside fuseki, create the "knora-test" repository
    repo_template = requests.get(f"{url_prefix}webapi/scripts/fuseki-repository-config.ttl.template").text
    repo_template = repo_template.replace("@REPOSITORY@", "knora-test")
    response = requests.post(
        url="http://0.0.0.0:3030/$/datasets",
        files={"file": ("file.ttl", repo_template, "text/turtle; charset=utf8")},
        auth=("admin", "test")
    )
    if not response.ok:
        raise BaseError("Cannot start DSP-API: Error when creating the 'knora-test' repository. Is there perhaps "
                        "another DSP-API running already?")

    # load some basic ontos and data into the repository
    graph_prefix = "http://0.0.0.0:3030/knora-test/data?graph="
    ttl_files = [
        ("knora-ontologies/knora-admin.ttl", "http://www.knora.org/ontology/knora-admin"),
        ("knora-ontologies/knora-base.ttl", "http://www.knora.org/ontology/knora-base"),
        ("knora-ontologies/standoff-onto.ttl", "http://www.knora.org/ontology/standoff"),
        ("knora-ontologies/standoff-data.ttl", "http://www.knora.org/data/standoff"),
        ("knora-ontologies/salsah-gui.ttl", "http://www.knora.org/ontology/salsah-gui"),
        ("test_data/all_data/admin-data-minimal.ttl", "http://www.knora.org/data/admin"),
        ("test_data/all_data/permissions-data-minimal.ttl", "http://www.knora.org/data/permissions")
    ]
    for ttl_file, graph in ttl_files:
        ttl_text = requests.get(url_prefix + ttl_file).text
        response = requests.post(
            url=graph_prefix + graph,
            files={"file": ("file.ttl", ttl_text, "text/turtle; charset: utf-8")},
            auth=("admin", "test"),
        )
        if not response.ok:
            raise BaseError(f"Cannot start DSP-API: Error when creating graph '{graph}'")

    # startup all other components
    subprocess.run("docker compose up -d", shell=True, cwd="knora/dsplib/docker")
    if enforce_docker_system_prune:
        prune_docker = "y\n"
    else:
        prune_docker = None
        while prune_docker != "y\n" or prune_docker != "N\n":
            prune_docker = subprocess.run(
                "read -p \"Allow us executing a docker system prune? This is necessary to keep your Docker clean. If "
                "you are unsure what that means, just type y and press Enter. [y/N]\" response; echo $response",
                shell=True,
                stdout=subprocess.PIPE,
                text=True
            ).stdout
    if prune_docker == "y\n":
        subprocess.run("docker system prune -f", shell=True, cwd="knora/dsplib/docker")


def stop_stack() -> None:
    """
    Shut down the Docker containers of DSP-API and delete all data that is in them.
    """
    subprocess.run("docker compose down --volumes", shell=True, cwd="knora/dsplib/docker")
