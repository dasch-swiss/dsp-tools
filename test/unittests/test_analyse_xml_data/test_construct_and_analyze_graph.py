# pylint: disable=missing-class-docstring,missing-function-docstring,protected-access,no-member

from typing import Any

import pytest
import rustworkx as rx
from lxml import etree
from pytest_unordered import unordered

from dsp_tools.analyse_xml_data.construct_and_analyze_graph import (
    _add_stash_to_lookup_dict,
    _create_info_from_xml_for_graph_from_one_resource,
    _create_resptr_link_objects,
    _create_text_link_objects,
    _extract_ids_from_one_text_value,
    _find_cheapest_outgoing_links,
    _find_phantom_xml_edges,
    _remove_edges_to_stash,
    _remove_leaf_nodes,
    create_info_from_xml_for_graph,
    generate_upload_order,
    make_graph,
)
from dsp_tools.analyse_xml_data.models import ResptrLink, XMLLink


def test_create_info_from_xml_for_graph_from_one_resource() -> None:
    test_ele = etree.fromstring(
        """<resource xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
        label="res_A_19" restype=":TestThing" id="res_A_19" permissions="res-default">
            <resptr-prop name=":hasResource1">
                <resptr permissions="prop-default">res_B_19</resptr>
                <resptr permissions="prop-default">res_C_19</resptr>
            </resptr-prop>
            <text-prop name=":hasRichtext">
                <text permissions="prop-default" encoding="xml">
                    <a class="salsah-link" href="IRI:res_B_19:IRI">res_B_19</a>
                    <a class="salsah-link" href="IRI:res_C_19:IRI">res_C_19</a>
                </text>
            </text-prop>
        </resource>"""
    )
    res_resptr_links, res_xml_links, subject_id = _create_info_from_xml_for_graph_from_one_resource(test_ele)
    res_B_19 = [obj.object_id for obj in res_resptr_links]
    assert "res_B_19" in res_B_19
    assert "res_C_19" in res_B_19
    assert "res_A_19" == subject_id
    assert res_xml_links[0].subject_id == "res_A_19"
    assert res_xml_links[0].object_link_ids == {"res_B_19", "res_C_19"}


def test_create_info_from_xml_for_graph_from_one_resource_one() -> None:
    test_ele = etree.fromstring(
        """
        <resource xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
        label="res_A_11" restype=":TestThing" id="res_A_11" permissions="res-default">
            <text-prop name=":hasRichtext">
                <text permissions="prop-default" encoding="xml">
                    <a class="salsah-link" href="IRI:res_B_11:IRI">res_B_11</a>
                </text>
            </text-prop>
            <resptr-prop name=":hasResource1">
                <resptr permissions="prop-default">res_B_11</resptr>
            </resptr-prop>
        </resource>
        """
    )
    res_resptr, res_xml, subject_id = _create_info_from_xml_for_graph_from_one_resource(test_ele)
    assert subject_id == "res_A_11"
    assert res_resptr[0].object_id == "res_B_11"
    assert isinstance(res_resptr[0], ResptrLink)
    assert res_xml[0].object_link_ids == {"res_B_11"}
    assert isinstance(res_xml[0], XMLLink)


def test_create_info_from_xml_for_graph_from_one_resource_no_links() -> None:
    test_ele = etree.fromstring(
        '<resource label="res_B_18" restype=":TestThing" id="res_B_18" permissions="res-default"/>'
    )
    res_resptr, res_xml, sub_id = _create_info_from_xml_for_graph_from_one_resource(test_ele)
    assert sub_id == "res_B_18"
    assert (res_resptr, res_xml) == ([], [])


