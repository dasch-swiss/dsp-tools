import time
from collections.abc import Callable
from functools import partial

from loguru import logger

from dsp_tools.clients.permissions_client import PermissionsClient
from dsp_tools.commands.create.models.parsed_project import DefaultPermissions
from dsp_tools.commands.create.models.parsed_project import GlobalLimitedViewPermission
from dsp_tools.commands.create.models.parsed_project import LimitedViewClasses
from dsp_tools.commands.create.models.parsed_project import ValidatedPermissions
from dsp_tools.commands.create.models.server_project_info import CreatedIriCollection
from dsp_tools.error.exceptions import UnreachableCodeError
from dsp_tools.setup.ansi_colors import BOLD
from dsp_tools.setup.ansi_colors import RESET_TO_DEFAULT
from dsp_tools.utils.rdf_constants import KNORA_ADMIN_PREFIX
from dsp_tools.utils.rdf_constants import KNORA_API_PREFIX
from dsp_tools.utils.request_utils import ResponseCodeAndText
from dsp_tools.utils.request_utils import should_retry_request


def create_default_permissions(
    perm_client: PermissionsClient,
    validated_permissions: ValidatedPermissions,
    created_iris: CreatedIriCollection,
) -> bool:
    print(BOLD + "Processing default permissions:" + RESET_TO_DEFAULT)
    logger.info("Processing default permissions:")
    if not _delete_existing_doaps(perm_client):
        print("    WARNING: Cannot delete the existing default permissions")
        logger.warning("Cannot delete the existing default permissions")
        return False
    if not _create_new_doap(perm_client, validated_permissions.default_permissions):
        print("    WARNING: Cannot create default permissions")
        logger.warning("Cannot create default permissions")
        return False
    if (
        validated_permissions.overrule_private is not None
        or validated_permissions.overrule_limited_view != GlobalLimitedViewPermission.NONE
    ):
        if not _create_overrules(validated_permissions, perm_client, created_iris):
            print("    WARNING: Cannot create default permissions overrules")
            logger.warning("Cannot create default permissions overrules")
            return False
    print("    Default permissions have been set")
    logger.info("Default permissions have been set")
    return True


def _delete_existing_doaps(perm_client: PermissionsClient) -> bool:
    doaps = perm_client.get_project_doaps()
    if isinstance(doaps, ResponseCodeAndText):
        if should_retry_request(doaps):
            logger.info("Server error while requesting existing DOAPs, retrying after 10 seconds...")
            time.sleep(10)
            doaps = perm_client.get_project_doaps()
            if isinstance(doaps, ResponseCodeAndText):
                return False
        else:
            return False
    # Handle empty list case (no DOAPs to delete)
    if not doaps:
        return True
    # Delete each DOAP
    existing_doap_iris: list[str] = [x["iri"] for x in doaps]
    for iri in existing_doap_iris:
        # partial used here to avoid using an unbound loop variable (ruff: B023)
        result = _execute_with_retry_on_server_error(partial(perm_client.delete_doap, iri), f"delete_doap({iri})")
        # don't continue with the others, it's better to stop DOAP handling immediately, to avoid a mess
        if not result:
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
        "forProject": perm_client.project_iri,
        "hasPermissions": perm,
    }

    return _execute_with_retry_on_server_error(lambda: perm_client.create_new_doap(payload), "create_new_doap")


def _create_overrules(
    validated_permissions: ValidatedPermissions,
    perm_client: PermissionsClient,
    created_collection: CreatedIriCollection,
) -> bool:
    overall_success = True
    if validated_permissions.overrule_private:
        if not _create_private_overrule(validated_permissions.overrule_private, perm_client, created_collection):
            overall_success = False

    match validated_permissions.overrule_limited_view:
        case GlobalLimitedViewPermission.NONE:
            pass
        case GlobalLimitedViewPermission.ALL | LimitedViewClasses():
            if not _handle_limited_view_overrule(validated_permissions.overrule_limited_view, perm_client):
                overall_success = False
        case _:
            raise UnreachableCodeError(
                f"Unknown overrule_limited_view: {validated_permissions.overrule_limited_view!r}"
            )

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


# DSP-API accepts property IRIs in the knora-api v2 namespace when creating DOAPs
_STILL_IMAGE_FILE_VALUE = f"{KNORA_API_PREFIX}hasStillImageFileValue"
_MOVING_IMAGE_FILE_VALUE = f"{KNORA_API_PREFIX}hasMovingImageFileValue"
_AUDIO_FILE_VALUE = f"{KNORA_API_PREFIX}hasAudioFileValue"


def _handle_limited_view_overrule(
    overrule_limited_view: GlobalLimitedViewPermission | LimitedViewClasses,
    perm_client: PermissionsClient,
) -> bool:
    overall_success = True
    match overrule_limited_view:
        case LimitedViewClasses():
            groups = [
                (_STILL_IMAGE_FILE_VALUE, overrule_limited_view.still_image),
                (_MOVING_IMAGE_FILE_VALUE, overrule_limited_view.moving_image),
                (_AUDIO_FILE_VALUE, overrule_limited_view.audio),
            ]
            for prop_iri, iris in groups:
                for iri in sorted(iris):
                    if not _create_one_limited_view_overrule(perm_client, prop_iri, iri):
                        overall_success = False
        case GlobalLimitedViewPermission.ALL:
            for prop_iri in (_STILL_IMAGE_FILE_VALUE, _MOVING_IMAGE_FILE_VALUE, _AUDIO_FILE_VALUE):
                if not _create_one_limited_view_overrule(perm_client, prop_iri, None):
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
        "forProject": perm_client.project_iri,
        "hasPermissions": perm,
    }

    return _execute_with_retry_on_server_error(
        lambda: perm_client.create_new_doap(payload), f"create_private_overrule(res={res_iri}, prop={prop_iri})"
    )


def _create_one_limited_view_overrule(
    perm_client: PermissionsClient, file_value_prop_iri: str, class_iri: str | None
) -> bool:
    perm = [
        {"additionalInformation": f"{KNORA_ADMIN_PREFIX}ProjectAdmin", "name": "CR", "permissionCode": None},
        {"additionalInformation": f"{KNORA_ADMIN_PREFIX}ProjectMember", "name": "D", "permissionCode": None},
        {"additionalInformation": f"{KNORA_ADMIN_PREFIX}KnownUser", "name": "RV", "permissionCode": None},
        {"additionalInformation": f"{KNORA_ADMIN_PREFIX}UnknownUser", "name": "RV", "permissionCode": None},
    ]
    payload = {
        "forProperty": file_value_prop_iri,
        "forResourceClass": class_iri,
        "forProject": perm_client.project_iri,
        "hasPermissions": perm,
    }

    return _execute_with_retry_on_server_error(
        lambda: perm_client.create_new_doap(payload),
        f"create_limited_view_overrule(prop={file_value_prop_iri}, class_iri={class_iri})",
    )


def _execute_with_retry_on_server_error(
    operation: Callable[[], ResponseCodeAndText | bool],
    operation_name: str,
) -> bool:
    result = operation()
    # Check if result is ResponseCodeAndText (error case)
    if isinstance(result, ResponseCodeAndText):
        if should_retry_request(result):
            logger.warning(f"Server error encountered during {operation_name}, retrying after 10 seconds...")
            time.sleep(10)
            result = operation()
    return result is True
