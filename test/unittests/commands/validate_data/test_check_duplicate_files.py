from pathlib import Path

import pytest

from dsp_tools.cli.args import ValidateDataConfig
from dsp_tools.cli.args import ValidationSeverity
from dsp_tools.commands.validate_data.check_duplicate_files import _get_filepath_count_dict
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

FILEPATH_1 = "file_path_1.jpg"
FILEPATH_2 = "file_path_2.jpg"


@pytest.fixture
def file_value_1():
    return ParsedFileValue(FILEPATH_1, None, ParsedFileValueMetadata(None, None, None, None))


@pytest.fixture
def file_value_2():
    return ParsedFileValue(FILEPATH_2, None, ParsedFileValueMetadata(None, None, None, None))


@pytest.fixture
def too_many_duplicate_files(file_value_1):
    return [
        ParsedResource(f"id_{i}", ":type", "lbl", None, [], file_value_1, None)
        for i in range(MAXIMUM_DUPLICATE_FILE_PATHS + 1)
    ]


@pytest.fixture
def ok_amount_of_duplicate_files(file_value_1):
    return [
        ParsedResource(f"id_{i}", ":type", "lbl", None, [], file_value_1, None)
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


def test_get_filepath_count_dict(file_value_1, file_value_2):
    file_1_number = 10
    file_2_number = 2
    resources = [ParsedResource(f"id_{i}", ":type", "lbl", None, [], file_value_1, None) for i in range(file_1_number)]
    resources.extend(
        [ParsedResource(f"id_{i}", ":type", "lbl", None, [], file_value_2, None) for i in range(file_2_number)]
    )
    result = _get_filepath_count_dict(resources)
    assert set(result.keys()) == {FILEPATH_1, FILEPATH_2}
    assert result[FILEPATH_1] == file_1_number
    assert result[FILEPATH_2] == file_2_number
