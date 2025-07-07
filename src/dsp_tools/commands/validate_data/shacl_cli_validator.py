import subprocess
from dataclasses import dataclass
from pathlib import Path

from loguru import logger
from rdflib import SH
from rdflib import Graph

from dsp_tools.commands.validate_data.models.api_responses import SHACLValidationReport
from dsp_tools.commands.validate_data.models.validation import ValidationFilePaths
from dsp_tools.error.exceptions import InternalError
from dsp_tools.error.exceptions import ValidationCliError

DOCKER_IMAGE = "daschswiss/shacl-cli:v0.0.5"


@dataclass
class ShaclCliValidator:
    file_directory: Path

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
            raise ValidationCliError(msg) from None
        return self._parse_validation_result(file_paths.report_file)

    def _run_validate_cli(self, file_paths: ValidationFilePaths) -> None:
        if not file_paths.shacl_file.exists():
            raise InternalError(f"SHACL file not found: {file_paths.shacl_file}")
        if not file_paths.data_file.exists():
            raise InternalError(f"Data file not found: {file_paths.data_file}")

        # Get relative paths within the container
        shacl_path = f"/data/{file_paths.shacl_file.name}"
        data_path = f"/data/{file_paths.data_file.name}"
        report_path = f"/data/{file_paths.report_file.name}"

        d_cmd = (
            f"docker run --rm -v {self.file_directory.absolute()}:/data {DOCKER_IMAGE} "
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

    def _parse_validation_result(self, filepath: Path) -> SHACLValidationReport:
        logger.debug(f"Parse validation response: {filepath}.")
        graph = Graph()
        graph.parse(filepath)
        conforms = bool(next(graph.objects(None, SH.conforms)))
        return SHACLValidationReport(conforms=conforms, validation_graph=graph)
