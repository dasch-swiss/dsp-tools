import importlib.resources
import os
import subprocess
from pathlib import Path

import yaml
from loguru import logger
from rdflib import SH
from rdflib import Graph

from dsp_tools.commands.validate_data.exceptions import ShaclValidationCliError
from dsp_tools.commands.validate_data.exceptions import ShaclValidationError
from dsp_tools.commands.validate_data.exceptions import ShaclValidationOutOfMemoryError
from dsp_tools.commands.validate_data.models.api_responses import SHACLValidationReport
from dsp_tools.commands.validate_data.models.validation import ValidationFilePaths

# As of 2026-10 (shacl-cli v0.0.6), the image's launcher passes JAVA_OPTS to the JVM, whose default heap is 25 %
# of the container memory. 50 % leaves room for a local DSP stack in the same Docker VM.
# ExitOnOutOfMemoryError turns an out-of-memory error into a recognisable exit, see `_ran_out_of_memory`.
_JAVA_OPTS = "-XX:MaxRAMPercentage=50 -XX:+ExitOnOutOfMemoryError"
_KILLED_EXIT_CODE = 137


class ShaclCliValidator:
    def validate(self, file_paths: ValidationFilePaths) -> SHACLValidationReport:
        try:
            self._run_validate_cli(file_paths)
        except subprocess.CalledProcessError as e:
            stdout = e.stdout or ""
            stderr = e.stderr or ""
            logger.exception(f"Docker command failed with {e.returncode}: stdout={stdout!r}, stderr={stderr!r}")
            if _ran_out_of_memory(e.returncode, stdout, stderr):
                raise ShaclValidationOutOfMemoryError(_get_docker_memory_bytes()) from None
            raise ShaclValidationCliError(e.returncode, stdout, stderr) from None
        return self._parse_validation_result(file_paths.directory / file_paths.report_file)

    def _run_validate_cli(self, file_paths: ValidationFilePaths) -> None:
        if not (file_paths.directory / file_paths.shacl_file).exists():
            raise ShaclValidationError(f"SHACL file not found: {file_paths.shacl_file}")
        if not (file_paths.directory / file_paths.data_file).exists():
            raise ShaclValidationError(f"Data file not found: {file_paths.data_file}")

        # Get relative paths within the container
        shacl_path = f"/data/{file_paths.shacl_file}"
        data_path = f"/data/{file_paths.data_file}"
        report_path = f"/data/{file_paths.report_file}"

        docker_file = importlib.resources.files("dsp_tools").joinpath("resources/validate_data/shacl-cli-image.yml")
        docker_spec = yaml.safe_load(docker_file.read_bytes())
        docker_image = docker_spec["image"]

        user_flag = ["--user", str(os.getuid())] if hasattr(os, "getuid") else []
        d_cmd = [
            "docker",
            "run",
            "--rm",
            *user_flag,
            "-e",
            f"JAVA_OPTS={_JAVA_OPTS}",
            "-v",
            f"{file_paths.directory.absolute()}:/data:z",
            docker_image,
            "validate",
            "--shacl",
            shacl_path,
            "--data",
            data_path,
            "--report",
            report_path,
        ]
        logger.debug(f"Running SHACL validation: {' '.join(d_cmd)}")
        result = subprocess.run(
            d_cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        if result.stdout:
            logger.debug(f"Validation output: {result.stdout}")
        if result.stderr:
            logger.error(f"Validation output error: {result.stderr}")

    def _parse_validation_result(self, filepath: Path) -> SHACLValidationReport:
        if not filepath.exists():
            raise ShaclValidationError(f"SHACL file not found: {filepath}")
        logger.debug(f"Parse validation response: {filepath}.")
        graph = Graph(store="Oxigraph")
        graph.parse(filepath)
        conforms = bool(next(graph.objects(None, SH.conforms)))
        return SHACLValidationReport(conforms=conforms, validation_graph=graph)


def _ran_out_of_memory(returncode: int, stdout: str, stderr: str) -> bool:
    # Exit code 137 means the container was killed (SIGKILL), usually by the out-of-memory killer.
    return returncode == _KILLED_EXIT_CODE or "java.lang.OutOfMemoryError" in f"{stdout}{stderr}"


def _get_docker_memory_bytes() -> int | None:
    try:
        result = subprocess.run(
            ["docker", "info", "--format", "{{.MemTotal}}"],  # noqa: S607 (docker is looked up on the PATH)
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
        return int(result.stdout.strip())
    except (subprocess.SubprocessError, OSError, ValueError):
        return None
