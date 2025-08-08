import pytest
import requests
from rdflib import Literal

from dsp_tools.cli.args import ServerCredentials
from test.e2e.commands.xmlupload.utils import util_request_resources_by_class

PROJECT_SHORTCODE = "4125"
ONTO_NAME = "e2e-testonto"
SECOND_ONTO_NAME = "second-onto"

PUBLIC_PERMISSIONS = Literal(
    "CR knora-admin:ProjectAdmin|D knora-admin:ProjectMember|V knora-admin:KnownUser,knora-admin:UnknownUser"
)
PRIVATE_PERMISSIONS = Literal("CR knora-admin:ProjectAdmin|D knora-admin:ProjectMember")


@pytest.fixture(scope="module")
def project_iri_4125(create_4125_e2e_project, creds: ServerCredentials) -> str:
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
def class_iri_ImageResource(onto_iri) -> str:
    return f"{onto_iri}ImageResource"


def class_iri_DefaultPermissionsResource(second_onto_iri) -> str:
    return f"{second_onto_iri}DefaultPermissionsResource"


@pytest.mark.usefixtures("_xmlupload_e2e_project")
def test_ImageResource_uses_doap_should_be_preview(
    class_iri_ImageResource: str, auth_header: dict[str, str], project_iri_4125: str, creds: ServerCredentials
) -> None:
    res_graph = util_request_resources_by_class(class_iri_ImageResource, auth_header, project_iri_4125, creds)
