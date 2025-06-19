from urllib.parse import quote_plus

from loguru import logger

from dsp_tools.clients.connection import Connection
from dsp_tools.error.exceptions import BaseError

USER_IRI_PREFIX = "http://www.knora.org/ontology/knora-admin#"


def create_default_permissions(con: Connection, project_default_permissions: str, proj_iri: str) -> bool:
    if not _delete_existing_doaps(con, proj_iri):
        print("WARNING: Cannot delete the existing default permissions")
        return False
    if not _create_new_doap(con, project_default_permissions, proj_iri):
        print("WARNING: Cannot create default permissions")
        return False
    print("Created default permissions for project")
    return True


def _delete_existing_doaps(con: Connection, proj_iri: str) -> bool:
    try:
        response = con.get(f"/admin/permissions/doap/{quote_plus(proj_iri)}")
    except BaseError:
        logger.exception("Error while retrieving existing DOAPs")
        return False
    existing_doap_iris = [x.iri for x in response["defaultObjectAccessPermissions"]]
    for iri in existing_doap_iris:
        try:
            response = con.delete(f"/admin/permissions/{quote_plus(iri)}")
        except BaseError:
            logger.exception(f"Error while deleting existing DOAP {iri}")
            return False
    return True


def _create_new_doap(con: Connection, project_default_permissions: str, proj_iri: str) -> bool:
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
        con.post("/admin/permissions/doap", payload)
    except BaseError:
        logger.exception("Error while creating new DOAP")
        return False
    return True
