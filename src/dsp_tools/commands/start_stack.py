import importlib.resources
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import regex
import requests
import yaml
from loguru import logger

from dsp_tools.models.exceptions import UserError

MAX_FILE_SIZE = 100_000


@dataclass(frozen=True)
class StackConfiguration:
    """
    Groups together configuration information for the StackHandler.

    Args:
        max_file_size: max. multimedia file size allowed for ingest, in MB (max: 100'000)
        enforce_docker_system_prune: if True, prune Docker without asking the user
        suppress_docker_system_prune: if True, don't prune Docker (and don't ask)
        latest_dev_version: if True, start DSP-API from repo's main branch, instead of the latest deployed version
        api_version_for_validate: if True a fixed API version is taken that has the features necessary for validate-data
    """

    max_file_size: Optional[int] = None
    enforce_docker_system_prune: bool = False
    suppress_docker_system_prune: bool = False
    latest_dev_version: bool = False
    upload_test_data: bool = False
    api_version_for_validate: bool = False

    def __post_init__(self) -> None:
        """
        Validate the input parameters passed by the user.

        Raises:
            UserError: if one of the parameters is invalid
        """
        if self.max_file_size is not None and not 1 <= self.max_file_size <= MAX_FILE_SIZE:
            raise UserError(f"max_file_size must be between 1 and {MAX_FILE_SIZE}")
        if self.enforce_docker_system_prune and self.suppress_docker_system_prune:
            raise UserError('The arguments "--prune" and "--no-prune" are mutually exclusive')


