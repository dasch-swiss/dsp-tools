from urllib.parse import quote_plus

from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.clients.mapping_client import MappingClient
from dsp_tools.clients.mapping_client_live import MappingClientLive
from dsp_tools.commands.mapping.models import MappingInfo
from dsp_tools.commands.mapping.models import MappingUploadFailure
from dsp_tools.commands.mapping.models import PrefixResolutionProblem
from dsp_tools.commands.mapping.models import ResolvedClassMapping
from dsp_tools.commands.mapping.models import ResolvedPropertyMapping
from dsp_tools.commands.mapping.parse_excel import parse_mapping_excel
from dsp_tools.commands.mapping.resolve_parsed_mappings import resolve_parsed_mappings
from dsp_tools.setup.ansi_colors import BACKGROUND_BOLD_GREEN
from dsp_tools.utils.data_formats.iri_util import make_dsp_ontology_prefix


def mapping_add(info: MappingInfo) -> bool:
    # TODO: add logging
    parsed_excel, prefix_lookup = parse_mapping_excel(info.config.excel_file)

    ontology_namespace = make_dsp_ontology_prefix(info.server.server, info.config.shortcode, info.config.ontology)

    resolved_mappings, problems = resolve_parsed_mappings(parsed_excel, prefix_lookup, ontology_namespace)

    if problems:
        _communicate_parsing_problems(problems)
        return False

    # TODO: make a check if the ontology exists
    encoded_ontology_iri = quote_plus(ontology_namespace.rstrip("#"))
    auth = AuthenticationClientLive(
        server=info.server.server,
        email=info.server.user,
        password=info.server.password,
    )
    client = MappingClientLive(server=auth.server, encoded_ontology_iri=encoded_ontology_iri, auth=auth)

    failures = _add_classes_mappings(client, resolved_mappings.classes)
    prop_failures = _add_properties_mappings(client, resolved_mappings.properties)
    failures.extend(prop_failures)

    if not failures:
        print(f"{BACKGROUND_BOLD_GREEN}All mappings were added successfully.")
        return True

    _communicate_upload_failures(failures)
    return False


def _communicate_parsing_problems(problem_list: list[PrefixResolutionProblem]) -> None:
    # TODO: change communication
    pass


def _add_classes_mappings(
    client: MappingClient, classes_mapping: list[ResolvedClassMapping]
) -> list[MappingUploadFailure]:
    # TODO: add progress bar, make the failures, etc. like in the xmlupload
    for cls in classes_mapping:
        pass


def _add_properties_mappings(
    client: MappingClient, properties_mapping: list[ResolvedPropertyMapping]
) -> list[MappingUploadFailure]:
    # TODO: add progress bar, make the failures, etc. like in the xmlupload
    for prop in properties_mapping:
        pass


def _communicate_upload_failures(failures: list[MappingUploadFailure]) -> None:
    pass
    # TODO: add printing
