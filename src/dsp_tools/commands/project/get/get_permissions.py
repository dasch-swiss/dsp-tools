from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.commands.project.models.permissions_client import PermissionsClient


def _get_default_permissions(auth: AuthenticationClientLive, project_iri: str) -> str:
    perm_client = PermissionsClient(auth, project_iri)
    project_doaps = perm_client.get_project_doaps()
    result = _parse_default_permissions(project_doaps)
    if result == "unknown":
        return (
            "We cannot determine if this project is public or private. "
            "The DSP-TOOLS devs can assist you in analysing the existing DOAPs, "
            "and help you deciding if the original intent was rather public or rather private."
        )
    return result


def _parse_default_permissions(project_doaps: list[dict[str, Any]]) -> str:  # noqa: PLR0911 (too many return statements)
    """If the DOAPs exactly match our definition of public/private, return public/private. Otherwise, return unknown."""
    unsupported_groups = ("SystemAdmin", "ProjectAdmin", "Creator", "KnownUser", "UnknownUser")
    if [x for x in project_doaps if x.get("forGroup", "").endswith(unsupported_groups)]:
        return "unknown"
    proj_member_doaps = [x for x in project_doaps if x["forGroup"].endswith("ProjectMember")]
    if len(proj_member_doaps) != 1:
        return "unknown"
    perms = proj_member_doaps[0]["hasPermissions"]
    if len(perms) not in [2, 4]:
        return "unknown"
    proj_adm_perms = [x for x in perms if x["additionalInformation"].endswith("ProjectAdmin")]
    proj_mem_perms = [x for x in perms if x["additionalInformation"].endswith("ProjectMember")]
    knwn_usr_perms = [x for x in perms if x["additionalInformation"].endswith("KnownUser")]
    unkn_usr_perms = [x for x in perms if x["additionalInformation"].endswith("UnknownUser")]
    if not (len(proj_adm_perms) == len(proj_mem_perms) == 1):
        return "unknown"
    if proj_adm_perms[0]["name"] != "CR" or proj_mem_perms[0]["name"] != "D":
        return "unknown"
    if len(knwn_usr_perms) == len(unkn_usr_perms) == 0:
        return "private"
    if not (len(knwn_usr_perms) == len(unkn_usr_perms) == 1):
        return "unknown"
    if knwn_usr_perms[0]["name"] != "V" or unkn_usr_perms[0]["name"] != "V":
        return "unknown"
    return "public"
