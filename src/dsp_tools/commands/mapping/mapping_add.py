from urllib.parse import quote_plus

from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.clients.mapping_client import MappingClient
from dsp_tools.clients.mapping_client_live import MappingClientLive
from dsp_tools.commands.mapping.models import MappingInfo
from dsp_tools.commands.mapping.models import MappingRequestFailedProblem
from dsp_tools.commands.mapping.models import PrefixResolutionProblem
from dsp_tools.commands.mapping.models import ResolvedClassMapping
from dsp_tools.commands.mapping.models import ResolvedPropertyMapping
from dsp_tools.commands.mapping.parse_excel import parse_mapping_excel
from dsp_tools.commands.mapping.resolve_parsed_mappings import resolve_parsed_mappings
from dsp_tools.utils.data_formats.iri_util import make_dsp_ontology_prefix
from dsp_tools.utils.request_utils import ResponseCodeAndText


def mapping_add(info: MappingInfo) -> bool:
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

    succeeded = 0
    failed: list[str] = []

    for cm in resolved_mappings.classes:
        result = _add_class_mappings(client, ontology_namespace, cm)
        if isinstance(result, ResponseCodeAndText):
            failed.append(f"FAILED: {cm.class_iri} — {result.status_code}: {result.text[:200]}")
        else:
            succeeded += 1

    for pm in resolved_mappings.properties:
        result = _add_property_with_retry(client, ontology_namespace, pm)
        if isinstance(result, ResponseCodeAndText):
            failed.append(f"FAILED: {pm.property_iri} — {result.status_code}: {result.text[:200]}")
        else:
            succeeded += 1

    _print_summary(
        n_classes=len(resolved_mappings.classes),
        n_properties=len(resolved_mappings.properties),
        succeeded=succeeded,
        failed=failed,
    )
    return len(failed) == 0


def _communicate_parsing_problems(problem_list: list[PrefixResolutionProblem]) -> None:
    # TODO: change communication
    problem_lines = "\n".join(
        f"  - {p.entity}: undeclared prefix '{p.prefix}'" if p.prefix else f"  - {p.entity}: invalid IRI format"
        for p in problem_list
    )
    print(f"ERROR: The following prefix resolution problems were found:\n{problem_lines}")
    return False


def _add_class_mappings(
    client: MappingClient, classes_mapping: list[ResolvedClassMapping]
) -> list[MappingRequestFailedProblem]:
    # TODO: add progress bar
    for cls in classes_mapping:
        pass


def _add_property_with_retry(
    client: MappingClient, properties_mapping: list[ResolvedPropertyMapping]
) -> list[MappingRequestFailedProblem]:
    # TODO: add progress bar
    for prop in properties_mapping:
        pass


def _print_summary(n_classes: int, n_properties: int, succeeded: int, failed: list[str]) -> None:
    print(f"Done: {n_classes} classes and {n_properties} properties processed.")
    print(f"  Failed: {len(failed)}")
    for msg in failed:
        print(f"    {msg}")
