# mypy: disable-error-code="no-untyped-def"


import pytest
from rdflib import RDF
from rdflib import RDFS
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.utils.rdflib_constants import KNORA_API
from dsp_tools.utils.rdflib_constants import KNORA_API_STR
from test.e2e.commands.xmlupload.utils import util_get_copyright_holders
from test.e2e.commands.xmlupload.utils import util_get_res_iri_from_label
from test.e2e.commands.xmlupload.utils import util_request_resources_by_class

PUBLIC_PERMISSIONS = Literal(
    "CR knora-admin:ProjectAdmin|D knora-admin:ProjectMember|V knora-admin:KnownUser,knora-admin:UnknownUser"
)
PRIVATE_PERMISSIONS = Literal("CR knora-admin:ProjectAdmin|D knora-admin:ProjectMember")

NUMBER_OF_RESOURCE_TRIPLES_WITHOUT_VALUES = 9

"""
Note on these tests:
- The xmlupload code that creates metadata triples (e.g. the permissions) is shared by all resource types.
- FileValue metadata is also created by code that is shared by all file value types,
  therefore it is not necessary to assert the correct creation for every FileValue type separately.
- The content of values is tested.
- For built-in DSP resources the presence of the expected values is explicitly tested here,
  but the content of the values is not as that is included in the tests for the values
  in the designated file of this directory.
"""


@pytest.fixture(scope="module")
def cls_with_everything_graph(
    _xmlupload_minimal_correct_9999, class_with_everything_iri_9999, auth_header, project_iri_9999, creds
) -> Graph:
    return util_request_resources_by_class(class_with_everything_iri_9999, auth_header, project_iri_9999, creds)


