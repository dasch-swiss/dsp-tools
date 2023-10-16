from datetime import datetime
from itertools import chain

import regex
import rustworkx as rx
from lxml import etree
from viztracer import VizTracer

from dsp_tools.analyse_xml_data.models_xml_to_graph import ResptrLink, UploadResource, XMLLink


def _create_classes_from_root(root: etree._Element) -> tuple[list[ResptrLink], list[XMLLink], set[str]]:
    """Create instances of the classes ResptrLink and XMLLink from the root of the XML file."""
    resptr_instances = []
    xml_instances = []
    all_link_ids = []
    for resource in root.iter(tag="{https://dasch.swiss/schema}resource"):
        resptr, xml, all_links = _create_classes_single_resource(resource)
        if resptr:
            resptr_instances.extend(resptr)
        if xml:
            xml_instances.extend(xml)
        if all_links:
            all_link_ids.extend(all_links)
    return resptr_instances, xml_instances, set(all_link_ids)


def _create_classes_from_single_resource(
    resource: etree._Element,
) -> tuple[list[ResptrLink], list[XMLLink], list[str]] | tuple[None, None, None]:
    subject_id = resource.attrib.get("id")
    if not subject_id:
        return None, None, None
    all_used_ids = [subject_id]
    resptr_links, xml_links = _get_all_links_one_resource(resource)
    resptr_link_objects = []
    xml_link_objects = []
    if resptr_links:
        all_used_ids.extend(resptr_links)
        resptr_link_objects = [ResptrLink(subject_id, object_id) for object_id in resptr_links]
    if xml_links:
        all_used_ids.extend(chain.from_iterable(xml_links))
        xml_link_objects = [XMLLink(subject_id, x) for x in xml_links]
    return resptr_link_objects, xml_link_objects, all_used_ids


def _get_all_links_from_one_resource(resource: etree._Element) -> tuple[list[str], list[set[str]]]:
    resptr_links: list[str] = []
    xml_links: list[set[str]] = []
    for prop in resource.getchildren():
        match prop.tag:
            case "{https://dasch.swiss/schema}resptr-prop":
                resptr_links.extend(_extract_id_one_resptr_prop(prop))
            case "{https://dasch.swiss/schema}text-prop":
                xml_links.extend(_extract_id_one_text_prop(prop))
    return resptr_links, xml_links


def _extract_ids_from_one_resptr_prop(resptr_prop: etree._Element) -> list[str]:
    return [x.text for x in resptr_prop.getchildren() if x.text]


def _extract_id_one_text_prop(text_prop: etree._Element) -> list[set[str]]:
    # if the same ID is in several separate <text> values of one <text-prop>, they are considered separate links
    xml_props = []
    for text in text_prop.getchildren():
        links = _extract_id_one_text(text)
        if links:
            xml_props.append(links)
    return xml_props


def _extract_id_one_text(text: etree._Element) -> set[str]:
    # the same id in one <text> only means one link to the resource
    all_links = set()
    for ele in text.iterdescendants():
        if href := ele.attrib.get("href"):
            searched = regex.search(r"IRI:(.*):IRI", href)
            if searched:
                all_links.add(searched.group(1))
    return all_links


def _make_graph(
    resptr_instances: list[ResptrLink], xml_instances: list[XMLLink], all_link_ids: set[str]
) -> rx.PyDiGraph:  # type: ignore[type-arg] # pylint: disable=no-member
    g: rx.PyDiGraph = rx.PyDiGraph()  # type: ignore[type-arg] # pylint: disable=no-member
    nodes = [(id_, None, None) for id_ in all_link_ids]
    node_ids = [x[0] for x in nodes]
    node_inidices = g.add_nodes_from(nodes)
    lookup = dict(zip(node_ids, node_inidices))
    print(f"number of nodes: {len(nodes)}")
    resptr_edges = [(lookup[x.subject_id], lookup[x.object_id], 1) for x in resptr_instances]
    g.add_edges_from(resptr_edges)
    print(f"number of resptr edges: {len(resptr_edges)}")
    xml_edges = []
    for xml in xml_instances:
        xml_edges.extend([(lookup[xml.subject_id], lookup[x], xml.cost_links) for x in xml.object_link_ids])
    g.add_edges_from(xml_edges)
    print(f"number of xml edges: {len(xml_edges)}")
    return g


def _remove_leaf_nodes(g: rx.PyDiGraph) -> list[UploadResource]:  # type: ignore[type-arg] # pylint: disable=no-member
    res: list[UploadResource] = []
    while leaf_nodes := [x for x in g.node_indexes() if g.out_degree(x) == 0]:
        print(f"number of leaf nodes removed: {len(leaf_nodes)}")
        res.extend(UploadResource(g[n][0]) for n in leaf_nodes)
        g.remove_nodes_from(leaf_nodes)
    return res


def _find_cheapest_node(
    g: rx.PyDiGraph, cycle: rx.EdgeList  # type: ignore[type-arg] # pylint: disable=no-member
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
    removed_target_ids = [g[x[1]][0] for x in edges_out]
    return cheapest_node, removed_target_ids


def _generate_upload_order(
    g: rx.PyDiGraph,  # type: ignore[type-arg] # pylint: disable=no-member
) -> list[UploadResource]:
    removed_nodes = []
    leaf_nodes = _remove_leaf_nodes(g)
    removed_nodes.extend(leaf_nodes)
    while g.num_nodes():
        print(f"total number of nodes remaining: {g.num_nodes()}")
        cycle = rx.digraph_find_cycle(g)  # type: ignore[attr-defined]  # pylint: disable=no-member
        print("-" * 10)
        print(f"cycle: {cycle}")
        node = _find_cheapest_node(g, cycle)
        source, targets = node
        removed_nodes.append(UploadResource(g[source][0], targets))
        g.remove_node(source)
        print(f"removed link: {node}")
        leaf_nodes = _remove_leaf_nodes(g)
        removed_nodes.extend(leaf_nodes)
    return removed_nodes


def analyse_circles_in_data(xml_filepath: str, tracer_output: str) -> None:
    """
    This function takes an XML filepath
    It analyzes how many and which links have to be removed
    so that all circular references are broken up.

    Args:
        xml_filepath: path to the file
        tracer_output: name of the file where the viztracer results should be saved
    """
    print(datetime.now())
    print("=" * 80)
    tracer = VizTracer(
        minimize_memory=True,
        ignore_c_function=True,
        ignore_frozen=True,
        include_files=["extract_links_from_XML.py", "models_xml_to_graph.py"],
    )
    tracer.start()
    tree = etree.parse(xml_filepath)
    root = tree.getroot()
    resptr_instances, xml_instances, all_link_ids = _create_classes_from_root(root)
    print(f"number of node ids: {len(all_link_ids)}")
    print(f"number of resptr instances: {len(resptr_instances)}")
    print(f"number of xml instances: {len(xml_instances)}")
    print("-" * 20)
    g = _make_graph(resptr_instances, xml_instances, all_link_ids)
    print("=" * 80)
    removed_nodes = _generate_upload_order(g)
    tracer.stop()
    tracer.save(output_file=tracer_output)
    print("=" * 80)
    for n in removed_nodes:
        print(n)
    print("=" * 80)
    print(datetime.now())
