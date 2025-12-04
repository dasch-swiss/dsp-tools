import time
from http import HTTPStatus

import regex
import rustworkx as rx
from loguru import logger
from rdflib import OWL
from rdflib import RDF
from rdflib import Graph
from rdflib import URIRef

from dsp_tools.clients.ontology_clients import OntologyCreateClient
from dsp_tools.clients.ontology_get_client_live import OntologyGetClientLive
from dsp_tools.commands.create.exceptions import CircularOntologyDependency
from dsp_tools.commands.create.models.server_project_info import OntoLastModDateLookup
from dsp_tools.commands.create.models.server_project_info import ProjectIriLookup
from dsp_tools.error.exceptions import ProjectOntologyNotFound
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


def get_project_iri_lookup(server: str, shortcode: str, project_iri: str) -> ProjectIriLookup:
    client = OntologyGetClientLive(server, shortcode)
    try:
        ontologies, onto_iris = client.get_ontologies()
        logger.debug(f"Project ontologies found: {', '.join(onto_iris)}")
        lookup = _get_name_to_iri_lookup(ontologies)
        return ProjectIriLookup(project_iri, lookup)
    except ProjectOntologyNotFound:
        logger.debug("No project ontologies on server.")
        return ProjectIriLookup(project_iri)


def _get_name_to_iri_lookup(ontologies: list[str]) -> dict[str, str]:
    lookup = {}
    for onto in ontologies:
        g = Graph()
        g.parse(data=onto, format="ttl")
        iri = str(next(g.subjects(RDF.type, OWL.Ontology)))
        name = iri.split("/")[-2]
        lookup[str(name)] = str(iri)
    return lookup
