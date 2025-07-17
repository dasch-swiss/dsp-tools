from collections import defaultdict

from loguru import logger

from dsp_tools.commands.validate_data.models.input_problems import DuplicateFileWarning
from dsp_tools.commands.validate_data.models.input_problems import InputProblem
from dsp_tools.commands.validate_data.models.input_problems import ProblemType
from dsp_tools.commands.validate_data.models.input_problems import Severity
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedResource


def check_for_duplicate_files(parsed_resources: list[ParsedResource]) -> DuplicateFileWarning | None:
    """
    Too many duplicate filepaths in the data may cause the SHACL validator to crash.
    If one file is referenced n times, this produces n * (n-1) validation errors.
    Therefore, this programmatic pre-validation prevents crashes during later validation steps.

    Args:
        parsed_resources: Resources to check

    Returns:
        Results for the user and decisions how the program should continue
    """
    count_dict = _get_filepaths_with_more_than_one_usage(parsed_resources)
    if not count_dict:
        return None
    input_problems = _create_input_problems(count_dict)
    return DuplicateFileWarning(input_problems)


def _get_filepaths_with_more_than_one_usage(parsed_resources: list[ParsedResource]) -> dict[str, int]:
    count_dict: dict[str, int] = defaultdict(int)
    for res in parsed_resources:
        if res.file_value and res.file_value.value:
            count_dict[res.file_value.value] += 1
    return {f_path: count for f_path, count in count_dict.items() if count > 1}


def _create_input_problems(duplicates: dict[str, int]) -> list[InputProblem]:
    all_duplicates = []
    for dup_entry, usage_count in duplicates.items():
        msg = f"value used {usage_count} times"
        logger.warning(f"File '{dup_entry}' {msg}")
        all_duplicates.append(
            InputProblem(
                problem_type=ProblemType.FILE_DUPLICATE,
                res_id=None,
                res_type=None,
                prop_name="bitstream / iiif-uri",
                severity=Severity.WARNING,
                message=msg,
                input_value=dup_entry,
            )
        )
    return all_duplicates
