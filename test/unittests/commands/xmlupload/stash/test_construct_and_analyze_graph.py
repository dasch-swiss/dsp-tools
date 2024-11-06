from typing import Any

import pytest
import rustworkx as rx
from lxml import etree
from pytest_unordered import unordered

from dsp_tools.commands.xmlupload.stash.construct_and_analyze_graph import _add_stash_to_lookup_dict
from dsp_tools.commands.xmlupload.stash.construct_and_analyze_graph import (
    _create_info_from_xml_for_graph_from_one_resource,
)
from dsp_tools.commands.xmlupload.stash.construct_and_analyze_graph import _create_resptr_link_objects
from dsp_tools.commands.xmlupload.stash.construct_and_analyze_graph import _create_text_link_objects
from dsp_tools.commands.xmlupload.stash.construct_and_analyze_graph import _extract_ids_from_one_text_value
from dsp_tools.commands.xmlupload.stash.construct_and_analyze_graph import _find_cheapest_outgoing_links
from dsp_tools.commands.xmlupload.stash.construct_and_analyze_graph import _find_phantom_xml_edges
from dsp_tools.commands.xmlupload.stash.construct_and_analyze_graph import _remove_edges_to_stash
from dsp_tools.commands.xmlupload.stash.construct_and_analyze_graph import _remove_leaf_nodes
from dsp_tools.commands.xmlupload.stash.construct_and_analyze_graph import create_info_from_xml_for_graph
from dsp_tools.commands.xmlupload.stash.construct_and_analyze_graph import generate_upload_order
from dsp_tools.commands.xmlupload.stash.construct_and_analyze_graph import make_graph
from dsp_tools.commands.xmlupload.stash.graph_models import Edge
from dsp_tools.commands.xmlupload.stash.graph_models import ResptrLink
from dsp_tools.commands.xmlupload.stash.graph_models import XMLLink


def test_create_info_from_xml_for_graph_from_one_resource() -> None:
    test_ele = etree.fromstring(
        """<resource label="res_A_19" restype=":TestThing" id="res_A_19" permissions="open">
            <resptr-prop name=":hasResource1">
                <resptr permissions="open">res_B_19</resptr>
                <resptr permissions="open">res_C_19</resptr>
            </resptr-prop>
            <text-prop name=":hasRichtext">
                <text permissions="open" encoding="xml">
                    <a class="salsah-link" href="IRI:res_B_19:IRI">res_B_19</a>
                    <a class="salsah-link" href="IRI:res_C_19:IRI">res_C_19</a>
                </text>
            </text-prop>
        </resource>"""
    )
    res_resptr_links, res_xml_links = _create_info_from_xml_for_graph_from_one_resource(test_ele)
    res_B_19 = [obj.target_id for obj in res_resptr_links]
    assert "res_B_19" in res_B_19
    assert "res_C_19" in res_B_19
    assert res_xml_links[0].source_id == "res_A_19"
    assert res_xml_links[0].target_ids == {"res_B_19", "res_C_19"}


def test_create_info_from_xml_for_graph_from_one_resource_one() -> None:
    test_ele = etree.fromstring(
        """<resource label="res_A_11" restype=":TestThing" id="res_A_11" permissions="open">
            <text-prop name=":hasRichtext">
                <text permissions="open" encoding="xml">
                    <a class="salsah-link" href="IRI:res_B_11:IRI">res_B_11</a>
                </text>
            </text-prop>
            <resptr-prop name=":hasResource1">
                <resptr permissions="open">res_B_11</resptr>
            </resptr-prop>
        </resource>"""
    )
    res_resptr, res_xml = _create_info_from_xml_for_graph_from_one_resource(test_ele)
    assert res_resptr[0].target_id == "res_B_11"
    assert isinstance(res_resptr[0], ResptrLink)
    assert res_xml[0].target_ids == {"res_B_11"}
    assert isinstance(res_xml[0], XMLLink)


