from itertools import chain
from typing import Any

import regex
import rustworkx as rx
from lxml import etree

from dsp_tools.analyse_xml_data.models_xml_to_graph import ResptrLink, XMLLink


def create_classes_from_root(root: etree._Element) -> tuple[list[ResptrLink], list[XMLLink], set[str]]:
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


def _create_classes_single_resource(
    resource: etree._Element,
) -> tuple[list[ResptrLink] | None, list[XMLLink] | None, list[str] | None]:
    subject_id = resource.attrib.get("id")
    if not subject_id:
        return None, None, None
    all_used_ids = [subject_id]
    resptr_links, xml_links = _get_all_links_one_resource(resource)
    if resptr_links:
        all_used_ids.extend(resptr_links)
        weight_dict = _make_weighted_resptr_links(resptr_links)
        resptr_link_objects = [ResptrLink(subject_id, k, v) for k, v in weight_dict.items()]
    if xml_links:
        all_used_ids.extend(chain.from_iterable(xml_links))
        xml_link_objects = [XMLLink(subject_id, x) for x in xml_links]
    return resptr_link_objects, xml_link_objects, all_used_ids


def _make_weighted_resptr_links(resptr_links: list[str]) -> dict[str, int]:
    weight_dict = {link: 0 for link in set(resptr_links)}
    for link in resptr_links:
        weight_dict[link] += 1
    return weight_dict


def _get_all_links_one_resource(resource: etree._Element) -> tuple[list[str], list[set[str]]]:
    resptr_links: list[str] = []
    xml_links: list[set[str]] = []
    for prop in resource.getchildren():
        match prop.tag:
            case "{https://dasch.swiss/schema}resptr-prop":
                resptr_links.extend(_extract_id_one_resptr_prop(prop))
            case "{https://dasch.swiss/schema}text-prop":
                xml_links.extend(_extract_id_one_text_prop(prop))
    return resptr_links, xml_links


def _extract_id_one_resptr_prop(resptr_prop: etree._Element) -> list[str]:
    return [x.text for x in resptr_prop.getchildren() if x.text]


def _extract_id_one_text_prop(text_prop: etree._Element) -> list[set[str]]:
    # the same ID is in several separate <text> in one <text-prop> are considered separate links
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


def make_graph(
    resptr_instances: list[ResptrLink], xml_instances: list[XMLLink], all_link_ids: set[str]
) -> rx.PyDiGraph[Any, Any]:  # pylint: disable=no-member
    g = rx.PyDiGraph[Any, Any]()  # pylint: disable=no-member
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


def _remove_leaf_nodes(g: rx.PyDiGraph[Any, Any]) -> None:  # pylint: disable=no-member
    while leaf_nodes := [x for x in g.node_indexes() if g.out_degree(x) == 0]:
        print(f"number of leaf nodes removed: {len(leaf_nodes)}")
        g.remove_nodes_from(leaf_nodes)


def _find_cheapest_node(
    g: rx.PyDiGraph[Any, Any], cycle: rx.EdgeList  # pylint: disable=no-member
) -> tuple[int, float]:
    costs = []
    for source, _ in cycle:
        edges_in = g.in_edges(source)
        node_gain = len(edges_in)
        edges_out = g.out_edges(source)
        node_cost = sum(x[2] for x in edges_out)
        node_value = node_cost / node_gain
        costs.append((source, node_value))
    cheapest_node = sorted(costs, key=lambda x: x[1])[0]
    return cheapest_node


def main() -> None:
    print("-" * 20)
    tree = etree.parse("testdata/xml-data/circular-references/test_circular_references_1.xml")
    root = tree.getroot()
    resptr_instances, xml_instances, all_link_ids = create_classes_from_root(root)
    print(f"number of node ids: {len(all_link_ids)}")
    print(f"number of resptr instances: {len(resptr_instances)}")
    print(f"number of xml instances: {len(xml_instances)}")
    print("-" * 20)
    g = make_graph(resptr_instances, xml_instances, all_link_ids)
    print("-" * 20)
    _remove_leaf_nodes(g)
    print("-" * 20)
    print(f"number of nodes remaining: {g.num_nodes()}")
    print(f"number of edges remaining: {g.num_edges()}")
    print("=" * 80)
    removed_nodes = []
    while g.num_nodes() > 0:
        cycle = rx.digraph_find_cycle(g)  # type: ignore[attr-defined]  # pylint: disable=no-member
        print("-" * 10)
        print(f"cycle: {cycle}")
        node = _find_cheapest_node(g, cycle)
        source, _ = node
        g.remove_node(source)
        removed_nodes.append(node)
        print(f"removed link: {node}")
        print("-" * 40)
        _remove_leaf_nodes(g)
        print(f"total number of nodes remaining: {g.num_nodes()}")
        print("-" * 50)
    print("=" * 80)
    print(removed_nodes)
    print("=" * 80)


if __name__ == "__main__":
    main()
