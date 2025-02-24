import pytest
from lxml import etree
from pytest_unordered import unordered

from dsp_tools.commands.xmlupload.stash.extract_info_for_graph_from_root import (
    _create_info_from_xml_for_graph_from_one_resource,
)
from dsp_tools.commands.xmlupload.stash.extract_info_for_graph_from_root import _create_resptr_link_objects
from dsp_tools.commands.xmlupload.stash.extract_info_for_graph_from_root import _create_text_link_objects
from dsp_tools.commands.xmlupload.stash.extract_info_for_graph_from_root import _extract_ids_from_one_text_value
from dsp_tools.commands.xmlupload.stash.extract_info_for_graph_from_root import create_info_from_xml_for_graph
from dsp_tools.commands.xmlupload.stash.graph_models import LinkValueLink
from dsp_tools.commands.xmlupload.stash.graph_models import StandOffLink


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
    assert isinstance(res_resptr[0], LinkValueLink)
    assert res_xml[0].target_ids == {"res_B_11"}
    assert isinstance(res_xml[0], StandOffLink)


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
    assert all(isinstance(x, LinkValueLink) for x in res)
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
    result_info = create_info_from_xml_for_graph(root)
    res_resptr = result_info.link_values[0]
    assert isinstance(res_resptr, LinkValueLink)
    res_xml = result_info.standoff_links[0]
    assert isinstance(res_xml, StandOffLink)
    assert unordered(result_info.all_resource_ids) == ["res_A_11", "res_B_11", "res_C_11"]
    xml_res_resptr = root.find(".//resptr")
    assert xml_res_resptr.attrib["linkUUID"] == res_resptr.link_uuid  # type: ignore[union-attr]
    xml_res_text = root.find(".//text")
    assert xml_res_text.attrib["linkUUID"] == res_xml.link_uuid  # type: ignore[union-attr]


if __name__ == "__main__":
    pytest.main([__file__])
