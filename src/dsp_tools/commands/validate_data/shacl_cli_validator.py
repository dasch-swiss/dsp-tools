import importlib.resources
import subprocess
from pathlib import Path

import yaml
from loguru import logger
from rdflib import SH
from rdflib import Graph

from dsp_tools.commands.validate_data.models.api_responses import SHACLValidationReport
from dsp_tools.commands.validate_data.models.validation import ValidationFilePaths
from dsp_tools.error.exceptions import InternalError
from dsp_tools.error.exceptions import ShaclValidationCliError


class ShaclCliValidator:
    def validate(self, file_paths: ValidationFilePaths) -> SHACLValidationReport:
        try:
            self._run_validate_cli(file_paths)
        except subprocess.CalledProcessError as e:
            logger.error(e)
            msg = (
                "Data validation requires Docker. Is your Docker Desktop Application open? "
                "If it is, please contact the DSP-TOOLS development team with your log file."
            )
            logger.error(msg)
            raise ShaclValidationCliError(msg) from None
        return self._parse_validation_result(file_paths.directory / file_paths.report_file)

    def _run_validate_cli(self, file_paths: ValidationFilePaths) -> None:
        if not (file_paths.directory / file_paths.shacl_file).exists():
            raise InternalError(f"SHACL file not found: {file_paths.shacl_file}")
        if not (file_paths.directory / file_paths.data_file).exists():
            raise InternalError(f"Data file not found: {file_paths.data_file}")

        # Get relative paths within the container
        shacl_path = f"/data/{file_paths.shacl_file}"
        data_path = f"/data/{file_paths.data_file}"
        report_path = f"/data/{file_paths.report_file}"

        docker_file = importlib.resources.files("dsp_tools").joinpath("resources/validate_data/shacl-cli-image.yml")
        docker_spec = yaml.safe_load(docker_file.read_bytes())
        docker_image = docker_spec["image"]

        d_cmd = (
            f"docker run --rm -v {file_paths.directory.absolute()}:/data {docker_image} "
            f"validate --shacl {shacl_path} --data {data_path} --report {report_path}"
        )
        logger.debug(f"Running SHACL validation: {d_cmd}")
        result = subprocess.run(
            d_cmd.split(),
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
            raise InternalError(f"SHACL file not found: {filepath}")
        logger.debug(f"Parse validation response: {filepath}.")
        graph = Graph()
        graph.parse(filepath)
        conforms = bool(next(graph.objects(None, SH.conforms)))
        return SHACLValidationReport(conforms=conforms, validation_graph=graph)
