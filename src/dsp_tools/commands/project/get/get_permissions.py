from typing import Any

import regex

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.commands.project.models.permissions_client import PermissionsClient
from dsp_tools.commands.project.models.permissions_models import DoapCategories
from dsp_tools.error.exceptions import UnknownDOAPException


def get_default_permissions(
    auth: AuthenticationClient, project_iri: str, prefixes: dict[str, str]
) -> tuple[str, dict[str, list[str]] | None]:
    perm_client = PermissionsClient(auth, project_iri)
    project_doaps = perm_client.get_project_doaps()
    fallback_text = (
        "We cannot determine if this project is public or private. "
        "The DSP-TOOLS devs can assist you in analysing the existing DOAPs, "
        "and help you deciding if the original intent was rather public or rather private."
    )
    try:
        default_permissions = _parse_default_permissions(project_doaps)
        default_permissions_override = _parse_default_permissions_override(project_doaps, prefixes)
    except UnknownDOAPException:
        default_permissions = fallback_text
        default_permissions_override = None
    return default_permissions, default_permissions_override


def _parse_default_permissions(project_doaps: list[dict[str, Any]]) -> str:
    """If the DOAPs exactly match our definition of public/private, return public/private. Otherwise, return unknown."""
    unsupported_groups = ("SystemAdmin", "ProjectAdmin", "Creator", "KnownUser", "UnknownUser")
    if [x for x in project_doaps if x.get("forGroup", "").endswith(unsupported_groups)]:
        raise UnknownDOAPException()
    proj_member_doaps = [x for x in project_doaps if x.get("forGroup", "").endswith("ProjectMember")]
    if len(proj_member_doaps) != 1:
        raise UnknownDOAPException()
    perms = proj_member_doaps[0]["hasPermissions"]
    if len(perms) not in [2, 4]:
        raise UnknownDOAPException()
    proj_adm_perms = [x for x in perms if x["additionalInformation"].endswith("ProjectAdmin")]
    proj_mem_perms = [x for x in perms if x["additionalInformation"].endswith("ProjectMember")]
    knwn_usr_perms = [x for x in perms if x["additionalInformation"].endswith("KnownUser")]
    unkn_usr_perms = [x for x in perms if x["additionalInformation"].endswith("UnknownUser")]
    if not (len(proj_adm_perms) == len(proj_mem_perms) == 1):
        raise UnknownDOAPException()
    if proj_adm_perms[0]["name"] != "CR" or proj_mem_perms[0]["name"] != "D":
        raise UnknownDOAPException()
    if len(knwn_usr_perms) == len(unkn_usr_perms) == 0:
        return "private"
    if not (len(knwn_usr_perms) == len(unkn_usr_perms) == 1):
        raise UnknownDOAPException()
    if knwn_usr_perms[0]["name"] != "V" or unkn_usr_perms[0]["name"] != "V":
        raise UnknownDOAPException()
    return "public"


def _parse_default_permissions_override(
    project_doaps: list[dict[str, Any]], prefixes: dict[str, str]
) -> dict[str, list[str]] | None:
    # these cases exist:
    # private for prop
    # private for class
    # limited view for http://api.knora.org/ontology/knora-api/v2#hasStillImageFileValue
    # limited view for http://api.knora.org/ontology/knora-api/v2#hasStillImageFileValue and a certain class

    prefixes_knora_base_inverted = _convert_prefixes(prefixes)
    doap_categories = _categorize_doaps(project_doaps)
    _validate_doap_categories(doap_categories)
    return _construct_override_object(doap_categories, prefixes_knora_base_inverted)


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