class TestResources:
    def test_class_with_everything_all_created(self, cls_with_everything_graph, class_with_everything_iri_9999):
        cls_iri = URIRef(class_with_everything_iri_9999)
        resource_iris = list(cls_with_everything_graph.subjects(RDF.type, cls_iri))
        expected_number_of_resources = 17
        assert len(resource_iris) == expected_number_of_resources

    def test_resource_no_values_assert_triples_present(
        self, cls_with_everything_graph, class_with_everything_iri_9999, project_iri_9999
    ):
        res_iri = util_get_res_iri_from_label(cls_with_everything_graph, "resource_no_values")
        number_of_triples = list(cls_with_everything_graph.triples((res_iri, None, None)))
        assert next(cls_with_everything_graph.objects(res_iri, KNORA_API.attachedToProject)) == URIRef(project_iri_9999)
        assert next(cls_with_everything_graph.objects(res_iri, RDF.type)) == URIRef(class_with_everything_iri_9999)
        assert len(list(cls_with_everything_graph.objects(res_iri, KNORA_API.hasPermissions))) == 1
        assert len(list(cls_with_everything_graph.objects(res_iri, KNORA_API.arkUrl))) == 1
        assert len(list(cls_with_everything_graph.objects(res_iri, KNORA_API.versionArkUrl))) == 1
        assert len(list(cls_with_everything_graph.objects(res_iri, KNORA_API.userHasPermission))) == 1
        assert len(list(cls_with_everything_graph.objects(res_iri, KNORA_API.creationDate))) == 1
        assert len(list(cls_with_everything_graph.objects(res_iri, KNORA_API.attachedToUser))) == 1
        assert len(number_of_triples) == NUMBER_OF_RESOURCE_TRIPLES_WITHOUT_VALUES

    def test_resource_no_permissions_specified(self, cls_with_everything_graph):
        res_iri = util_get_res_iri_from_label(cls_with_everything_graph, "resource_no_values")
        actual_permissions = next(cls_with_everything_graph.objects(res_iri, KNORA_API.hasPermissions))
        assert actual_permissions == PUBLIC_PERMISSIONS

    def test_resource_with_private_permissions(self, cls_with_everything_graph):
        res_iri = util_get_res_iri_from_label(cls_with_everything_graph, "resource_no_values_private_permissions")
        actual_permissions = next(cls_with_everything_graph.objects(res_iri, KNORA_API.hasPermissions))
        assert actual_permissions == PRIVATE_PERMISSIONS

    @pytest.mark.usefixtures("_xmlupload_minimal_correct_9999")
    def test_second_onto_class(self, second_onto_iri_9999, onto_iri_9999, auth_header, project_iri_9999, creds):
        cls_iri_str = f"{second_onto_iri_9999}SecondOntoClass"
        g = util_request_resources_by_class(cls_iri_str, auth_header, project_iri_9999, creds)
        resource_iris = list(g.subjects(RDF.type, URIRef(cls_iri_str)))
        expected_number_of_resources = 1
        assert len(resource_iris) == expected_number_of_resources
        res_iri = resource_iris.pop(0)
        assert next(g.objects(res_iri, URIRef(f"{second_onto_iri_9999}testBoolean")))
        assert next(g.objects(res_iri, URIRef(f"{onto_iri_9999}testSimpleText")))

    @pytest.mark.usefixtures("_xmlupload_minimal_correct_9999")
    def test_still_image(self, onto_iri_9999, auth_header, project_iri_9999, creds):
        cls_iri_str = f"{onto_iri_9999}TestStillImageRepresentation"
        g = util_request_resources_by_class(cls_iri_str, auth_header, project_iri_9999, creds)
        resource_iris = list(g.subjects(RDF.type, URIRef(cls_iri_str)))
        expected_number_of_resources = 2
        assert len(resource_iris) == expected_number_of_resources

        image = util_get_res_iri_from_label(g, "image")
        image_triples = list(g.triples((image, None, None)))
        assert len(image_triples) == NUMBER_OF_RESOURCE_TRIPLES_WITHOUT_VALUES + 1
        image_val = next(g.objects(image, KNORA_API.hasStillImageFileValue))
        assert next(g.objects(image_val, RDF.type)) == KNORA_API.StillImageFileValue
        assert next(g.objects(image_val, KNORA_API.hasPermissions)) == PUBLIC_PERMISSIONS
        assert next(g.objects(image_val, KNORA_API.hasAuthorship)) == Literal("Johannes Nussbaum")
        assert next(g.objects(image_val, KNORA_API.hasCopyrightHolder)) == Literal("DaSCH")
        assert next(g.objects(image_val, KNORA_API.hasLicense)) == URIRef("http://rdfh.ch/licenses/cc-by-4.0")

        iiif_uri = util_get_res_iri_from_label(g, "iiif_uri")
        iiif_uri_triples = list(g.triples((iiif_uri, None, None)))
        assert len(iiif_uri_triples) == NUMBER_OF_RESOURCE_TRIPLES_WITHOUT_VALUES + 1
        iiif_uri_val = next(g.objects(iiif_uri, KNORA_API.hasStillImageFileValue))
        assert next(g.objects(iiif_uri_val, RDF.type)) == KNORA_API.StillImageExternalFileValue
        assert next(g.objects(iiif_uri_val, KNORA_API.hasPermissions)) == PRIVATE_PERMISSIONS
        assert next(g.objects(iiif_uri_val, KNORA_API.hasAuthorship)) == Literal("Cavanagh, Annie")
        assert next(g.objects(iiif_uri_val, KNORA_API.hasCopyrightHolder)) == Literal("Wellcome Collection")
        assert next(g.objects(iiif_uri_val, KNORA_API.hasLicense)) == URIRef("http://rdfh.ch/licenses/cc-by-nc-4.0")

    @pytest.mark.usefixtures("_xmlupload_minimal_correct_9999")
    def test_audio(self, onto_iri_9999, auth_header, project_iri_9999, creds):
        cls_iri_str = f"{onto_iri_9999}TestAudioRepresentation"
        g = util_request_resources_by_class(cls_iri_str, auth_header, project_iri_9999, creds)
        resource_iris = list(g.subjects(RDF.type, URIRef(cls_iri_str)))
        assert next(g.objects(predicate=RDFS.label)) == Literal("audio")
        expected_number_of_resources = 1
        assert len(resource_iris) == expected_number_of_resources

    @pytest.mark.usefixtures("_xmlupload_minimal_correct_9999")
    def test_video(self, onto_iri_9999, auth_header, project_iri_9999, creds):
        cls_iri_str = f"{onto_iri_9999}TestMovingImageRepresentation"
        g = util_request_resources_by_class(cls_iri_str, auth_header, project_iri_9999, creds)
        resource_iris = list(g.subjects(RDF.type, URIRef(cls_iri_str)))
        assert next(g.objects(predicate=RDFS.label)) == Literal("video")
        expected_number_of_resources = 1
        assert len(resource_iris) == expected_number_of_resources


