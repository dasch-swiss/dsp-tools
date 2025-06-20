from urllib.parse import quote_plus

from loguru import logger

from dsp_tools.commands.project.models.permissions_client import PermissionsClient
from dsp_tools.error.exceptions import BaseError

USER_IRI_PREFIX = "http://www.knora.org/ontology/knora-admin#"


def create_default_permissions(perm_client: PermissionsClient, project_default_permissions: str, proj_iri: str) -> bool:
    if not _delete_existing_doaps(perm_client, proj_iri):
        print("WARNING: Cannot delete the existing default permissions")
        return False
    if not _create_new_doap(perm_client, project_default_permissions, proj_iri):
        print("WARNING: Cannot create default permissions")
        return False
    print("Created default permissions for project")
    return True


def _delete_existing_doaps(perm_client: PermissionsClient, proj_iri: str) -> bool:
    try:
        response = perm_client.get(f"/admin/permissions/doap/{quote_plus(proj_iri)}")
    except BaseError:
        logger.exception("Error while retrieving existing DOAPs")
        return False
    existing_doap_iris = [x.iri for x in response["defaultObjectAccessPermissions"]]
    for iri in existing_doap_iris:
        try:
            response = perm_client.delete(f"/admin/permissions/{quote_plus(iri)}")
        except BaseError:
            logger.exception(f"Error while deleting existing DOAP {iri}")
            return False
    return True


def _create_new_doap(perm_client: PermissionsClient, project_default_permissions: str, proj_iri: str) -> bool:
    perm = [
        {"additionalInformation": f"{USER_IRI_PREFIX}ProjectAdmin", "name": "CR", "permissionCode": None},
        {"additionalInformation": f"{USER_IRI_PREFIX}ProjectMember", "name": "D", "permissionCode": None},
    ]
    if project_default_permissions == "public":
        perm.append({"additionalInformation": f"{USER_IRI_PREFIX}KnownUser", "name": "V", "permissionCode": None})
        perm.append({"additionalInformation": f"{USER_IRI_PREFIX}UnknownUser", "name": "V", "permissionCode": None})
    payload = {
        "forGroup": f"{USER_IRI_PREFIX}ProjectMember",
        "forProject": proj_iri,
        "hasPermissions": perm,
    }
    try:
        perm_client.post("/admin/permissions/doap", payload)
    except BaseError:
        logger.exception("Error while creating new DOAP")
        return False
    return True