def _categorize_doaps(project_doaps: list[dict[str, Any]]) -> DoapCategories:
    class_doaps = []
    prop_doaps = []
    has_img_all_classes_doaps = []
    has_img_specific_class_doaps = []
    other_doaps = []
    for doap in project_doaps:
        match (doap.get("forResourceClass"), doap.get("forProperty")):
            case (for_class, None) if for_class is not None:
                class_doaps.append(doap)
            case (None, for_prop) if for_prop is not None and "hasStillImageFileValue" not in for_prop:
                prop_doaps.append(doap)
            case (None, for_prop) if "hasStillImageFileValue" in str(for_prop):
                has_img_all_classes_doaps.append(doap)
            case (for_class, for_prop) if for_class is not None and "hasStillImageFileValue" in str(for_prop):
                has_img_specific_class_doaps.append(doap)
            case _:
                other_doaps.append(doap)
    if other_doaps:
        raise UnknownDOAPException()
    return DoapCategories(
        class_doaps=class_doaps,
        prop_doaps=prop_doaps,
        has_img_all_classes_doaps=has_img_all_classes_doaps,
        has_img_specific_class_doaps=has_img_specific_class_doaps,
    )


def _validate_doap_categories(doap_categories: DoapCategories) -> None:
    for expected_private_doap in doap_categories.class_doaps + doap_categories.prop_doaps:
        perm = sorted(expected_private_doap["hasPermissions"], key=lambda x: x["name"])
        if len(perm) != 2:
            raise UnknownDOAPException()
        CR, D = perm
        if CR["name"] != "CR" or not CR["additionalInformation"].endswith("ProjectAdmin"):
            raise UnknownDOAPException()
        if D["name"] != "D" or not D["additionalInformation"].endswith("ProjectMember"):
            raise UnknownDOAPException()

    for expected_limited_view in (
        doap_categories.has_img_all_classes_doaps + doap_categories.has_img_specific_class_doaps
    ):
        perm = sorted(expected_limited_view["hasPermissions"], key=lambda x: x["name"])
        if len(perm) != 4:
            raise UnknownDOAPException()
        CR, D, RV1, RV2 = perm
        if CR["name"] != "CR" or not CR["additionalInformation"].endswith("ProjectAdmin"):
            raise UnknownDOAPException()
        if D["name"] != "D" or not D["additionalInformation"].endswith("ProjectMember"):
            raise UnknownDOAPException()
        if RV1["name"] != "RV" or not RV2["additionalInformation"].endswith("nownUser"):
            raise UnknownDOAPException()
        if RV2["name"] != "RV" or not RV2["additionalInformation"].endswith("nownUser"):
            raise UnknownDOAPException()


def _construct_override_object(
    doap_categories: DoapCategories, prefixes_knora_base_inverted: dict[str, str]
) -> dict[str, list[str]]:
    privates: list[str] = []
    for class_doap in doap_categories.class_doaps:
        privates.append(_shorten_iri(class_doap["forResourceClass"], prefixes_knora_base_inverted))
    for prop_doap in doap_categories.prop_doaps:
        privates.append(_shorten_iri(prop_doap["forProperty"], prefixes_knora_base_inverted))

    limited_views: list[str] = []
    if len(doap_categories.has_img_all_classes_doaps) > 1:
        raise UnknownDOAPException()
    if len(doap_categories.has_img_all_classes_doaps) == 1 and len(doap_categories.has_img_specific_class_doaps) > 0:
        raise UnknownDOAPException()
    if len(doap_categories.has_img_all_classes_doaps) == 1:
        limited_views.append("all")
    for img_doap in doap_categories.has_img_specific_class_doaps:
        limited_views.append(_shorten_iri(img_doap["forResourceClass"], prefixes_knora_base_inverted))

    result: dict[str, list[str]] = {}
    if privates:
        result["private"] = privates
    if limited_views:
        result["limited_view"] = limited_views
    return result


def _shorten_iri(full_iri: str, prefixes_inverted: dict[str, str]) -> str:
    before_hashtag, after_hashtag = full_iri.rsplit("#", maxsplit=1)
    prefix = prefixes_inverted[before_hashtag]
    return f"{prefix}:{after_hashtag}"
