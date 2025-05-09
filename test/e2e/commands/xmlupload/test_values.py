# mypy: disable-error-code="no-untyped-def"


import pytest

from dsp_tools.utils.rdflib_constants import KNORA_API_STR, KNORA_API
from test.e2e.commands.xmlupload.conftest import _util_request_resources_by_class, _util_get_res_iri_from_label


def test_class_with_everything_all_created(self, class_with_everything_resource_graph):
    assert len(class_with_everything_resource_graph) != 0


def test_(class_with_everything_resource_graph):
    res_iri = _util_get_res_iri_from_label(class_with_everything_resource_graph, "")
    

