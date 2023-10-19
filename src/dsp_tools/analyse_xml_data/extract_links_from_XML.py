from datetime import datetime
from pathlib import Path

import regex
import rustworkx as rx
from lxml import etree
from viztracer import VizTracer

from dsp_tools.analyse_xml_data.models import ResourceStashInfo, ResptrLink, XMLLink


def _create_info_from_xml_for_graph(
    root: etree._Element,
) -> tuple[etree._Element, list[ResptrLink], list[XMLLink], list[str]]:
    """Create instances of the classes ResptrLink and XMLLink from the root of the XML file."""
    resptr_instances = []
    xml_instances = []
    all_resource_ids = []
    for resource in root.iter(tag="{https://dasch.swiss/schema}resource"):
        resptr, xml, subject_id = _create_info_from_xml_for_graph_from_one_resource(resource)
        all_resource_ids.append(subject_id)
        resptr_instances.extend(resptr)
        xml_instances.extend(xml)
    return root, resptr_instances, xml_instances, all_resource_ids


def _create_info_from_xml_for_graph_from_one_resource(
    resource: etree._Element,
) -> tuple[list[ResptrLink], list[XMLLink], str]:
    subject_id = resource.attrib["id"]
    resptr_links, xml_links = _get_all_links_from_one_resource(subject_id, resource)
    return resptr_links, xml_links, subject_id


def _get_all_links_from_one_resource(
    subject_id: str, resource: etree._Element
) -> tuple[list[ResptrLink], list[XMLLink]]:
    resptr_links: list[ResptrLink] = []
    xml_links: list[XMLLink] = []
    for prop in resource.getchildren():
        match prop.tag:
            case "{https://dasch.swiss/schema}resptr-prop":
                resptr_links.extend(_create_class_instance_resptr_link(subject_id, prop))
            case "{https://dasch.swiss/schema}text-prop":
                xml_links.extend(_create_class_instance_text_prop(subject_id, prop))
    return resptr_links, xml_links


def _create_class_instance_resptr_link(subject_id: str, resptr_prop: etree._Element) -> list[ResptrLink]:
    resptr_links = []
    for resptr in resptr_prop.getchildren():
        if r_text := resptr.text:
            instance = ResptrLink(subject_id, r_text)
            # this UUID is so that the links that were stashed can be identified in the XML data file
            resptr.attrib["stashUUID"] = instance.link_uuid
            resptr_links.append(instance)
    return resptr_links


def _create_class_instance_text_prop(subject_id: str, text_prop: etree._Element) -> list[XMLLink]:
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


def _make_graph(
    resptr_instances: list[ResptrLink], xml_instances: list[XMLLink], all_resource_ids: list[str]
) -> tuple[  # type: ignore[type-arg]
    rx.PyDiGraph,  # pylint: disable=no-member
    dict[int, str],
    list[tuple[int, int, ResptrLink | XMLLink]],
    set[int],
]:
    """
    This function takes information about the resources (nodes) and links between them (edges).
    From that it constructs a rustworkx directed graph.

    Args:
        resptr_instances: Instances of resptr links
        xml_instances: Instances of links to texts containing links to other resources
        all_resource_ids: IDs of all the resources in the graph

    Returns:
        The rustworkx graph and a dictionary that contains the index number of the nodes with the original resource id
    """
    g: rx.PyDiGraph = rx.PyDiGraph()  # type: ignore[type-arg] # pylint: disable=no-member
    nodes = [(id_, None, None) for id_ in all_resource_ids]
    node_indices = g.add_nodes_from(nodes)
    node_indices = list(node_indices)  # type: ignore[assignment]
    node_id_lookup = dict(zip(all_resource_ids, node_indices))
    node_index_lookup = dict(zip(node_indices, all_resource_ids))
    edges: list[tuple[int, int, ResptrLink | XMLLink]] = [
        (node_id_lookup[x.subject_id], node_id_lookup[x.object_id], x) for x in resptr_instances
    ]
    for xml in xml_instances:
        edges.extend([(node_id_lookup[xml.subject_id], node_id_lookup[x], xml) for x in xml.object_link_ids])
    g.add_edges_from(edges)
    return g, node_index_lookup, edges, set(node_indices)


