import pytest

from dsp_tools.commands.validate_data.constants import MAXIMUM_DUPLICATE_FILE_PATHS
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedFileValue
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedFileValueMetadata
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedResource


@pytest.fixture
def parsed_file_value():
    return ParsedFileValue("file_path.jpg", None, ParsedFileValueMetadata(None, None, None, None))


@pytest.fixture
def too_many_duplicate_files(parsed_file_value):
    return [
        ParsedResource(f"id_{i}", ":type", "lbl", None, [], parsed_file_value, None)
        for i in range(MAXIMUM_DUPLICATE_FILE_PATHS + 1)
    ]


@pytest.fixture
def ok_amount_of_duplicate_files(parsed_file_value):
    return [
        ParsedResource(f"id_{i}", ":type", "lbl", None, [], parsed_file_value, None)
        for i in range(MAXIMUM_DUPLICATE_FILE_PATHS - 1)
    ]
