from dsp_tools.cli.args import ValidateDataConfig
from dsp_tools.commands.validate_data.models.validation import DuplicateFileResult
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedResource


def check_for_duplicate_files(
    parsed_resources: list[ParsedResource], config: ValidateDataConfig
) -> DuplicateFileResult:
    """
    Too many duplicate filepaths in the data may cause the SHACL validator to crash.
    If one file is referenced n times, this produces n * (n-1) validation errors.
    Therefore, this programmatic pre-validation prevents crashes during later validation steps.

    Args:
        parsed_resources: Resources to check
        config: Validate data config

    Returns:
        Results for the user and decisions how the program should continue
    """
    count_dict = _get_filepath_with_more_than_one_usage(parsed_resources)


def _get_filepath_with_more_than_one_usage(parsed_resources: list[ParsedResource]) -> dict[str, int]:
    pass


def _determine_if_the_validation_should_continue(
    is_on_prod_like_server: bool, duplicate_files_must_be_ignored: bool
) -> bool:
    if not duplicate_files_must_be_ignored:
        return True
    # Too many duplicate files are present
    if is_on_prod_like_server:
        return False
    # On a test environment we will ignore them but continue
    return True