class TestDspResources:
    @pytest.mark.usefixtures("_xmlupload_minimal_correct_9999")
    def test_region(self, auth_header, project_iri_9999, creds):
        cls_iri_str = f"{KNORA_API_STR}Region"
        g = util_request_resources_by_class(cls_iri_str, auth_header, project_iri_9999, creds)
        resource_iris = list(g.subjects(RDF.type, URIRef(cls_iri_str)))
        expected_number_of_resources = 1
        assert len(resource_iris) == expected_number_of_resources
        res_iri = resource_iris.pop(0)
        res_triples = list(g.triples((res_iri, None, None)))
        assert len(list(g.objects(res_iri, KNORA_API.hasColor))) == 1
        assert len(list(g.objects(res_iri, KNORA_API.isRegionOfValue))) == 1
        assert len(list(g.objects(res_iri, KNORA_API.hasGeometry))) == 1
        assert len(list(g.objects(res_iri, KNORA_API.hasComment))) == 1
        number_of_values = 4
        expected_number_of_triples = NUMBER_OF_RESOURCE_TRIPLES_WITHOUT_VALUES + number_of_values
        assert len(res_triples) == expected_number_of_triples

    @pytest.mark.usefixtures("_xmlupload_minimal_correct_9999")
    def test_link_obj(self, auth_header, project_iri_9999, creds):
        cls_iri_str = f"{KNORA_API_STR}LinkObj"
        g = util_request_resources_by_class(cls_iri_str, auth_header, project_iri_9999, creds)
        resource_iris = list(g.subjects(RDF.type, URIRef(cls_iri_str)))
        expected_number_of_resources = 1
        assert len(resource_iris) == expected_number_of_resources
        res_iri = resource_iris.pop(0)
        res_triples = list(g.triples((res_iri, None, None)))
        assert len(list(g.objects(res_iri, KNORA_API.hasComment))) == 1
        assert len(list(g.objects(res_iri, KNORA_API.hasLinkToValue))) == 2
        number_of_values = 3
        expected_number_of_triples = NUMBER_OF_RESOURCE_TRIPLES_WITHOUT_VALUES + number_of_values
        assert len(res_triples) == expected_number_of_triples

    @pytest.mark.usefixtures("_xmlupload_minimal_correct_9999")
    def test_audio_segment(self, auth_header, project_iri_9999, creds):
        cls_iri_str = f"{KNORA_API_STR}AudioSegment"
        g = util_request_resources_by_class(cls_iri_str, auth_header, project_iri_9999, creds)
        resource_iris = list(g.subjects(RDF.type, URIRef(cls_iri_str)))
        expected_number_of_resources = 1
        assert len(resource_iris) == expected_number_of_resources
        res_iri = resource_iris.pop(0)
        res_triples = list(g.triples((res_iri, None, None)))
        assert len(list(g.objects(res_iri, KNORA_API.isAudioSegmentOfValue))) == 1
        assert len(list(g.objects(res_iri, KNORA_API.hasSegmentBounds))) == 1
        assert len(list(g.objects(res_iri, KNORA_API.hasTitle))) == 1
        assert len(list(g.objects(res_iri, KNORA_API.hasComment))) == 1
        assert len(list(g.objects(res_iri, KNORA_API.hasDescription))) == 1
        assert len(list(g.objects(res_iri, KNORA_API.hasKeyword))) == 1
        number_of_values = 6
        expected_number_of_triples = NUMBER_OF_RESOURCE_TRIPLES_WITHOUT_VALUES + number_of_values
        assert len(res_triples) == expected_number_of_triples

    @pytest.mark.usefixtures("_xmlupload_minimal_correct_9999")
    def test_video_segment(self, auth_header, project_iri_9999, creds):
        cls_iri_str = f"{KNORA_API_STR}VideoSegment"
        g = util_request_resources_by_class(cls_iri_str, auth_header, project_iri_9999, creds)
        resource_iris = list(g.subjects(RDF.type, URIRef(cls_iri_str)))
        expected_number_of_resources = 1
        assert len(resource_iris) == expected_number_of_resources
        res_iri = resource_iris.pop(0)
        res_triples = list(g.triples((res_iri, None, None)))
        assert len(list(g.objects(res_iri, KNORA_API.isVideoSegmentOfValue))) == 1
        assert len(list(g.objects(res_iri, KNORA_API.hasSegmentBounds))) == 1
        assert len(list(g.objects(res_iri, KNORA_API.hasTitle))) == 1
        assert len(list(g.objects(res_iri, KNORA_API.hasComment))) == 1
        assert len(list(g.objects(res_iri, KNORA_API.hasDescription))) == 1
        assert len(list(g.objects(res_iri, KNORA_API.hasKeyword))) == 1
        number_of_values = 6
        expected_number_of_triples = NUMBER_OF_RESOURCE_TRIPLES_WITHOUT_VALUES + number_of_values
        assert len(res_triples) == expected_number_of_triples


@pytest.mark.usefixtures("_xmlupload_minimal_correct_9999")
def test_all_copyright_holders(auth_header: dict[str, str], creds: ServerCredentials) -> None:
    default_copyright_holders = {
        "AI-Generated Content - Not Protected by Copyright",
        "Public Domain - Not Protected by Copyright",
    }
    copyright_holders_from_xml = {"DaSCH", "Wellcome Collection"}
    response = util_get_copyright_holders(auth_header, creds)
    assert set(response["data"]) == default_copyright_holders.union(copyright_holders_from_xml)
