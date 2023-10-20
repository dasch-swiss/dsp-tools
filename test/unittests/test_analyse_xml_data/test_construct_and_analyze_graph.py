# pylint: disable=missing-class-docstring,missing-function-docstring,protected-access,no-member
# mypy: disable-error-code="var-annotated,assignment,arg-type"

from unittest.mock import patch

import pytest
import rustworkx as rx
from lxml import etree
from pytest_unordered import unordered

from dsp_tools.analyse_xml_data.construct_and_analyze_graph import (
    _create_info_from_xml_for_graph_from_one_resource,
    _create_resptr_link_objects,
    _create_text_link_objects,
    _extract_ids_from_one_text_value,
    _find_cheapest_outgoing_links,
    _remove_leaf_nodes,
    create_info_from_xml_for_graph,
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
    g = rx.PyDiGraph()
    nodes = ["a", "b", "c", "d", "e", "f"]
    node_idx = g.add_nodes_from(nodes)
    node_idx_lookup = dict(zip(node_idx, nodes))
    node_idx = set(node_idx)
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


def test_find_cheapest_outgoing_links_one_resptr_link() -> None:
    g = rx.PyDiGraph()
    nodes = [
        #      out in cycle
        "a",  # 1
        "b",  # 2
        "c",  # 3
        "d",  # 4
        "e",
    ]
    g.add_nodes_from(nodes)
    circle = [(0, 1), (1, 2), (2, 3), (3, 0)]
    with patch("dsp_tools.analyse_xml_data.models.ResptrLink.cost_links", 1):
        edges = [
            (0, 1, ResptrLink),
            (0, 4, ResptrLink),
            (0, 4, ResptrLink),
            (1, 2, ResptrLink),
            (1, 3, ResptrLink),
            (2, 0, ResptrLink),
            (2, 1, ResptrLink),
            (2, 3, ResptrLink),
            (3, 0, ResptrLink),
            (3, 0, ResptrLink),
            (3, 1, ResptrLink),
            (3, 2, ResptrLink),
        ]
        g.add_edges_from(edges)
        cheapest_links = _find_cheapest_outgoing_links(g, circle, edges)
        assert cheapest_links == [(0, 1, ResptrLink)]  # type: ignore[comparison-overlap]


def test_find_cheapest_outgoing_links_four_circle() -> None:
    g = rx.PyDiGraph()
    nodes = [
        #       out in cycle
        "a",  # 1
        "b",  # 2
        "c",  # 3
        "d",  # 2
        "e",
        "f",
    ]
    g.add_nodes_from(nodes)
    with patch("dsp_tools.analyse_xml_data.models.ResptrLink.cost_links", 1):
        edges = [
            (0, 1, ResptrLink),
            (1, 2, ResptrLink),
            (1, 2, ResptrLink),
            (2, 3, ResptrLink),
            (2, 3, ResptrLink),
            (2, 3, ResptrLink),
            (3, 0, ResptrLink),
            (3, 0, ResptrLink),
            (3, 5, ResptrLink),
            (3, 5, ResptrLink),
            (3, 5, ResptrLink),
            (3, 5, ResptrLink),
            (4, 2, ResptrLink),
            (4, 2, ResptrLink),
            (4, 2, ResptrLink),
            (4, 2, ResptrLink),
        ]
        g.add_edges_from(edges)
        circle = [(0, 1), (1, 2), (2, 3), (3, 0)]
        cheapest_links = _find_cheapest_outgoing_links(g, circle, edges)
        assert cheapest_links == [(0, 1, ResptrLink)]  # type: ignore[comparison-overlap]


# def test_find_cheapest_outgoing_links_only_resptr() -> None:
#     g = rx.PyDiGraph()
#     nodes = [
#         #      in / out
#         "a",  # 4 / 2
#         "b",  # 3 / 2
#         "c",  # 2 / 5
#         "d",
#         "e",
#         "f",
#     ]
#     ab1_resptr = ResptrLink("a", "b")
#     ab2_resptr = ResptrLink("a", "b")
#     with patch("dsp_tools.analyse_xml_data.models.ResptrLink.cost_links", 1):
#         edges = [
#             (0, 1, ab1_resptr),
#             (0, 1, ab2_resptr),
#             (1, 2, ResptrLink),
#             (1, 2, ResptrLink),
#             (2, 0, ResptrLink),
#             (2, 0, ResptrLink),
#             (2, 1, ResptrLink),
#             (2, 3, ResptrLink),
#             (2, 4, ResptrLink),
#             (3, 4, ResptrLink),
#             (3, 5, ResptrLink),
#             (4, 5, ResptrLink),
#             (5, 0, ResptrLink),
#             (5, 0, ResptrLink),
#         ]
#         circle = [(0, 1), (1, 2), (2, 0)]
#         g.add_nodes_from(nodes)
#         g.add_edges_from(edges)
#         cheapest_links = _find_cheapest_outgoing_links(g, circle, edges)
#         expected = [(0, 1, ab1_resptr), (0, 1, ab2_resptr)]
#         assert unordered(cheapest_links) == expected
#
#
# def test_find_cheapest_outgoing_links_xml() -> None:
#     g = rx.PyDiGraph()
#     nodes = [
#         #      in / out in cycle
#         "a",  # 1 / 2
#         "b",  # 2 / 2
#         "c",  # 2 / 1
#         "d",  # 5 / 2
#         "e",
#         "f"
#     ]
#     g.add_nodes_from(nodes)
#     a_de_xml = XMLLink("a", {"d", "e"})
#     b_d_xml = XMLLink("b", {"d"})
#     c_bdf_xml = XMLLink("c", {"b", "d", "f"})
#     circle = [(0, 1), (1, 2), (2, 3), (3, 0)]
#     with patch("dsp_tools.analyse_xml_data.models.ResptrLink.cost_links", 1):
#         edges = [
#             (0, 2, ResptrLink),
#             (0, 3, a_de_xml),
#             (0, 4, a_de_xml),
#             (1, 0, ResptrLink),
#             (1, 3, b_d_xml),
#             (2, 1, c_bdf_xml),
#             (2, 3, c_bdf_xml),
#             (2, 5, c_bdf_xml),
#             (3, 2, ResptrLink),
#             (3, 5, ResptrLink),
#         ]
#         g.add_edges_from(edges)
#         cheapest_links = _find_cheapest_outgoing_links(g, circle, edges)


# def test_find_cheapest_outgoing_links_mixed_links() -> None:
#     g = rx.PyDiGraph()
#     nodes = [
#         #      out in cycle
#         "a",  # 2
#         "b",  # 3
#         "c",  # 4
#         "d",  # 3 xml that are the same XMLLink -> 1
#         "e",
#     ]
#     g.add_nodes_from(nodes)
#     circle = [(0, 1), (1, 2), (2, 3), (3, 0)]
#     xml_link = XMLLink("d", {"a", "b", "c", "e"})
#     with patch("dsp_tools.analyse_xml_data.models.ResptrLink.cost_links", 1):
#         edges = [
#             (0, 1, ResptrLink),
#             (0, 3, ResptrLink),
#             (1, 2, ResptrLink),
#             (1, 2, ResptrLink),
#             (1, 3, ResptrLink),
#             (2, 0, ResptrLink),
#             (2, 0, ResptrLink),
#             (2, 1, ResptrLink),
#             (2, 3, ResptrLink),
#             (2, 3, ResptrLink),
#             (3, 0, xml_link),
#             (3, 1, xml_link),
#             (3, 2, xml_link),
#             (3, 4, xml_link),
#         ]
#     g.add_edges_from(edges)
#     cheapest_links = _find_cheapest_outgoing_links(g, circle, edges)
#     # TODO: this cannot be handled at the moment,
#     #  XMl all count the same, because they are only cheaper than resptr if they are in the same circle,
#     #  otherwise they are the same value


if __name__ == "__main__":
    pytest.main([__file__])
