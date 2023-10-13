from itertools import chain

import regex
import rustworkx as rx
from lxml import etree

from dsp_tools.analyse_xml_data.models_xml_to_graph import ResptrLink, XMLLink


def create_classes_from_root(root: etree._Element) -> tuple[list[ResptrLink], list[XMLLink], set[str]]:
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
    all_used_ids = [subject_id]
    resptr_links, xml_links = _get_all_links_one_resource(resource)
    if resptr_links:
        all_used_ids.extend(resptr_links)
        weight_dict = _make_weighted_resptr_links(resptr_links)
        resptr_links = [ResptrLink(subject_id=subject_id, object_id=k, edge_weight=v) for k, v in weight_dict.items()]
    if xml_links:
        all_used_ids.extend(chain.from_iterable(xml_links))
        xml_links = [XMLLink(subject_id=subject_id, object_link_ids=x) for x in xml_links]
    return resptr_links, xml_links, all_used_ids


def _make_weighted_resptr_links(resptr_links: list[str]) -> dict[str, int]:
    weight_dict = {link: 0 for link in set(resptr_links)}
    for link in resptr_links:
        weight_dict[link] += 1
    return weight_dict


def _get_all_links_one_resource(resource: etree._Element) -> list[str] | None and list[set[str]] | None:
    resptr_links = []
    xml_links = []
    for prop in resource.getchildren():
        match prop.tag:
            case "{https://dasch.swiss/schema}resptr-prop":
                links = _extract_id_one_resptr_prop(prop)
                match links:
                    case list():
                        resptr_links.extend(links)
                    case None:
                        continue
            case "{https://dasch.swiss/schema}text-prop":
                links = _extract_id_one_text_prop(prop)
                match links:
                    case list():
                        xml_links.extend(links)
                    case None:
                        continue
    if len(resptr_links) == 0:
        resptr_links = None
    if len(xml_links) == 0:
        xml_links = None
    return resptr_links, xml_links


def _extract_id_one_resptr_prop(resptr_prop: etree._Element) -> list[str]:
    return [x.text for x in resptr_prop.getchildren()]


def _extract_id_one_text_prop(text_prop: etree._Element) -> list[set[str]] | None:
    # the same ID is in several separate <text> in one <text-prop> are considered separate links
    xml_props = []
    for text in text_prop.getchildren():
        links = _extract_id_one_text(text)
        match links:
            case set():
                xml_props.append(links)
            case None:
                continue
    if len(xml_props) == 0:
        return None
    else:
        return xml_props


def _extract_id_one_text(text: etree._Element) -> set[str] | None:
    # the same id in one <text> only means one link to the resource
    all_links = set()
    for ele in text.iterdescendants():
        if href := ele.attrib.get("href"):
            searched = regex.search(r"IRI:(.*):IRI", href)
            match searched:
                case regex.Match():
                    all_links.add(searched.group(1))
                case None:
                    continue
    if len(all_links) == 0:
        return None
    else:
        return all_links


def make_graph(
    resptr_instances: list[ResptrLink], xml_instances: list[XMLLink], all_link_ids: set[str]
) -> rx.PyDiGraph:
    g = rx.PyDiGraph()
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


def find_cheapest_link(g: rx.PyDiGraph, cycle: rx.EdgeList) -> tuple[int, int, float]:
    costs = []
    for source, target in cycle:
        edges_in = g.in_edges(source)
        node_gain = len(edges_in)
        edges_out = g.out_edges(source)
        node_cost = sum([x[2] for x in edges_out])
        node_value = node_cost / node_gain
        costs.append((source, target, node_value))
    out_going_link_to_remove = sorted(costs, key=lambda x: x[2])[0]
    return out_going_link_to_remove


def main() -> None:
    tree = etree.parse("testdata/xml-data/circular-references/test_circular_references_1.xml")
    root = tree.getroot()
    resptr_instances, xml_instances, all_link_ids = create_classes_from_root(root)
    print(f"number of node ids: {len(all_link_ids)}")
    print(f"number of resptr instances: {len(resptr_instances)}")
    print(f"number of xml instances: {len(xml_instances)}")
    print("-" * 20)
    g = make_graph(resptr_instances, xml_instances, all_link_ids)
    print("-" * 20)
    removed_edges = []
    while cycle := rx.digraph_find_cycle(g):
        print(f"cycle: {cycle}")
        link = find_cheapest_link(g, cycle)
        source, target, _ = link
        g.remove_edge(source, target)
        removed_edges.append(link)
    print(removed_edges)


if __name__ == "__main__":
    main()
