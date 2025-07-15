from collections import defaultdict

from dsp_tools.commands.validate_data.constants import MAXIMUM_DUPLICATE_FILE_PATHS
from dsp_tools.commands.validate_data.models.input_problems import DuplicateFileWarnings
from dsp_tools.commands.validate_data.models.input_problems import InputProblem
from dsp_tools.commands.validate_data.models.input_problems import ProblemType
from dsp_tools.commands.validate_data.models.input_problems import Severity
from dsp_tools.commands.validate_data.models.validation import DuplicateFileResult
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedResource


def check_for_duplicate_files(parsed_resources: list[ParsedResource]) -> DuplicateFileWarnings | None:
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
    return DuplicateFileWarnings(input_problems)


def _get_filepaths_with_more_than_one_usage(parsed_resources: list[ParsedResource]) -> dict[str, int]:
    count_dict: dict[str, int] = defaultdict(int)
    for res in parsed_resources:
        if res.file_value and res.file_value.value:
            count_dict[res.file_value.value] += 1
    return {f_path: count for f_path, count in count_dict.items() if count > 1}


def _create_input_problems(duplicates: dict[str, int]) -> list[InputProblem]:
    all_duplicates = []
    for dup_entry, usage_count in duplicates.items():
        msg = f"{usage_count} entries for this value."
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


def _determine_if_max_count_has_been_reached(path_count: dict[str, int]) -> bool:
    return any([cnt > MAXIMUM_DUPLICATE_FILE_PATHS for cnt in path_count.values()])


def _determine_duplicate_file_result(
    count_dict: dict[str, int], max_count_of_duplicates_reached: bool, is_on_prod_server: bool
) -> DuplicateFileResult:
    if not max_count_of_duplicates_reached:
        return DuplicateFileResult(
            user_msg=None,
            duplicate_files_must_be_ignored=False,
            should_continue=True,
        )
    msg = _get_duplicate_msg(count_dict, is_on_prod_server)
    should_continue = not is_on_prod_server
    return DuplicateFileResult(
        user_msg=msg,
        duplicate_files_must_be_ignored=True,
        should_continue=should_continue,
    )


def _get_duplicate_msg(count_dict: dict[str, int], is_on_prod: bool) -> str:
    file_paths = sorted([f"{count} - '{path}'" for path, count in count_dict.items()])
    msg = (
        f"{len(count_dict)} file(s) were used multiple times in your data. "
        f"Due to the large number of duplicates they cannot be included in the schema validation.\n"
    )
    if is_on_prod:
        msg += (
            "Since you are on a production server, the validation or xmlupload cannot continue. "
            "If you wish to upload duplicate images, use the designated flag to ignore them."
        )
    else:
        msg += (
            "Since you are on a test environment, "
            "the validation or xmlupload will continue without the duplicate check. "
            "Please note that this is not allowed on a production server."
        )
    msg += (
        f"\nThe following filepaths are used more than once, "
        f"result displayed as: file count - 'file path'\n{' | '.join(file_paths)}"
    )
    return msg
