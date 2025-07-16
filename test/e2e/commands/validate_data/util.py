from pathlib import Path

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.commands.validate_data.models.validation import RDFGraphs
from dsp_tools.commands.validate_data.prepare_data.prepare_data import get_info_and_parsed_resources_from_file
from dsp_tools.commands.validate_data.prepare_data.prepare_data import prepare_data_for_validation_from_parsed_resource
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedResource


def prepare_data_for_validation_from_file(
    filepath: Path, auth: AuthenticationClient
) -> tuple[RDFGraphs, set[str], list[ParsedResource]]:
    parsed_resources, shortcode, authorship_lookup, permission_ids = get_info_and_parsed_resources_from_file(
        file=filepath,
        api_url=auth.server,
    )
    graphs, used_iris = prepare_data_for_validation_from_parsed_resource(
        parsed_resources=parsed_resources,
        authorship_lookup=authorship_lookup,
        permission_ids=permission_ids,
        auth=auth,
        shortcode=shortcode,
    )
    return graphs, used_iris, parsed_resources
