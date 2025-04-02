import pytest

from dsp_tools.utils.rdflib_constants import KNORA_API_STR
from dsp_tools.utils.xml_parsing.get_parsed_resources import _get_one_absolute_iri


@pytest.mark.parametrize(
    ("local_name", "expected"),
    [
        (":defaultOnto", "http://url.ch/ontology/0000/default/v2#defaultOnto"),
        ("knora-api:localName", f"{KNORA_API_STR}localName"),
        ("knoraApiNoPrefix", f"{KNORA_API_STR}knoraApiNoPrefix"),
        ("other-onto:localName", "http://url.ch/ontology/0000/other-onto/v2#localName"),
        ("default:withDefaultOnto", "http://url.ch/ontology/0000/default/v2#withDefaultOnto"),
    ],
)
def test_get_one_absolute_iri(local_name, expected):
    result = _get_one_absolute_iri(local_name, "0000", "default", "http://url.ch")
    assert result == expected
