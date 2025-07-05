import subprocess
from dataclasses import dataclass
from pathlib import Path

from loguru import logger

from dsp_tools.commands.validate_data.models.validation import ValidationFilePaths
from dsp_tools.error.exceptions import InternalError

DOCKER_IMAGE = "daschswiss/shacl-cli:latest"


@dataclass
class ShaclDockerValidator:
    file_directory: Path
    container_id: str | None = None

    def start_container(self) -> None:
        try:
            if not self._local_image_exists():
                if not self._pull_image():
                    raise InternalError("Image could not be pulled.")
            d_cmd = (
                f"docker run -d -v {self.file_directory.absolute()}:/data "
                f"--name shacl-validator {DOCKER_IMAGE} tail -f /dev/null"
            )
            logger.debug(f"Starting SHACL validation container: {d_cmd}")
            result = subprocess.run(
                d_cmd.split(),
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
                f"docker pull {DOCKER_IMAGE}".split(),
                capture_output=True,
                text=True,
                check=True,
            )
            logger.debug("Docker image pulled successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to pull Docker image: {e.stderr}")
            return False

    def stop_container(self) -> None:
        if not self.container_id:
            logger.warning("No container to stop")
        try:
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
            logger.debug(f"Container '{self.container_id}' stopped and removed")
            self.container_id = None
        except subprocess.CalledProcessError as e:
            raise InternalError(f"Failed to stop container: {e.stderr}")

    def validate(self, file_paths: ValidationFilePaths) -> None:
        if not self.container_id:
            raise InternalError("Container not started. Call start_container() first.")
        try:
            if not file_paths.shacl_file.exists():
                raise InternalError(f"SHACL file not found: {file_paths.shacl_file}")
            if not file_paths.data_file.exists():
                raise InternalError(f"Data file not found: {file_paths.data_file}")

            # Get relative paths within the container
            shacl_path = f"/data/{file_paths.shacl_file.name}"
            data_path = f"/data/{file_paths.data_file.name}"
            report_path = f"/data/{file_paths.report_file.name}"

            d_cmd = [
                "docker",
                "exec",
                self.container_id,
                "sh",
                "-c",
                f"validate --shacl {shacl_path} --data {data_path} --report {report_path}",
            ]
            logger.debug(f"Running SHACL validation: {d_cmd}")
            result = subprocess.run(
                d_cmd,
                capture_output=True,
                text=True,
                check=True,
            )
            logger.debug(f"Validation completed. Report saved to: {file_paths.report_file}")
            if result.stdout:
                logger.debug(f"Validation output: {result.stdout}")
        except subprocess.CalledProcessError as e:
            raise InternalError(f"SHACL validation failed: {e.stderr}")
