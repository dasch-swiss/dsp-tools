import re
import subprocess
import time

import requests


def start_stack() -> None:
    """
    Start the Docker containers of DSP-API, and load some basic data models and data.
    """
    # start up the fuseki database
    completed_process = subprocess.run("docker compose up db -d", shell=True)
    if not completed_process or completed_process.returncode != 0:
        exit(1)
    time.sleep(5)

    # create the "knora-test" repository
    url_prefix = "https://raw.githubusercontent.com/dasch-swiss/dsp-api/main"
    repo_template_response = requests.get(f"{url_prefix}/webapi/scripts/fuseki-repository-config.ttl.template")
    if not repo_template_response or repo_template_response.status_code != 200:
        exit(1)
    repo_template = re.sub(r"@REPOSITORY@", "knora-test", repo_template_response.text)
    response = requests.post(
        url="http://0.0.0.0:3030/$/datasets",
        files={"file": ("file.ttl", repo_template, "text/turtle; charset=utf8")},
        auth=("admin", "test")
    )
    if not response or response.status_code != 200:
        exit(1)

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
        response = requests.get(ttl_file)
        requests.post(
            url=graph,
            files={"file": ("file.ttl", response.text, "text/turtle; charset: utf-8")},
            auth=("admin", "test"),
        )

    # startup all other components
    subprocess.run("docker compose up -d", shell=True)


def stop_stack() -> None:
    """
    Shut down the Docker containers of DSP-API and delete all data that is in them.
    """
    subprocess.run("docker compose down", shell=True)
