

from dsp_tools.cli.args import ValidateDataConfig
from dsp_tools.commands.validate_data.models.validation import DuplicateFileResult
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedResource


def check_for_duplicate_files(
    parsed_resources: list[ParsedResource], config: ValidateDataConfig
) -> DuplicateFileResult:
    pass


def _get_filepath_count_dict(parsed_resources: list[ParsedResource]) -> dict[str, int]:
    pass
