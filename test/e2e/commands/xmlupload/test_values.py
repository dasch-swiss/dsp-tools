# mypy: disable-error-code="no-untyped-def"


import pytest
from rdflib import Literal

from dsp_tools.utils.rdflib_constants import KNORA_API_STR, KNORA_API
from test.e2e.commands.xmlupload.conftest import _util_request_resources_by_class, _util_get_res_iri_from_label

BASE_NUMBER_OF_TRIPLES_PER_VALUE = 0

def test_(class_with_everything_resource_graph):
    res_iri = _util_get_res_iri_from_label(class_with_everything_resource_graph, "")
    
    expected_val = Literal("")