def test_create_info_from_xml_for_graph_from_one_resource_no_links() -> None:
    test_ele = etree.fromstring('<resource label="res_B_18" restype=":TestThing" id="res_B_18" permissions="open"/>')
    res_resptr, res_xml = _create_info_from_xml_for_graph_from_one_resource(test_ele)
    assert (res_resptr, res_xml) == ([], [])


def test_text_only_create_info_from_xml_for_graph_from_one_resource() -> None:
    test_ele = etree.fromstring(
        """<resource label="res_C_18" restype=":TestThing" id="res_C_18" permissions="open">
            <text-prop name=":hasRichtext">
                <text permissions="open" encoding="xml">
                    <a class="salsah-link" href="IRI:res_A_18:IRI">res_A_18</a>
                </text>
                <text permissions="open" encoding="xml">
                    <a class="salsah-link" href="IRI:res_B_18:IRI">res_B_18</a>
                </text>
            </text-prop>
        </resource>"""
    )
    res_resptr, res_xml = _create_info_from_xml_for_graph_from_one_resource(test_ele)
    assert not res_resptr
    res_xml_ids = [x.target_ids for x in res_xml]
    assert unordered(res_xml_ids) == [{"res_A_18"}, {"res_B_18"}]


def test_extract_id_one_text_with_one_id() -> None:
    test_ele = etree.fromstring(
        """<text permissions="open" encoding="xml">
            <a class="salsah-link" href="IRI:res_A_11:IRI">res_A_11</a>
        </text>"""
    )
    res = _extract_ids_from_one_text_value(test_ele)
    assert res == {"res_A_11"}


def test_extract_id_one_text_with_iri() -> None:
    test_ele = etree.fromstring(
        '<text permissions="open" encoding="xml">'
        '<a class="salsah-link" href="http://rdfh.ch/0801/RDE7_KU1STuDhHnGr5uu0g">res_A_11</a></text>'
    )
    res = _extract_ids_from_one_text_value(test_ele)
    assert res == set()


def test_extract_id_one_text_with_several_id() -> None:
    test_ele = etree.fromstring(
        """<text permissions="open" encoding="xml">
            <a class="salsah-link" href="IRI:res_A_11:IRI">res_A_11</a>
            <a class="salsah-link" href="IRI:res_B_11:IRI">res_B_11</a>
            <a class="salsah-link" href="IRI:res_B_11:IRI">res_B_11</a>
        </text>"""
    )
    res = _extract_ids_from_one_text_value(test_ele)
    assert res == {"res_A_11", "res_B_11"}


def test_extract_ids_from_text_prop_with_several_text_links() -> None:
    test_ele = etree.fromstring(
        """<text-prop name=":hasRichtext">
            <text permissions="open" encoding="xml">
                <a class="salsah-link" href="IRI:res_A_18:IRI">res_A_18</a>
            </text>
            <text permissions="open" encoding="xml">
                <a class="salsah-link" href="IRI:res_B_18:IRI">res_B_18</a>
            </text>
        </text-prop>"""
    )
    res = _create_text_link_objects("res_C_18", test_ele)
    res_ids = [x.target_ids for x in res]
    assert unordered(res_ids) == [{"res_A_18"}, {"res_B_18"}]


def test_extract_ids_from_text_prop_with_iris_and_ids() -> None:
    test_ele = etree.fromstring(
        """<text-prop name=":hasRichtext">
            <text permissions="open" encoding="xml">
                <a class="salsah-link" href="http://rdfh.ch/4123/vEpjk7zAQBC2j3pvTGSxcw">foo</a>
            </text>
            <text permissions="open" encoding="xml">
                <a class="salsah-link" href="IRI:res_B_18:IRI">res_B_18</a>
            </text>
        </text-prop>"""
    )
    res = _create_text_link_objects("foo", test_ele)
    assert len(res) == 1
    assert res[0].target_ids == {"res_B_18"}
    children = list(test_ele.iterchildren())
    assert not children[0].attrib.get("linkUUID")
    assert children[1].attrib.get("linkUUID")


