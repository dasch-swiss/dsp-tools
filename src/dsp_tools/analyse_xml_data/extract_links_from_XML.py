from datetime import datetime
from pathlib import Path

import regex
import rustworkx as rx
from lxml import etree
from viztracer import VizTracer

from dsp_tools.analyse_xml_data.models import ResourceStashInfo, ResptrLink, XMLLink


def create_info_from_xml_for_graph(
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
    # TODO: etree ele should not need to be returned, check
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
    resptr_instances: list[ResptrLink], xml_instances: list[XMLLink], all_resource_ids: list[str]
) -> tuple[
    rx.PyDiGraph,  # type: ignore[type-arg] # pylint: disable=no-member
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
    node_inidices = g.add_nodes_from(nodes)
    node_inidices = list(node_inidices)
    node_id_lookup = dict(zip(all_resource_ids, node_inidices))
    node_index_lookup = dict(zip(node_inidices, all_resource_ids))
    print(f"number of nodes: {len(nodes)}")
    edges: list[tuple[int, int, ResptrLink | XMLLink]] = [
        (node_id_lookup[x.subject_id], node_id_lookup[x.object_id], x) for x in resptr_instances
    ]
    for xml in xml_instances:
        edges.extend([(node_id_lookup[xml.subject_id], node_id_lookup[x], xml) for x in xml.object_link_ids])
    g.add_edges_from(edges)
    print(f"number of edges: {len(edges)}")
    return g, node_index_lookup, edges, set(node_inidices)


def _remove_leaf_nodes(
    g: rx.PyDiGraph,  # type: ignore[type-arg] # pylint: disable=no-member
    node_index_lookup: dict[int, str],
    node_inidices: set[int],
) -> tuple[list[ResourceStashInfo], set[int]]:
    res: list[ResourceStashInfo] = []
    # TODO: research g.node_indexes() get as list/set
    while leaf_nodes := [x for x in node_inidices if g.out_degree(x) == 0]:
        print(f"number of leaf nodes removed: {len(leaf_nodes)}")
        res.extend(ResourceStashInfo(node_index_lookup[n]) for n in leaf_nodes)
        # TODO: remove indices form the node ingex list/set return
        g.remove_nodes_from(leaf_nodes)
        node_inidices = node_inidices - set(leaf_nodes)
    return res, node_inidices


def _find_cheapest_node(
    g: rx.PyDiGraph,  # type: ignore[type-arg] # pylint: disable=no-member
    cycle: rx.EdgeList,  # pylint: disable=no-member
) -> tuple[int, int]:
    costs = []
    for source, target in cycle:
        edges_in = g.in_edges(source)
        node_gain = len(edges_in)
        edges_out = g.out_edges(source)
        node_cost = sum(x[2].cost_links for x in edges_out)
        node_value = node_cost / node_gain
        costs.append((source, node_value, target))
    sorted_nodes = sorted(costs, key=lambda x: x[1])
    cheapest_node, _, target_node = sorted_nodes[0]
    print("cheapest node", cheapest_node)
    return cheapest_node, target_node


def _remove_edges_get_removed_class_instances(
    g: rx.PyDiGraph,  # type: ignore[type-arg] # pylint: disable=no-member,
    edges_to_remove: tuple[int, int],  # pylint: disable=no-member
    node_index_lookup: dict[int, str],
    edge_list: list[tuple[int, int, XMLLink | ResptrLink]],
) -> ResourceStashInfo:
    g.remove_nodes_from(edges_to_remove)
    links_to_stash = [x[2] for x in edge_list if x[0] == edges_to_remove[0] and x[1] == edges_to_remove[1]]
    return ResourceStashInfo(node_index_lookup[edges_to_remove[0]], links_to_stash)


def _generate_upload_order(
    g: rx.PyDiGraph,  # type: ignore[type-arg] # pylint: disable=no-member
    node_index_lookup: dict[int, str],
    edge_list: list[tuple[int, int, XMLLink | ResptrLink]],
    node_inidices: set[int],
) -> list[ResourceStashInfo]:
    """
    This function takes a graph and a dictionary with the mapping between the graph indices and original ids.
    It generates the order in which the resources should be uploaded to the DSP-API based on the dependencies.

    Args:
        g: graph
        node_index_lookup: reference between graph indices and original id

    Returns:
        List of instances that contain the information of the resource id and its links.
    """
    removed_nodes = []
    leaf_nodes, node_inidices = _remove_leaf_nodes(g, node_index_lookup, node_inidices)
    removed_nodes.extend(leaf_nodes)
    removed_from_cycle = 0
    while node_inidices:
        # TODO: find length of cycles in real data
        cycles = list(rx.simple_cycles(g))
        # TODO: make sets then find ones that don't overlap
        # TODO: find overlap (innumerate iteration over list) find not overlapping set
        # TODO: get the original list from cycles and
        print(f"total number of nodes remaining: {g.num_nodes()}")
        cycle = rx.digraph_find_cycle(g)  # type: ignore[attr-defined]  # pylint: disable=no-member
        print("-" * 10)
        print(f"cycle: {cycle}")
        node_edges = _find_cheapest_node(g, cycle)
        removed_nodes.append(
            _remove_edges_get_removed_class_instances(
                g=g, edges_to_remove=node_edges, node_index_lookup=node_index_lookup, edge_list=edge_list
            )
        )
        source, targets = node_edges
        g.remove_node(source)
        removed_nodes.append(ResourceStashInfo(node_index_lookup[source]))
        removed_from_cycle += 1
        print(f"removed link: {node_edges}")
        leaf_nodes, node_inidices = _remove_leaf_nodes(g, node_index_lookup, node_inidices)
        removed_nodes.extend(leaf_nodes)
    print("=" * 80)
    print(f"total cycles broken: {removed_from_cycle}")
    return removed_nodes


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
        ignore_c_function=True,
        ignore_frozen=True,
        include_files=["extract_links_from_XML.py", "models.py"],
    )
    tracer.start()
    tree = etree.parse(xml_filepath)
    root = tree.getroot()
    root, resptr_instances, xml_instances, all_resource_ids = create_info_from_xml_for_graph(root)
    print(f"Total Number of Resources: {len(all_resource_ids)}")
    print(f"Total Number of resptr Links: {len(resptr_instances)}")
    print(f"Total Number of XML Texts with Links: {len(xml_instances)}")
    print("=" * 80)
    # TODO: we also need the xml_instances later
    g, node_index_lookup, edges, node_inidices = make_graph(resptr_instances, xml_instances, all_resource_ids)
    print("=" * 80)
    resource_upload_order = _generate_upload_order(g, node_index_lookup, edges, node_inidices)
    print("=" * 80)
    tracer.stop()
    if save_tracer:
        tracer.save(output_file=tracer_output_file)
    print("=" * 80)
    print("Start time:", start)
    print("End time:", datetime.now())
    return resource_upload_order


if __name__ == "__main__":
    analyse_circles_in_data(
        xml_filepath=Path(
            "/Users/noraammann/Documents/Miscelaneous/dsp-tools_notes/improve_xmlupload/analyse_real_data/sgv_data/sgv-v8.7_v3.0_final-clean-up.xml"
        ),
        tracer_output_file="circular_references_tracer.json",
        save_tracer=False,
    )
