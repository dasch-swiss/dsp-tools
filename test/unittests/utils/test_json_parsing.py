import logging
from pathlib import Path

import pytest

from dsp_tools.utils.exceptions import JSONFileParsingError
from dsp_tools.utils.json_parsing import parse_json_file


class TestParseJsonFile:
    def test_invalid_json_logs_and_raises(self, tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
        filepath = tmp_path / "invalid.json"
        filepath.write_text("{not valid json", encoding="utf-8")
        with caplog.at_level(logging.ERROR):
            with pytest.raises(JSONFileParsingError):
                parse_json_file(filepath)
        assert len(caplog.records) == 1
