import time

from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.clients.mapping_client import MappingClient
from dsp_tools.clients.mapping_client_live import MappingClientLive
from dsp_tools.commands.mapping.excel_parser import parse_mapping_excel
from dsp_tools.commands.mapping.iri_resolver import resolve_all
from dsp_tools.commands.mapping.models import ClassMapping
from dsp_tools.commands.mapping.models import MappingInfo
from dsp_tools.commands.mapping.models import ParsedMappingExcel
from dsp_tools.commands.mapping.models import PropertyMapping
from dsp_tools.utils.data_formats.iri_util import make_dsp_ontology_prefix
from dsp_tools.utils.request_utils import ResponseCodeAndText
from dsp_tools.utils.request_utils import is_server_error


def mapping_add(info: MappingInfo) -> bool:
    raw_excel, prefix_map = parse_mapping_excel(info.config.excel_file)

    ontology_iri = make_dsp_ontology_prefix(info.server.server, info.config.shortcode, info.config.ontology).rstrip("#")

    classes = [
        ClassMapping(class_iri=f"{ontology_iri}#{cm.class_iri}", mapping_iris=cm.mapping_iris)
        for cm in raw_excel.classes
    ]
    properties = [
        PropertyMapping(property_iri=f"{ontology_iri}#{pm.property_iri}", mapping_iris=pm.mapping_iris)
        for pm in raw_excel.properties
    ]
    excel_with_full_iris = ParsedMappingExcel(classes=classes, properties=properties)
    resolved_excel, problems = resolve_all(excel_with_full_iris, prefix_map)

    if problems:
        problem_lines = "\n".join(
            f"  - {p.entity}: undeclared prefix '{p.prefix}'" if p.prefix else f"  - {p.entity}: invalid IRI format"
            for p in problems
        )
        print(f"ERROR: The following prefix resolution problems were found:\n{problem_lines}")
        return False

    auth = AuthenticationClientLive(
        server=info.server.server,
        email=info.server.user,
        password=info.server.password,
    )
    client = MappingClientLive(server=info.server.server, auth=auth)

    succeeded = 0
    failed: list[str] = []
    total = len(resolved_excel.classes) + len(resolved_excel.properties)

    for cm in resolved_excel.classes:
        result = _add_class_with_retry(client, ontology_iri, cm)
        if isinstance(result, ResponseCodeAndText):
            failed.append(f"FAILED: {cm.class_iri} — {result.status_code}: {result.text[:200]}")
        else:
            succeeded += 1

    for pm in resolved_excel.properties:
        result = _add_property_with_retry(client, ontology_iri, pm)
        if isinstance(result, ResponseCodeAndText):
            failed.append(f"FAILED: {pm.property_iri} — {result.status_code}: {result.text[:200]}")
        else:
            succeeded += 1

    _print_summary(total=total, succeeded=succeeded, failed=failed)
    return len(failed) == 0


def _add_class_with_retry(client: MappingClient, ontology_iri: str, cm: ClassMapping) -> str | ResponseCodeAndText:
    result = client.add_class_mapping(ontology_iri, cm.class_iri, cm.mapping_iris)
    if isinstance(result, ResponseCodeAndText) and is_server_error(result):
        time.sleep(5)
        result = client.add_class_mapping(ontology_iri, cm.class_iri, cm.mapping_iris)
    return result


def _add_property_with_retry(
    client: MappingClient, ontology_iri: str, pm: PropertyMapping
) -> str | ResponseCodeAndText:
    result = client.add_property_mapping(ontology_iri, pm.property_iri, pm.mapping_iris)
    if isinstance(result, ResponseCodeAndText) and is_server_error(result):
        time.sleep(5)
        result = client.add_property_mapping(ontology_iri, pm.property_iri, pm.mapping_iris)
    return result


def _print_summary(total: int, succeeded: int, failed: list[str]) -> None:
    print(f"Done: {total} entries processed.")
    print(f"  Succeeded: {succeeded}")
    print(f"  Failed: {len(failed)}")
    for msg in failed:
        print(f"    {msg}")
