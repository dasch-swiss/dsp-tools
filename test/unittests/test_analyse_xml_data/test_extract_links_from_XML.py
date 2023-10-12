# pylint: disable=missing-class-docstring,missing-function-docstring,protected-access

import pytest
from lxml import etree
from pytest_unordered import unordered

from dsp_tools.analyse_xml_data.extract_links_from_XML import (
    _extract_id_one_resptr_prop,
    _extract_id_one_text,
    _extract_id_one_text_prop,
    _get_all_links_one_resource,
    _make_weighted_resptr_links,
)


def test_get_all_links_one_resource() -> None:
    test_ele = etree.fromstring(
        '<resource xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'label="res_A_11" restype=":TestThing" id="res_A_11" permissions="res-default"><text-prop '
        'name=":hasRichtext"><text permissions="prop-default" encoding="xml"><a class="salsah-link" '
        'href="IRI:res_B_11:IRI">res_B_11</a></text></text-prop><resptr-prop name=":hasResource1"><resptr '
        'permissions="prop-default">res_B_11</resptr></resptr-prop></resource>'
    )
    res_resptr, res_xml = _get_all_links_one_resource(test_ele)
    expected_resptr, expected_xml = ["res_B_11"], [{"res_B_11"}]
    assert expected_resptr == res_resptr
    assert expected_xml == unordered(res_xml)


def test_get_all_links_one_resource_no_links() -> None:
    test_ele = etree.fromstring(
        '<resource label="res_B_18" restype=":TestThing" id="res_B_18" permissions="res-default"/>'
    )
    res = _get_all_links_one_resource(test_ele)
    assert (None, None) == res


def test_text_only_get_all_links_one_resource() -> None:
    test_ele = etree.fromstring(
        '<resource xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'label="res_C_18" restype=":TestThing" id="res_C_18" permissions="res-default"><text-prop '
        'name=":hasRichtext"><text permissions="prop-default" encoding="xml"><a class="salsah-link" '
        'href="IRI:res_A_18:IRI">res_A_18</a></text><text permissions="prop-default" encoding="xml"><a '
        'class="salsah-link" href="IRI:res_B_18:IRI">res_B_18</a></text></text-prop></resource>'
    )
    res_resptr, res_xml = _get_all_links_one_resource(test_ele)
    expected_xml = [{"res_A_18"}, {"res_B_18"}]
    assert res_resptr is None
    assert expected_xml == unordered(res_xml)


def test__extract_id_one_text_with_one_id() -> None:
    test_ele = etree.fromstring(
        '<text permissions="prop-default" encoding="xml"><a class="salsah-link" '
        'href="IRI:res_A_11:IRI">res_A_11</a></text>'
    )
    res = _extract_id_one_text(test_ele)
    expected = {"res_A_11"}
    assert expected == res


def test_extract_id_one_text_with_iri() -> None:
    test_ele = etree.fromstring(
        '<text permissions="prop-default" encoding="xml"><a class="salsah-link" '
        'href="http://rdfh.ch/0801/RDE7_KU1STuDhHnGr5uu0g">res_A_11</a></text>'
    )
    res = _extract_id_one_text(test_ele)
    assert res is None


def test_extract_id_one_text_with_several_id() -> None:
    test_ele = etree.fromstring(
        '<text permissions="prop-default" encoding="xml"><a class="salsah-link" '
        'href="IRI:res_A_11:IRI">res_A_11</a><a class="salsah-link" href="IRI:res_B_11:IRI">res_A_11</a><a '
        'class="salsah-link" href="IRI:res_B_11:IRI">res_A_11</a></text>'
    )
    res = _extract_id_one_text(test_ele)
    expected = {"res_A_11", "res_B_11"}
    assert expected == res


def test_extract_id_one_text_prop_with_several_text_links() -> None:
    test_ele = etree.fromstring(
        '<text-prop xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'name=":hasRichtext"><text permissions="prop-default" encoding="xml"><a class="salsah-link" '
        'href="IRI:res_A_18:IRI">res_A_18</a></text><text permissions="prop-default" encoding="xml"><a '
        'class="salsah-link" href="IRI:res_B_18:IRI">res_B_18</a></text></text-prop>'
    )
    res = _extract_id_one_text_prop(test_ele)
    expected = [{"res_A_18"}, {"res_B_18"}]
    assert expected == unordered(res)


def test_extract_one_id_resptr_prop() -> None:
    test_ele = etree.fromstring(
        '<resptr-prop xmlns="https://dasch.swiss/schema" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" name=":hasResource1"><resptr '
        'permissions="prop-default">res_C_15</resptr></resptr-prop>'
    )
    res = _extract_id_one_resptr_prop(test_ele)
    expected = ["res_C_15"]
    assert expected == unordered(res)


def test_extract_several_id_resptr_prop() -> None:
    test_ele = etree.fromstring(
        '<resptr-prop xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'name=":hasResource1"><resptr permissions="prop-default">res_A_13</resptr><resptr '
        'permissions="prop-default">res_B_13</resptr><resptr permissions="prop-default">res_C_13</resptr></resptr-prop>'
    )
    res = _extract_id_one_resptr_prop(test_ele)
    expected = ["res_A_13", "res_B_13", "res_C_13"]
    assert expected == unordered(res)


def test_make_weighted_resptr_links() -> None:
    links = ["A", "B", "C", "D", "A", "A", "B", "A", "D", "D"]
    res_dict = _make_weighted_resptr_links(links)
    expected_dict = {"A": 4, "B": 2, "C": 1, "D": 3}
    assert set(expected_dict.keys()) == set(expected_dict.keys())
    for k, v in expected_dict.items():
        assert v == res_dict[k]


if __name__ == "__main__":
    pytest.main([__file__])
