# mypy: disable-error-code="no-untyped-def"


import pytest

from dsp_tools.utils.rdflib_constants import KNORA_API_STR
from test.e2e.commands.xmlupload.conftest import _util_request_resources_by_class

# ruff: noqa: ARG001 Unused function argument


@pytest.mark.usefixtures("_xmlupload")
def test_region(auth_header, project_iri, creds):
    cls_iri_str = f"{KNORA_API_STR}Region"
    resources = _util_request_resources_by_class(cls_iri_str, auth_header, project_iri, creds)
    assert len(resources) != 0


@pytest.mark.usefixtures("_xmlupload")
def test_link_obj(auth_header, project_iri, creds):
    cls_iri_str = f"{KNORA_API_STR}LinkObj"
    resources = _util_request_resources_by_class(cls_iri_str, auth_header, project_iri, creds)
    assert len(resources) != 0


@pytest.mark.usefixtures("_xmlupload")
def test_audio_segment(auth_header, project_iri, creds):
    cls_iri_str = f"{KNORA_API_STR}AudioSegment"
    resources = _util_request_resources_by_class(cls_iri_str, auth_header, project_iri, creds)
    assert len(resources) != 0


@pytest.mark.usefixtures("_xmlupload")
def test_video_segment(auth_header, project_iri, creds):
    cls_iri_str = f"{KNORA_API_STR}VideoSegment"
    resources = _util_request_resources_by_class(cls_iri_str, auth_header, project_iri, creds)
    assert len(resources) != 0
