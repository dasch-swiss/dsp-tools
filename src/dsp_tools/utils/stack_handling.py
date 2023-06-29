import importlib.resources
from logging import Logger
import re
import shutil
import subprocess
import time
from pathlib import Path
from typing import Optional

import requests
import yaml

from dsp_tools.models.exceptions import BaseError, UserError
from dsp_tools.utils.logging import get_logger


class StackHandler:
    """
    This class contains functions to start and stop the Docker containers of DSP-API and DSP-APP.
    """

    max_file_size: Optional[int]
    enforce_docker_system_prune: bool
    suppress_docker_system_prune: bool

    latest_dev_version: bool
    url_prefix: str

    logger: Logger
    docker_path_of_user: Path

    def __init__(
        self,
        max_file_size: Optional[int] = None,
        enforce_docker_system_prune: bool = False,
        suppress_docker_system_prune: bool = False,
        latest_dev_version: bool = False,
    ) -> None:
        """
        Initialize a StackHandler.

        Args:
            max_file_size: max. multimedia file size allowed by SIPI, in MB (max: 100'000)
            enforce_docker_system_prune: if True, prune Docker without asking the user
            suppress_docker_system_prune: if True, don't prune Docker (and don't ask)
            latest_dev_version: if True, start DSP-API from repo's main branch, instead of the latest deployed version
        """
        self._validate_input(
            max_file_size=max_file_size,
            enforce_docker_system_prune=enforce_docker_system_prune,
            suppress_docker_system_prune=suppress_docker_system_prune,
        )
        self.max_file_size = max_file_size
        self.enforce_docker_system_prune = enforce_docker_system_prune
        self.suppress_docker_system_prune = suppress_docker_system_prune

        self.latest_dev_version = latest_dev_version
        self.url_prefix = self._get_url_prefix()

        self.logger = get_logger(__name__)
        self.docker_path_of_user = Path.home() / Path(".dsp-tools/start-stack")
        self.docker_path_of_user.mkdir(parents=True, exist_ok=True)

    def _validate_input(
        self,
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

    def _get_url_prefix(self) -> str:
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

        If the latest development version of DSP-API is started,
        the URL prefix points to the main branch of the DSP-API repository.

        Returns:
            URL prefix used to retrieve files from the DSP-API repository
        """
        url_prefix_base = "https://github.com/dasch-swiss/dsp-api/raw"

        if self.latest_dev_version:
            return f"{url_prefix_base}/main/"

        config_file = Path("src/dsp_tools/resources/start-stack/start-stack-config.yml")
        if not config_file.is_file():
            return f"{url_prefix_base}/main/"

        with open("src/dsp_tools/resources/start-stack/start-stack-config.yml", "r", encoding="utf-8") as f:
            try:
                start_stack_config = yaml.safe_load(f)
            except yaml.YAMLError:
                start_stack_config = {}
        commit_of_used_api_version = start_stack_config.get("DSP-API commit", "main")
        return f"{url_prefix_base}/{commit_of_used_api_version}/"

    def _copy_resources_to_home_dir(self) -> None:
        """
        On most systems, Docker is not allowed to access files outside of the user's home directory.
        For this reason, copy the contents of the distribution (src/dsp_tools/resources/start-stack)
        to the user's home directory (~/.dsp-tools/start-stack).

        Important: The files of the home directory might have been modified
        by an earlier run of _inject_latest_tag_into_docker_compose_file().
        So, this method must always be called, at every run of start-stack.
        """
        docker_path_of_distribution = importlib.resources.files("dsp_tools").joinpath("resources/start-stack")
        for file in docker_path_of_distribution.iterdir():
            with importlib.resources.as_file(file) as f:
                file_path = Path(f)
            shutil.copy(file_path, self.docker_path_of_user / file.name)

    def _get_sipi_docker_config_lua(self) -> None:
        """
        Retrieve the config file sipi.docker-config.lua from the DSP-API repository,
        and set the max_file_size parameter if necessary.

        Raises:
            UserError: if max_file_size is set but cannot be injected into sipi.docker-config.lua
        """
        docker_config_lua_text = requests.get(f"{self.url_prefix}sipi/config/sipi.docker-config.lua", timeout=5).text
        if self.max_file_size:
            max_post_size_regex = r"max_post_size ?= ?[\'\"]\d+M[\'\"]"
            if not re.search(max_post_size_regex, docker_config_lua_text):
                raise UserError("Unable to set max_file_size. Please try again without this flag.")
            docker_config_lua_text = re.sub(
                max_post_size_regex,
                f"max_post_size = '{self.max_file_size}M'",
                docker_config_lua_text,
            )
        with open(self.docker_path_of_user / "sipi.docker-config.lua", "w", encoding="utf-8") as f:
            f.write(docker_config_lua_text)

    def _start_up_fuseki(self) -> None:
        """
        Start up the Docker container of the fuseki database.

        Raises:
            UserError: if the database cannot be started
        """
        completed_process = subprocess.run(
            "docker compose up db -d",
            shell=True,
            cwd=self.docker_path_of_user,
            check=False,
        )
        if not completed_process or completed_process.returncode != 0:
            msg = "Cannot start the API: Error while executing 'docker compose up db -d'"
            self.logger.error(f"{msg}. completed_process = '{completed_process}'")
            raise UserError(msg)

    def _wait_for_fuseki(self) -> None:
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

    def _create_knora_test_repo(self) -> None:
        """
        Inside fuseki, create the "knora-test" repository.
        This function imitates the behaviour of the script dsp-api/webapi/scripts/fuseki-init-knora-test.sh.

        Raises:
            UserError: in case of failure
        """
        repo_template = requests.get(
            f"{self.url_prefix}webapi/scripts/fuseki-repository-config.ttl.template",
            timeout=5,
        ).text
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
            self.logger.error(f"{msg}. response = {response}")
            raise UserError(msg)

    def _load_data_into_repo(self) -> None:
        """
        Load some basic ontologies and data into the repository.
        This function imitates the behaviour of the script
        dsp-api/webapi/target/docker/stage/opt/docker/scripts/fuseki-init-knora-test.sh.

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
            ttl_text = requests.get(self.url_prefix + ttl_file, timeout=5).text
            response = requests.post(
                url=graph_prefix + graph,
                files={"file": ("file.ttl", ttl_text, "text/turtle; charset: utf-8")},
                auth=("admin", "test"),
                timeout=5,
            )
            if not response.ok:
                self.logger.error(f"Cannot start DSP-API: Error when creating graph '{graph}'. response = {response}")
                raise UserError(f"Cannot start DSP-API: Error when creating graph '{graph}'")

    def _initialize_fuseki(self) -> None:
        """
        Create the "knora-test" repository and load some basic ontologies and data into it.
        """
        self._create_knora_test_repo()
        self._load_data_into_repo()

    def _start_remaining_docker_containers(self) -> None:
        """
        Start the other Docker containers that are not running yet.
        (Fuseki is already running at this point.)
        """
        subprocess.run("docker compose up -d", shell=True, cwd=self.docker_path_of_user, check=True)
        print("DSP-API is now running on http://0.0.0.0:3333/ and DSP-APP on http://0.0.0.0:4200/")

    def _execute_docker_system_prune(self) -> None:
        """
        Depending on the CLI parameters or the user's input,
        execute "docker system prune" or not.
        """
        if self.enforce_docker_system_prune:
            prune_docker = "y"
        elif self.suppress_docker_system_prune:
            prune_docker = "n"
        else:
            prune_docker = None
            while prune_docker not in ["y", "n"]:
                prune_docker = input(
                    "Allow dsp-tools to execute 'docker system prune'? This is necessary to keep your Docker clean. "
                    "If you are unsure what that means, just type y and press Enter. [y/n]"
                )
        if prune_docker == "y":
            subprocess.run("docker system prune -f", shell=True, cwd=self.docker_path_of_user, check=False)

    def _start_docker_containers(self) -> None:
        """
        Start the fuseki Docker container,
        wait until it is up and running,
        load some basic ontologies and data into it,
        start the other Docker containers,
        and execute "docker system prune" if necessary.
        """
        self._start_up_fuseki()
        self._wait_for_fuseki()
        self._initialize_fuseki()
        self._start_remaining_docker_containers()
        self._execute_docker_system_prune()

    def _inject_latest_tag_into_docker_compose_file(self) -> None:
        docker_compose_file = self.docker_path_of_user / "docker-compose.yml"
        if not docker_compose_file.is_file():
            raise BaseError(
                "Cannot inject the 'latest' tag into docker-compose.yml, "
                f"because there is no such file in {self.docker_path_of_user}"
            )

        with open(docker_compose_file, "r", encoding="utf-8") as f:
            try:
                docker_compose_text = yaml.safe_load(f)
            except yaml.YAMLError:
                docker_compose_text = {}
        old_tag = docker_compose_text.get("services", {}).get("api", {}).get("image", "")
        if not re.search(r"daschswiss/knora-api:\d+\.\d+\.\d+", old_tag):
            raise BaseError(f"Invalid tag '{old_tag}' in docker-compose.yml > services > api > image")

        docker_compose_text["services"]["api"]["image"] = "daschswiss/knora-api:latest"
        with open(docker_compose_file, "w", encoding="utf-8") as f:
            yaml.dump(docker_compose_text, f)

    def start_stack(self) -> bool:
        """
        Start the Docker containers of DSP-API and DSP-APP, and load some basic data models and data.
        After startup, ask user if Docker should be pruned or not.

        Raises:
            UserError if the stack cannot be started with the parameters passed by the user

        Returns:
            True if everything went well, False otherwise
        """
        self._copy_resources_to_home_dir()
        if self.latest_dev_version:
            self._inject_latest_tag_into_docker_compose_file()
        self._get_sipi_docker_config_lua()
        self._start_docker_containers()
        return True

    def stop_stack(self) -> bool:
        """
        Shut down the Docker containers of your local DSP stack and delete all data that is in it.

        Returns:
            True if everything went well, False otherwise
        """
        subprocess.run("docker compose down --volumes", shell=True, cwd=self.docker_path_of_user, check=True)
        return True
