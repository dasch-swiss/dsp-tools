import logging
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from dsp_tools.commands.validate_data.exceptions import ShaclValidationCliError
from dsp_tools.commands.validate_data.exceptions import ShaclValidationOutOfMemoryError
from dsp_tools.commands.validate_data.models.validation import ValidationFilePaths
from dsp_tools.commands.validate_data.shacl_cli_validator import _JAVA_OPTS
from dsp_tools.commands.validate_data.shacl_cli_validator import ShaclCliValidator
from dsp_tools.commands.validate_data.shacl_cli_validator import _get_docker_memory_bytes


def test_docker_command_failure_logs_once_and_suppresses_the_original_traceback(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    (tmp_path / "data.ttl").touch()
    (tmp_path / "shapes.ttl").touch()
    file_paths = ValidationFilePaths(
        directory=tmp_path, data_file="data.ttl", shacl_file="shapes.ttl", report_file="report.ttl"
    )
    called_process_error = subprocess.CalledProcessError(returncode=1, cmd=["docker"], output="stdout", stderr="stderr")
    with patch.object(ShaclCliValidator, "_run_validate_cli", side_effect=called_process_error):
        with caplog.at_level(logging.ERROR):
            with pytest.raises(ShaclValidationCliError) as exc_info:
                ShaclCliValidator().validate(file_paths)
    assert len(caplog.records) == 1
    # `from None` must suppress the chain so the original CalledProcessError's traceback
    # isn't rendered a second time wherever this exception is eventually logged upstream
    assert exc_info.value.__suppress_context__ is True
    assert exc_info.value.__cause__ is None


def _make_file_paths(tmp_path: Path) -> ValidationFilePaths:
    (tmp_path / "data.ttl").touch()
    (tmp_path / "shapes.ttl").touch()
    return ValidationFilePaths(
        directory=tmp_path, data_file="data.ttl", shacl_file="shapes.ttl", report_file="report.ttl"
    )


def test_docker_command_sets_the_java_options(tmp_path: Path) -> None:
    file_paths = _make_file_paths(tmp_path)
    with patch("dsp_tools.commands.validate_data.shacl_cli_validator.subprocess.run") as run:
        ShaclCliValidator()._run_validate_cli(file_paths)
    docker_args = run.call_args.args[0]
    java_opts_index = docker_args.index(f"JAVA_OPTS={_JAVA_OPTS}")
    assert docker_args[java_opts_index - 1] == "-e"
    assert docker_args.index("-e") < docker_args.index("validate")


@pytest.mark.parametrize(
    ("returncode", "stdout", "stderr"),
    [
        (3, "Terminating due to java.lang.OutOfMemoryError: Java heap space", ""),
        (1, "", "Exception in thread main java.lang.OutOfMemoryError: Java heap space"),
        (137, "", ""),
    ],
)
def test_out_of_memory_raises_user_error(tmp_path: Path, returncode: int, stdout: str, stderr: str) -> None:
    file_paths = _make_file_paths(tmp_path)
    called_process_error = subprocess.CalledProcessError(returncode, cmd=["docker"], output=stdout, stderr=stderr)
    with patch.object(ShaclCliValidator, "_run_validate_cli", side_effect=called_process_error):
        with pytest.raises(ShaclValidationOutOfMemoryError, match="memory"):
            ShaclCliValidator().validate(file_paths)


def test_out_of_memory_message_names_the_docker_memory() -> None:
    assert "8.0 GB" in str(ShaclValidationOutOfMemoryError(8 * 1024**3))
    assert "GB" not in str(ShaclValidationOutOfMemoryError(None))


def test_other_docker_failure_raises_internal_error(tmp_path: Path) -> None:
    file_paths = _make_file_paths(tmp_path)
    called_process_error = subprocess.CalledProcessError(1, cmd=["docker"], output="", stderr="no such image")
    with patch.object(ShaclCliValidator, "_run_validate_cli", side_effect=called_process_error):
        with pytest.raises(ShaclValidationCliError):
            ShaclCliValidator().validate(file_paths)


@pytest.mark.parametrize(
    "side_effect",
    [
        OSError("docker not found"),
        subprocess.TimeoutExpired(cmd=["docker"], timeout=10),
        subprocess.CalledProcessError(1, cmd=["docker"]),
    ],
)
def test_docker_memory_is_none_when_docker_info_fails(side_effect: Exception) -> None:
    with patch("dsp_tools.commands.validate_data.shacl_cli_validator.subprocess.run", side_effect=side_effect):
        assert _get_docker_memory_bytes() is None


def test_docker_memory_is_none_when_output_is_not_a_number() -> None:
    completed = subprocess.CompletedProcess(args=["docker"], returncode=0, stdout="unknown\n")
    with patch("dsp_tools.commands.validate_data.shacl_cli_validator.subprocess.run", return_value=completed):
        assert _get_docker_memory_bytes() is None
