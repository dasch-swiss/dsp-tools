import re
import subprocess
import time

import requests

from knora.dsplib.models.helpers import BaseError


def start_stack() -> None:
    """
    Start the Docker containers of DSP-API, and load some basic data models and data.
    """
    # start up the fuseki database
    completed_process = subprocess.run("docker compose up db -d", shell=True, cwd="knora/dsplib/docker")
    if not completed_process or completed_process.returncode != 0:
        raise BaseError("Cannot start the API: Error while executing 'docker compose up db -d'")

    # wait until fuseki is up (same behaviour as dsp-api/webapi/scripts/wait-for-db.sh)
    for i in range(360):
        try:
            response = requests.get(
                url="http://0.0.0.0:3030/$/server",
                auth=("admin", "test")
            )
            if response.ok:
                break
        except:
            time.sleep(1)
        time.sleep(1)

    # inside fuseki, create the "knora-test" repository
    url_prefix = "https://raw.githubusercontent.com/dasch-swiss/dsp-api/main"
    repo_template = requests.get(f"{url_prefix}/webapi/scripts/fuseki-repository-config.ttl.template").text
    repo_template = re.sub(r"@REPOSITORY@", "knora-test", repo_template)
    response = requests.post(
        url="http://0.0.0.0:3030/$/datasets",
        files={"file": ("file.ttl", repo_template, "text/turtle; charset=utf8")},
        auth=("admin", "test")
    )
    if not response.ok:
        raise BaseError("Cannot start the API: Error when creating the 'knora-test' repository")

    # load some basic ontos and data into the repository
    graph_prefix = "http://0.0.0.0:3030/knora-test/data?graph="
    ttl_files = [
        (f"{url_prefix}/knora-ontologies/knora-admin.ttl", f"{graph_prefix}http://www.knora.org/ontology/knora-admin"),
        (f"{url_prefix}/knora-ontologies/knora-base.ttl", f"{graph_prefix}http://www.knora.org/ontology/knora-base"),
        (f"{url_prefix}/knora-ontologies/standoff-onto.ttl", f"{graph_prefix}http://www.knora.org/ontology/standoff"),
        (f"{url_prefix}/knora-ontologies/standoff-data.ttl", f"{graph_prefix}http://www.knora.org/data/standoff"),
        (f"{url_prefix}/knora-ontologies/salsah-gui.ttl", f"{graph_prefix}http://www.knora.org/ontology/salsah-gui"),
        (f"{url_prefix}/test_data/all_data/admin-data-minimal.ttl", f"{graph_prefix}http://www.knora.org/data/admin"),
        (f"{url_prefix}/test_data/all_data/permissions-data-minimal.ttl",
         f"{graph_prefix}http://www.knora.org/data/permissions")
    ]
    for ttl_file, graph in ttl_files:
        ttl_text = requests.get(ttl_file).text
        response = requests.post(
            url=graph,
            files={"file": ("file.ttl", ttl_text, "text/turtle; charset: utf-8")},
            auth=("admin", "test"),
        )
        if not response.ok:
            raise BaseError(f"Cannot start the API: Error when creating graph '{graph}'")

    # get sipi.docker-config.lua
    docker_config_lua_text = requests.get(f"{url_prefix}/sipi/config/sipi.docker-config.lua").text
    with open("knora/dsplib/docker/sipi.docker-config.lua", "w") as f:
        f.write(docker_config_lua_text)

    # startup all other components
    subprocess.run("docker compose up -d", shell=True, cwd="knora/dsplib/docker")
    subprocess.run("docker system prune -f", shell=True, cwd="knora/dsplib/docker")


def stop_stack() -> None:
    """
    Shut down the Docker containers of DSP-API and delete all data that is in them.
    """
    subprocess.run("docker compose down --volumes", shell=True, cwd="knora/dsplib/docker")