def test_create_class_instance_resptr_link_one_link() -> None:
    test_ele = etree.fromstring(
        """<resptr-prop xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
        name=":hasResource1">
            <resptr permissions="open">res_C_15</resptr>
        </resptr-prop>"""
    )
    res = _create_resptr_link_objects("res_A_15", test_ele)
    assert res[0].target_id == "res_C_15"


def test_create_class_instance_resptr_link_several() -> None:
    test_ele = etree.fromstring(
        """<resptr-prop name=":hasResource1">
            <resptr permissions="open">res_A_13</resptr>
            <resptr permissions="open">res_B_13</resptr>
            <resptr permissions="open">res_C_13</resptr>
        </resptr-prop>"""
    )
    res = _create_resptr_link_objects("res_D_13", test_ele)
    assert all(isinstance(x, ResptrLink) for x in res)
    assert res[0].target_id == "res_A_13"
    assert res[1].target_id == "res_B_13"
    assert res[2].target_id == "res_C_13"


def test_create_class_instance_resptr_link_with_iris() -> None:
    test_ele = etree.fromstring(
        """<resptr-prop name=":hasResource1">
            <resptr permissions="open">res_A_13</resptr>
            <resptr permissions="open">res_B_13</resptr>
            <resptr permissions="open">http://rdfh.ch/4123/vEpjk7zAQBC2j3pvTGSxcw</resptr>
        </resptr-prop>"""
    )
    res = _create_resptr_link_objects("foo", test_ele)
    assert len(res) == 2
    assert res[0].target_id == "res_A_13"
    assert res[1].target_id == "res_B_13"
    children = list(test_ele.iterchildren())
    assert children[0].attrib.get("linkUUID")
    assert children[1].attrib.get("linkUUID")
    assert not children[2].attrib.get("linkUUID")


def test_create_info_from_xml_for_graph_check_UUID_in_root() -> None:
    root = etree.fromstring(
        """<knora shortcode="0700" default-ontology="simcir">
            <resource label="res_A_11" restype=":TestThing" id="res_A_11" permissions="open">
                <resptr-prop name=":hasResource1">
                    <resptr permissions="open">res_B_11</resptr>
                </resptr-prop>
            </resource>
            <resource label="res_B_11" restype=":TestThing" id="res_B_11" permissions="open">
                <text-prop name=":hasRichtext">
                    <text permissions="open" encoding="xml">
                        Start text<a class="salsah-link" href="IRI:res_C_11:IRI">res_C_11</a>end text.
                    </text>
                </text-prop>
            </resource>
            <resource label="res_C_11" restype=":TestThing" id="res_C_11" permissions="open"></resource>
        </knora>"""
    )
    res_resptr_li, res_xml_li, res_all_ids = create_info_from_xml_for_graph(root)
    res_resptr = res_resptr_li[0]
    assert isinstance(res_resptr, ResptrLink)
    res_xml = res_xml_li[0]
    assert isinstance(res_xml, XMLLink)
    assert unordered(res_all_ids) == ["res_A_11", "res_B_11", "res_C_11"]
    xml_res_resptr = root.find(".//resptr")
    assert xml_res_resptr.attrib["linkUUID"] == res_resptr.link_uuid  # type: ignore[union-attr]
    xml_res_text = root.find(".//text")
    assert xml_res_text.attrib["linkUUID"] == res_xml.link_uuid  # type: ignore[union-attr]


def test_make_graph() -> None:
    resptr = ResptrLink("a", "b")
    resptr_links = [resptr]
    xml = XMLLink("a", {"b", "c"})
    xml_links = [xml]
    all_ids = ["a", "b", "c"]
    graph, node_to_id, edges = make_graph(resptr_links, xml_links, all_ids)
    assert graph.num_nodes() == 3
    assert graph.num_edges() == 3
    assert node_to_id[0] == "a"
    assert node_to_id[1] == "b"
    assert node_to_id[2] == "c"
    assert unordered(edges) == [Edge(0, 1, resptr), Edge(0, 1, xml), Edge(0, 2, xml)]
    assert set(node_to_id.keys()) == {0, 1, 2}