def _remove_leaf_nodes(
    g: rx.PyDiGraph,  # type: ignore[type-arg] # pylint: disable=no-member
    node_index_lookup: dict[int, str],
    node_indices: set[int],
) -> tuple[list[str], set[int]]:
    """
    Leaf nodes are nodes that do not have any outgoing links.
    This means that they have no dependencies and are ok to upload.
    This function removes them from the graph and the set with remaining nodes in the graph.

    Args:
        g: graph
        node_index_lookup: the dictionary so that we can find our IDs with the nodes index number from rx
        node_indices: The set with the remaining node indices in the graph

    Returns:
        A list with the ids of the removed leaf nodes
        The set with the remaining nodes minus the leaf nodes
    """
    res: list[str] = []
    while leaf_nodes := [x for x in node_indices if g.out_degree(x) == 0]:
        res.extend(node_index_lookup[n] for n in leaf_nodes)
        g.remove_nodes_from(leaf_nodes)
        node_indices = node_indices - set(leaf_nodes)
    return res, node_indices


def _find_cheapest_outgoing_links(
    g: rx.PyDiGraph,  # type: ignore[type-arg] # pylint: disable=no-member
    cycle: list[tuple[int, int]],
    edge_list: list[tuple[int, int, XMLLink | ResptrLink]],
) -> list[tuple[int, int, XMLLink | ResptrLink]]:
    """
    This function searches for the nodes whose outgoing links should be removed in order to break the cycle.
    It calculates which links between the resources create the smallest stash.

    Args:
        g: graph
        cycle: the list with (source, target) for each edge in the cycle
        edge_list: list of all the edges that were in the original graph

    Returns:
        A list with the links that should be stashed.
        It contains all the edges connecting the two nodes.
    """
    costs = []
    for source, target in cycle:
        edges_in = g.in_edges(source)
        node_gain = len(edges_in)
        edges_out = g.out_edges(source)
        node_cost = sum(x[2].cost_links for x in edges_out)
        node_value = node_cost / node_gain
        costs.append((source, target, node_value, edges_out))
    cheapest_nodes = sorted(costs, key=lambda x: x[2])[0]
    cheapest_links = [x for x in edge_list if x[0] == cheapest_nodes[0] and x[1] == cheapest_nodes[1]]
    return cheapest_links


