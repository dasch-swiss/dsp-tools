from loguru import logger

from dsp_tools.clients.connection import Connection
from dsp_tools.error.exceptions import BaseError

USER_IRI_PREFIX = "http://www.knora.org/ontology/knora-admin#"


def create_default_permissions(con: Connection, project_default_permissions: str, proj_iri: str) -> bool:
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
        err_msg = "Cannot create default permissions for project."
        print(f"WARNING: {err_msg}")
        logger.exception(err_msg)
        return False
    return True