def test_text_only_create_info_from_xml_for_graph_from_one_resource() -> None:
    test_ele = etree.fromstring(
        """
        <resource xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
        label="res_C_18" restype=":TestThing" id="res_C_18" permissions="res-default">
            <text-prop name=":hasRichtext">
                <text permissions="prop-default" encoding="xml">
                    <a class="salsah-link" href="IRI:res_A_18:IRI">res_A_18</a>
                </text>
                <text permissions="prop-default" encoding="xml">
                    <a class="salsah-link" href="IRI:res_B_18:IRI">res_B_18</a>
                </text>
            </text-prop>
        </resource>
        """
    )
    res_resptr, res_xml, subject_id = _create_info_from_xml_for_graph_from_one_resource(test_ele)
    assert subject_id == "res_C_18"
    assert not res_resptr
    res_xml_ids = [x.object_link_ids for x in res_xml]
    assert unordered(res_xml_ids) == [{"res_A_18"}, {"res_B_18"}]


def test_extract_id_one_text_with_one_id() -> None:
    test_ele = etree.fromstring(
        """
        <text permissions="prop-default" encoding="xml">
            <a class="salsah-link" href="IRI:res_A_11:IRI">res_A_11</a>
        </text>
        """
    )
    res = _extract_ids_from_one_text_value(test_ele)
    assert res == {"res_A_11"}


def test_extract_id_one_text_with_iri() -> None:
    test_ele = etree.fromstring(
        '<text permissions="prop-default" encoding="xml"><a class="salsah-link" '
        'href="http://rdfh.ch/0801/RDE7_KU1STuDhHnGr5uu0g">res_A_11</a></text>'
    )
    res = _extract_ids_from_one_text_value(test_ele)
    assert res == set()


def test_extract_id_one_text_with_several_id() -> None:
    test_ele = etree.fromstring(
        """
        <text permissions="prop-default" encoding="xml">
            <a class="salsah-link" href="IRI:res_A_11:IRI">res_A_11</a>
            <a class="salsah-link" href="IRI:res_B_11:IRI">res_A_11</a>
            <a class="salsah-link" href="IRI:res_B_11:IRI">res_A_11</a>
        </text>
        """
    )
    res = _extract_ids_from_one_text_value(test_ele)
    assert res == {"res_A_11", "res_B_11"}


def test_extract_ids_from_text_prop_with_several_text_links() -> None:
    test_ele = etree.fromstring(
        '<text-prop xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'name=":hasRichtext"><text permissions="prop-default" encoding="xml"><a class="salsah-link" '
        'href="IRI:res_A_18:IRI">res_A_18</a></text><text permissions="prop-default" encoding="xml"><a '
        'class="salsah-link" href="IRI:res_B_18:IRI">res_B_18</a></text></text-prop>'
    )
    res = _create_text_link_objects("res_C_18", test_ele)
    res_ids = [x.object_link_ids for x in res]
    assert unordered(res_ids) == [{"res_A_18"}, {"res_B_18"}]


def test_create_class_instance_resptr_link_one_link() -> None:
    test_ele = etree.fromstring(
        """
        <resptr-prop xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
        name=":hasResource1">
            <resptr permissions="prop-default">res_C_15</resptr>
        </resptr-prop>
        """
    )
    res = _create_resptr_link_objects("res_A_15", test_ele)
    assert res[0].object_id == "res_C_15"


def test_create_class_instance_resptr_link_several() -> None:
    test_ele = etree.fromstring(
        """
        <resptr-prop xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
        name=":hasResource1">
            <resptr permissions="prop-default">res_A_13</resptr>
            <resptr permissions="prop-default">res_B_13</resptr>
            <resptr permissions="prop-default">res_C_13</resptr>
        </resptr-prop>
        """
    )
    res = _create_resptr_link_objects("res_D_13", test_ele)
    assert all(isinstance(x, ResptrLink) for x in res)
    assert res[0].object_id == "res_A_13"
    assert res[1].object_id == "res_B_13"
    assert res[2].object_id == "res_C_13"


