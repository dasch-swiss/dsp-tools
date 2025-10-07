# mypy: disable-error-code="no-untyped-def"
from pathlib import Path

import pytest

from dsp_tools.error.exceptions import UserFilepathNotFoundError
from dsp_tools.utils.replace_id_with_iri import use_id2iri_mapping_to_replace_ids
from dsp_tools.utils.xml_parsing.models.parsed_resource import KnoraValueType
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedResource
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedValue

ONTO = "http://0.0.0.0:3333/ontology/9999/onto/v2#"
HAS_PROP = f"{ONTO}hasProp"
RES_TYPE = f"{ONTO}ResourceType"
RES_IRI = "http://rdfh.ch/4123/DiAmYQzQSzC7cdTo6OJMYA"


MAPPING_PATH = Path("testdata/id2iri/test-id2iri-mapping.json")


def test_with_replacement():
    orig_list_val = ("list", "node")
    link_val = ParsedValue(HAS_PROP, "test_thing_1", KnoraValueType.LINK_VALUE, None, None)
    list_val = ParsedValue(HAS_PROP, orig_list_val, KnoraValueType.LIST_VALUE, None, None)
    res = ParsedResource(
        res_id="id",
        res_type=RES_TYPE,
        label="lbl",
        permissions_id=None,
        values=[list_val, link_val],
        file_value=None,
        migration_metadata=None,
    )
    result = use_id2iri_mapping_to_replace_ids([res], MAPPING_PATH)
    assert len(result) == 1
    returned_res = result.pop(0)
    assert len(returned_res.values) == 2


def test_raises():
    with pytest.raises(UserFilepathNotFoundError):
        use_id2iri_mapping_to_replace_ids([], Path("foo.json"))
