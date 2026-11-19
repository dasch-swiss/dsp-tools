from pathlib import Path
from unittest.mock import Mock
from unittest.mock import patch

from dsp_tools.commands.xmlupload.upload_config import UploadConfig
from dsp_tools.commands.xmlupload.xmlupload import _handle_validation

VALIDATE_TARGET = "dsp_tools.commands.xmlupload.xmlupload.validate_parsed_resources"
STDIN_TARGET = "dsp_tools.utils.interactive.stdin_is_interactive"


class TestSkipValidationPrompt:
    def test_non_interactive_defaults_to_skip(self) -> None:
        config = UploadConfig(skip_validation=True)
        with patch(VALIDATE_TARGET) as validate_mock:
            with patch(STDIN_TARGET, return_value=False):
                with patch("builtins.input", side_effect=AssertionError("input() must not be called")):
                    result = _handle_validation(
                        parsed_resources=[],
                        lookups=Mock(),
                        config=config,
                        is_on_prod_like_server=True,
                        auth=Mock(),
                        input_file=Path("data.xml"),
                    )
        assert result is True
        validate_mock.assert_not_called()

    def test_interactive_no_runs_validation(self) -> None:
        config = UploadConfig(skip_validation=True)
        lookups = Mock()
        lookups.authorships = {}
        lookups.permissions = {}
        with patch(VALIDATE_TARGET, return_value=True) as validate_mock:
            with patch(STDIN_TARGET, return_value=True):
                with patch("builtins.input", return_value="no"):
                    result = _handle_validation(
                        parsed_resources=[],
                        lookups=lookups,
                        config=config,
                        is_on_prod_like_server=True,
                        auth=Mock(),
                        input_file=Path("data.xml"),
                    )
        assert result is True
        validate_mock.assert_called_once()


class TestIgnoreDuplicateFilesPrompt:
    def test_non_interactive_keeps_ignore_duplicates(self) -> None:
        config = UploadConfig(skip_validation=False, ignore_duplicate_files_warning=True)
        lookups = Mock()
        lookups.authorships = {}
        lookups.permissions = {}
        with patch(VALIDATE_TARGET, return_value=True) as validate_mock:
            with patch(STDIN_TARGET, return_value=False):
                with patch("builtins.input", side_effect=AssertionError("input() must not be called")):
                    result = _handle_validation(
                        parsed_resources=[],
                        lookups=lookups,
                        config=config,
                        is_on_prod_like_server=True,
                        auth=Mock(),
                        input_file=Path("data.xml"),
                    )
        assert result is True
        validate_mock.assert_called_once()
        assert validate_mock.call_args.kwargs["config"].ignore_duplicate_files_warning is True