def test_remove_leaf_nodes() -> None:
    graph: rx.PyDiGraph[Any, Any] = rx.PyDiGraph()
    nodes = ["a", "b", "c", "d", "e", "f"]
    node_idx = set(graph.add_nodes_from(nodes))
    node_idx_lookup = dict(zip(node_idx, nodes))
    graph.add_edges_from(
        [
            (0, 1, "ab"),
            (0, 4, "ae"),
            (0, 2, "ac"),
            (1, 2, "bc"),
            (1, 3, "bd"),
            (2, 4, "ce"),
            (3, 1, "da"),
            (3, 2, "dc"),
            (3, 4, "de"),
        ]
    )
    # c is a second degree leaf
    # e is a leaf
    # f has no edges

    removed_leaf_nodes, remaining_node_indices = _remove_leaf_nodes(graph, node_idx_lookup, node_idx)
    assert unordered(removed_leaf_nodes) == ["c", "e", "f"]
    assert remaining_node_indices == {0, 1, 3}
    assert unordered(graph.nodes()) == ["a", "b", "d"]
    assert unordered(graph.edges()) == ["ab", "bd", "da"]


def test_find_cheapest_outgoing_links_one_resptr_link() -> None:
    nodes = [
        #     out / in
        "0",  # 3 / 3
        "1",  # 2 / 3
        "2",  # 3 / 2
        "3",  # 4 / 2
        "4",
    ]
    graph: rx.PyDiGraph[Any, Any] = rx.PyDiGraph()
    graph.add_nodes_from(nodes)
    circle = [(0, 1), (1, 2), (2, 3), (3, 0)]
    edges = [
        Edge(0, 1, ResptrLink("", "")),
        Edge(0, 4, ResptrLink("", "")),
        Edge(0, 4, ResptrLink("", "")),
        Edge(1, 2, ResptrLink("", "")),
        Edge(1, 3, ResptrLink("", "")),
        Edge(2, 0, ResptrLink("", "")),
        Edge(2, 1, ResptrLink("", "")),
        Edge(2, 3, ResptrLink("", "")),
        Edge(3, 0, ResptrLink("", "")),
        Edge(3, 0, ResptrLink("", "")),
        Edge(3, 1, ResptrLink("", "")),
        Edge(3, 2, ResptrLink("", "")),
    ]
    graph.add_edges_from([e.as_tuple() for e in edges])
    cheapest_links = _find_cheapest_outgoing_links(graph, circle, edges)
    assert cheapest_links == [edges[3]]


def test_find_cheapest_outgoing_links_four_circle() -> None:
    nodes = [
        #     out / in
        "0",  # 1 / 3
        "1",  # 2 / 1
        "2",  # 3 / 6
        "3",  # 6 / 3
        "4",
        "5",
    ]
    graph: rx.PyDiGraph[Any, Any] = rx.PyDiGraph()
    graph.add_nodes_from(nodes)
    edges = [
        Edge(0, 1, ResptrLink("", "")),
        Edge(1, 0, ResptrLink("", "")),
        Edge(1, 2, ResptrLink("", "")),
        Edge(1, 2, ResptrLink("", "")),
        Edge(2, 3, ResptrLink("", "")),
        Edge(2, 3, ResptrLink("", "")),
        Edge(2, 3, ResptrLink("", "")),
        Edge(3, 0, ResptrLink("", "")),
        Edge(3, 0, ResptrLink("", "")),
        Edge(3, 5, ResptrLink("", "")),
        Edge(3, 5, ResptrLink("", "")),
        Edge(3, 5, ResptrLink("", "")),
        Edge(3, 5, ResptrLink("", "")),
        Edge(4, 2, ResptrLink("", "")),
        Edge(4, 2, ResptrLink("", "")),
        Edge(4, 2, ResptrLink("", "")),
        Edge(4, 2, ResptrLink("", "")),
    ]
    graph.add_edges_from([e.as_tuple() for e in edges])
    circle = [(0, 1), (1, 2), (2, 3), (3, 0)]
    cheapest_links = _find_cheapest_outgoing_links(graph, circle, edges)
    assert cheapest_links == [edges[0]]


