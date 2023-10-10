# pylint: disable=missing-class-docstring,missing-function-docstring,protected-access

import pytest
from lxml import etree

from dsp_tools.analyse_xml_data.extract_links_from_XML import _extract_links_one_text_prop


def test_extract_links_one_text_prop_with_one_iri() -> None:
    test_ele = etree.fromstring(
        '<text-prop xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'name=":hasRichtext"><text permissions="prop-default" encoding="xml"><a class="salsah-link" '
        'href="IRI:res_A_11:IRI">res_A_11</a></text></text-prop>'
    )
    res = _extract_links_one_text_prop(test_ele)
    expected = ["res_A_11"]
    assert res == expected


def test_extract_links_one_text_prop_with_several_iri() -> None:
    test_ele = etree.fromstring(
        '<text-prop xmlns="https://dasch.swiss/schema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'name=":hasRichtext"><text permissions="prop-default" encoding="xml"><a class="salsah-link" '
        'href="IRI:res_A_11:IRI">res_A_11</a><a class="salsah-link" href="IRI:res_B_11:IRI">res_A_11</a><a '
        'class="salsah-link" href="IRI:res_B_11:IRI">res_A_11</a></text></text-prop>'
    )
    res = _extract_links_one_text_prop(test_ele)
    expected = ["res_A_11", "res_B_11"]
    assert res == expected


if __name__ == "__main__":
    pytest.main([__file__])
