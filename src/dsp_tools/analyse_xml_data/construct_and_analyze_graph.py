from __future__ import annotations

from typing import Any

import regex
import rustworkx as rx
from lxml import etree

from dsp_tools.analyse_xml_data.models import ResptrLink, XMLLink


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
        all resptr links contained in the XML file, represented as ResptrLink objects
        all XML links contained in the XML file, represented as XMLLink objects
        a list with all resource IDs used in the XML file
    """
    resptr_links = []
    xml_links = []
    all_resource_ids = []
    for resource in root.iter(tag="{https://dasch.swiss/schema}resource"):
        resptr, xml, subject_id = _create_info_from_xml_for_graph_from_one_resource(resource)
        all_resource_ids.append(subject_id)
        resptr_links.extend(resptr)
        xml_links.extend(xml)
    return resptr_links, xml_links, all_resource_ids


def _create_info_from_xml_for_graph_from_one_resource(
    resource: etree._Element,
) -> tuple[list[ResptrLink], list[XMLLink], str]:
    subject_id = resource.attrib["id"]
    resptr_links: list[ResptrLink] = []
    xml_links: list[XMLLink] = []
    for prop in resource.getchildren():
        match prop.tag:
            case "{https://dasch.swiss/schema}resptr-prop":
                resptr_links.extend(_create_resptr_link_objects(subject_id, prop))
            case "{https://dasch.swiss/schema}text-prop":
                xml_links.extend(_create_text_link_objects(subject_id, prop))
    return resptr_links, xml_links, subject_id


def _create_resptr_link_objects(subject_id: str, resptr_prop: etree._Element) -> list[ResptrLink]:
    resptr_links = []
    for resptr in resptr_prop.getchildren():
        if r_text := resptr.text:
            instance = ResptrLink(subject_id, r_text)
            # this UUID is so that the links that were stashed can be identified in the XML data file
            resptr.attrib["stashUUID"] = instance.link_uuid
            resptr_links.append(instance)
    return resptr_links


def _create_text_link_objects(subject_id: str, text_prop: etree._Element) -> list[XMLLink]:
    # if the same ID is in several separate <text> values of one <text-prop>, they are considered separate links
    xml_props = []
    for text in text_prop.getchildren():
        links = _extract_ids_from_one_text_value(text)
        if links:
            xml_link = XMLLink(subject_id, links)
            xml_props.append(xml_link)
            # this UUID is so that the links that were stashed can be identified in the XML data file
            text.attrib["stashUUID"] = xml_link.link_uuid
    return xml_props


def _extract_ids_from_one_text_value(text: etree._Element) -> set[str]:
    # the same id in one <text> only means one link to the resource
    all_links = set()
    for ele in text.iterdescendants():
        if href := ele.attrib.get("href"):
            searched = regex.search(r"IRI:(.*):IRI", href)
            if searched:
                all_links.add(searched.group(1))
    return all_links


def make_graph(
    resptr_links: list[ResptrLink],
    xml_links: list[XMLLink],
    all_resource_ids: list[str],
) -> tuple[rx.PyDiGraph[Any, Any], dict[int, str], list[tuple[int, int, ResptrLink | XMLLink]], set[int]]:
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
        The rustworkx graph.
        A dictionary that maps the rustworkx index number of the nodes to the original resource ID from the XML file.
        A list with all the edges in the graph.
        A set with the rustworkx index numbers of all the nodes in the graph.
    """
    graph: rx.PyDiGraph[Any, Any] = rx.PyDiGraph()  # pylint: disable=no-member
    nodes = [(id_, None, None) for id_ in all_resource_ids]
    node_indices = list(graph.add_nodes_from(nodes))
    id_to_rustworkx_index = dict(zip(all_resource_ids, node_indices))
    rustworkx_index_to_id = dict(zip(node_indices, all_resource_ids))
    edges: list[tuple[int, int, ResptrLink | XMLLink]] = [
        (id_to_rustworkx_index[x.source_id], id_to_rustworkx_index[x.target_id], x) for x in resptr_links
    ]
    for xml in xml_links:
        edges.extend([(id_to_rustworkx_index[xml.source_id], id_to_rustworkx_index[x], xml) for x in xml.target_ids])
    graph.add_edges_from(edges)
    return graph, rustworkx_index_to_id, edges, set(node_indices)


def _remove_leaf_nodes(
    graph: rx.PyDiGraph[Any, Any],
    rustworkx_index_to_id: dict[int, str],
    node_indices: set[int],
) -> tuple[list[str], set[int]]:
    """
    Leaf nodes are nodes that do not have any outgoing links.
    This means that they have no dependencies and are ok to upload.
    This function removes them from the graph and the set with remaining nodes in the graph.

    Args:
        graph: graph
        rustworkx_index_to_id: the dictionary so that we can find our IDs with the nodes index number from rx
        node_indices: The set with the remaining node indices in the graph

    Returns:
        A list with the ids of the removed leaf nodes
        The set with the remaining nodes minus the leaf nodes
    """
    res: list[str] = []
    while leaf_nodes := [x for x in node_indices if graph.out_degree(x) == 0]:
        res.extend(rustworkx_index_to_id[n] for n in leaf_nodes)
        graph.remove_nodes_from(leaf_nodes)
        node_indices = node_indices - set(leaf_nodes)
    return res, node_indices


