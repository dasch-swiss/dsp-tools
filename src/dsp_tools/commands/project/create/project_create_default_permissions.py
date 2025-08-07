from loguru import logger

from dsp_tools.commands.project.models.permissions_client import PermissionsClient

USER_IRI_PREFIX = "http://www.knora.org/ontology/knora-admin#"


def create_default_permissions(
    perm_client: PermissionsClient,
    default_permissions: str,
    default_permissions_overrule: dict[str, str | list[str]] | None,
) -> bool:
    logger.info("Set default permissions...")
    print("Set default permissions...")
    if not _delete_existing_doaps(perm_client):
        print("WARNING: Cannot delete the existing default permissions")
        logger.warning("Cannot delete the existing default permissions")
        return False
    if not _create_new_doap(perm_client, default_permissions):
        print("WARNING: Cannot create default permissions")
        logger.warning("Cannot create default permissions")
        return False
    if default_permissions_overrule:
        if not _create_overrules(perm_client, default_permissions_overrule):
            print("WARNING: Cannot create default permissions overrules")
            logger.warning("Cannot create default permissions overrules")
            return False
    logger.info("Default permissions have been set")
    print("Default permissions have been set")
    return True


def _delete_existing_doaps(perm_client: PermissionsClient) -> bool:
    if not (doaps := perm_client.get_project_doaps()):
        return False
    existing_doap_iris: list[str] = [x["iri"] for x in doaps]
    for iri in existing_doap_iris:
        if not perm_client.delete_doap(iri):
            # don't continue with the others, it's better to stop DOAP handling immediately, to avoid a mess
            return False
    return True


def _create_new_doap(perm_client: PermissionsClient, default_permissions: str) -> bool:
    perm = [
        {"additionalInformation": f"{USER_IRI_PREFIX}ProjectAdmin", "name": "CR", "permissionCode": None},
        {"additionalInformation": f"{USER_IRI_PREFIX}ProjectMember", "name": "D", "permissionCode": None},
    ]
    if default_permissions == "public":
        perm.append({"additionalInformation": f"{USER_IRI_PREFIX}KnownUser", "name": "V", "permissionCode": None})
        perm.append({"additionalInformation": f"{USER_IRI_PREFIX}UnknownUser", "name": "V", "permissionCode": None})
    payload = {
        "forGroup": f"{USER_IRI_PREFIX}ProjectMember",
        "forProject": perm_client.proj_iri,
        "hasPermissions": perm,
    }
    return perm_client.create_new_doap(payload)


def _create_overrules(perm_client: PermissionsClient, default_permissions_overrule: dict[str, str | list[str]]) -> bool:
    overall_success = True
    for entity in default_permissions_overrule["private"]:
        first_letter = entity.split(":")[-1][0]
        is_res = first_letter.upper() == first_letter
        if is_res:
            success = _create_one_private_overrule(perm_client=perm_client, prefixed_res=entity, prefixed_prop=None)
        else:
            success = _create_one_private_overrule(perm_client=perm_client, prefixed_res=None, prefixed_prop=entity)
        if not success:
            overall_success = False
    for prefixed_img_class in default_permissions_overrule["limited_view"]:
        success = _create_one_limited_view_overrule(perm_client=perm_client, prefixed_img_class=prefixed_img_class)
        if not success:
            overall_success = False
    return overall_success


def _create_one_private_overrule(
    perm_client: PermissionsClient, prefixed_res: str | None, prefixed_prop: str | None
) -> bool:
    perm = [
        {"additionalInformation": f"{USER_IRI_PREFIX}ProjectAdmin", "name": "CR", "permissionCode": None},
        {"additionalInformation": f"{USER_IRI_PREFIX}ProjectMember", "name": "D", "permissionCode": None},
    ]
    payload = {
        "forProperty": prefixed_prop,
        "forResourceClass": prefixed_res,
        "forProject": perm_client.proj_iri,
        "hasPermissions": perm,
    }
    return perm_client.create_new_doap(payload)


def _create_one_limited_view_overrule(perm_client: PermissionsClient, prefixed_img_class: str) -> bool:
    perm = [
        {"additionalInformation": f"{USER_IRI_PREFIX}ProjectAdmin", "name": "CR", "permissionCode": None},
        {"additionalInformation": f"{USER_IRI_PREFIX}ProjectMember", "name": "D", "permissionCode": None},
        {"additionalInformation": f"{USER_IRI_PREFIX}KnownUser", "name": "RV", "permissionCode": None},
        {"additionalInformation": f"{USER_IRI_PREFIX}UnknownUser", "name": "RV", "permissionCode": None},
   ]
    payload = {
        "forProperty": "knora-api:hasStillImageFileValue",
        "forResourceClass": prefixed_img_class,
        "forProject": perm_client.proj_iri,
        "hasPermissions": perm,
    }
    return perm_client.create_new_doap(payload)
