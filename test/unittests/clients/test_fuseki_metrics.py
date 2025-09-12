# mypy: disable-error-code="no-untyped-def"

from unittest.mock import Mock
from unittest.mock import patch

import pytest

from dsp_tools.clients.fuseki_metrics import FusekiMetrics


@patch.object(FusekiMetrics, "_get_size")
def test_get_start_size(mock_get_size: Mock):
    mock_get_size.return_value = 1500
    metrics = FusekiMetrics()
    metrics.try_get_start_size()
    assert metrics.start_size == 1500
    mock_get_size.assert_called_once()


@patch.object(FusekiMetrics, "_get_size")
def test_get_end_size(mock_get_size: Mock):
    mock_get_size.return_value = 2500
    metrics = FusekiMetrics()
    metrics.try_get_end_size()
    assert metrics.end_size == 2500
    mock_get_size.assert_called_once()


@patch.object(FusekiMetrics, "_run_command")
def test_get_size_with_container_id(mock_run_command: Mock):
    mock_run_command.return_value = "1024\t/fuseki"
    metrics = FusekiMetrics(container_id="test_container")
    result = metrics._try_get_size()
    assert result == 1024
    mock_run_command.assert_called_once_with(["docker", "exec", "test_container", "du", "-sb", "/fuseki"])


@patch.object(FusekiMetrics, "_get_container_id")
@patch.object(FusekiMetrics, "_run_command")
def test_get_size_without_container_id_success(mock_run_command: Mock, mock_get_container_id: Mock):
    mock_run_command.return_value = "2048\t/fuseki"

    def set_container_id():
        metrics.container_id = "test_container"

    mock_get_container_id.side_effect = set_container_id
    metrics = FusekiMetrics()
    metrics.container_id = None
    result = metrics._try_get_size()
    mock_get_container_id.assert_called_once()
    assert result == 2048


@patch.object(FusekiMetrics, "_get_container_id")
def test_get_size_no_container_found(mock_get_container_id: Mock):
    metrics = FusekiMetrics()
    metrics.container_id = None
    result = metrics._try_get_size()
    mock_get_container_id.assert_called_once()
    assert result is None


@patch.object(FusekiMetrics, "_run_command")
def test_get_size_command_fails(mock_run_command: Mock):
    mock_run_command.return_value = None
    metrics = FusekiMetrics(container_id="test_container")
    result = metrics._try_get_size()
    assert result is None


@patch("dsp_tools.clients.fuseki_metrics.subprocess.run")
def test_get_size_parsing_value_error(mock_subprocess: Mock):
    mock_result = Mock()
    mock_result.returncode = 0
    mock_result.stdout = "not_a_number\t/fuseki"
    mock_subprocess.return_value = mock_result
    metrics = FusekiMetrics(container_id="test_container")
    result = metrics._try_get_size()
    assert result is None


def test_get_size_empty_command_output():
    with patch.object(FusekiMetrics, "_run_command") as mock_run_command:
        mock_run_command.return_value = ""  # Empty string is falsy, so won't enter parsing
        metrics = FusekiMetrics(container_id="test_container")
        result = metrics._try_get_size()
        assert result is None


@patch.object(FusekiMetrics, "_run_command")
def test_get_container_id_success(mock_run_command: Mock):
    mock_run_command.return_value = "abc123 daschswiss/apache-jena-fuseki:latest\ndef456 other/image:tag"
    metrics = FusekiMetrics()
    metrics._try_get_container_id()
    assert metrics.container_id == "abc123"


@patch.object(FusekiMetrics, "_run_command")
def test_get_container_id_no_fuseki_container(mock_run_command: Mock):
    mock_run_command.return_value = "abc123 other/image:latest\ndef456 another/image:tag"
    metrics = FusekiMetrics()
    metrics._try_get_container_id()
    assert metrics.container_id is None


@patch.object(FusekiMetrics, "_run_command")
def test_get_container_id_command_fails(mock_run_command: Mock):
    mock_run_command.return_value = None
    metrics = FusekiMetrics()
    metrics._try_get_container_id()
    assert metrics.container_id is None


@patch.object(FusekiMetrics, "_run_command")
def test_get_container_id_malformed_output(mock_run_command: Mock):
    mock_run_command.return_value = "abc123\ndef456 daschswiss/apache-jena-fuseki"
    metrics = FusekiMetrics()
    metrics._try_get_container_id()
    assert metrics.container_id == "def456"


@patch.object(FusekiMetrics, "_run_command")
def test_get_container_id_incomplete_line(mock_run_command: Mock):
    mock_run_command.return_value = "abc123\nsingular_element"
    metrics = FusekiMetrics()
    metrics._try_get_container_id()
    assert metrics.container_id is None


def test_integration_workflow_success():
    with patch.object(FusekiMetrics, "_run_command") as mock_run_command:
        mock_run_command.side_effect = [
            "abc123 daschswiss/apache-jena-fuseki:latest",  # docker ps
            "1000\t/fuseki",  # first du command
            "1500\t/fuseki",  # second du command
        ]
        metrics = FusekiMetrics()
        metrics.try_get_start_size()
        metrics.try_get_end_size()
        assert metrics.container_id == "abc123"
        assert metrics.start_size == 1000
        assert metrics.end_size == 1500


def test_integration_workflow_no_container():
    with patch.object(FusekiMetrics, "_run_command") as mock_run_command:
        mock_run_command.return_value = "def456 other/image:latest"

        metrics = FusekiMetrics()
        metrics.try_get_start_size()
        metrics.try_get_end_size()

        assert metrics.container_id is None
        assert metrics.start_size is None
        assert metrics.end_size is None


def test_integration_workflow_command_failure():
    with patch.object(FusekiMetrics, "_run_command") as mock_run_command:
        mock_run_command.side_effect = [
            "abc123 daschswiss/apache-jena-fuseki:latest",  # docker ps succeeds
            None,  # first du command fails
            None,  # second du command fails
        ]

        metrics = FusekiMetrics()
        metrics.try_get_start_size()
        metrics.try_get_end_size()

        assert metrics.container_id == "abc123"
        assert metrics.start_size is None
        assert metrics.end_size is None


if __name__ == "__main__":
    pytest.main([__file__])
