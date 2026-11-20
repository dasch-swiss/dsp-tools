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
from dsp_tools.commands.create.models.parsed_ontology import ParsedClass
from dsp_tools.commands.create.models.server_project_info import CreatedIriCollection
from dsp_tools.commands.create.models.server_project_info import OntoLastModDateLookup
from dsp_tools.commands.create.models.server_project_info import ProjectIriLookup
from dsp_tools.commands.create.serialisation.ontology import serialise_class_graph_for_request


def create_all_classes(
    classes: list[ParsedClass],
    project_iri_lookup: ProjectIriLookup,
    created_iris: CreatedIriCollection,
    client: OntologyCreateClient,
) -> tuple[CreatedIriCollection, CollectedProblems | None]:
    upload_order = _get_class_create_order(classes)
    logger.debug(f"Class creation order: {upload_order}")
    cls_lookup = {c.name: c for c in classes}
    all_problems: list[CreateProblem] = []
    onto_lookup = get_modification_date_onto_lookup(project_iri_lookup, client)
    progress_bar = tqdm(upload_order, desc="    Creating classes", dynamic_ncols=True)
    logger.debug("Starting class creation")
    for c in progress_bar:
        cls = cls_lookup[c]
        if previous_blocker := _is_class_blocked(cls.name, set(cls.supers), created_iris):
            all_problems.append(previous_blocker)
            created_iris.failed_classes.add(cls.name)
        else:
            create_result = _create_one_class(cls, onto_lookup, client)
            if isinstance(create_result, Literal):
                onto_lookup.update_last_mod_date(cls.onto_iri, create_result)
                created_iris.created_classes.add(cls.name)
            else:
                all_problems.append(create_result)
                created_iris.failed_classes.add(cls.name)
    upload_problems = None
    if all_problems:
        upload_problems = CollectedProblems("    While creating classes the following problems occurred:", all_problems)
    return created_iris, upload_problems


def _get_class_create_order(classes: list[ParsedClass]) -> list[str]:
    logger.debug("Creating class upload order.")
    graph, node_to_iri = _make_graph_to_sort(classes)
    return sort_for_upload(graph, node_to_iri)


def _make_graph_to_sort(classes: list[ParsedClass]) -> tuple[rx.PyDiGraph, dict[int, str]]:
    graph: rx.PyDiGraph[Any, Any] = rx.PyDiGraph()
    cls_iris = [x.name for x in classes]
    node_indices = list(graph.add_nodes_from(cls_iris))
    iri_to_node = dict(zip(cls_iris, node_indices))
    node_to_iri = dict(zip(node_indices, cls_iris))
    for i, p in enumerate(classes):
        for super_cls in p.supers:
            if super_cls in cls_iris:
                graph.add_edge(iri_to_node[p.name], iri_to_node[super_cls], i)
    return graph, node_to_iri


def _is_class_blocked(cls_name: str, supers: set[str], created_iris: CreatedIriCollection) -> CreateProblem | None:
    if created_iris.any_classes_failed(supers):
        return UploadProblem(cls_name, UploadProblemType.CLASS_SUPER_FAILED)
    return None


def _create_one_class(
    cls: ParsedClass, onto_lookup: OntoLastModDateLookup, client: OntologyCreateClient
) -> Literal | CreateProblem:
    cls_serialised = serialise_class_graph_for_request(
        cls, URIRef(cls.onto_iri), onto_lookup.get_last_mod_date(cls.onto_iri)
    )
    request_result = client.post_new_class(cls_serialised)
    if isinstance(request_result, Literal):
        return request_result
    if should_retry_request(request_result):
        new_mod_date = client.get_last_modification_date(onto_lookup.project_iri, cls.onto_iri)
        cls_serialised = serialise_class_graph_for_request(cls, URIRef(cls.onto_iri), new_mod_date)
        request_result = client.post_new_class(cls_serialised)
        if isinstance(request_result, Literal):
            return request_result
    if request_result.status_code == HTTPStatus.BAD_REQUEST:
        return UploadProblem(cls.name, request_result.text)
    return UploadProblem(cls.name, UploadProblemType.CLASS_COULD_NOT_BE_CREATED)
