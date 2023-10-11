# pylint: disable=missing-class-docstring,missing-function-docstring,protected-access

import pytest
from lxml import etree
from pytest_unordered import unordered

from dsp_tools.analyse_xml_data.extract_links_from_XML import _extract_id_one_text_prop


def test_extract_extract_id_one_text_prop_with_one_id() -> None:
    test_ele = etree.fromstring(
        '<text-prop xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'name=":hasRichtext"><text permissions="prop-default" encoding="xml"><a class="salsah-link" '
        'href="IRI:res_A_11:IRI">res_A_11</a></text></text-prop>'
    )
    res = _extract_id_one_text_prop(test_ele)
    expected = ["res_A_11"]
    assert expected == res


def test_extract_id_one_text_prop_with_iri() -> None:
    test_ele = etree.fromstring(
        '<text-prop xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'name=":hasRichtext"><text permissions="prop-default" encoding="xml"><a class="salsah-link" '
        'href="http://rdfh.ch/0801/RDE7_KU1STuDhHnGr5uu0g">res_A_11</a></text></text-prop>'
    )
    res = _extract_id_one_text_prop(test_ele)
    expected = []
    assert expected == res


def test_extract_id_one_text_prop_with_several_id() -> None:
    test_ele = etree.fromstring(
        '<text-prop xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'name=":hasRichtext"><text permissions="prop-default" encoding="xml"><a class="salsah-link" '
        'href="IRI:res_A_11:IRI">res_A_11</a><a class="salsah-link" href="IRI:res_B_11:IRI">res_A_11</a><a '
        'class="salsah-link" href="IRI:res_B_11:IRI">res_A_11</a></text></text-prop>'
    )
    res = _extract_id_one_text_prop(test_ele)
    expected = ["res_A_11", "res_B_11"]
    assert expected == unordered(res)


if __name__ == "__main__":
    pytest.main([__file__])
