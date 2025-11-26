import time
from http import HTTPStatus

import regex
import rustworkx as rx
from loguru import logger
from rdflib import URIRef

from dsp_tools.clients.ontology_clients import OntologyCreateClient
from dsp_tools.commands.create.models.server_project_info import OntoLastModDateLookup
from dsp_tools.commands.create.models.server_project_info import ProjectIriLookup
from dsp_tools.error.exceptions import CircularOntologyDependency
from dsp_tools.utils.request_utils import ResponseCodeAndText


def should_retry_request(response: ResponseCodeAndText) -> bool:
    if response.status_code == HTTPStatus.BAD_REQUEST:
        if regex.search(r"Ontology .+ modified", response.text):
            return True
    elif HTTPStatus.INTERNAL_SERVER_ERROR <= response.status_code <= HTTPStatus.NETWORK_AUTHENTICATION_REQUIRED:
        time.sleep(5)
        return True
    return False


def sort_for_upload(graph: rx.PyDiGraph, node_to_iri: dict[int, str]) -> list[str]:
    try:
        node_sorting_order = rx.topological_sort(graph)
        return [node_to_iri[x] for x in reversed(node_sorting_order)]
    except rx.DAGHasCycle as e:
        logger.error(e)
        raise CircularOntologyDependency("super-properties") from None


def get_modification_date_onto_lookup(
    project_iri_lookup: ProjectIriLookup,
    onto_client: OntologyCreateClient,
) -> OntoLastModDateLookup:
    lookup = OntoLastModDateLookup(
        project_iri=project_iri_lookup.project_iri,
        onto_iris={name: URIRef(iri) for name, iri in project_iri_lookup.onto_iris.items()},
    )
    for onto_iri in project_iri_lookup.onto_iris.values():
        last_mod = onto_client.get_last_modification_date(project_iri_lookup.project_iri, onto_iri)
        lookup.update_last_mod_date(onto_iri, last_mod)
    return lookup
