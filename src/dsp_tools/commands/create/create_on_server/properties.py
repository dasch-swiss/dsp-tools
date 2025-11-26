from http import HTTPStatus
from typing import Any

import rustworkx as rx
from loguru import logger
from rdflib import Literal
from rdflib import URIRef
from tqdm import tqdm

from dsp_tools.clients.ontology_clients import OntologyCreateClient
from dsp_tools.commands.create.create_on_server.onto_utils import get_modification_date_onto_lookup
from dsp_tools.commands.create.create_on_server.onto_utils import should_retry_request
from dsp_tools.commands.create.create_on_server.onto_utils import sort_for_upload
from dsp_tools.commands.create.models.create_problems import CollectedProblems
from dsp_tools.commands.create.models.create_problems import CreateProblem
from dsp_tools.commands.create.models.create_problems import UploadProblem
from dsp_tools.commands.create.models.create_problems import UploadProblemType
from dsp_tools.commands.create.models.parsed_ontology import ParsedProperty
from dsp_tools.commands.create.models.server_project_info import CreatedIriCollection
from dsp_tools.commands.create.models.server_project_info import ListNameToIriLookup
from dsp_tools.commands.create.models.server_project_info import OntoLastModDateLookup
from dsp_tools.commands.create.models.server_project_info import ProjectIriLookup
from dsp_tools.commands.create.serialisation.ontology import serialise_property_graph_for_request


def create_all_properties(
    properties: list[ParsedProperty],
    project_iri_lookup: ProjectIriLookup,
    created_iris: CreatedIriCollection,
    list_lookup: ListNameToIriLookup,
    client: OntologyCreateClient,
) -> tuple[CreatedIriCollection, CollectedProblems | None]:
    upload_order = _get_property_create_order(properties)
    logger.debug(f"Property creation order: {upload_order}")
    prop_lookup = {p.name: p for p in properties}
    all_problems: list[CreateProblem] = []
    onto_lookup = get_modification_date_onto_lookup(project_iri_lookup, client)
    progress_bar = tqdm(upload_order, desc="    Creating properties", dynamic_ncols=True)
    logger.debug("Starting property creation")
    for p in progress_bar:
        prop = prop_lookup[p]
        if previous_blocker := _is_property_blocked(prop, created_iris):
            all_problems.append(previous_blocker)
            created_iris.failed_properties.add(prop.name)
        else:
            list_iri = None
            if prop.node_name is not None:
                if not (found := list_lookup.get_iri(prop.node_name)):
                    all_problems.append(UploadProblem(prop.name, UploadProblemType.PROPERTY_LIST_NOT_FOUND))
                    continue
                else:
                    list_iri = Literal(f"hlist=<{found}>")
            create_result = _create_one_property(prop, list_iri, onto_lookup, client)
            if isinstance(create_result, Literal):
                onto_lookup.update_last_mod_date(prop.onto_iri, create_result)
                created_iris.created_properties.add(prop.name)
            else:
                all_problems.append(create_result)
                created_iris.failed_properties.add(prop.name)
    upload_problems = None
    if all_problems:
        upload_problems = CollectedProblems(
            "    While creating properties the following problems occurred:", all_problems
        )
    return created_iris, upload_problems


def _is_property_blocked(prop: ParsedProperty, created_iris: CreatedIriCollection) -> CreateProblem | None:
    if created_iris.any_properties_failed(set(prop.supers)):
        return UploadProblem(prop.name, UploadProblemType.PROPERTY_SUPER_FAILED)
    if prop.object:
        if created_iris.any_classes_failed({str(prop.object)}):
            return UploadProblem(prop.name, UploadProblemType.PROPERTY_REFERENCES_FAILED_CLASS)
    if prop.subject:
        if created_iris.any_classes_failed({prop.subject}):
            return UploadProblem(prop.name, UploadProblemType.PROPERTY_REFERENCES_FAILED_CLASS)
    return None


def _get_property_create_order(properties: list[ParsedProperty]) -> list[str]:
    logger.debug("Creating property upload order.")
    graph, node_to_iri = _make_graph_to_sort(properties)
    return sort_for_upload(graph, node_to_iri)


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


def _create_one_property(
    prop: ParsedProperty,
    list_iri: Literal | None,
    onto_lookup: OntoLastModDateLookup,
    client: OntologyCreateClient,
) -> Literal | CreateProblem:
    prop_serialised = serialise_property_graph_for_request(
        prop, list_iri, URIRef(prop.onto_iri), onto_lookup.get_last_mod_date(prop.onto_iri)
    )
    request_result = client.post_new_property(prop_serialised)
    if isinstance(request_result, Literal):
        return request_result
    if should_retry_request(request_result):
        new_mod_date = client.get_last_modification_date(onto_lookup.project_iri, prop.onto_iri)
        prop_serialised = serialise_property_graph_for_request(prop, list_iri, URIRef(prop.onto_iri), new_mod_date)
        request_result = client.post_new_property(prop_serialised)
        if isinstance(request_result, Literal):
            return request_result
    if request_result.status_code == HTTPStatus.BAD_REQUEST:
        return UploadProblem(prop.name, request_result.text)
    return UploadProblem(prop.name, UploadProblemType.PROPERTY_COULD_NOT_BE_CREATED)
