import pytest
from lxml import etree

from dsp_tools.utils.rdflib_constants import KNORA_API_STR
from dsp_tools.utils.xml_parsing.get_parsed_resources import _create_namespace_lookup
from dsp_tools.utils.xml_parsing.get_parsed_resources import _get_one_absolute_iri

API_URL = "http://url.ch"
DEFAULT_ONTO_NAMESPACE = f"{API_URL}/ontology/0000/default/v2#"


def test_create_namespace_lookup():
    root = etree.fromstring("""
    <knora shortcode="4124"
       default-ontology="default">
        <resource label="The only resource"
                  restype=":minimalResource"
                  id="the_only_resource">
        </resource>
        
        <link label="value with permissions" id="value_with_permissions">
            <resptr-prop name="hasLinkTo">
                <resptr permissions="open">target_empty_1</resptr>
            </resptr-prop>
        </link>
    </knora>
    """)
    result = _create_namespace_lookup(root, API_URL)
    expected = {}


@pytest.mark.parametrize(
    ("local_name", "expected"),
    [
        (":defaultOnto", f"{DEFAULT_ONTO_NAMESPACE}defaultOnto"),
        ("knora-api:localName", f"{KNORA_API_STR}localName"),
        ("knoraApiNoPrefix", f"{KNORA_API_STR}knoraApiNoPrefix"),
        ("other-onto:localName", f"{API_URL}/ontology/0000/other-onto/v2#localName"),
        ("default:withDefaultOnto", f"{DEFAULT_ONTO_NAMESPACE}withDefaultOnto"),
    ],
)
def test_get_one_absolute_iri(local_name, expected):
    result = _get_one_absolute_iri(local_name, "0000", "default", API_URL)
    assert result == expected
