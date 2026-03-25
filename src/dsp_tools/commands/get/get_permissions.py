from typing import Any
from typing import Literal

import regex
from loguru import logger

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.permissions_client_live import PermissionsClientLive
from dsp_tools.commands.get.get_permissions_legacy import parse_legacy_doaps
from dsp_tools.commands.get.models.permissions_models import DoapCategories
from dsp_tools.utils.request_utils import ResponseCodeAndText


def get_default_permissions(
    auth: AuthenticationClient, project_iri: str, prefixes: dict[str, str]
) -> tuple[str, dict[str, list[str] | Literal["all"]] | None]:
    """
    Retrieve the DOAPs of a project from the server,
    and try to fit them into our system of "default_permissions" and "default_permissions_overrule".
    If an anomaly is found, return an error message for "default_permissions",
    and None for "default_permissions_overrule".

    Returns:
        "default_permissions": "public" or "private" or error message
        "default_permissions_overrule": {"private": [<classes_or_props>], "limited_view": ["all" or <img_classes>]}
    """
    perm_client = PermissionsClientLive(
        server=auth.server,
        auth=auth,
        project_iri=project_iri,
    )
    project_doaps = perm_client.get_project_doaps()
    fallback_text = (
        "We cannot determine if this project is public or private. "
        "The DSP-TOOLS devs can assist you in analysing the existing DOAPs, "
        "and help you decide if the original intent was rather public or rather private."
    )
    if isinstance(project_doaps, ResponseCodeAndText):
        return fallback_text, None
    default_permissions_result = _parse_default_permissions(project_doaps)
    default_permissions = default_permissions_result if default_permissions_result is not None else fallback_text
    default_permissions_overrule = _parse_default_permissions_overrule(project_doaps, prefixes)
    return default_permissions, default_permissions_overrule


def _parse_default_permissions(project_doaps: list[dict[str, Any]]) -> str | None:
    """
    First tries to parse legacy DOAPs with multiple groups, then falls back to new-style parsing.
    New-style parsing: If the DOAPs exactly match our definition of public/private, return public/private.
    Otherwise, log a warning and return None.
    """
    if legacy_result := parse_legacy_doaps(project_doaps):
        return legacy_result
    return _parse_new_style_permissions(project_doaps)


def _parse_new_style_permissions(project_doaps: list[dict[str, Any]]) -> str | None:
    unsupported_groups = ("SystemAdmin", "ProjectAdmin", "Creator", "KnownUser", "UnknownUser")
    if [x for x in project_doaps if x.get("forGroup", "").endswith(unsupported_groups)]:
        logger.warning("The only supported target group for DOAPs is ProjectMember.")
        return None
    proj_member_doaps = [x for x in project_doaps if x.get("forGroup", "").endswith("ProjectMember")]
    if len(proj_member_doaps) != 1:
        logger.warning("There must be exactly 1 DOAP for ProjectMember.")
        return None
    return _parse_project_member_perms(proj_member_doaps[0]["hasPermissions"])


def _parse_project_member_perms(perms: list[dict[str, Any]]) -> str | None:
    if len(perms) not in [2, 4]:
        err_msg = "The only allowed permissions are 'private' (with 2 elements), and 'limited_view' (with 4 elements)"
        logger.warning(err_msg)
        return None
    proj_adm_perms = [x for x in perms if x["additionalInformation"].endswith("ProjectAdmin")]
    proj_mem_perms = [x for x in perms if x["additionalInformation"].endswith("ProjectMember")]
    knwn_usr_perms = [x for x in perms if x["additionalInformation"].endswith("KnownUser")]
    unkn_usr_perms = [x for x in perms if x["additionalInformation"].endswith("UnknownUser")]
    valid_adm_mem = (
        len(proj_adm_perms) == len(proj_mem_perms) == 1
        and proj_adm_perms[0]["name"] == "CR"
        and proj_mem_perms[0]["name"] == "D"
    )
    if not valid_adm_mem:
        logger.warning("ProjectAdmin must have 1 CR permission and ProjectMember must have 1 D permission")
        return None
    if len(knwn_usr_perms) == len(unkn_usr_perms) == 0:
        return "private"
    if (
        len(knwn_usr_perms) != 1
        or len(unkn_usr_perms) != 1
        or knwn_usr_perms[0]["name"] != "V"
        or unkn_usr_perms[0]["name"] != "V"
    ):
        logger.warning("In case of 'public', there must be exactly 1 V permission each for KnownUser and UnknownUser")
        return None
    return "public"


