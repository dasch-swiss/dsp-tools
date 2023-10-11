# pylint: disable=missing-class-docstring,missing-function-docstring,protected-access

import pytest
from lxml import etree
from pytest_unordered import unordered

from dsp_tools.analyse_xml_data.extract_links_from_XML import (
    _extract_id_one_resptr_prop,
    _extract_id_one_text,
    _extract_id_one_text_prop,
    _extract_weighted_id_one_text_prop,
    _extract_weighted_text_id,
    _get_all_links_one_resource,
    get_links_all_resources_from_root,
)


def test_get_links_all_resources_from_root() -> None:
    test_root = etree.fromstring(
        '<knora xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'xsi:schemaLocation="https://dasch.swiss/schema '
        'https://raw.githubusercontent.com/dasch-swiss/dsp-tools/main/src/dsp_tools/resources/schema/data.xsd" '
        'shortcode="0700" default-ontology="simcir"><resource label="res_A_11" restype=":TestThing" id="res_A_11" '
        'permissions="res-default"><text-prop name=":hasRichtext"><text permissions="prop-default" encoding="xml"><a '
        'class="salsah-link" href="IRI:res_B_11:IRI">res_B_11</a></text></text-prop><resptr-prop '
        'name=":hasResource1"><resptr permissions="prop-default">res_B_11</resptr></resptr-prop></resource><resource '
        'label="res_B_11" restype=":TestThing" id="res_B_11" permissions="res-default"><text-prop '
        'name=":hasRichtext"><text permissions="prop-default" encoding="xml"><a class="salsah-link" '
        'href="IRI:res_C_11:IRI">res_C_11</a></text></text-prop><resptr-prop name=":hasResource1"><resptr '
        'permissions="prop-default">res_C_11</resptr></resptr-prop></resource><resource label="res_C_11" '
        'restype=":TestThing" id="res_C_11" permissions="res-default"><text-prop name=":hasRichtext"><text '
        'permissions="prop-default" encoding="xml"><a class="salsah-link" '
        'href="IRI:res_A_11:IRI">res_A_11</a></text></text-prop><resptr-prop name=":hasResource1"><resptr '
        'permissions="prop-default">res_A_11</resptr></resptr-prop></resource></knora>'
    )
    res = get_links_all_resources_from_root(test_root)
    expected = {
        "res_A_11": ["res_B_11", "res_B_11"],
        "res_B_11": ["res_C_11", "res_C_11"],
        "res_C_11": ["res_A_11", "res_A_11"],
    }
    assert list(expected.keys()) == unordered(list(res.keys()))
    for k_expected, v_expected in expected.items():
        assert v_expected == unordered(res[k_expected])


def test_get_all_links_one_resource() -> None:
    test_ele = etree.fromstring(
        '<resource xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'label="res_A_11" restype=":TestThing" id="res_A_11" permissions="res-default"><text-prop '
        'name=":hasRichtext"><text permissions="prop-default" encoding="xml"><a class="salsah-link" '
        'href="IRI:res_B_11:IRI">res_B_11</a></text></text-prop><resptr-prop name=":hasResource1"><resptr '
        'permissions="prop-default">res_B_11</resptr></resptr-prop></resource>'
    )
    res = _get_all_links_one_resource(test_ele)
    expected = ["res_B_11", "res_B_11"]
    assert expected == unordered(res)


def test_get_all_links_one_resource_no_links() -> None:
    test_ele = etree.fromstring(
        '<resource label="res_B_18" restype=":TestThing" id="res_B_18" permissions="res-default"/>'
    )
    res = _get_all_links_one_resource(test_ele)
    assert None is res


def test_text_only_get_all_links_one_resource() -> None:
    test_ele = etree.fromstring(
        '<resource xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'label="res_C_18" restype=":TestThing" id="res_C_18" permissions="res-default"><text-prop '
        'name=":hasRichtext"><text permissions="prop-default" encoding="xml"><a class="salsah-link" '
        'href="IRI:res_A_18:IRI">res_A_18</a></text><text permissions="prop-default" encoding="xml"><a '
        'class="salsah-link" href="IRI:res_B_18:IRI">res_B_18</a></text></text-prop></resource>'
    )
    res = _get_all_links_one_resource(test_ele)
    expected = ["res_A_18", "res_B_18"]
    assert expected == unordered(res)