def _remove_edges_get_removed_class_instances(
    g: rx.PyDiGraph,  # type: ignore[type-arg] # pylint: disable=no-member,
    edges_to_remove: list[tuple[int, int, XMLLink | ResptrLink]],
    node_index_lookup: dict[int, str],
    edge_list: list[tuple[int, int, XMLLink | ResptrLink]],
    remaining_nodes: set[int],
) -> list[XMLLink | ResptrLink]:
    """
    This function removes the edges from the graph in order to break a cycle.
    It returns the information that enables us to identify the links in the real data.

    Args:
        g: graph
        edges_to_remove: list of all the edges that should be removed
        node_index_lookup: lookup to identify our IDs according to rx node indices
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
            phantom_links.extend(_find_remove_phantom_xml_edges(source, target, edge_list, instance, remaining_nodes))
    to_remove_list.extend(phantom_links)
    g.remove_edges_from(to_remove_list)
    return links_to_stash


def _find_remove_phantom_xml_edges(
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
    stash_dict: dict[str, list[str]], to_stash_links: list[XMLLink | ResptrLink]
) -> dict[str, list[str]]:
    stash_list = [stash_link.link_uuid for stash_link in to_stash_links]
    # all stashed links have the same subject id, so we can just take the first one
    subj_id = to_stash_links[0].subject_id
    if subj_id in stash_dict.keys():
        stash_dict[subj_id].extend(stash_list)
    else:
        stash_dict[subj_id] = stash_list
    return stash_dict


def generate_upload_order(
    g: rx.PyDiGraph,  # type: ignore[type-arg] # pylint: disable=no-member
    node_index_lookup: dict[int, str],
    edge_list: list[tuple[int, int, XMLLink | ResptrLink]],
    node_indices: set[int],
) -> tuple[dict[str, list[str]], list[str], int]:
    """
    This function takes a graph and a dictionary with the mapping between the graph indices and original ids.
    It generates the order in which the resources should be uploaded to the DSP-API based on the dependencies.

    Args:
        g: graph
        node_index_lookup: reference between graph indices and original id
        edge_list: list of edges in the graph as tuple (source_node, target_node, Class Instance)
        node_indices: index numbers of the nodes still in the graph

    Returns:
        List of instances that contain the information of the resource id and its links.
        The number of links in the stash.
    """
    upload_order: list[str] = []
    stash_lookup: dict[str, list[str]] = {}
    leaf_nodes, node_indices = _remove_leaf_nodes(g, node_index_lookup, node_indices)
    upload_order.extend(leaf_nodes)
    stash_counter = 0
    while node_indices:
        cycle = list(rx.digraph_find_cycle(g))  # type: ignore[attr-defined]  # pylint: disable=no-member
        links_to_remove = _find_cheapest_outgoing_links(g, cycle, edge_list)
        stash_counter += len(links_to_remove)
        links_to_stash = _remove_edges_get_removed_class_instances(
            g=g,
            edges_to_remove=links_to_remove,
            node_index_lookup=node_index_lookup,
            edge_list=edge_list,
            remaining_nodes=node_indices,
        )
        stash_lookup = _add_stash_to_lookup_dict(stash_lookup, links_to_stash)
        leaf_nodes, node_indices = _remove_leaf_nodes(g, node_index_lookup, node_indices)
        upload_order.extend(leaf_nodes)
    return stash_lookup, upload_order, stash_counter


def analyse_circles_in_data(
    xml_filepath: Path, tracer_output_file: str, save_tracer: bool = False
) -> list[ResourceStashInfo]:
    """
    This function takes an XML filepath
    It analyzes how many and which links have to be removed
    so that all circular references are broken up.

    Args:
        xml_filepath: path to the file
        tracer_output_file: name of the file where the viztracer results should be saved
        save_tracer: True if the output of the viztracer should be saved

    Returns:
        The order in which the resources should be uploaded.
    """
    start = datetime.now()
    print("=" * 80)
    tracer = VizTracer(
        minimize_memory=True,
        max_stack_depth=3,
    )
    tracer.start()
    tree = etree.parse(xml_filepath)
    root = tree.getroot()
    root, resptr_instances, xml_instances, all_resource_ids = _create_info_from_xml_for_graph(root)
    print(f"Total Number of Resources: {len(all_resource_ids)}")
    print(f"Total Number of resptr Links: {len(resptr_instances)}")
    print(f"Total Number of XML Texts with Links: {len(xml_instances)}")
    print("=" * 80)
    g, node_index_lookup, edges, node_indices = _make_graph(resptr_instances, xml_instances, all_resource_ids)
    _, _, stash_counter = generate_upload_order(g, node_index_lookup, edges, node_indices)
    print("Number of Links Stashed:", stash_counter)
    tracer.stop()
    if save_tracer:
        tracer.save(output_file=tracer_output_file)
    print("=" * 80)
    print("Start time:", start)
    print("End time:", datetime.now())
    print("=" * 80)
    # TODO: change here to list with IDs
    # TODO: change here to dict


if __name__ == "__main__":
    analyse_circles_in_data(
        xml_filepath=Path("testdata/xml-data/circular-references/test_circular_references_1.xml"),
        tracer_output_file="circular_references_tracer.json",
        save_tracer=False,
    )
