# mypy: disable-error-code="no-untyped-def"


import pytest
from rdflib import RDF
from rdflib import URIRef

from dsp_tools.utils.rdflib_constants import KNORA_API_STR
from test.e2e.commands.xmlupload.conftest import _util_request_resources_by_class

# ruff: noqa: ARG001 Unused function argument


class TestResources:
    def test_class_with_everything_all_created(self, class_with_everything_resource_graph, class_with_everything_iri):
        expected_number = 17
        cls_iri = URIRef(class_with_everything_iri)
        resources_in_graph = list(class_with_everything_resource_graph.subjects(RDF.type, cls_iri))
        assert resources_in_graph == expected_number

    @pytest.mark.usefixtures("_xmlupload")
    def test_second_onto_class(self, second_onto_iri, auth_header, project_iri, creds):
        cls_iri_str = f"{second_onto_iri}SecondOntoClass"
        resources = _util_request_resources_by_class(cls_iri_str, auth_header, project_iri, creds)
        assert len(resources) != 0

    @pytest.mark.usefixtures("_xmlupload")
    def test_still_image(self, onto_iri, auth_header, project_iri, creds):
        cls_iri_str = f"{onto_iri}TestStillImageRepresentation"
        resources = _util_request_resources_by_class(cls_iri_str, auth_header, project_iri, creds)
        assert len(resources) != 0

    @pytest.mark.usefixtures("_xmlupload")
    def test_audio(self, onto_iri, auth_header, project_iri, creds):
        cls_iri_str = f"{onto_iri}TestAudioRepresentation"
        resources = _util_request_resources_by_class(cls_iri_str, auth_header, project_iri, creds)
        assert len(resources) != 0

    @pytest.mark.usefixtures("_xmlupload")
    def test_video(self, onto_iri, auth_header, project_iri, creds):
        cls_iri_str = f"{onto_iri}TestMovingImageRepresentation"
        resources = _util_request_resources_by_class(cls_iri_str, auth_header, project_iri, creds)
        assert len(resources) != 0


class TestDspResources:
    @pytest.mark.usefixtures("_xmlupload")
    def test_region(self, auth_header, project_iri, creds):
        cls_iri_str = f"{KNORA_API_STR}Region"
        resources = _util_request_resources_by_class(cls_iri_str, auth_header, project_iri, creds)
        assert len(resources) != 0

    @pytest.mark.usefixtures("_xmlupload")
    def test_link_obj(self, auth_header, project_iri, creds):
        cls_iri_str = f"{KNORA_API_STR}LinkObj"
        resources = _util_request_resources_by_class(cls_iri_str, auth_header, project_iri, creds)
        assert len(resources) != 0

    @pytest.mark.usefixtures("_xmlupload")
    def test_audio_segment(self, auth_header, project_iri, creds):
        cls_iri_str = f"{KNORA_API_STR}AudioSegment"
        resources = _util_request_resources_by_class(cls_iri_str, auth_header, project_iri, creds)
        assert len(resources) != 0

    @pytest.mark.usefixtures("_xmlupload")
    def test_video_segment(self, auth_header, project_iri, creds):
        cls_iri_str = f"{KNORA_API_STR}VideoSegment"
        resources = _util_request_resources_by_class(cls_iri_str, auth_header, project_iri, creds)
        assert len(resources) != 0
