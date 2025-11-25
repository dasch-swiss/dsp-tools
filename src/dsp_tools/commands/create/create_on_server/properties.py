from typing import Any

import rustworkx as rx
from loguru import logger

from dsp_tools.commands.create.models.parsed_ontology import ParsedProperty
from dsp_tools.error.exceptions import CircularOntologyDependency


def create_all_properties():
    pass


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
