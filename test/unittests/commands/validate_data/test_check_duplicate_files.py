from pathlib import Path

import pytest

from dsp_tools.cli.args import ValidateDataConfig
from dsp_tools.cli.args import ValidationSeverity
from dsp_tools.commands.validate_data.check_duplicate_files import check_for_duplicate_files
from dsp_tools.commands.validate_data.constants import MAXIMUM_DUPLICATE_FILE_PATHS
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedFileValue
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedFileValueMetadata
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedResource

TEST_ENV_CONFIG = ValidateDataConfig(
    xml_file=Path(),
    save_graph_dir=None,
    severity=ValidationSeverity.INFO,
    ignore_duplicate_files_warning=False,
    is_on_prod_server=False,
)

PROD_ENV_CONFIG = ValidateDataConfig(
    xml_file=Path(),
    save_graph_dir=None,
    severity=ValidationSeverity.INFO,
    ignore_duplicate_files_warning=False,
    is_on_prod_server=True,
)


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


class TestCheckForDuplicateFiles:
    def test_too_many_files_on_test_environment(self, too_many_duplicate_files):
        result = check_for_duplicate_files(too_many_duplicate_files, TEST_ENV_CONFIG)
        expected_msg = ""
        assert result.user_msg == expected_msg
        assert result.should_continue
        assert result.ignore_duplicate_file_shapes

    def test_too_many_files_on_prod_environment(self, too_many_duplicate_files):
        result = check_for_duplicate_files(too_many_duplicate_files, PROD_ENV_CONFIG)
        expected_msg = ""
        assert result.user_msg == expected_msg
        assert not result.should_continue
        assert result.ignore_duplicate_file_shapes

    def test_ok_amount_of_duplicate_files_on_test_environment(self, ok_amount_of_duplicate_files):
        result = check_for_duplicate_files(ok_amount_of_duplicate_files, TEST_ENV_CONFIG)
        assert result.user_msg is None
        assert result.should_continue
        assert not result.ignore_duplicate_file_shapes

    def test_ok_amount_of_duplicate_files_on_prod_environment(self, ok_amount_of_duplicate_files):
        result = check_for_duplicate_files(ok_amount_of_duplicate_files, PROD_ENV_CONFIG)
        assert result.user_msg is None
        assert result.should_continue
        assert not result.ignore_duplicate_file_shapes
