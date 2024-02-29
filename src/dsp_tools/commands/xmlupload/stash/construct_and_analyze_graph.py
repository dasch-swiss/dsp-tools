from __future__ import annotations

from typing import Any
from typing import cast

import regex
import rustworkx as rx
from lxml import etree

from dsp_tools.commands.xmlupload.stash.graph_models import Cost
from dsp_tools.commands.xmlupload.stash.graph_models import Edge
from dsp_tools.commands.xmlupload.stash.graph_models import ResptrLink
from dsp_tools.commands.xmlupload.stash.graph_models import XMLLink
from dsp_tools.utils.iri_util import is_resource_iri


def create_info_from_xml_for_graph(
    root: etree._Element,
) -> tuple[list[ResptrLink], list[XMLLink], list[str]]:
    """
    Create link objects (ResptrLink/XMLLink) from the XML file,
    and add a reference UUID to each XML element that contains a link (<resptr> or <text>).
    With this UUID, the link objects can be identified in the XML data file.

    Args:
        root: root of the parsed XML file

    Returns:
        - All resptr links contained in the XML file, represented as ResptrLink objects.
        - All XML links contained in the XML file, represented as XMLLink objects.
        - A list with all resource IDs used in the XML file.
    """
    resptr_links = []
    xml_links = []
    all_resource_ids = []
    for resource in root.iter(tag="resource"):
        resptr, xml = _create_info_from_xml_for_graph_from_one_resource(resource)
        all_resource_ids.append(resource.attrib["id"])
        resptr_links.extend(resptr)
        xml_links.extend(xml)
    return resptr_links, xml_links, all_resource_ids


def _create_info_from_xml_for_graph_from_one_resource(
    resource: etree._Element,
) -> tuple[list[ResptrLink], list[XMLLink]]:
    resptr_links: list[ResptrLink] = []
    xml_links: list[XMLLink] = []
    for prop in resource.getchildren():
        match prop.tag:
            case "resptr-prop":
                resptr_links.extend(_create_resptr_link_objects(resource.attrib["id"], prop))
            case "text-prop":
                xml_links.extend(_create_text_link_objects(resource.attrib["id"], prop))
    return resptr_links, xml_links


def _create_resptr_link_objects(subject_id: str, resptr_prop: etree._Element) -> list[ResptrLink]:
    resptr_links = []
    for resptr in resptr_prop.getchildren():
        resptr.text = cast(str, resptr.text)
        if not is_resource_iri(resptr.text):
            link_object = ResptrLink(subject_id, resptr.text)
            # this UUID is so that the links that were stashed can be identified in the XML data file
            resptr.attrib["linkUUID"] = link_object.link_uuid
            resptr_links.append(link_object)
    return resptr_links


def _create_text_link_objects(subject_id: str, text_prop: etree._Element) -> list[XMLLink]:
    # if the same ID is in several separate <text> values of one <text-prop>, they are considered separate links
    xml_props = []
    for text in text_prop.getchildren():
        if links := _extract_ids_from_one_text_value(text):
            xml_link = XMLLink(subject_id, links)
            xml_props.append(xml_link)
            # this UUID is so that the links that were stashed can be identified in the XML data file
            text.attrib["linkUUID"] = xml_link.link_uuid
    return xml_props


def _extract_ids_from_one_text_value(text: etree._Element) -> set[str]:
    # the same id in one <text> only means one link to the resource
    all_links = set()
    for ele in text.iterdescendants():
        if href := ele.attrib.get("href"):
            if internal_id := regex.search(r"IRI:(.*):IRI", href):
                all_links.add(internal_id.group(1))
    return all_links