def _find_cheapest_outgoing_links(
    graph: rx.PyDiGraph[Any, Any],
    cycle: list[tuple[int, int]],
    edge_list: list[tuple[int, int, XMLLink | ResptrLink]],
) -> list[tuple[int, int, XMLLink | ResptrLink]]:
    """
    This function searches for the nodes whose outgoing links should be removed in order to break the cycle.
    It calculates which links between the resources create the smallest stash.

    Args:
        graph: graph
        cycle: the list with (source, target) for each edge in the cycle
        edge_list: list of all the edges that were in the original graph

    Returns:
        A list with the links that should be stashed.
        It contains all the edges connecting the two nodes.
    """
    costs = []
    for source, target in cycle:
        edges_in = graph.in_edges(source)
        node_gain = len(edges_in)
        edges_out = graph.out_edges(source)
        node_cost = sum(x[2].cost_links for x in edges_out)
        node_value = node_cost / node_gain
        costs.append((source, target, node_value, edges_out))
    cheapest_nodes = sorted(costs, key=lambda x: x[2])[0]
    cheapest_links = [x for x in edge_list if x[0] == cheapest_nodes[0] and x[1] == cheapest_nodes[1]]
    return cheapest_links


def _remove_edges_to_stash(
    graph: rx.PyDiGraph[Any, Any],
    edges_to_remove: list[tuple[int, int, XMLLink | ResptrLink]],
    edge_list: list[tuple[int, int, XMLLink | ResptrLink]],
    remaining_nodes: set[int],
) -> list[XMLLink | ResptrLink]:
    """
    This function removes the edges from the graph in order to break a cycle.
    It returns the information that enables us to identify the links in the real data.

    Args:
        graph: graph
        edges_to_remove: list of all the edges that should be removed
        edge_list: list of all the edges in the original graph
        remaining_nodes: set with the indexes of the nodes in the graph

    Returns:
        a list with the class instances that represent links to stash
    """
    source, target = edges_to_remove[0][0], edges_to_remove[0][1]
    links_to_stash = [x[2] for x in edges_to_remove]
    # if only one (source, target) is entered, it removes only one edge, not all
    # therefore we need as many entries in the list as there are edges between the source and target to break the cycle
    to_remove_list = [(x[0], x[1]) for x in edges_to_remove]
    phantom_links = []
    for instance in links_to_stash:
        if isinstance(instance, XMLLink):
            phantom_links.extend(_find_phantom_xml_edges(source, target, edge_list, instance, remaining_nodes))
    to_remove_list.extend(phantom_links)
    graph.remove_edges_from(to_remove_list)
    return links_to_stash


def _find_phantom_xml_edges(
    source: int,
    target: int,
    edge_list: list[tuple[int, int, XMLLink | ResptrLink]],
    xml_instance: XMLLink,
    remaining_nodes: set[int],
) -> list[tuple[int, int]]:
    """
    If an edge that will be removed represents an XML link
    the link may contain further links to other resources.
    If we stash the XMLLink then in the real data all the links are stashed.
    This is not automatically the case in the rx graph.
    We identify all the edges that need to be removed so that the rx graph represents the links that remain
    in the real data.

    Args:
        source: index of source node
        target: index of target node
        edge_list: list of all the edges in the original graph
        xml_instance: class instance that will be stashed
        remaining_nodes: indexes of all the nodes in the graph

    Returns:
        list with edges that represent the links in the original XML text
    """

    def check(x: tuple[int, int, XMLLink | ResptrLink]) -> bool:
        # if we do not check if the target is in the remaining_nodes (maybe removed because of leaf node)
        # we would get a NoEdgeBetweenNodes error
        return x[0] == source and x[1] != target and x[2] == xml_instance and x[1] in remaining_nodes

    return [(x[0], x[1]) for x in edge_list if check(x)]


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
    rustworkx_index_to_id: dict[int, str],
    edge_list: list[tuple[int, int, XMLLink | ResptrLink]],
    node_indices: set[int],
) -> tuple[dict[str, list[str]], list[str], int]:
    """
    Generate the order in which the resources should be uploaded to the DSP-API based on the dependencies.

    Args:
        graph: graph
        rustworkx_index_to_id: mapping between graph indices and original IDs
        edge_list: list of edges in the graph as tuple (source node, target node, link info)
        node_indices: index numbers of the nodes still in the graph

    Returns:
        A dictionary which maps the resources that have stashes to the UUIDs of the stashed links.
        A list of resource IDs which gives the order in which the resources should be uploaded to DSP-API.
        The number of links in the stash.
    """
    upload_order: list[str] = []
    stash_lookup: dict[str, list[str]] = {}
    leaf_nodes, node_indices = _remove_leaf_nodes(graph, rustworkx_index_to_id, node_indices)
    upload_order.extend(leaf_nodes)
    stash_counter = 0
    while node_indices:
        cycle = list(rx.digraph_find_cycle(graph))  # type: ignore[attr-defined]  # pylint: disable=no-member
        links_to_remove = _find_cheapest_outgoing_links(graph, cycle, edge_list)
        stash_counter += len(links_to_remove)
        links_to_stash = _remove_edges_to_stash(
            graph=graph,
            edges_to_remove=links_to_remove,
            edge_list=edge_list,
            remaining_nodes=node_indices,
        )
        stash_lookup = _add_stash_to_lookup_dict(stash_lookup, links_to_stash)
        leaf_nodes, node_indices = _remove_leaf_nodes(graph, rustworkx_index_to_id, node_indices)
        upload_order.extend(leaf_nodes)
    return stash_lookup, upload_order, stash_counter
