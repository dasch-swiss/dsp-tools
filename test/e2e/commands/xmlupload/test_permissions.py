import pytest
import requests
from rdflib import Literal

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.utils.rdflib_constants import KNORA_API
from test.e2e.commands.xmlupload.utils import util_get_res_iri_from_label
from test.e2e.commands.xmlupload.utils import util_request_resources_by_class

PROJECT_SHORTCODE = "4125"
ONTO_NAME = "e2e-testonto"
SECOND_ONTO_NAME = "second-onto"

PUBLIC_PERMISSIONS = Literal(
    "CR knora-admin:ProjectAdmin|D knora-admin:ProjectMember|V knora-admin:KnownUser,knora-admin:UnknownUser"
)
PRIVATE_PERMISSIONS = Literal("CR knora-admin:ProjectAdmin|D knora-admin:ProjectMember")
PREVIEW_PERMISSIONS = Literal(
    "CR knora-admin:ProjectAdmin|D knora-admin:ProjectMember|RV knora-admin:KnownUser,knora-admin:UnknownUser"
)


@pytest.fixture(scope="module")
def project_iri_4125(create_4125_e2e_project, creds: ServerCredentials) -> str:  # noqa: ARG001 (unused argument)
    get_project_route = f"{creds.server}/admin/projects/shortcode/{PROJECT_SHORTCODE}"
    project_iri: str = requests.get(get_project_route, timeout=3).json()["project"]["id"]
    return project_iri


@pytest.fixture(scope="module")
def onto_iri_4125(creds: ServerCredentials) -> str:
    return f"{creds.server}/ontology/{PROJECT_SHORTCODE}/{ONTO_NAME}/v2#"


@pytest.fixture(scope="module")
def second_onto_iri_4125(creds: ServerCredentials) -> str:
    return f"{creds.server}/ontology/{PROJECT_SHORTCODE}/{SECOND_ONTO_NAME}/v2#"


@pytest.fixture(scope="module")
def class_iri_ImageResource(onto_iri_4125: str) -> str:
    return f"{onto_iri_4125}ImageResource"


def class_iri_DefaultPermissionsResource(second_onto_iri: str) -> str:
    return f"{second_onto_iri}DefaultPermissionsResource"


@pytest.mark.usefixtures("_xmlupload_4125_e2e_project")
def test_ImageResource_uses_doap_should_be_preview(
    class_iri_ImageResource: str, auth_header: dict[str, str], project_iri_4125: str, creds: ServerCredentials
) -> None:
    res_graph = util_request_resources_by_class(class_iri_ImageResource, auth_header, project_iri_4125, creds)
    resource_iri = util_get_res_iri_from_label(res_graph, "ImageResource_uses_doap_should_be_preview")
    resource_permissions = next(res_graph.objects(resource_iri, KNORA_API.hasPermissions))
    assert resource_permissions == PUBLIC_PERMISSIONS

    bitstream_val_iri = next(res_graph.objects(resource_iri, KNORA_API.hasStillImageFileValue))
    bitstream_permissions = next(res_graph.objects(bitstream_val_iri, KNORA_API.hasPermissions))
    assert bitstream_permissions == PREVIEW_PERMISSIONS