def make_graph(
    resptr_links: list[ResptrLink],
    xml_links: list[XMLLink],
    all_resource_ids: list[str],
) -> tuple[rx.PyDiGraph[Any, Any], dict[int, str], list[Edge]]:
    """
    This function takes information about the resources of an XML file and links between them.
    From that it constructs a rustworkx directed graph.
    Resources are represented as nodes and links as edges.

    Args:
        resptr_links: objects representing a direct link between a starting resource and a target resource
        xml_links: objects representing one or more links from a single text value of a single starting resource
                   to a set of target resources
        all_resource_ids: IDs of all resources in the graph

    Returns:
        - The rustworkx graph.
        - A dictionary that maps the rustworkx index number of the nodes to the original resource ID from the XML file.
        - A list with all the edges in the graph.
    """
    graph: rx.PyDiGraph[Any, Any] = rx.PyDiGraph()
    nodes = [(id_, None, None) for id_ in all_resource_ids]
    node_indices = list(graph.add_nodes_from(nodes))
    id_to_node = dict(zip(all_resource_ids, node_indices))
    node_to_id = dict(zip(node_indices, all_resource_ids))
    edges = [Edge(id_to_node[x.source_id], id_to_node[x.target_id], x) for x in resptr_links]
    for xml in xml_links:
        edges.extend([Edge(id_to_node[xml.source_id], id_to_node[x], xml) for x in xml.target_ids])
    graph.add_edges_from([e.as_tuple() for e in edges])
    return graph, node_to_id, edges


def _remove_leaf_nodes(
    graph: rx.PyDiGraph[Any, Any],
    node_to_id: dict[int, str],
    node_indices: set[int],
) -> tuple[list[str], set[int]]:
    """
    Leaf nodes are nodes that do not have any outgoing links.
    This means that they have no dependencies and are ok to upload.
    This function removes them from the graph.

    Args:
        graph: graph
        node_to_id: mapping of the rustworkx index number of the nodes to the original resource ID from the XML file
        node_indices: node indices that are in the graph

    Returns:
        - A list with the IDs of the removed leaf nodes.
        - A set with the indices of the nodes that remain in the graph.
    """
    removed_leaf_nodes: list[str] = []
    remaining_node_indices = set(node_indices)
    while leaf_nodes := [x for x in remaining_node_indices if graph.out_degree(x) == 0]:
        removed_leaf_nodes.extend(node_to_id[n] for n in leaf_nodes)
        graph.remove_nodes_from(leaf_nodes)
        remaining_node_indices = remaining_node_indices - set(leaf_nodes)
    return removed_leaf_nodes, remaining_node_indices


def _find_cheapest_outgoing_links(
    graph: rx.PyDiGraph[Any, Any],
    cycle: list[tuple[int, int]],
    edges: list[Edge],
) -> list[Edge]:
    """
    This function searches for the nodes whose outgoing links should be removed in order to break the cycle.
    It calculates which links between the resources create the smallest stash.

    Args:
        graph: graph
        cycle: the list with (source, target) for each edge in the cycle
        edges: edges in the graph (contains info about source node, target node, and link info)

    Returns:
        The edges (i.e. links) that should be stashed (containing all the edges connecting the two nodes)
    """
    costs: list[Cost] = []
    for source, target in cycle:
        edges_in = graph.in_edges(source)
        node_gain = len(edges_in)
        edges_out = graph.out_edges(source)
        node_cost = sum(x[2].cost_links for x in edges_out)
        node_value = node_cost / node_gain
        costs.append(Cost(source, target, node_value))
    cheapest_cost = sorted(costs, key=lambda x: x.node_value)[0]
    return [x for x in edges if x.source == cheapest_cost.source and x.target == cheapest_cost.target]


def _remove_edges_to_stash(
    graph: rx.PyDiGraph[Any, Any],
    edges_to_remove: list[Edge],
    all_edges: list[Edge],
    remaining_nodes: set[int],
) -> None:
    """
    This function removes the edges from the graph in order to break a cycle.

    Args:
        graph: graph
        edges_to_remove: edges that should be removed
        all_edges: all edges in the original graph
        remaining_nodes: indices of the nodes in the graph
    """
    normal_edges_to_remove = [(x.source, x.target) for x in edges_to_remove]
    # if only one (source, target) is removed, it removes only one edge, not all
    # therefore we need as many entries in the list as there are edges between the source and the target

    phantom_edges_to_remove = []
    source, target = edges_to_remove[0].source, edges_to_remove[0].target
    for link_to_stash in [x.link_object for x in edges_to_remove]:
        if isinstance(link_to_stash, XMLLink):
            phantom_edges_to_remove.extend(
                _find_phantom_xml_edges(source, target, all_edges, link_to_stash, remaining_nodes)
            )

    all_edges_to_remove = normal_edges_to_remove + phantom_edges_to_remove
    graph.remove_edges_from(all_edges_to_remove)


