from datetime import datetime
from pathlib import Path

import regex
import rustworkx as rx
from lxml import etree
from viztracer import VizTracer

from dsp_tools.analyse_xml_data.models import ResptrLink, UploadResource, XMLLink


def _create_info_from_xml_for_graph(root: etree._Element) -> tuple[list[ResptrLink], list[XMLLink], set[str]]:
    """Create instances of the classes ResptrLink and XMLLink from the root of the XML file."""
    resptr_instances = []
    xml_instances = []
    all_resource_ids = set()
    for resource in root.iter(tag="{https://dasch.swiss/schema}resource"):
        resptr, xml, subject_id = _create_info_from_xml_for_graph_from_one_resource(resource)
        if resptr:
            resptr_instances.extend(resptr)
        if xml:
            xml_instances.extend(xml)
        if subject_id:
            all_resource_ids.add(subject_id)
    return resptr_instances, xml_instances, set(all_resource_ids)


def _create_info_from_xml_for_graph_from_one_resource(
    resource: etree._Element,
) -> tuple[list[ResptrLink], list[XMLLink], str]:
    subject_id = resource.attrib["id"]
    resptr_links, xml_links = _get_all_links_from_one_resource(resource)
    resptr_link_objects = []
    xml_link_objects = []
    if resptr_links:
        resptr_link_objects = [ResptrLink(subject_id, object_id) for object_id in resptr_links]
    if xml_links:
        xml_link_objects = [XMLLink(subject_id, x) for x in xml_links]
    return resptr_link_objects, xml_link_objects, subject_id


def _get_all_links_from_one_resource(resource: etree._Element) -> tuple[list[str], list[set[str]]]:
    resptr_links: list[str] = []
    xml_links: list[set[str]] = []
    for prop in resource.getchildren():
        match prop.tag:
            case "{https://dasch.swiss/schema}resptr-prop":
                resptr_links.extend(_extract_ids_from_one_resptr_prop(prop))
            case "{https://dasch.swiss/schema}text-prop":
                xml_links.extend(_extract_ids_from_text_prop(prop))
    return resptr_links, xml_links


def _extract_ids_from_one_resptr_prop(resptr_prop: etree._Element) -> list[str]:
    return [x.text for x in resptr_prop.getchildren() if x.text]


def _extract_ids_from_text_prop(text_prop: etree._Element) -> list[set[str]]:
    # if the same ID is in several separate <text> values of one <text-prop>, they are considered separate links
    xml_props = []
    for text in text_prop.getchildren():
        links = _extract_ids_from_one_text_value(text)
        if links:
            xml_props.append(links)
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
    resptr_instances: list[ResptrLink], xml_instances: list[XMLLink], all_resource_ids: set[str]
) -> tuple[rx.PyDiGraph, dict[int, str]]:  # type: ignore[type-arg] # pylint: disable=no-member
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
    node_ids = [x[0] for x in nodes]
    node_inidices = g.add_nodes_from(nodes)
    node_id_lookup = dict(zip(node_ids, node_inidices))
    node_index_lookup = dict(zip(node_inidices, node_ids))
    print(f"number of nodes: {len(nodes)}")
    resptr_edges = [(node_id_lookup[x.subject_id], node_id_lookup[x.object_id], 1) for x in resptr_instances]
    g.add_edges_from(resptr_edges)
    print(f"number of resptr edges: {len(resptr_edges)}")
    xml_edges = []
    for xml in xml_instances:
        xml_edges.extend(
            [(node_id_lookup[xml.subject_id], node_id_lookup[x], xml.cost_links) for x in xml.object_link_ids]
        )
    g.add_edges_from(xml_edges)
    print(f"number of xml edges: {len(xml_edges)}")
    return g, node_index_lookup


def _remove_leaf_nodes(
    g: rx.PyDiGraph,  # type: ignore[type-arg] # pylint: disable=no-member
    node_index_lookup: dict[int, str],
) -> list[UploadResource]:
    res: list[UploadResource] = []
    while leaf_nodes := [x for x in g.node_indexes() if g.out_degree(x) == 0]:
        print(f"number of leaf nodes removed: {len(leaf_nodes)}")
        res.extend(UploadResource(node_index_lookup[n]) for n in leaf_nodes)
        g.remove_nodes_from(leaf_nodes)
    return res


def _find_cheapest_node(
    g: rx.PyDiGraph,  # type: ignore[type-arg] # pylint: disable=no-member
    cycle: rx.EdgeList,  # type: ignore[type-arg] # pylint: disable=no-member
    node_index_lookup: dict[int, str],
) -> tuple[int, list[str]]:
    costs = []
    for source, _ in cycle:
        edges_in = g.in_edges(source)
        node_gain = len(edges_in)
        edges_out = g.out_edges(source)
        node_cost = sum(x[2] for x in edges_out)
        node_value = node_cost / node_gain
        costs.append((source, node_value, edges_out))
    sorted_nodes = sorted(costs, key=lambda x: x[1])
    cheapest_node, _, edges_out = sorted_nodes[0]
    print("cheapest", cheapest_node)
    removed_target_ids: list[str] = [node_index_lookup[x[1]] for x in edges_out]
    return cheapest_node, removed_target_ids


def _generate_upload_order(
    g: rx.PyDiGraph,  # type: ignore[type-arg] # pylint: disable=no-member
    node_index_lookup: dict[int, str],
) -> list[UploadResource]:
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
    leaf_nodes = _remove_leaf_nodes(g, node_index_lookup)
    removed_nodes.extend(leaf_nodes)
    removed_from_cycle = 0
    while g.num_nodes():
        print(f"total number of nodes remaining: {g.num_nodes()}")
        cycle = rx.digraph_find_cycle(g)  # type: ignore[attr-defined]  # pylint: disable=no-member
        print("-" * 10)
        print(f"cycle: {cycle}")
        node = _find_cheapest_node(g, cycle, node_index_lookup)
        source, targets = node
        removed_nodes.append(UploadResource(g[source][0], targets))
        g.remove_node(source)
        removed_from_cycle += 1
        print(f"removed link: {node}")
        leaf_nodes = _remove_leaf_nodes(g, node_index_lookup)
        removed_nodes.extend(leaf_nodes)
    print("=" * 80)
    print(f"removed links total: {removed_from_cycle}")
    return removed_nodes


def analyse_circles_in_data(xml_filepath: Path, tracer_output_file: str) -> list[UploadResource]:
    """
    This function takes an XML filepath
    It analyzes how many and which links have to be removed
    so that all circular references are broken up.

    Args:
        xml_filepath: path to the file
        tracer_output_file: name of the file where the viztracer results should be saved
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
    resptr_instances, xml_instances, all_resource_ids = _create_info_from_xml_for_graph(root)
    print(f"Total Number of Resources: {len(all_resource_ids)}")
    print(f"Total Number of resptr Links: {len(resptr_instances)}")
    print(f"Total Number of XML Texts with Links: {len(xml_instances)}")
    print("=" * 80)
    g, node_index_lookup = _make_graph(resptr_instances, xml_instances, all_resource_ids)
    print("=" * 80)
    resource_upload_order = _generate_upload_order(g, node_index_lookup)
    print("=" * 80)
    tracer.stop()
    tracer.save(output_file=tracer_output_file)
    print("=" * 80)
    print("Start time:", start)
    print("End time:", datetime.now())
    return resource_upload_order


if __name__ == "__main__":
    analyse_circles_in_data(
        xml_filepath=Path("testdata/xml-data/circular-references/test_circular_references_1.xml"),
        tracer_output_file="circular_references_tracer.json",
    )