def test_find_cheapest_outgoing_links_xml() -> None:
    nodes = [
        #      out / in
        "0",  # 4 (2 XML) / 3
        "1",  # 3 / 3
        "2",  # 1 (3 XML) / 3
        "3",  # 3 / 3
        "4",
        "5",
    ]
    graph: rx.PyDiGraph[Any, Any] = rx.PyDiGraph()
    graph.add_nodes_from(nodes)
    a_de_xml = XMLLink("0", {"3", "4"})
    b_d_xml = XMLLink("1", {"3"})
    c_bdf_xml = XMLLink("2", {"1", "3", "5"})
    circle = [(0, 1), (1, 2), (2, 3), (3, 0)]
    edges = [
        Edge(0, 1, ResptrLink("", "")),
        Edge(0, 1, ResptrLink("", "")),
        Edge(0, 2, ResptrLink("", "")),
        Edge(1, 2, ResptrLink("", "")),
        Edge(1, 2, ResptrLink("", "")),
        Edge(3, 0, ResptrLink("", "")),
        Edge(3, 0, ResptrLink("", "")),
        Edge(3, 0, ResptrLink("", "")),
        Edge(1, 3, b_d_xml),
        Edge(2, 1, c_bdf_xml),
        Edge(2, 3, c_bdf_xml),
        Edge(2, 5, c_bdf_xml),
        Edge(0, 3, a_de_xml),
        Edge(0, 4, a_de_xml),
    ]
    graph.add_edges_from([e.as_tuple() for e in edges])
    cheapest_links = _find_cheapest_outgoing_links(graph, circle, edges)
    assert cheapest_links == [edges[10]]