def _find_phantom_xml_edges(
    source_node_index: int,
    target_node_index: int,
    all_edges: list[Edge],
    xml_link_to_stash: XMLLink,
    remaining_nodes: set[int],
) -> list[tuple[int, int]]:
    """
    If an edge that will be removed represents an XML link,
    the text value may contain further links to other resources.
    If we stash the XMLLink, then in the real data all links of that text value are stashed.
    So, these "phantom" links must be removed from the graph.
    This function identifies the edges that must be removed from the rx graph.

    Args:
        source_node_index: rustworkx index of source node
        target_node_index: rustworkx index of target node
        all_edges: all edges in the original graph
        xml_link_to_stash: XML link that will be stashed
        remaining_nodes: indices of all nodes in the graph

    Returns:
        edges (rustworkx indices of nodes) that represent the links in the original XML text
    """

    def check(x: Edge) -> bool:
        return all(
            (
                x.source == source_node_index,
                x.target != target_node_index,
                x.link_object == xml_link_to_stash,
                x.target in remaining_nodes,
                # the target could have been removed because it was a leaf node, so we must check if it is still there
            )
        )

    return [(x.source, x.target) for x in all_edges if check(x)]


def _add_stash_to_lookup_dict(
    stash_dict: dict[str, list[str]],
    links_to_stash: list[XMLLink | ResptrLink],
) -> dict[str, list[str]]:
    stash_list = [stash_link.link_uuid for stash_link in links_to_stash]
    # all stashed links have the same subject id, so we can just take the first one
    subj_id = links_to_stash[0].source_id
    if subj_id in stash_dict:
        stash_dict[subj_id].extend(stash_list)
    else:
        stash_dict[subj_id] = stash_list
    return stash_dict


def generate_upload_order(
    graph: rx.PyDiGraph[Any, Any],
    node_to_id: dict[int, str],
    edges: list[Edge],
) -> tuple[dict[str, list[str]], list[str], int]:
    """
    Generate the order in which the resources should be uploaded to the DSP-API based on the dependencies.

    Args:
        graph: graph
        node_to_id: mapping between indices of the graph nodes and original resource IDs from the XML file
        edges: edges in the graph (contains info about source node, target node, and link info)

    Returns:
        - A dictionary which maps the resources that have stashes to the UUIDs of the stashed links.
        - A list of resource IDs which gives the order in which the resources should be uploaded to DSP-API.
        - The number of links in the stash.
    """
    upload_order: list[str] = []
    stash_lookup: dict[str, list[str]] = {}
    node_indices = set(node_to_id.keys())
    leaf_nodes, remaining_node_indices = _remove_leaf_nodes(graph, node_to_id, node_indices)
    upload_order.extend(leaf_nodes)
    stash_counter = 0
    while remaining_node_indices:
        cycle = list(rx.digraph_find_cycle(graph))
        links_to_remove = _find_cheapest_outgoing_links(graph, cycle, edges)
        stash_counter += len(links_to_remove)
        _remove_edges_to_stash(
            graph=graph,
            edges_to_remove=links_to_remove,
            all_edges=edges,
            remaining_nodes=remaining_node_indices,
        )
        stash_lookup = _add_stash_to_lookup_dict(stash_lookup, [x.link_object for x in links_to_remove])
        leaf_nodes, remaining_node_indices = _remove_leaf_nodes(graph, node_to_id, remaining_node_indices)
        upload_order.extend(leaf_nodes)
    return stash_lookup, upload_order, stash_counter
