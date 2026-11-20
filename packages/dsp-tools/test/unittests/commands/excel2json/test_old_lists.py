import logging

import pytest

from dsp_tools.commands.excel2json.exceptions import InvalidListSectionError
from dsp_tools.commands.excel2json.old_lists import validate_lists_section_with_schema


class TestValidateListsSectionWithSchema:
    def test_invalid_section_logs_and_raises(self, caplog: pytest.LogCaptureFixture) -> None:
        lists_section = [{"name": "list1"}]  # missing required "labels"
        with caplog.at_level(logging.ERROR):
            with pytest.raises(InvalidListSectionError):
                validate_lists_section_with_schema(lists_section)
        assert len(caplog.records) == 1
