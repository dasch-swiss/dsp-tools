# pylint: disable=missing-class-docstring,missing-function-docstring,protected-access

import pytest
from lxml import etree
from pytest_unordered import unordered

from dsp_tools.analyse_xml_data.extract_links_from_XML import (
    _create_info_from_xml_for_graph_from_one_resource,
    _extract_ids_from_one_resptr_prop,
    _extract_ids_from_one_text_value,
    _extract_ids_from_text_prop,
    _get_all_links_from_one_resource,
)


def test_create_info_from_xml_for_graph_from_one_resource() -> None:
    test_ele = etree.fromstring(
        '<resource xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'label="res_A_19" restype=":TestThing" id="res_A_19" permissions="res-default"><resptr-prop '
        'name=":hasResource1"><resptr permissions="prop-default">res_B_19</resptr><resptr '
        'permissions="prop-default">res_C_19</resptr></resptr-prop><text-prop name=":hasRichtext"><text '
        'permissions="prop-default" encoding="xml"><a class="salsah-link" href="IRI:res_B_19:IRI">res_B_19</a><a '
        'class="salsah-link" href="IRI:res_C_19:IRI">res_C_19</a></text></text-prop></resource>'
    )
    res_resptr_links, res_xml_links, res_all_used_ids = _create_info_from_xml_for_graph_from_one_resource(test_ele)
    res_B_19 = [obj.object_id for obj in res_resptr_links]
    assert "res_B_19" in res_B_19
    res_C_19 = [obj.object_id for obj in res_resptr_links]
    assert "res_C_19" in res_C_19
    assert "res_A_19" == res_all_used_ids
    assert res_xml_links[0].subject_id == "res_A_19"
    assert res_xml_links[0].object_link_ids == {"res_B_19", "res_C_19"}


def test_get_all_links_from_one_resource() -> None:
    test_ele = etree.fromstring(
        '<resource xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'label="res_A_11" restype=":TestThing" id="res_A_11" permissions="res-default"><text-prop '
        'name=":hasRichtext"><text permissions="prop-default" encoding="xml"><a class="salsah-link" '
        'href="IRI:res_B_11:IRI">res_B_11</a></text></text-prop><resptr-prop name=":hasResource1"><resptr '
        'permissions="prop-default">res_B_11</resptr></resptr-prop></resource>'
    )
    res_resptr, res_xml = _get_all_links_from_one_resource(test_ele)
    assert res_resptr == ["res_B_11"]
    res_xml_ids, res_xml_text = res_xml[0]
    assert res_xml_ids == {"res_B_11"}
    expected_xml_text = (
        '<text xmlns="https://dasch.swiss/schema" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" permissions="prop-default" '
        'encoding="xml">\n  <a class="salsah-link" href="IRI:res_B_11:IRI">res_B_11</a>\n</text>\n'
    )
    assert res_xml_text == expected_xml_text


def test_get_all_links_from_one_resource_no_links() -> None:
    test_ele = etree.fromstring(
        '<resource label="res_B_18" restype=":TestThing" id="res_B_18" permissions="res-default"/>'
    )
    res = _get_all_links_from_one_resource(test_ele)
    assert res == ([], [])


def test_text_only_get_all_links_from_one_resource() -> None:
    test_ele = etree.fromstring(
        '<resource xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'label="res_C_18" restype=":TestThing" id="res_C_18" permissions="res-default"><text-prop '
        'name=":hasRichtext"><text permissions="prop-default" encoding="xml"><a class="salsah-link" '
        'href="IRI:res_A_18:IRI">res_A_18</a></text><text permissions="prop-default" encoding="xml"><a '
        'class="salsah-link" href="IRI:res_B_18:IRI">res_B_18</a></text></text-prop></resource>'
    )
    res_resptr, res_xml = _get_all_links_from_one_resource(test_ele)
    assert not res_resptr
    res_xml_ids = [x[0] for x in res_xml]
    assert unordered(res_xml_ids) == [{"res_A_18"}, {"res_B_18"}]


def test_extract_id_one_text_with_one_id() -> None:
    test_ele = etree.fromstring(
        '<text permissions="prop-default" encoding="xml"><a class="salsah-link" '
        'href="IRI:res_A_11:IRI">res_A_11</a></text>'
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
        '<text permissions="prop-default" encoding="xml"><a class="salsah-link" '
        'href="IRI:res_A_11:IRI">res_A_11</a><a class="salsah-link" href="IRI:res_B_11:IRI">res_A_11</a><a '
        'class="salsah-link" href="IRI:res_B_11:IRI">res_A_11</a></text>'
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
    res = _extract_ids_from_text_prop(test_ele)
    res_ids = [x[0] for x in res]
    assert unordered(res_ids) == [{"res_A_18"}, {"res_B_18"}]


def test_extract_one_id_resptr_prop() -> None:
    test_ele = etree.fromstring(
        '<resptr-prop xmlns="https://dasch.swiss/schema" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" name=":hasResource1"><resptr '
        'permissions="prop-default">res_C_15</resptr></resptr-prop>'
    )
    res = _extract_ids_from_one_resptr_prop(test_ele)
    assert unordered(res) == ["res_C_15"]


def test_extract_several_id_resptr_prop() -> None:
    test_ele = etree.fromstring(
        '<resptr-prop xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'name=":hasResource1"><resptr permissions="prop-default">res_A_13</resptr><resptr '
        'permissions="prop-default">res_B_13</resptr><resptr permissions="prop-default">res_C_13</resptr></resptr-prop>'
    )
    res = _extract_ids_from_one_resptr_prop(test_ele)
    assert unordered(res) == ["res_A_13", "res_B_13", "res_C_13"]


if __name__ == "__main__":
    pytest.main([__file__])
