from loguru import logger

from dsp_tools.clients.permissions_client import PermissionsClient
from dsp_tools.commands.create.models.parsed_project import DefaultPermissions
from dsp_tools.commands.create.models.parsed_project import GlobalLimitedViewPermission
from dsp_tools.commands.create.models.parsed_project import LimitedViewPermissionsSelection
from dsp_tools.commands.create.models.parsed_project import ParsedPermissions
from dsp_tools.commands.create.models.server_project_info import CreatedIriCollection
from dsp_tools.error.exceptions import UnreachableCodeError
from dsp_tools.setup.ansi_colors import BOLD
from dsp_tools.setup.ansi_colors import RESET_TO_DEFAULT
from dsp_tools.utils.rdf_constants import KNORA_ADMIN_PREFIX


def create_default_permissions(
    perm_client: PermissionsClient,
    parsed_permissions: ParsedPermissions,
    created_iris: CreatedIriCollection,
) -> bool:
    print(BOLD + "Processing default permissions:" + RESET_TO_DEFAULT)
    logger.info("Processing default permissions:")
    if not _delete_existing_doaps(perm_client):
        print("    WARNING: Cannot delete the existing default permissions")
        logger.warning("Cannot delete the existing default permissions")
        return False
    if not _create_new_doap(perm_client, parsed_permissions.default_permissions):
        print("    WARNING: Cannot create default permissions")
        logger.warning("Cannot create default permissions")
        return False
    if parsed_permissions.overrule_private or parsed_permissions.overrule_limited_view:
        if not _create_overrules(parsed_permissions, perm_client, created_iris):
            print("    WARNING: Cannot create default permissions overrules")
            logger.warning("Cannot create default permissions overrules")
            return False
    print("    Default permissions have been set")
    logger.info("Default permissions have been set")
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


def _create_new_doap(perm_client: PermissionsClient, default_permissions: DefaultPermissions) -> bool:
    perm = [
        {"additionalInformation": f"{KNORA_ADMIN_PREFIX}ProjectAdmin", "name": "CR", "permissionCode": None},
        {"additionalInformation": f"{KNORA_ADMIN_PREFIX}ProjectMember", "name": "D", "permissionCode": None},
    ]
    if default_permissions == DefaultPermissions.PUBLIC:
        perm.append({"additionalInformation": f"{KNORA_ADMIN_PREFIX}KnownUser", "name": "V", "permissionCode": None})
        perm.append({"additionalInformation": f"{KNORA_ADMIN_PREFIX}UnknownUser", "name": "V", "permissionCode": None})
    payload = {
        "forGroup": f"{KNORA_ADMIN_PREFIX}ProjectMember",
        "forProject": perm_client.proj_iri,
        "hasPermissions": perm,
    }
    return perm_client.create_new_doap(payload)


def _create_overrules(
    parsed_permissions: ParsedPermissions, perm_client: PermissionsClient, created_collection: CreatedIriCollection
) -> bool:
    overall_success = True
    if parsed_permissions.overrule_private:
        success = _create_private_overrule(parsed_permissions.overrule_private, perm_client, created_collection)
        if not success:
            overall_success = False

    if isinstance(parsed_permissions.overrule_limited_view, GlobalLimitedViewPermission):
        if parsed_permissions.overrule_limited_view == GlobalLimitedViewPermission.NONE:
            return overall_success

    success = _handle_limited_view_overrule(parsed_permissions.overrule_limited_view, perm_client)
    if not success:
        overall_success = False

    return overall_success


def _create_private_overrule(
    private_overrule: list[str], perm_client: PermissionsClient, created_collection: CreatedIriCollection
) -> bool:
    results = []
    props, cls = _separate_props_and_classes(private_overrule, created_collection)
    for p in props:
        results.append(_create_one_private_overrule(perm_client=perm_client, res_iri=None, prop_iri=p))
    for c in cls:
        results.append(_create_one_private_overrule(perm_client=perm_client, res_iri=c, prop_iri=None))
    return all(results)


def _separate_props_and_classes(
    iris: list[str], created_collection: CreatedIriCollection
) -> tuple[list[str], list[str]]:
    props = [x for x in iris if x in created_collection.created_properties]
    cls = [x for x in iris if x in created_collection.created_classes]
    return props, cls


def _handle_limited_view_overrule(
    overrule_limited_view: GlobalLimitedViewPermission | LimitedViewPermissionsSelection, perm_client: PermissionsClient
) -> bool:
    overall_success = True
    match overrule_limited_view:
        case LimitedViewPermissionsSelection():
            for ele in overrule_limited_view.limited_selection:
                success = _create_one_limited_view_overrule(perm_client=perm_client, img_class_iri=ele)
                if not success:
                    overall_success = False
        case GlobalLimitedViewPermission.ALL:
            success = _create_one_limited_view_overrule(perm_client=perm_client, img_class_iri=None)
            if not success:
                overall_success = False
        case _:
            raise UnreachableCodeError(f"Unknown overrule_limited_view: {overrule_limited_view!s}")
    return overall_success


def _create_one_private_overrule(perm_client: PermissionsClient, res_iri: str | None, prop_iri: str | None) -> bool:
    perm = [
        {"additionalInformation": f"{KNORA_ADMIN_PREFIX}ProjectAdmin", "name": "CR", "permissionCode": None},
        {"additionalInformation": f"{KNORA_ADMIN_PREFIX}ProjectMember", "name": "D", "permissionCode": None},
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
        {"additionalInformation": f"{KNORA_ADMIN_PREFIX}ProjectAdmin", "name": "CR", "permissionCode": None},
        {"additionalInformation": f"{KNORA_ADMIN_PREFIX}ProjectMember", "name": "D", "permissionCode": None},
        {"additionalInformation": f"{KNORA_ADMIN_PREFIX}KnownUser", "name": "RV", "permissionCode": None},
        {"additionalInformation": f"{KNORA_ADMIN_PREFIX}UnknownUser", "name": "RV", "permissionCode": None},
    ]
    payload = {
        "forProperty": "http://api.knora.org/ontology/knora-api/v2#hasStillImageFileValue",
        "forResourceClass": img_class_iri,
        "forProject": perm_client.proj_iri,
        "hasPermissions": perm,
    }
    return perm_client.create_new_doap(payload)