def test_remove_edges_to_stash_phantom_xml() -> None:
    nodes = ["0", "1", "2", "3", "4", "5"]
    graph: rx.PyDiGraph[Any, Any] = rx.PyDiGraph()
    graph.add_nodes_from(nodes)
    a_de_xml = XMLLink("0", {"3", "4"})
    b_d_xml = XMLLink("1", {"3"})
    c_bdf_xml = XMLLink("2", {"1", "3", "5"})
    edges_to_remove = [Edge(2, 3, c_bdf_xml)]
    remaining_nodes = set(range(10))
    edges = [
        Edge(0, 1, ResptrLink("", "")),
        Edge(0, 1, ResptrLink("", "")),
        Edge(0, 2, ResptrLink("", "")),
        Edge(1, 2, ResptrLink("", "")),
        Edge(1, 2, ResptrLink("", "")),
        Edge(3, 0, ResptrLink("", "")),
        Edge(3, 0, ResptrLink("", "")),
        Edge(3, 0, ResptrLink("", "")),
        Edge(0, 3, a_de_xml),
        Edge(0, 4, a_de_xml),
        Edge(1, 3, b_d_xml),
        Edge(2, 1, c_bdf_xml),
        Edge(2, 3, c_bdf_xml),
        Edge(2, 5, c_bdf_xml),
    ]
    graph.add_edges_from([e.as_tuple() for e in edges])
    _remove_edges_to_stash(graph, edges_to_remove, edges, remaining_nodes)
    remaining_edges = list(graph.edge_list())
    expected_edges = [(0, 1), (0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (1, 2), (1, 3), (3, 0), (3, 0), (3, 0)]
    assert unordered(remaining_edges) == expected_edges


def test_remove_edges_to_stash_several_resptr() -> None:
    nodes = ["0", "1", "2"]
    graph: rx.PyDiGraph[Any, Any] = rx.PyDiGraph()
    graph.add_nodes_from(nodes)
    edges = [
        Edge(0, 1, ResptrLink("", "")),
        Edge(0, 1, ResptrLink("", "")),
        Edge(1, 2, ResptrLink("", "")),
        Edge(1, 2, ResptrLink("", "")),
        Edge(1, 2, ResptrLink("", "")),
        Edge(1, 2, ResptrLink("", "")),
        Edge(1, 2, ResptrLink("", "")),
        Edge(2, 0, ResptrLink("", "")),
        Edge(2, 0, ResptrLink("", "")),
        Edge(2, 0, ResptrLink("", "")),
        Edge(2, 0, ResptrLink("", "")),
    ]
    graph.add_edges_from([e.as_tuple() for e in edges])
    edges_to_remove = edges[:2]
    remaining_nodes = set(range(10))
    _remove_edges_to_stash(graph, edges_to_remove, edges, remaining_nodes)
    remaining_edges = list(graph.edge_list())
    assert unordered(remaining_edges) == [(1, 2), (1, 2), (1, 2), (1, 2), (1, 2), (2, 0), (2, 0), (2, 0), (2, 0)]


def test_remove_edges_to_stash_missing_nodes() -> None:
    nodes = ["a", "b", "c", "d"]
    graph: rx.PyDiGraph[Any, Any] = rx.PyDiGraph()
    graph.add_nodes_from(nodes)
    xml_link = XMLLink("a", {"b", "d"})
    edges = [
        Edge(0, 1, xml_link),
        Edge(1, 2, ResptrLink("", "")),
        Edge(2, 0, ResptrLink("", "")),
    ]
    graph.add_edges_from([e.as_tuple() for e in edges])
    remaining_nodes = {0, 1, 2}
    edges_to_remove = [Edge(0, 1, xml_link)]
    _remove_edges_to_stash(graph, edges_to_remove, edges, remaining_nodes)
    remaining_edges = list(graph.edge_list())
    assert unordered(remaining_edges) == [(1, 2), (2, 0)]


def test_find_phantom_xml_edges_no_remaining() -> None:
    xml_link = XMLLink("0", {"2", "3"})
    edges = [
        Edge(0, 1, xml_link),
        Edge(1, 2, ResptrLink("", "")),
        Edge(2, 0, ResptrLink("", "")),
    ]
    remaining_nodes = {0, 1, 2}
    phantoms = _find_phantom_xml_edges(0, 1, edges, xml_link, remaining_nodes)
    assert phantoms == []


def test_find_phantom_xml_edges_one_link() -> None:
    xml_link = XMLLink("0", {"1", "3"})
    edges = [
        Edge(0, 1, xml_link),
        Edge(0, 3, xml_link),
        Edge(1, 2, ResptrLink("", "")),
        Edge(2, 0, ResptrLink("", "")),
    ]
    remaining_nodes = {0, 1, 2, 3}
    phantoms = _find_phantom_xml_edges(0, 1, edges, xml_link, remaining_nodes)
    assert phantoms == [(0, 3)]


def test_add_stash_to_lookup_dict_none_existing() -> None:
    resptr_a1 = ResptrLink("0", "1")
    resptr_a2 = ResptrLink("0", "1")
    xml_a = XMLLink("0", {"1", "2"})
    to_stash: list[XMLLink | ResptrLink] = [resptr_a1, resptr_a2, xml_a]
    expected = {"0": [resptr_a1.link_uuid, resptr_a2.link_uuid, xml_a.link_uuid]}
    result = _add_stash_to_lookup_dict({}, to_stash)
    assert result.keys() == expected.keys()
    assert unordered(result["0"]) == expected["0"]


def test_add_stash_to_lookup_dict() -> None:
    resptr_a1 = ResptrLink("0", "1")
    stash_dict = {"0": ["existingUUID1", "existingUUID2"], "1": ["existingUUID1"]}
    expected = {"0": ["existingUUID1", "existingUUID2", resptr_a1.link_uuid], "1": ["existingUUID1"]}
    result = _add_stash_to_lookup_dict(stash_dict, [resptr_a1])
    assert result.keys() == expected.keys()
    assert unordered(result["0"]) == expected["0"]


def test_generate_upload_order_with_stash() -> None:
    graph: rx.PyDiGraph[Any, Any] = rx.PyDiGraph()
    nodes = ["0", "1", "2", "3", "4", "5", "6"]
    node_idx = set(graph.add_nodes_from(nodes))
    node_idx_lookup = dict(zip(node_idx, nodes))
    abf_xml = XMLLink("0", {"1", "5"})
    edges = [
        Edge(1, 2, ResptrLink("", "")),
        Edge(2, 3, ResptrLink("", "")),
        Edge(3, 0, ResptrLink("", "")),
        Edge(3, 0, ResptrLink("", "")),
        Edge(3, 0, ResptrLink("", "")),
        Edge(3, 4, ResptrLink("", "")),
        Edge(5, 6, ResptrLink("", "")),
        Edge(0, 1, abf_xml),
        Edge(0, 5, abf_xml),
    ]
    graph.add_edges_from([e.as_tuple() for e in edges])
    stash_lookup, upload_order, stash_counter = generate_upload_order(graph, node_idx_lookup, edges)
    expected_stash_lookup = {"0": [abf_xml.link_uuid]}
    assert stash_counter == 1
    assert unordered(upload_order[:2]) == ["4", "6"]
    assert upload_order[2:] == ["5", "0", "3", "2", "1"]
    assert stash_lookup.keys() == expected_stash_lookup.keys()
    assert stash_lookup["0"] == expected_stash_lookup["0"]
    assert not list(graph.edges())
    assert not list(graph.nodes())


def test_generate_upload_order_no_stash() -> None:
    graph: rx.PyDiGraph[Any, Any] = rx.PyDiGraph()
    nodes = ["0", "1", "2", "3"]
    node_idx = set(graph.add_nodes_from(nodes))
    node_idx_lookup = dict(zip(node_idx, nodes))
    edges = [
        Edge(0, 1, ResptrLink("", "")),
        Edge(1, 2, ResptrLink("", "")),
        Edge(2, 3, ResptrLink("", "")),
    ]
    graph.add_edges_from([e.as_tuple() for e in edges])
    stash_lookup, upload_order, stash_counter = generate_upload_order(graph, node_idx_lookup, edges)
    assert not stash_lookup
    assert stash_counter == 0
    assert upload_order == ["3", "2", "1", "0"]
    assert not list(graph.edges())
    assert not list(graph.nodes())


def test_generate_upload_order_two_circles() -> None:
    graph: rx.PyDiGraph[Any, Any] = rx.PyDiGraph()
    nodes = ["0", "1", "2", "3", "4", "5", "6"]
    node_idx = set(graph.add_nodes_from(nodes))
    node_idx_lookup = dict(zip(node_idx, nodes))
    edges = [
        Edge(0, 1, ResptrLink("0", "1")),
        Edge(0, 5, ResptrLink("0", "5")),
        Edge(1, 2, ResptrLink("1", "2")),
        Edge(2, 3, ResptrLink("2", "3")),
        Edge(2, 0, ResptrLink("2", "0")),
        Edge(3, 0, ResptrLink("3", "0")),
        Edge(3, 0, ResptrLink("3", "0")),
        Edge(3, 0, ResptrLink("3", "0")),
        Edge(3, 4, ResptrLink("3", "4")),
        Edge(5, 6, ResptrLink("5", "6")),
        Edge(5, 6, ResptrLink("5", "6")),
        Edge(6, 5, ResptrLink("6", "5")),
        Edge(6, 5, ResptrLink("6", "5")),
        Edge(6, 5, ResptrLink("6", "5")),
    ]
    graph.add_edges_from([e.as_tuple() for e in edges])
    stash_lookup, upload_order, stash_counter = generate_upload_order(graph, node_idx_lookup, edges)
    circles = ["0", "1", "2", "3", "5", "6"]
    expected_stash = {"0": [edges[0].link_object.link_uuid], "5": [x.link_object.link_uuid for x in edges[9:11]]}
    assert upload_order[0] == "4"
    assert unordered(upload_order[1:]) == circles
    assert stash_counter == 3
    assert stash_lookup.keys() == expected_stash.keys()
    assert stash_lookup["0"] == expected_stash["0"]
    assert unordered(stash_lookup["5"]) == expected_stash["5"]
    assert not list(graph.edges())
    assert not list(graph.nodes())


if __name__ == "__main__":
    pytest.main([__file__])