class StackHandler:
    """This class contains functions to start and stop the Docker containers of DSP-API and DSP-APP."""

    __stack_configuration: StackConfiguration
    __url_prefix: str
    __docker_path_of_user: Path
    __localhost_url = "http://0.0.0.0"

    def __init__(self, stack_configuration: StackConfiguration) -> None:
        """
        Initialize a StackHandler with a StackConfiguration

        Args:
            stack_configuration: configuration information for the StackHandler
        """
        self.__stack_configuration = stack_configuration
        self.__url_prefix = self._get_url_prefix()
        self.__docker_path_of_user = Path.home() / Path(".dsp-tools/start-stack")
        self.__docker_path_of_user.mkdir(parents=True, exist_ok=True)

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

        if self.__stack_configuration.latest_dev_version:
            return f"{url_prefix_base}/main/"

        config_file = importlib.resources.files("dsp_tools").joinpath("resources/start-stack/start-stack-config.yml")
        start_stack_config = yaml.safe_load(config_file.read_bytes())
        commit_of_used_api_version = start_stack_config["DSP-API commit"]
        return f"{url_prefix_base}/{commit_of_used_api_version}/"

    def _copy_resources_to_home_dir(self) -> None:
        """
        On most systems, Docker is not allowed to access files outside of the user's home directory.
        For this reason, copy the contents of the distribution (src/dsp_tools/resources/start-stack)
        to the user's home directory (~/.dsp-tools/start-stack).

        Important: The files of the home directory might have been modified
        by an earlier run of this method.
        So, this method must always be called, at every run of start-stack.
        """
        docker_path_of_distribution = importlib.resources.files("dsp_tools").joinpath("resources/start-stack")
        for file in docker_path_of_distribution.iterdir():
            with importlib.resources.as_file(file) as f:
                file_path = Path(f)
            shutil.copy(file_path, self.__docker_path_of_user / file.name)
        if not self.__stack_configuration.latest_dev_version:
            Path(self.__docker_path_of_user / "docker-compose.override.yml").unlink()
        if not self.__stack_configuration.api_version_for_validate:
            Path(self.__docker_path_of_user / "docker-compose-validation.yml").unlink()

    def _get_sipi_docker_config_lua(self) -> None:
        """
        Retrieve the config file sipi.docker-config.lua from the DSP-API repository,
        and set the max_file_size parameter if necessary.

        Raises:
            UserError: if max_file_size is set but cannot be injected into sipi.docker-config.lua
        """
        docker_config_lua_response = requests.get(f"{self.__url_prefix}sipi/config/sipi.docker-config.lua", timeout=30)
        docker_config_lua_text = docker_config_lua_response.text
        if self.__stack_configuration.max_file_size:
            max_post_size_regex = r"max_post_size ?= ?[\'\"]?\d+[MG][\'\"]?"
            if not regex.search(max_post_size_regex, docker_config_lua_text):
                raise UserError("Unable to set max_file_size. Please try again without this flag.")
            docker_config_lua_text = regex.sub(
                max_post_size_regex,
                f"max_post_size = '{self.__stack_configuration.max_file_size}M'",
                docker_config_lua_text,
            )
        with open(self.__docker_path_of_user / "sipi.docker-config.lua", "w", encoding="utf-8") as f:
            f.write(docker_config_lua_text)

    def _start_up_fuseki(self) -> None:
        """
        Start up the Docker container of the fuseki database.

        Raises:
            UserError: if the database cannot be started
        """
        cmd = "docker compose up db -d".split()
        completed_process = subprocess.run(cmd, cwd=self.__docker_path_of_user, check=False)
        if not completed_process or completed_process.returncode != 0:
            msg = "Cannot start the API: Error while executing 'docker compose up db -d'"
            logger.error(f"{msg}. completed_process = '{vars(completed_process)}'")
            raise UserError(msg)

    def _wait_for_fuseki(self) -> None:
        """
        Wait up to 6 minutes, until the fuseki database is up and running.
        This function imitates the behaviour of the script dsp-api/webapi/scripts/wait-for-db.sh.
        """
        for _ in range(6 * 60):
            try:
                response = requests.get(f"{self.__localhost_url}:3030/$/server", auth=("admin", "test"), timeout=10)
                if response.ok:
                    break
            except Exception:  # noqa: BLE001 (blind-except)
                time.sleep(1)
            time.sleep(1)

    def _create_knora_test_repo(self) -> None:
        """
        Inside fuseki, create the "knora-test" repository.
        This function imitates the behaviour of the script dsp-api/webapi/scripts/fuseki-init-knora-test.sh.

        Raises:
            UserError: in case of failure
        """
        repo_template_response = requests.get(
            f"{self.__url_prefix}webapi/scripts/fuseki-repository-config.ttl.template",
            timeout=30,
        )
        repo_template = repo_template_response.text
        repo_template = repo_template.replace("@REPOSITORY@", "knora-test")
        response = requests.post(
            f"{self.__localhost_url}:3030/$/datasets",
            files={"file": ("file.ttl", repo_template, "text/turtle; charset=utf8")},
            auth=("admin", "test"),
            timeout=30,
        )
        if not response.ok:
            msg = (
                "Cannot start DSP-API: Error when creating the 'knora-test' repository. "
                "Is DSP-API perhaps running already?"
            )
            logger.error(f"{msg}. response = {vars(response)}")
            raise UserError(msg)

    def _load_data_into_repo(self) -> None:
        """
        Load some basic ontologies and data into the repository.
        This function imitates the behaviour of the script
        dsp-api/webapi/target/docker/stage/opt/docker/scripts/fuseki-init-knora-test.sh.

        Raises:
            UserError: if one of the graphs cannot be created
        """
        graph_prefix = f"{self.__localhost_url}:3030/knora-test/data?graph="
        ttl_files = [
            ("webapi/src/main/resources/knora-ontologies/knora-admin.ttl", "http://www.knora.org/ontology/knora-admin"),
            ("webapi/src/main/resources/knora-ontologies/knora-base.ttl", "http://www.knora.org/ontology/knora-base"),
            ("webapi/src/main/resources/knora-ontologies/standoff-onto.ttl", "http://www.knora.org/ontology/standoff"),
            ("webapi/src/main/resources/knora-ontologies/standoff-data.ttl", "http://www.knora.org/data/standoff"),
            ("webapi/src/main/resources/knora-ontologies/salsah-gui.ttl", "http://www.knora.org/ontology/salsah-gui"),
            ("test_data/project_data/admin-data.ttl", "http://www.knora.org/data/admin"),
            ("test_data/project_data/permissions-data.ttl", "http://www.knora.org/data/permissions"),
            ("test_data/project_ontologies/anything-onto.ttl", "http://www.knora.org/ontology/0001/anything"),
            ("test_data/project_data/anything-data.ttl", "http://www.knora.org/data/0001/anything"),
        ]
        for ttl_file, graph in ttl_files:
            ttl_response = requests.get(self.__url_prefix + ttl_file, timeout=30)
            if not ttl_response.ok:
                msg = f"Cannot start DSP-API: Error when retrieving '{self.__url_prefix + ttl_file}'"
                logger.error(f"{msg}'. response = {vars(ttl_response)}")
                raise UserError(msg)
            ttl_text = ttl_response.text
            response = requests.post(
                graph_prefix + graph,
                files={"file": ("file.ttl", ttl_text, "text/turtle; charset: utf-8")},
                auth=("admin", "test"),
                timeout=30,
            )
            if not response.ok:
                logger.error(f"Cannot start DSP-API: Error when creating graph '{graph}'. response = {vars(response)}")
                raise UserError(f"Cannot start DSP-API: Error when creating graph '{graph}'")

    def _create_admin_user(self) -> None:
        """
        This function adds the default system admin user to the database.
        The password is the hash for "test".

        Raises:
            UserError: If the user cannot be created.
        """
        graph_prefix = f"{self.__localhost_url}:3030/knora-test/data?graph="
        admin_graph = "http://www.knora.org/data/admin"
        admin_user = """
        @prefix xsd:         <http://www.w3.org/2001/XMLSchema#> .
        @prefix rdf:         <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
        @prefix knora-admin: <http://www.knora.org/ontology/knora-admin#> .
        
        <http://rdfh.ch/users/root>
        rdf:type                         knora-admin:User ;
        knora-admin:username             "root"^^xsd:string ;
        knora-admin:email                "root@example.com"^^xsd:string ;
        knora-admin:givenName            "System"^^xsd:string ;
        knora-admin:familyName           "Administrator"^^xsd:string ;
        knora-admin:password             "$2a$12$7XEBehimXN1rbhmVgQsyve08.vtDmKK7VMin4AdgCEtE4DWgfQbTK"^^xsd:string ;
        knora-admin:phone                "123456"^^xsd:string ;
        knora-admin:preferredLanguage    "en"^^xsd:string ;
        knora-admin:status               "true"^^xsd:boolean ;
        knora-admin:isInSystemAdminGroup "true"^^xsd:boolean .
        """
        response = requests.post(
            graph_prefix + admin_graph,
            files={"file": ("file.ttl", admin_user, "text/turtle; charset: utf-8")},
            auth=("admin", "test"),
            timeout=30,
        )
        if not response.ok:
            logger.error(f"Cannot start DSP-API: Error when creating the admin user. response = {vars(response)}")
            raise UserError("Cannot start DSP-API: Error when creating the admin user.")

    def _initialize_fuseki(self) -> None:
        """
        Create the "knora-test" repository and load some basic ontologies and data into it.
        """
        self._create_knora_test_repo()
        if self.__stack_configuration.upload_test_data:
            self._load_data_into_repo()
        else:
            self._create_admin_user()

    def _start_remaining_docker_containers(self) -> None:
        """
        Start the other Docker containers that are not running yet.
        (Fuseki is already running at this point.)
        """
        compose_str = "docker compose -f docker-compose.yml"
        if self.__stack_configuration.latest_dev_version:
            subprocess.run("docker compose pull".split(), cwd=self.__docker_path_of_user, check=True)
            compose_str += " -f docker-compose.override.yml"
        elif self.__stack_configuration.api_version_for_validate:
            compose_str += " -f docker-compose-validation.yml"
        compose_str += " up -d"
        subprocess.run(compose_str.split(), cwd=self.__docker_path_of_user, check=True)

    def _wait_for_api(self) -> None:
        """
        Wait until the API is up and running.
        This mimicks the behaviour of the script webapi/scripts/wait-for-api.sh in the DSP-API repository.
        """
        for _ in range(6 * 60):
            try:
                response = requests.get(f"{self.__localhost_url}:3333/health", timeout=1)
                if not response.ok:
                    time.sleep(1)
                    continue
            except requests.exceptions.RequestException:
                time.sleep(1)
                continue
        print(f"DSP-API is now running on {self.__localhost_url}:3333/ and DSP-APP on {self.__localhost_url}:4200/")

    def _execute_docker_system_prune(self) -> None:
        """
        Depending on the CLI parameters or the user's input,
        execute "docker system prune" or not.
        """
        if self.__stack_configuration.enforce_docker_system_prune:
            prune_docker = "y"
        elif self.__stack_configuration.suppress_docker_system_prune:
            prune_docker = "n"
        else:
            prune_docker = None
            while prune_docker not in ["y", "n"]:
                prune_docker = input(
                    "Allow dsp-tools to execute 'docker system prune'? \n"
                    "If you press 'y', all unused containers, networks, and images (both dangling and unused) "
                    "in your docker will be deleted.\n"
                    "It is recommended that you do this every once in a while "
                    "to keep your docker clean and running smoothly. [y/n]"
                )
        if prune_docker == "y":
            subprocess.run("docker system prune --volumes -f".split(), cwd=self.__docker_path_of_user, check=False)

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
        self._wait_for_api()
        self._execute_docker_system_prune()

    def start_stack(self) -> bool:
        """
        Start the Docker containers of DSP-API and DSP-APP, and load some basic data models and data.
        After startup, ask user if Docker should be pruned or not.

        Raises:
            UserError: if the stack cannot be started with the parameters passed by the user

        Returns:
            True if everything went well, False otherwise
        """
        if subprocess.run("docker stats --no-stream".split(), check=False, capture_output=True).returncode != 0:
            raise UserError("Docker is not running properly. Please start Docker and try again.")
        self._copy_resources_to_home_dir()
        self._get_sipi_docker_config_lua()
        self._start_docker_containers()
        return True

    def stop_stack(self) -> bool:
        """
        Shut down the Docker containers of your local DSP stack and delete all data that is in it.

        Returns:
            True if everything went well, False otherwise
        """
        subprocess.run("docker compose down --volumes".split(), cwd=self.__docker_path_of_user, check=True)
        return True