def test_create_info_from_xml_for_graph_check_UUID_in_root() -> None:
    root = etree.fromstring(
        b'<?xml version="1.0" encoding="UTF-8"?><knora xmlns="https://dasch.swiss/schema" '
        b'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="https://dasch.swiss/schema '
        b'https://raw.githubusercontent.com/dasch-swiss/dsp-tools/main/src/dsp_tools/resources/schema/data.xsd" '
        b'shortcode="0700" default-ontology="simcir"><resource label="res_A_11" restype=":TestThing" id="res_A_11" '
        b'permissions="res-default"><resptr-prop name=":hasResource1"><resptr '
        b'permissions="prop-default">res_B_11</resptr></resptr-prop></resource><resource label="res_B_11" '
        b'restype=":TestThing" id="res_B_11" permissions="res-default"><text-prop name=":hasRichtext"><text '
        b'permissions="prop-default" encoding="xml">Start text<a class="salsah-link" '
        b'href="IRI:res_C_11:IRI">res_C_11</a>end text.</text></text-prop></resource><resource label="res_C_11" '
        b'restype=":TestThing" id="res_C_11" permissions="res-default"></resource></knora>'
    )
    res_resptr_li, res_xml_li, res_all_ids = create_info_from_xml_for_graph(root)
    res_resptr = res_resptr_li[0]
    assert isinstance(res_resptr, ResptrLink)
    res_xml = res_xml_li[0]
    assert isinstance(res_xml, XMLLink)
    assert unordered(res_all_ids) == ["res_A_11", "res_B_11", "res_C_11"]
    xml_res_resptr = root.find(".//{https://dasch.swiss/schema}resptr")
    assert xml_res_resptr.attrib["stashUUID"] == res_resptr.link_uuid  # type: ignore[union-attr]
    xml_res_text = root.find(".//{https://dasch.swiss/schema}text")
    assert xml_res_text.attrib["stashUUID"] == res_xml.link_uuid  # type: ignore[union-attr]


def test_make_graph() -> None:
    resptr = ResptrLink("a", "b")
    resptr_links = [resptr]
    xml = XMLLink("a", {"b", "c"})
    xml_links = [xml]
    all_ids = ["a", "b", "c"]
    g, node_index_lookup, edges, node_indices = make_graph(resptr_links, xml_links, all_ids)
    assert g.num_nodes() == 3
    assert g.num_edges() == 3
    assert node_index_lookup[0] == "a"
    assert node_index_lookup[1] == "b"
    assert node_index_lookup[2] == "c"
    assert unordered(edges) == [(0, 1, resptr), (0, 1, xml), (0, 2, xml)]
    assert node_indices == {0, 1, 2}


