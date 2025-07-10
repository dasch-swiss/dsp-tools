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


def _get_filepath_count_dict(parsed_resources: list[ParsedResource]) -> dict[str, int]:
    pass