def test__extract_id_one_text_with_one_id() -> None:
    test_ele = etree.fromstring(
        '<text permissions="prop-default" encoding="xml"><a class="salsah-link" '
        'href="IRI:res_A_11:IRI">res_A_11</a></text>'
    )
    res = _extract_id_one_text(test_ele)
    expected = ["res_A_11"]
    assert expected == res


def test_extract_id_one_text_with_iri() -> None:
    test_ele = etree.fromstring(
        '<text permissions="prop-default" encoding="xml"><a class="salsah-link" '
        'href="http://rdfh.ch/0801/RDE7_KU1STuDhHnGr5uu0g">res_A_11</a></text>'
    )
    res = _extract_id_one_text(test_ele)
    expected = []  # type: ignore[var-annotated]
    assert expected == res


def test_extract_id_one_text_with_several_id() -> None:
    test_ele = etree.fromstring(
        '<text permissions="prop-default" encoding="xml"><a class="salsah-link" '
        'href="IRI:res_A_11:IRI">res_A_11</a><a class="salsah-link" href="IRI:res_B_11:IRI">res_A_11</a><a '
        'class="salsah-link" href="IRI:res_B_11:IRI">res_A_11</a></text>'
    )
    res = _extract_id_one_text(test_ele)
    expected = ["res_A_11", "res_B_11"]
    assert expected == unordered(res)


def test_extract_id_one_text_prop_with_several_text_links() -> None:
    test_ele = etree.fromstring(
        '<text-prop xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'name=":hasRichtext"><text permissions="prop-default" encoding="xml"><a class="salsah-link" '
        'href="IRI:res_A_18:IRI">res_A_18</a></text><text permissions="prop-default" encoding="xml"><a '
        'class="salsah-link" href="IRI:res_B_18:IRI">res_B_18</a></text></text-prop>'
    )
    res = _extract_id_one_text_prop(test_ele)
    expected = ["res_A_18", "res_B_18"]
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


def test_extract_extract_weighted_id_one_text_prop_one_link() -> None:
    test_ele = etree.fromstring(
        '<text permissions="prop-default" encoding="xml"><a class="salsah-link" '
        'href="IRI:res_A_18:IRI">res_A_18</a></text>'
    )
    res = _extract_weighted_text_id(test_ele)
    expected = {"res_A_18": 1}
    assert expected == res


def test_extract_extract_weighted_id_one_text_prop_three_link() -> None:
    test_ele = etree.fromstring(
        '<text-prop xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'name=":hasRichtext"><text permissions="prop-default" encoding="xml"><a class="salsah-link" '
        'href="IRI:res_A_16:IRI">res_A_16</a><a class="salsah-link" href="IRI:res_B_16:IRI">res_B_16</a><a '
        'class="salsah-link" href="IRI:res_C_16:IRI">res_C_16</a></text></text-prop>'
    )
    res = _extract_weighted_text_id(test_ele)
    expected_keys = ["res_A_16", "res_B_16", "res_C_16"]
    assert expected_keys == unordered(list(res.keys()))
    assert sum(res.values()) == 1


def test_extract_weighted_id_one_text_prop() -> None:
    test_ele = etree.fromstring(
        '<text-prop xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'name=":hasRichtext"><text permissions="prop-default" encoding="xml"><a class="salsah-link" '
        'href="IRI:res_A_19:IRI">res_A_19</a></text><text permissions="prop-default" encoding="xml"><a '
        'class="salsah-link" href="IRI:res_B_19:IRI">res_B_19</a></text></text-prop>'
    )
    res = _extract_weighted_id_one_text_prop(test_ele)
    expected = [{"res_A_19": 1}, {"res_B_19": 1}]
    assert expected == unordered(res)


if __name__ == "__main__":
    pytest.main([__file__])
