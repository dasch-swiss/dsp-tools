import subprocess
from dataclasses import dataclass
from pathlib import Path

from loguru import logger

from dsp_tools.error.exceptions import InternalError

DOCKER_IMAGE = "daschswiss/shacl-cli:latest"


@dataclass
class ShaclDockerValidator:
    file_directory: Path
    container_id: str | None = None

    def validate(self, shacl_file: Path, data_file: Path, report_file: Path) -> None:
        """
        Run SHACL validation on the provided files.

        Args:
            shacl_file: Path to the SHACL shapes file
            data_file: Path to the RDF data file
            report_file: Path where validation report should be saved

        Returns:
            True if validation completed successfully, False otherwise.
        """
        if not self.container_id:
            raise InternalError("Container not started. Call start_container() first.")
        try:
            if not shacl_file.exists():
                raise InternalError(f"SHACL file not found: {shacl_file}")
            if not data_file.exists():
                raise InternalError(f"Data file not found: {data_file}")

            # Get relative paths within the container
            shacl_path = f"/data/{shacl_file.name}"
            data_path = f"/data/{data_file.name}"
            report_path = f"/data/{report_file.name}"

            logger.debug(f"Running SHACL validation: {shacl_file.name} -> {data_file.name}")
            result = subprocess.run(
                f"docker exec {self.container_id} validate "
                f"--shacl {shacl_path} --data {data_path} --report {report_path}",
                capture_output=True,
                text=True,
                check=True,
            )
            logger.debug(f"Validation completed. Report saved to: {report_file}")
            if result.stdout:
                logger.debug(f"Validation output: {result.stdout}")
        except subprocess.CalledProcessError as e:
            raise InternalError(f"SHACL validation failed: {e.stderr}")

    def run_multiple_validations(self, validation_configs: list[dict]) -> None:
        """
        Run multiple SHACL validations without restarting the container.

        Args:
            validation_configs: List of dictionaries with keys:
                - shacl_file: Path to SHACL shapes file
                - data_file: Path to RDF data file
                - report_file: Path for validation report

        Returns:
            List of boolean results for each validation.
        """
        for i, config in enumerate(validation_configs, 1):
            logger.debug(f"Running validation {i}/{len(validation_configs)}")
            self.validate(
                shacl_file=config["shacl_file"],
                data_file=config["data_file"],
                report_file=config["report_file"],
            )

    def __enter__(self):
        """Context manager entry - start the container automatically."""
        if not self._start_container():
            raise RuntimeError("Failed to start SHACL validation container")
        return self

    def _start_container(self) -> None:
        try:
            if not self._local_image_exists():
                if not self._pull_image():
                    raise InternalError("Image could not be pulled.")
            logger.debug("Starting SHACL validation container")
            result = subprocess.run(
                f"docker run -d -v {self.file_directory.absolute()}:/data "
                f"--name shacl-validator {DOCKER_IMAGE} tail -f /dev/null".split(),
                capture_output=True,
                text=True,
                check=True,
            )
            self.container_id = result.stdout.strip()
            logger.debug(f"Container started with ID: {self.container_id}")
        except subprocess.CalledProcessError as e:
            raise InternalError(f"Failed to start container: {e.stderr}")

    def _local_image_exists(self) -> bool:
        try:
            subprocess.run(
                f"docker image inspect {DOCKER_IMAGE}".split(),
                capture_output=True,
                text=True,
                check=True,
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def _pull_image(self) -> bool:
        try:
            logger.debug(f"Pulling Docker image: {DOCKER_IMAGE}")
            subprocess.run(
                f"docker pull {DOCKER_IMAGE}",
                capture_output=True,
                text=True,
                check=True,
            )
            logger.debug("Docker image pulled successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to pull Docker image: {e.stderr}")
            return False

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - stop the container automatically."""
        self._stop_container()

    def _stop_container(self) -> None:
        if not self.container_id:
            logger.warning("No container to stop")
        try:
            logger.debug(f"Stopping container: {self.container_id}")
            subprocess.run(
                f"docker stop {self.container_id}".split(),
                capture_output=True,
                text=True,
                check=True,
            )
            subprocess.run(
                f"docker rm {self.container_id}".split(),
                capture_output=True,
                text=True,
                check=True,
            )
            logger.debug("Container stopped and removed")
            self.container_id = None
        except subprocess.CalledProcessError as e:
            raise InternalError(f"Failed to stop container: {e.stderr}")
