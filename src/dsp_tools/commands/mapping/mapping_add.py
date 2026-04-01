from http import HTTPStatus
from urllib.parse import quote_plus

from loguru import logger
from tqdm import tqdm

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
from dsp_tools.utils.request_utils import ResponseCodeAndText


def mapping_add(info: MappingInfo) -> bool:
    # TODO: add logging
    parsed_excel, prefix_lookup = parse_mapping_excel(info.config.excel_file)

    ontology_namespace = make_dsp_ontology_prefix(info.server.server, info.config.shortcode, info.config.ontology)

    resolved_mappings, problems = resolve_parsed_mappings(parsed_excel, prefix_lookup, ontology_namespace)

    if problems:
        _communicate_parsing_problems(problems)
        return False

    # TODO: make ontology exists check

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
    # TODO: add printing
    pass


def _add_classes_mappings(
    client: MappingClient, classes_mapping: list[ResolvedClassMapping]
) -> list[MappingUploadFailure]:
    progress_bar = tqdm(classes_mapping, desc="    Adding mapping to classes", dynamic_ncols=True)
    logger.debug("Adding mapping to classes")
    for cls in progress_bar:
        problem_response = client.put_class_mapping(cls.iri, cls.mapping_iris)
        if problem_response:
            pass
        # TODO: deal with retry


def _add_properties_mappings(
    client: MappingClient, properties_mapping: list[ResolvedPropertyMapping]
) -> list[MappingUploadFailure]:
    progress_bar = tqdm(properties_mapping, desc="    Adding mapping to properties", dynamic_ncols=True)
    logger.debug("Adding mapping to properties")
    for prop in progress_bar:
        problem_response = client.put_property_mapping(prop.iri, prop.mapping_iris)
        if problem_response:
            pass
        # TODO: deal with retry (look at error code)


def _deal_with_non_ok_response(iri: str, response_code_text: ResponseCodeAndText) -> list[MappingUploadFailure]:
    if response_code_text.status_code == HTTPStatus.BAD_REQUEST:
        return _deal_with_bad_request(iri, response_code_text)
    # TODO: deal with other errors


def _deal_with_bad_request(iri: str, response_code_text: ResponseCodeAndText) -> list[MappingUploadFailure]:
    if not response_code_text.v3_errors:
        return [MappingUploadFailure(iri=iri, mapping_iri=None, message=response_code_text.text)]
    failures = []
    # TODO: implmement message construction
    for v3_err in response_code_text.v3_errors:
        match v3_err.error_code:
            case "class_not_found":
                pass
            case "property_not_found":
                pass
            case "invalid_ontology_mapping_iri":
                pass
            case _:
                pass  # make logging warning, unknown error code and then join infos
    return failures


def _communicate_upload_failures(failures: list[MappingUploadFailure]) -> None:
    pass
    # TODO: add printing