def _parse_default_permissions_overrule(
    project_doaps: list[dict[str, Any]], prefixes: dict[str, str]
) -> dict[str, list[str] | Literal["all"]] | None:
    """
    The DOAPs retrieved from the server are examined if they fit into our system of the overrules.
    If yes, an overrule object is returned. Otherwise, None is returned.

    Args:
        project_doaps: DOAPs as retrieved from the server
        prefixes: dict in the form {"my-onto": "http://0.0.0.0:3333/ontology/1234/my-onto/v2"}

    Returns:
        an overrule object that can be written into the JSON project definition file, in this form:
        "default_permissions_overrule": {"private": [<classes_or_props>], "limited_view": ["all" or <img_classes>]}
        or None if the DOAPs do not fit into our system.
    """
    prefixes_knora_base_inverted = _convert_prefixes(prefixes)
    doap_categories = _categorize_doaps(project_doaps)
    if doap_categories is None:
        return None
    if not _validate_doap_categories(doap_categories):
        return None
    return _construct_overrule_object(doap_categories, prefixes_knora_base_inverted)


def _convert_prefixes(prefixes: dict[str, str]) -> dict[str, str]:
    """
    Convert knora-api form of prefixes into knora-base form (used by DOAPs), and invert it.

    Args:
        prefixes: dict in the form of {"my-onto": "http://0.0.0.0:3333/ontology/1234/my-onto/v2"}

    Returns:
        dict in the form of {"http://www.knora.org/ontology/1234/my-onto": "my-onto"}
    """
    prefixes_knora_base_inverted = {}
    for onto_shorthand, knora_api_iri in prefixes.items():
        if match := regex.search(r"/ontology/([0-9A-Fa-f]{4})/([^/]+)/v2", knora_api_iri):
            shortcode, onto_name = match.groups()
            prefixes_knora_base_inverted[f"http://www.knora.org/ontology/{shortcode}/{onto_name}"] = onto_shorthand
    return prefixes_knora_base_inverted


def _categorize_doaps(project_doaps: list[dict[str, Any]]) -> DoapCategories | None:
    """
    The overrule object of the JSON project definition file has 2 categories: private and limited_view.
    - "private" is a list of classes/properties that are private.
      The DOAPs for these correspond 1:1 to the classes/properties.
    - "limited_view" is
        - a list of image classes that are limited_view:
          The DOAPs for these are for knora-api:hasStillImageFileValue and the respective class.
        - or the string "all". The DOAPs for these are only for knora-api:hasStillImageFileValue.

    This function groups the DOAPs into these categories.

    Args:
        project_doaps: the DOAPs as retrieved from the server

    Returns:
        a DTO with the categories, or None if there are DOAPs that do not fit into our system
    """
    class_doaps = []
    prop_doaps = []
    has_img_all_classes_doaps = []
    has_img_specific_class_doaps = []
    other_doaps = []
    for doap in project_doaps:
        match (doap.get("forResourceClass"), doap.get("forProperty")):
            case (for_class, None) if for_class:
                class_doaps.append(doap)
            case (None, for_prop) if for_prop and "hasStillImageFileValue" not in for_prop:
                prop_doaps.append(doap)
            case (None, for_prop) if for_prop and "hasStillImageFileValue" in for_prop:
                has_img_all_classes_doaps.append(doap)
            case (for_class, for_prop) if for_class and for_prop and "hasStillImageFileValue" in for_prop:
                has_img_specific_class_doaps.append(doap)
            case _:
                other_doaps.append(doap)
    # Only validate other_doaps if there are any
    if other_doaps:
        if _parse_default_permissions(other_doaps) is None:
            logger.warning("Found DOAPs that do not fit into our system")
            return None
    return DoapCategories(
        class_doaps=class_doaps,
        prop_doaps=prop_doaps,
        has_img_all_classes_doaps=has_img_all_classes_doaps,
        has_img_specific_class_doaps=has_img_specific_class_doaps,
    )


def _validate_doap_categories(doap_categories: DoapCategories) -> bool:
    privates_valid = all(_validate_private_doap(d) for d in doap_categories.class_doaps + doap_categories.prop_doaps)
    limited_views_valid = all(
        _validate_limited_view_doap(d)
        for d in doap_categories.has_img_all_classes_doaps + doap_categories.has_img_specific_class_doaps
    )
    return privates_valid and limited_views_valid


