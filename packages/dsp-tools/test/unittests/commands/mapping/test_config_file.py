import logging
from pathlib import Path

import pytest

from dsp_tools.commands.mapping.config_file import _parse_yaml
from dsp_tools.commands.mapping.exceptions import InvalidMappingConfigFileError


class TestParseYaml:
    def test_invalid_yaml_logs_and_raises(self, tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
        filepath = tmp_path / "invalid.yaml"
        filepath.write_text("key: [unclosed", encoding="utf-8")
        with caplog.at_level(logging.ERROR):
            with pytest.raises(InvalidMappingConfigFileError):
                _parse_yaml(filepath)
        assert len(caplog.records) == 1
