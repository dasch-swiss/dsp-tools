import pytest
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.utils.rdflib_constants import KNORA_API
from test.e2e.commands.xmlupload.utils import util_get_res_iri_from_label
from test.e2e.commands.xmlupload.utils import util_request_resources_by_class

PUBLIC_PERMISSIONS = Literal(
    "CR knora-admin:ProjectAdmin|D knora-admin:ProjectMember|V knora-admin:KnownUser,knora-admin:UnknownUser"
)
PRIVATE_PERMISSIONS = Literal("CR knora-admin:ProjectAdmin|D knora-admin:ProjectMember")
PREVIEW_PERMISSIONS = Literal(
    "CR knora-admin:ProjectAdmin|D knora-admin:ProjectMember|RV knora-admin:KnownUser,knora-admin:UnknownUser"
)


@pytest.fixture(scope="module")
def class_iri_ImageResource(onto_iri_4125: str) -> str:
    return f"{onto_iri_4125}ImageResource"


@pytest.fixture(scope="module")
def class_iri_DefaultPermissionsResource(second_onto_iri_4125: str) -> str:
    return f"{second_onto_iri_4125}DefaultPermissionsResource"


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


@pytest.mark.usefixtures("_xmlupload_4125_e2e_project")
def test_ImageResource_overrules_doap_is_open(
    class_iri_ImageResource: str, auth_header: dict[str, str], project_iri_4125: str, creds: ServerCredentials
) -> None:
    res_graph = util_request_resources_by_class(class_iri_ImageResource, auth_header, project_iri_4125, creds)
    resource_iri = util_get_res_iri_from_label(res_graph, "ImageResource_overrules_doap_is_open")
    resource_permissions = next(res_graph.objects(resource_iri, KNORA_API.hasPermissions))
    assert resource_permissions == PUBLIC_PERMISSIONS

    bitstream_val_iri = next(res_graph.objects(resource_iri, KNORA_API.hasStillImageFileValue))
    bitstream_permissions = next(res_graph.objects(bitstream_val_iri, KNORA_API.hasPermissions))
    assert bitstream_permissions == PUBLIC_PERMISSIONS


@pytest.mark.usefixtures("_xmlupload_4125_e2e_project")
def test_DefaultPermissionsResource_uses_doap_should_be_public(
    class_iri_DefaultPermissionsResource: str,
    auth_header: dict[str, str],
    project_iri_4125: str,
    creds: ServerCredentials,
) -> None:
    res_graph = util_request_resources_by_class(
        class_iri_DefaultPermissionsResource, auth_header, project_iri_4125, creds
    )
    resource_iri = util_get_res_iri_from_label(res_graph, "DefaultPermissionsResource_uses_doap_should_be_public")
    resource_permissions = next(res_graph.objects(resource_iri, KNORA_API.hasPermissions))
    assert resource_permissions == PUBLIC_PERMISSIONS


@pytest.mark.usefixtures("_xmlupload_4125_e2e_project")
def test_DefaultPermissionsResource_overrules_doap_should_be_private(
    class_iri_DefaultPermissionsResource: str,
    auth_header: dict[str, str],
    project_iri_4125: str,
    creds: ServerCredentials,
) -> None:
    res_graph = util_request_resources_by_class(
        class_iri_DefaultPermissionsResource, auth_header, project_iri_4125, creds
    )
    resource_iri = util_get_res_iri_from_label(res_graph, "DefaultPermissionsResource_overrules_doap_should_be_private")
    resource_permissions = next(res_graph.objects(resource_iri, KNORA_API.hasPermissions))
    assert resource_permissions == PRIVATE_PERMISSIONS


@pytest.mark.usefixtures("_xmlupload_4125_e2e_project")
def test_defaultPermissionsProp_uses_doap_should_be_public(
    class_iri_DefaultPermissionsResource: str,
    auth_header: dict[str, str],
    project_iri_4125: str,
    creds: ServerCredentials,
    second_onto_iri_4125: str,
) -> None:
    res_graph = util_request_resources_by_class(
        class_iri_DefaultPermissionsResource, auth_header, project_iri_4125, creds
    )
    resource_iri = util_get_res_iri_from_label(res_graph, "defaultPermissionsProp_uses_doap_should_be_public")

    prop_iri = URIRef(f"{second_onto_iri_4125}defaultPermissionsProp")
    prop_val_iri = next(res_graph.objects(resource_iri, prop_iri))
    prop_permissions = next(res_graph.objects(prop_val_iri, KNORA_API.hasPermissions))
    assert prop_permissions == PUBLIC_PERMISSIONS


@pytest.mark.usefixtures("_xmlupload_4125_e2e_project")
def test_defaultPermissionsProp_overrules_doap_should_be_private(
    class_iri_DefaultPermissionsResource: str,
    auth_header: dict[str, str],
    project_iri_4125: str,
    creds: ServerCredentials,
    second_onto_iri_4125: str,
) -> None:
    res_graph = util_request_resources_by_class(
        class_iri_DefaultPermissionsResource, auth_header, project_iri_4125, creds
    )
    resource_iri = util_get_res_iri_from_label(res_graph, "defaultPermissionsProp_overrules_doap_should_be_private")

    prop_iri = URIRef(f"{second_onto_iri_4125}defaultPermissionsProp")
    prop_val_iri = next(res_graph.objects(resource_iri, prop_iri))
    prop_permissions = next(res_graph.objects(prop_val_iri, KNORA_API.hasPermissions))
    assert prop_permissions == PRIVATE_PERMISSIONS


@pytest.mark.usefixtures("_xmlupload_4125_e2e_project")
def test_privateProp_uses_doap_should_be_private(
    class_iri_DefaultPermissionsResource: str,
    auth_header: dict[str, str],
    project_iri_4125: str,
    creds: ServerCredentials,
    second_onto_iri_4125: str,
) -> None:
    res_graph = util_request_resources_by_class(
        class_iri_DefaultPermissionsResource, auth_header, project_iri_4125, creds
    )
    resource_iri = util_get_res_iri_from_label(res_graph, "privateProp_uses_doap_should_be_private")

    prop_iri = URIRef(f"{second_onto_iri_4125}privateProp")
    prop_val_iri = next(res_graph.objects(resource_iri, prop_iri))
    prop_permissions = next(res_graph.objects(prop_val_iri, KNORA_API.hasPermissions))
    assert prop_permissions == PRIVATE_PERMISSIONS


@pytest.mark.usefixtures("_xmlupload_4125_e2e_project")
def test_privateProp_overrules_doap_should_be_public(
    class_iri_DefaultPermissionsResource: str,
    auth_header: dict[str, str],
    project_iri_4125: str,
    creds: ServerCredentials,
    second_onto_iri_4125: str,
) -> None:
    res_graph = util_request_resources_by_class(
        class_iri_DefaultPermissionsResource, auth_header, project_iri_4125, creds
    )
    resource_iri = util_get_res_iri_from_label(res_graph, "privateProp_overrules_doap_should_be_public")

    prop_iri = URIRef(f"{second_onto_iri_4125}privateProp")
    prop_val_iri = next(res_graph.objects(resource_iri, prop_iri))
    prop_permissions = next(res_graph.objects(prop_val_iri, KNORA_API.hasPermissions))
    assert prop_permissions == PUBLIC_PERMISSIONS
