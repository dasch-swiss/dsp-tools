from loguru import logger

from dsp_tools.commands.project.models.permissions_client import PermissionsClient

USER_IRI_PREFIX = "http://www.knora.org/ontology/knora-admin#"


def create_default_permissions(
    perm_client: PermissionsClient,
    default_permissions: str,
    default_permissions_overrule: dict[str, str | list[str]] | None,
    shortcode: str,
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
        if not _create_overrules(perm_client, default_permissions_overrule, shortcode):
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


def _create_overrules(
    perm_client: PermissionsClient, default_permissions_overrule: dict[str, str | list[str]], shortcode: str
) -> bool:
    overall_success = True

    # Handle private overrules
    for entity in default_permissions_overrule.get("private", []):
        first_letter = entity.split(":")[-1][0]
        is_res = first_letter.upper() == first_letter
        entity_iri = _get_iri_from_prefixed_name(entity, shortcode, perm_client.auth.server)
        if is_res:
            success = _create_one_private_overrule(perm_client=perm_client, res_iri=entity_iri, prop_iri=None)
        else:
            success = _create_one_private_overrule(perm_client=perm_client, res_iri=None, prop_iri=entity_iri)
        if not success:
            overall_success = False

    # Handle limited_view overrules
    if not (limited_view := default_permissions_overrule.get("limited_view")):
        return overall_success
    if limited_view == "all":
        success = _create_one_limited_view_overrule(perm_client=perm_client, img_class_iri=None)
        if not success:
            overall_success = False
    else:
        # limited_view is a list of prefixed class names
        for prefixed_img_class in limited_view:
            img_class_iri = _get_iri_from_prefixed_name(prefixed_img_class, shortcode, perm_client.auth.server)
            success = _create_one_limited_view_overrule(perm_client=perm_client, img_class_iri=img_class_iri)
            if not success:
                overall_success = False

    return overall_success


def _create_one_private_overrule(perm_client: PermissionsClient, res_iri: str | None, prop_iri: str | None) -> bool:
    perm = [
        {"additionalInformation": f"{USER_IRI_PREFIX}ProjectAdmin", "name": "CR", "permissionCode": None},
        {"additionalInformation": f"{USER_IRI_PREFIX}ProjectMember", "name": "D", "permissionCode": None},
    ]
    payload = {
        "forProperty": prop_iri,
        "forResourceClass": res_iri,
        "forProject": perm_client.proj_iri,
        "hasPermissions": perm,
    }
    return perm_client.create_new_doap(payload)


def _create_one_limited_view_overrule(perm_client: PermissionsClient, img_class_iri: str | None) -> bool:
    # This makes only sense for the knora-api:hasStillImageFileValue property of image classes
    # To set it for all image classes, set img_class_iri to None
    perm = [
        {"additionalInformation": f"{USER_IRI_PREFIX}ProjectAdmin", "name": "CR", "permissionCode": None},
        {"additionalInformation": f"{USER_IRI_PREFIX}ProjectMember", "name": "D", "permissionCode": None},
        {"additionalInformation": f"{USER_IRI_PREFIX}KnownUser", "name": "RV", "permissionCode": None},
        {"additionalInformation": f"{USER_IRI_PREFIX}UnknownUser", "name": "RV", "permissionCode": None},
    ]
    payload = {
        "forProperty": "http://api.knora.org/ontology/knora-api/v2#hasStillImageFileValue",
        "forResourceClass": img_class_iri,
        "forProject": perm_client.proj_iri,
        "hasPermissions": perm,
    }
    return perm_client.create_new_doap(payload)


def _get_iri_from_prefixed_name(prefixed_name: str, proj_shortcode: str, server: str) -> str:
    onto, name = prefixed_name.split(":")
    host_iri = server.replace("https://", "http://")
    if onto == "knora-api":
        return f"http://api.knora.org/ontology/knora-api/v2#{name}"
    return f"{host_iri}/ontology/{proj_shortcode}/{onto}/v2#{name}"
