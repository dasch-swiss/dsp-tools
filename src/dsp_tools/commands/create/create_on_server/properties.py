from http import HTTPStatus
from typing import Any

import regex
import rustworkx as rx
from loguru import logger
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.clients.ontology_clients import OntologyCreateClient
from dsp_tools.commands.create.models.create_problems import CreateProblem
from dsp_tools.commands.create.models.create_problems import UploadProblem
from dsp_tools.commands.create.models.create_problems import UploadProblemType
from dsp_tools.commands.create.models.parsed_ontology import ParsedProperty
from dsp_tools.commands.create.models.server_project_info import CreatedIriCollection
from dsp_tools.commands.create.models.server_project_info import OntoCreateLookup
from dsp_tools.commands.create.models.server_project_info import ProjectIriLookup
from dsp_tools.commands.create.serialisation.ontology import serialise_property_graph_for_request
from dsp_tools.error.exceptions import CircularOntologyDependency
from dsp_tools.utils.request_utils import ResponseCodeAndText


def create_all_properties(
    properties: list[ParsedProperty],
    project_iri_lookup: ProjectIriLookup,
    created_iris: CreatedIriCollection,
    onto_client: OntologyCreateClient,
):
    upload_order = _get_property_create_order(properties)
    prop_lookup = {p.name: p for p in properties}
    problems: CreateProblem = []
    onto_lookup = _get_onto_lookup(project_iri_lookup, onto_client)


def _get_onto_lookup(
    project_iri_lookup: ProjectIriLookup,
    onto_client: OntologyCreateClient,
) -> OntoCreateLookup:
    lookup = OntoCreateLookup(
        project_iri=project_iri_lookup.project_iri,
        onto_iris={name: URIRef(iri) for name, iri in project_iri_lookup.onto_iris.items()},
    )
    for name, onto_iri in project_iri_lookup.onto_iris.items():
        last_mod = onto_client.get_last_modification_date(project_iri_lookup.project_iri, onto_iri)
        lookup = lookup.add_date(name, last_mod)
    return lookup


def _get_property_create_order(properties: list[ParsedProperty]) -> list[str]:
    logger.debug("Creating property upload order.")
    graph, node_to_iri = _make_graph_to_sort(properties)
    return _sort_properties(graph, node_to_iri)


def _make_graph_to_sort(properties: list[ParsedProperty]) -> tuple[rx.PyDiGraph, dict[int, str]]:
    graph: rx.PyDiGraph[Any, Any] = rx.PyDiGraph()
    prop_iris = [x.name for x in properties]
    node_indices = list(graph.add_nodes_from(prop_iris))
    iri_to_node = dict(zip(prop_iris, node_indices))
    node_to_iri = dict(zip(node_indices, prop_iris))
    for i, p in enumerate(properties):
        for super_prop in p.supers:
            if super_prop in prop_iris:
                graph.add_edge(iri_to_node[p.name], iri_to_node[super_prop], i)
    return graph, node_to_iri


def _sort_properties(graph: rx.PyDiGraph, node_to_iri: dict[int, str]) -> list[str]:
    try:
        node_sorting_order = rx.topological_sort(graph)
        return [node_to_iri[x] for x in node_sorting_order]
    except rx.DAGHasCycle as e:
        logger.error(e)
        raise CircularOntologyDependency(
            "A circular dependency of superproperties was found in your project. "
            "It is not possible for an ontology to have circular dependencies."
        ) from None


def _create_one_property(
    prop: ParsedProperty,
    list_iri: Literal | None,
    lookup: OntoCreateLookup,
    onto_client: OntologyCreateClient,
) -> Literal | CreateProblem:
    onto_iri = lookup.get_onto_iri(prop.onto_name)
    prop_serialised = serialise_property_graph_for_request(
        prop, list_iri, onto_iri, lookup.get_last_mod_date(prop.onto_name)
    )
    request_result = onto_client.post_new_property(prop_serialised)
    if isinstance(request_result, Literal):
        return request_result
    if _should_retry(request_result):
        new_mod_date = onto_client.get_last_modification_date(lookup.project_iri, onto_iri)
        prop_serialised = serialise_property_graph_for_request(prop, list_iri, onto_iri, new_mod_date)
        request_result = onto_client.post_new_property(prop_serialised)
        if isinstance(request_result, Literal):
            return request_result
    if request_result.status_code == HTTPStatus.BAD_REQUEST:
        return UploadProblem(prop.name, request_result.text)
    return UploadProblem(prop.name, UploadProblemType.PROPERTY_COULD_NOT_BE_CREATED)


def _should_retry(response: ResponseCodeAndText) -> bool:
    if response.status_code == HTTPStatus.BAD_REQUEST:
        if regex.search(r"Ontology .+ modified", response.text):
            return True
    elif HTTPStatus.INTERNAL_SERVER_ERROR <= response.status_code <= HTTPStatus.NETWORK_AUTHENTICATION_REQUIRED:
        return True
    return False