def _validate_private_doap(doap: dict[str, Any]) -> bool:
    err_msg = "'private' is defined as CR ProjectAdmin|D ProjectMember"
    perm = sorted(doap["hasPermissions"], key=lambda x: x["name"])
    if len(perm) != 2:
        logger.warning(err_msg)
        return False
    CR, D = perm
    if CR["name"] != "CR" or not CR["additionalInformation"].endswith("ProjectAdmin"):
        logger.warning(err_msg)
        return False
    if D["name"] != "D" or not D["additionalInformation"].endswith("ProjectMember"):
        logger.warning(err_msg)
        return False
    return True


def _validate_limited_view_doap(doap: dict[str, Any]) -> bool:
    err_msg = "'limited_view' is defined as CR ProjectAdmin|D ProjectMember|RV KnownUser|RV UnknownUser"
    perm = sorted(doap["hasPermissions"], key=lambda x: x["name"])
    if len(perm) != 4:
        logger.warning(err_msg)
        return False
    CR, D, RV1, RV2 = perm
    if CR["name"] != "CR" or not CR["additionalInformation"].endswith("ProjectAdmin"):
        logger.warning(err_msg)
        return False
    if D["name"] != "D" or not D["additionalInformation"].endswith("ProjectMember"):
        logger.warning(err_msg)
        return False
    if RV1["name"] != "RV" or not RV2["additionalInformation"].endswith("nownUser"):
        logger.warning(err_msg)
        return False
    if RV2["name"] != "RV" or not RV2["additionalInformation"].endswith("nownUser"):
        logger.warning(err_msg)
        return False
    return True


def _construct_overrule_object(
    doap_categories: DoapCategories, prefixes_knora_base_inverted: dict[str, str]
) -> dict[str, list[str] | Literal["all"]] | None:
    """
    Construct the final overrules object that can be written into the JSON project definition file.
    To do so, the fully qualified IRIs of the classes/properties must be converted to prefixed IRIs.

    Args:
        doap_categories: The categorized DOAPs from the server
        prefixes_knora_base_inverted: lookup from fully qualified IRIs to prefixed IRIs

    Returns:
        the final overrules object that can be written into the JSON project definition file,
        or None if the DOAPs do not fit into our system
    """
    privates: list[str] = []
    for class_doap in doap_categories.class_doaps:
        privates.append(_get_prefixed_iri(class_doap["forResourceClass"], prefixes_knora_base_inverted))
    for prop_doap in doap_categories.prop_doaps:
        privates.append(_get_prefixed_iri(prop_doap["forProperty"], prefixes_knora_base_inverted))

    limited_views: list[str] | Literal["all"]
    if len(doap_categories.has_img_all_classes_doaps) > 1:
        logger.warning("There can only be 1 all-images DOAP for 'hasStillImageFileValue'")
        return None
    if len(doap_categories.has_img_all_classes_doaps) == 1 and len(doap_categories.has_img_specific_class_doaps) > 0:
        logger.warning("If there is a DOAP for all images, there cannot be DOAPs for specific img classes")
        return None
    if len(doap_categories.has_img_all_classes_doaps) == 1:
        limited_views = "all"
    else:
        limited_views = []
        for img_doap in doap_categories.has_img_specific_class_doaps:
            limited_views.append(_get_prefixed_iri(img_doap["forResourceClass"], prefixes_knora_base_inverted))

    result: dict[str, list[str] | Literal["all"]] = {}
    if privates:
        result["private"] = privates
    if limited_views:
        result["limited_view"] = limited_views
    return result


def _get_prefixed_iri(full_iri: str, prefixes_inverted: dict[str, str]) -> str:
    # example:
    #    - full_iri = "http://www.knora.org/ontology/1234/my-onto/v2#MyClass"
    #    - prefixes_inverted = {"http://www.knora.org/ontology/1234/my-onto": "my-onto"}
    #    - output = "my-onto:MyClass"
    if "#" not in full_iri:
        raise ValueError(f"{full_iri} is not a valid full IRI")
    before_hashtag, after_hashtag = full_iri.rsplit("#", maxsplit=1)
    if before_hashtag not in prefixes_inverted:
        raise ValueError(f"{full_iri} belongs to an unknown ontology. It cannot be found in the prefixes.")
    prefix = prefixes_inverted[before_hashtag]
    return f"{prefix}:{after_hashtag}"
