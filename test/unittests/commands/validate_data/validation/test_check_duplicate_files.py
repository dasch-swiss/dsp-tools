# mypy: disable-error-code="no-untyped-def"

from pathlib import Path

import pytest

from dsp_tools.cli.args import ValidateDataConfig
from dsp_tools.cli.args import ValidationSeverity
from dsp_tools.commands.validate_data.models.input_problems import DuplicateFileWarning
from dsp_tools.commands.validate_data.models.input_problems import ProblemType
from dsp_tools.commands.validate_data.models.input_problems import Severity
from dsp_tools.commands.validate_data.validation.check_duplicate_files import _get_filepaths_with_more_than_one_usage
from dsp_tools.commands.validate_data.validation.check_duplicate_files import check_for_duplicate_files
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedFileValue
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedFileValueMetadata
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedResource

TEST_ENV_CONFIG = ValidateDataConfig(
    xml_file=Path(),
    save_graph_dir=None,
    severity=ValidationSeverity.INFO,
    ignore_duplicate_files_warning=False,
    is_on_prod_server=False,
    skip_ontology_validation=False,
)

PROD_ENV_CONFIG = ValidateDataConfig(
    xml_file=Path(),
    save_graph_dir=None,
    severity=ValidationSeverity.INFO,
    ignore_duplicate_files_warning=False,
    is_on_prod_server=True,
    skip_ontology_validation=False,
)

FILEPATH_1 = "file_path_1.jpg"
FILEPATH_2 = "file_path_2.jpg"


@pytest.fixture
def file_value_1():
    return ParsedFileValue(FILEPATH_1, None, ParsedFileValueMetadata(None, None, None, None))


@pytest.fixture
def file_value_2():
    return ParsedFileValue(FILEPATH_2, None, ParsedFileValueMetadata(None, None, None, None))


class TestCheckDuplicates:
    def test_no_duplicates(self, file_value_1, file_value_2):
        resources = [
            ParsedResource("no_file", ":type", "lbl", None, [], None, None),
            ParsedResource("file_value_1", ":type", "lbl", None, [], file_value_1, None),
            ParsedResource("file_value_2", ":type", "lbl", None, [], file_value_2, None),
        ]
        result = check_for_duplicate_files(resources)
        assert not result

    def test_one_duplicate(self, file_value_1):
        resources = [
            ParsedResource("no_file", ":type", "lbl", None, [], None, None),
            ParsedResource("id_1", ":type", "lbl", None, [], file_value_1, None),
            ParsedResource("id_2", ":type", "lbl", None, [], file_value_1, None),
        ]
        result = check_for_duplicate_files(resources)
        assert isinstance(result, DuplicateFileWarning)
        assert len(result.problems) == 1
        problem = result.problems.pop(0)
        expected_msg = "value used 2 times"
        assert problem.problem_type == ProblemType.FILE_DUPLICATE
        assert not problem.res_id
        assert not problem.res_type
        assert problem.prop_name == "bitstream / iiif-uri"
        assert problem.severity == Severity.WARNING
        assert problem.message == expected_msg
        assert problem.input_value == file_value_1.value

    def test_several_duplicates(self, file_value_1, file_value_2):
        resources = [
            ParsedResource("no_file", ":type", "lbl", None, [], None, None),
            ParsedResource("file_value_1_1", ":type", "lbl", None, [], file_value_1, None),
            ParsedResource("file_value_1_2", ":type", "lbl", None, [], file_value_1, None),
            ParsedResource("file_value_1_3", ":type", "lbl", None, [], file_value_1, None),
            ParsedResource("file_value_2_1", ":type", "lbl", None, [], file_value_2, None),
            ParsedResource("file_value_2_2", ":type", "lbl", None, [], file_value_2, None),
        ]
        result = check_for_duplicate_files(resources)
        assert isinstance(result, DuplicateFileWarning)
        assert len(result.problems) == 2
        file_1 = next(x for x in result.problems if x.input_value == file_value_1.value)
        assert file_1.message == "value used 3 times"
        file_2 = next(x for x in result.problems if x.input_value == file_value_2.value)
        assert file_2.message == "value used 2 times"


class TestGetFilePathCountDict:
    def test_several_duplicates(self, file_value_1, file_value_2):
        file_1_number = 10
        file_2_number = 2
        resources = [
            ParsedResource(f"id_{i}", ":type", "lbl", None, [], file_value_1, None) for i in range(file_1_number)
        ]
        resources.extend(
            [ParsedResource(f"id_{i}", ":type", "lbl", None, [], file_value_2, None) for i in range(file_2_number)]
        )
        result = _get_filepaths_with_more_than_one_usage(resources)
        assert set(result.keys()) == {FILEPATH_1, FILEPATH_2}
        assert result[FILEPATH_1] == file_1_number
        assert result[FILEPATH_2] == file_2_number

    def test_one_duplicate(self, file_value_1, file_value_2):
        file_1_number = 10
        file_2_number = 1
        resources = [
            ParsedResource(f"id_{i}", ":type", "lbl", None, [], file_value_1, None) for i in range(file_1_number)
        ]
        resources.extend(
            [ParsedResource(f"id_{i}", ":type", "lbl", None, [], file_value_2, None) for i in range(file_2_number)]
        )
        result = _get_filepaths_with_more_than_one_usage(resources)
        assert set(result.keys()) == {FILEPATH_1}
        assert result[FILEPATH_1] == file_1_number

    def test_no_duplicate(self, file_value_1, file_value_2):
        resources = [
            ParsedResource("id_1", ":type", "lbl", None, [], file_value_1, None),
            ParsedResource("id_2", ":type", "lbl", None, [], file_value_2, None),
        ]
        result = _get_filepaths_with_more_than_one_usage(resources)
        assert not result