def test_remove_leaf_nodes() -> None:
    g: rx.PyDiGraph[Any, Any] = rx.PyDiGraph()
    nodes = ["a", "b", "c", "d", "e", "f"]
    node_idx = set(g.add_nodes_from(nodes))
    node_idx_lookup = dict(zip(node_idx, nodes))
    g.add_edges_from(
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

    removed_leaf_id, remaining_node_idx = _remove_leaf_nodes(g, node_idx_lookup, node_idx)
    assert unordered(removed_leaf_id) == ["c", "e", "f"]
    assert remaining_node_idx == {0, 1, 3}
    assert unordered(g.nodes()) == ["a", "b", "d"]
    assert unordered(g.edges()) == ["ab", "bd", "da"]


def get_resptr_instances(edges_list: list[tuple[int, int]]) -> list[tuple[int, int, ResptrLink]]:
    resptrs = [ResptrLink(str(x[0]), str(x[1])) for x in edges_list]
    return [(x[0], x[1], link) for x, link in zip(edges_list, resptrs)]


def test_find_cheapest_outgoing_links_one_resptr_link() -> None:
    nodes = [
        #     out / in
        "0",  # 3 / 3
        "1",  # 2 / 3
        "2",  # 3 / 2
        "3",  # 4 / 2
        "4",
    ]
    g: rx.PyDiGraph[Any, Any] = rx.PyDiGraph()
    g.add_nodes_from(nodes)
    circle = [(0, 1), (1, 2), (2, 3), (3, 0)]
    edges = [
        (0, 1),
        (0, 4),
        (0, 4),
        (1, 2),
        (1, 3),
        (2, 0),
        (2, 1),
        (2, 3),
        (3, 0),
        (3, 0),
        (3, 1),
        (3, 2),
    ]
    edges_returned: list[tuple[int, int, XMLLink | ResptrLink]] = list(get_resptr_instances(edges))
    g.add_edges_from(edges_returned)
    cheapest_links = _find_cheapest_outgoing_links(g, circle, edges_returned)
    assert cheapest_links == [edges_returned[3]]


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
    g: rx.PyDiGraph[Any, Any] = rx.PyDiGraph()
    g.add_nodes_from(nodes)
    edges = [
        (0, 1),
        (1, 0),
        (1, 2),
        (1, 2),
        (2, 3),
        (2, 3),
        (2, 3),
        (3, 0),
        (3, 0),
        (3, 5),
        (3, 5),
        (3, 5),
        (3, 5),
        (4, 2),
        (4, 2),
        (4, 2),
        (4, 2),
    ]
    edges_returned: list[tuple[int, int, XMLLink | ResptrLink]] = list(get_resptr_instances(edges))
    g.add_edges_from(edges_returned)
    g.add_edges_from(edges_returned)
    circle = [(0, 1), (1, 2), (2, 3), (3, 0)]
    cheapest_links = _find_cheapest_outgoing_links(g, circle, edges_returned)
    assert cheapest_links == [edges_returned[0]]


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
    g: rx.PyDiGraph[Any, Any] = rx.PyDiGraph()
    g.add_nodes_from(nodes)
    a_de_xml = XMLLink("0", {"3", "4"})
    b_d_xml = XMLLink("1", {"3"})
    c_bdf_xml = XMLLink("2", {"1", "3", "5"})
    circle = [(0, 1), (1, 2), (2, 3), (3, 0)]
    edges_resptr = [
        (0, 1),
        (0, 1),
        (0, 2),
        (1, 2),
        (1, 2),
        (3, 0),
        (3, 0),
        (3, 0),
    ]
    xml_edges = [
        (1, 3, b_d_xml),
        (2, 1, c_bdf_xml),
        (2, 3, c_bdf_xml),
        (2, 5, c_bdf_xml),
        (0, 3, a_de_xml),
        (0, 4, a_de_xml),
    ]
    edges_returned: list[tuple[int, int, XMLLink | ResptrLink]] = list(get_resptr_instances(edges_resptr))
    edges_returned.extend(xml_edges)
    g.add_edges_from(edges_returned)
    cheapest_links = _find_cheapest_outgoing_links(g, circle, edges_returned)
    assert cheapest_links == [edges_returned[10]]


def test_remove_edges_to_stash_phantom_xml() -> None:
    nodes = ["0", "1", "2", "3", "4", "5"]
    g: rx.PyDiGraph[Any, Any] = rx.PyDiGraph()
    g.add_nodes_from(nodes)
    a_de_xml = XMLLink("0", {"3", "4"})
    b_d_xml = XMLLink("1", {"3"})
    c_bdf_xml = XMLLink("2", {"1", "3", "5"})
    edges_to_remove: list[tuple[int, int, XMLLink | ResptrLink]] = [(2, 3, c_bdf_xml)]
    remaining_nodes = set(range(10))
    resptr_edges = [
        (0, 1),
        (0, 1),
        (0, 2),
        (1, 2),
        (1, 2),
        (3, 0),
        (3, 0),
        (3, 0),
    ]
    xml_edges = [
        (0, 3, a_de_xml),
        (0, 4, a_de_xml),
        (1, 3, b_d_xml),
        (2, 1, c_bdf_xml),
        (2, 3, c_bdf_xml),
        (2, 5, c_bdf_xml),
    ]
    edges_returned: list[tuple[int, int, XMLLink | ResptrLink]] = list(get_resptr_instances(resptr_edges))
    edges_returned.extend(xml_edges)
    g.add_edges_from(edges_returned)
    res_links_to_stash = _remove_edges_to_stash(g, edges_to_remove, edges_returned, remaining_nodes)
    assert res_links_to_stash == [c_bdf_xml]
    remaining_edges = list(g.edge_list())
    expected_edges = [(0, 1), (0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (1, 2), (1, 3), (3, 0), (3, 0), (3, 0)]
    assert unordered(remaining_edges) == expected_edges


def test_remove_edges_to_stash_several_resptr() -> None:
    nodes = ["0", "1", "2"]
    g: rx.PyDiGraph[Any, Any] = rx.PyDiGraph()
    g.add_nodes_from(nodes)
    edges = [
        (0, 1),
        (0, 1),
        (1, 2),
        (1, 2),
        (1, 2),
        (1, 2),
        (1, 2),
        (2, 0),
        (2, 0),
        (2, 0),
        (2, 0),
    ]
    all_edges = get_resptr_instances(edges)
    g.add_edges_from(all_edges)
    edges_to_remove: list[tuple[int, int, XMLLink | ResptrLink]] = list(all_edges[0:2])
    remaining_nodes = set(range(10))
    res_links = _remove_edges_to_stash(g, edges_to_remove, edges, remaining_nodes)
    remaining_edges = list(g.edge_list())
    assert unordered(remaining_edges) == [(1, 2), (1, 2), (1, 2), (1, 2), (1, 2), (2, 0), (2, 0), (2, 0), (2, 0)]
    assert unordered(res_links) == [all_edges[0][2], all_edges[1][2]]


def test_remove_edges_to_stash_missing_nodes() -> None:
    nodes = ["a", "b", "c", "d"]
    g: rx.PyDiGraph[Any, Any] = rx.PyDiGraph()
    g.add_nodes_from(nodes)
    xml_link = XMLLink("a", {"b", "d"})
    edges: list[tuple[int, int, XMLLink | ResptrLink]] = [
        (0, 1, xml_link),
        (1, 2, ResptrLink("", "")),
        (2, 0, ResptrLink("", "")),
    ]
    g.add_edges_from(edges)
    remaining_nodes = {0, 1, 2}
    edges_to_remove: list[tuple[int, int, XMLLink | ResptrLink]] = [(0, 1, xml_link)]
    res_links = _remove_edges_to_stash(g, edges_to_remove, edges, remaining_nodes)
    remaining_edges = list(g.edge_list())
    assert unordered(remaining_edges) == [(1, 2), (2, 0)]
    assert res_links == [xml_link]


def test_find_phantom_xml_edges_no_remaining() -> None:
    xml_link = XMLLink("0", {"2", "3"})
    edges: list[tuple[int, int, XMLLink | ResptrLink]] = [
        (0, 1, xml_link),
        (1, 2, ResptrLink("", "")),
        (2, 0, ResptrLink("", "")),
    ]
    remaining_nodes = {0, 1, 2}
    phantoms = _find_phantom_xml_edges(0, 1, edges, xml_link, remaining_nodes)
    assert phantoms == []


def test_find_phantom_xml_edges_one_link() -> None:
    xml_link = XMLLink("0", {"1", "3"})
    edges: list[tuple[int, int, XMLLink | ResptrLink]] = [
        (0, 1, xml_link),
        (0, 3, xml_link),
        (1, 2, ResptrLink("", "")),
        (2, 0, ResptrLink("", "")),
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
    stash_dict: dict[str, list[str]] = dict()
    result = _add_stash_to_lookup_dict(stash_dict, to_stash)
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
    g: rx.PyDiGraph[Any, Any] = rx.PyDiGraph()
    nodes = ["0", "1", "2", "3", "4", "5", "6"]
    node_idx = set(g.add_nodes_from(nodes))
    node_idx_lookup = dict(zip(node_idx, nodes))
    abf_xml = XMLLink("0", {"1", "5"})
    edges = [
        (1, 2),
        (2, 3),
        (3, 0),
        (3, 0),
        (3, 0),
        (3, 4),
        (5, 6),
    ]
    xml_edges = [
        (0, 1, abf_xml),
        (0, 5, abf_xml),
    ]
    edges_returned: list[tuple[int, int, XMLLink | ResptrLink]] = list(get_resptr_instances(edges))
    edges_returned.extend(xml_edges)

    g.add_edges_from(edges_returned)
    stash_lookup, upload_order, stash_counter = generate_upload_order(g, node_idx_lookup, edges_returned, node_idx)
    expected_stash_lookup = {"0": [abf_xml.link_uuid]}
    assert stash_counter == 1
    assert unordered(upload_order[0:2]) == ["4", "6"]
    assert upload_order[2:] == ["5", "0", "3", "2", "1"]
    assert stash_lookup.keys() == expected_stash_lookup.keys()
    assert stash_lookup["0"] == expected_stash_lookup["0"]
    assert not list(g.edges())
    assert not list(g.nodes())


def test_generate_upload_order_no_stash() -> None:
    g: rx.PyDiGraph[Any, Any] = rx.PyDiGraph()
    nodes = ["0", "1", "2", "3"]
    node_idx = set(g.add_nodes_from(nodes))
    node_idx_lookup = dict(zip(node_idx, nodes))
    edges = [
        (0, 1),
        (1, 2),
        (2, 3),
    ]
    edges_returned: list[tuple[int, int, XMLLink | ResptrLink]] = list(get_resptr_instances(edges))
    g.add_edges_from(edges_returned)
    stash_lookup, upload_order, stash_counter = generate_upload_order(
        g,
        node_idx_lookup,
        edges_returned,
        node_idx,
    )
    assert stash_lookup == dict()
    assert stash_counter == 0
    assert upload_order == ["3", "2", "1", "0"]
    assert not list(g.edges())
    assert not list(g.nodes())


def test_generate_upload_order_two_circles() -> None:
    g: rx.PyDiGraph[Any, Any] = rx.PyDiGraph()
    nodes = ["0", "1", "2", "3", "4", "5", "6"]
    node_idx = set(g.add_nodes_from(nodes))
    node_idx_lookup = dict(zip(node_idx, nodes))
    edges = [
        (0, 1),
        (0, 5),
        (1, 2),
        (2, 3),
        (2, 0),
        (3, 0),
        (3, 0),
        (3, 0),
        (3, 4),
        (5, 6),
        (5, 6),
        (6, 5),
        (6, 5),
        (6, 5),
    ]
    all_edges: list[tuple[int, int, XMLLink | ResptrLink]] = list(get_resptr_instances(edges))
    g.add_edges_from(all_edges)
    stash_lookup, upload_order, stash_counter = generate_upload_order(
        g,
        node_idx_lookup,
        all_edges,
        node_idx,
    )
    circles = ["0", "1", "2", "3", "5", "6"]
    expected_stash = {"0": [all_edges[0][2].link_uuid], "5": [x[2].link_uuid for x in all_edges[9:11]]}
    assert upload_order[0] == "4"
    assert unordered(upload_order[1:]) == circles
    assert stash_counter == 3
    assert stash_lookup.keys() == expected_stash.keys()
    assert stash_lookup["0"] == expected_stash["0"]
    assert unordered(stash_lookup["5"]) == expected_stash["5"]
    assert not list(g.edges())
    assert not list(g.nodes())


if __name__ == "__main__":
    pytest.main([__file__])
