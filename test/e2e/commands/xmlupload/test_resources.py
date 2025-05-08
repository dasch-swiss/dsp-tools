# mypy: disable-error-code="no-untyped-def"


import pytest
from rdflib import RDF
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.utils.rdflib_constants import KNORA_API
from dsp_tools.utils.rdflib_constants import KNORA_API_STR
from test.e2e.commands.xmlupload.conftest import _util_get_res_iri_from_label
from test.e2e.commands.xmlupload.conftest import _util_request_resources_by_class

# ruff: noqa: ARG001 Unused function argument


class TestResources:
    def test_class_with_everything_all_created(self, cls_with_everything_graph, class_with_everything_iri):
        cls_iri = URIRef(class_with_everything_iri)
        resource_iris = list(cls_with_everything_graph.subjects(RDF.type, cls_iri))
        expected_number = 17
        assert len(resource_iris) == expected_number

    def test_resource_no_values_assert_triples_present(
        self, cls_with_everything_graph, class_with_everything_iri, project_iri
    ):
        res_iri = _util_get_res_iri_from_label(cls_with_everything_graph, "resource_no_values")
        expected_number_of_resource_triples = 9
        number_of_triples = list(cls_with_everything_graph.triples((res_iri, None, None)))
        assert len(number_of_triples) == expected_number_of_resource_triples
        assert next(cls_with_everything_graph.objects(res_iri, KNORA_API.attachedToProject)) == URIRef(project_iri)
        assert next(cls_with_everything_graph.objects(res_iri, RDF.type)) == (URIRef(class_with_everything_iri))
        assert next(cls_with_everything_graph.objects(res_iri, KNORA_API.hasPermissions))
        assert next(cls_with_everything_graph.objects(res_iri, KNORA_API.arkUrl))
        assert next(cls_with_everything_graph.objects(res_iri, KNORA_API.versionArkUrl))
        assert next(cls_with_everything_graph.objects(res_iri, KNORA_API.userHasPermission))
        assert next(cls_with_everything_graph.objects(res_iri, KNORA_API.creationDate))
        assert next(cls_with_everything_graph.objects(res_iri, KNORA_API.attachedToUser))

    def test_resource_no_permissions_specified(self, cls_with_everything_graph):
        res_iri = _util_get_res_iri_from_label(cls_with_everything_graph, "resource_no_values")
        expected_permissions = Literal("CR knora-admin:ProjectAdmin|D knora-admin:ProjectMember")
        actual_permissions = next(cls_with_everything_graph.objects(res_iri, KNORA_API.hasPermissions))
        assert actual_permissions == expected_permissions

    def test_resource_with_open_permissions(self, cls_with_everything_graph):
        res_iri = _util_get_res_iri_from_label(cls_with_everything_graph, "resource_no_values_open_permissions")
        expected_permissions = Literal(
            "CR knora-admin:ProjectAdmin|D knora-admin:ProjectMember|V knora-admin:KnownUser,knora-admin:UnknownUser"
        )
        actual_permissions = next(cls_with_everything_graph.objects(res_iri, KNORA_API.hasPermissions))
        assert actual_permissions == expected_permissions

    @pytest.mark.usefixtures("_xmlupload")
    def test_second_onto_class(self, second_onto_iri, onto_iri, auth_header, project_iri, creds):
        cls_iri_str = f"{second_onto_iri}SecondOntoClass"
        res_g = _util_request_resources_by_class(cls_iri_str, auth_header, project_iri, creds)
        resource_iris = list(res_g.subjects(RDF.type, URIRef(cls_iri_str)))
        expected_number = 1
        assert len(resource_iris) == expected_number
        res_iri = resource_iris.pop(0)
        assert next(res_g.objects(res_iri, URIRef(f"{second_onto_iri}testBoolean")))
        assert next(res_g.objects(res_iri, URIRef(f"{onto_iri}testSimpleText")))

    @pytest.mark.usefixtures("_xmlupload")
    def test_still_image(self, onto_iri, auth_header, project_iri, creds):
        cls_iri_str = f"{onto_iri}TestStillImageRepresentation"
        res_g = _util_request_resources_by_class(cls_iri_str, auth_header, project_iri, creds)
        resource_iris = list(res_g.subjects(RDF.type, URIRef(cls_iri_str)))
        expected_number = 2
        assert len(resource_iris) == expected_number

        image = _util_get_res_iri_from_label(res_g, "image")
        image_val = next(res_g.objects(image, KNORA_API.hasStillImageFileValue))
        assert next(res_g.objects(image_val, RDF.type)) == KNORA_API.StillImageFileValue

        iiif_uri = _util_get_res_iri_from_label(res_g, "iiif_uri")
        iiif_uri_val = next(res_g.objects(iiif_uri, KNORA_API.hasStillImageFileValue))
        assert next(res_g.objects(iiif_uri_val, RDF.type)) == KNORA_API.StillImageExternalFileValue

    @pytest.mark.usefixtures("_xmlupload")
    def test_audio(self, onto_iri, auth_header, project_iri, creds):
        cls_iri_str = f"{onto_iri}TestAudioRepresentation"
        res_g = _util_request_resources_by_class(cls_iri_str, auth_header, project_iri, creds)
        resource_iris = list(res_g.subjects(RDF.type, URIRef(cls_iri_str)))
        expected_number = 1
        assert len(resource_iris) == expected_number

    @pytest.mark.usefixtures("_xmlupload")
    def test_video(self, onto_iri, auth_header, project_iri, creds):
        cls_iri_str = f"{onto_iri}TestMovingImageRepresentation"
        res_g = _util_request_resources_by_class(cls_iri_str, auth_header, project_iri, creds)
        resource_iris = list(res_g.subjects(RDF.type, URIRef(cls_iri_str)))
        expected_number = 1
        assert len(resource_iris) == expected_number


class TestDspResources:
    @pytest.mark.usefixtures("_xmlupload")
    def test_region(self, auth_header, project_iri, creds):
        cls_iri_str = f"{KNORA_API_STR}Region"
        res_g = _util_request_resources_by_class(cls_iri_str, auth_header, project_iri, creds)
        resource_iris = list(res_g.subjects(RDF.type, URIRef(cls_iri_str)))
        expected_number = 1
        assert len(resource_iris) == expected_number

    @pytest.mark.usefixtures("_xmlupload")
    def test_link_obj(self, auth_header, project_iri, creds):
        cls_iri_str = f"{KNORA_API_STR}LinkObj"
        res_g = _util_request_resources_by_class(cls_iri_str, auth_header, project_iri, creds)
        resource_iris = list(res_g.subjects(RDF.type, URIRef(cls_iri_str)))
        expected_number = 1
        assert len(resource_iris) == expected_number

    @pytest.mark.usefixtures("_xmlupload")
    def test_audio_segment(self, auth_header, project_iri, creds):
        cls_iri_str = f"{KNORA_API_STR}AudioSegment"
        res_g = _util_request_resources_by_class(cls_iri_str, auth_header, project_iri, creds)
        resource_iris = list(res_g.subjects(RDF.type, URIRef(cls_iri_str)))
        expected_number = 1
        assert len(resource_iris) == expected_number

    @pytest.mark.usefixtures("_xmlupload")
    def test_video_segment(self, auth_header, project_iri, creds):
        cls_iri_str = f"{KNORA_API_STR}VideoSegment"
        res_g = _util_request_resources_by_class(cls_iri_str, auth_header, project_iri, creds)
        resource_iris = list(res_g.subjects(RDF.type, URIRef(cls_iri_str)))
        expected_number = 1
        assert len(resource_iris) == expected_number
