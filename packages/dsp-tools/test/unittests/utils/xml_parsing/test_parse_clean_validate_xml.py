import logging
from pathlib import Path

import pytest

from dsp_tools.utils.exceptions import XsdValidationError
from dsp_tools.utils.xml_parsing.parse_clean_validate_xml import parse_xml_file


class TestParseXmlFile:
    def test_syntax_error_logs_and_raises(self, tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
        filepath = tmp_path / "invalid.xml"
        filepath.write_text("<root><unclosed></root>", encoding="utf-8")
        with caplog.at_level(logging.ERROR):
            with pytest.raises(XsdValidationError):
                parse_xml_file(filepath)
        assert len(caplog.records) == 1
