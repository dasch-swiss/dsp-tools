from pathlib import Path

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.commands.validate_data.models.validation import RDFGraphs
from dsp_tools.commands.validate_data.prepare_data.prepare_data import get_info_and_parsed_resources_from_file
from dsp_tools.commands.validate_data.prepare_data.prepare_data import prepare_data_for_validation_from_parsed_resource


def prepare_data_for_validation_from_file(
    filepath: Path, auth: AuthenticationClient, ignore_duplicate_files_warning: bool
) -> tuple[RDFGraphs, set[str]]:
    parsed_resources, shortcode, authorship_lookup, permission_ids = get_info_and_parsed_resources_from_file(
        file=filepath,
        api_url=auth.server,
    )
    return prepare_data_for_validation_from_parsed_resource(
        parsed_resources=parsed_resources,
        authorship_lookup=authorship_lookup,
        permission_ids=permission_ids,
        auth=auth,
        shortcode=shortcode,
        ignore_duplicate_files_warning=ignore_duplicate_files_warning,
    )
