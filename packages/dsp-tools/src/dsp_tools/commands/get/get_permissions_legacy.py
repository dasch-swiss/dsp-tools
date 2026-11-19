from typing import Any
from typing import Literal


def parse_legacy_doaps(project_doaps: list[dict[str, Any]]) -> Literal["public", "private"] | None:
    """
    Check if DOAPs match one of the legacy patterns.

    Legacy private:
    - For group ProjectAdmin: ProjectAdmin CR, ProjectMember CR/M
    - For group ProjectMember: ProjectAdmin CR, ProjectMember CR/M

    Legacy public:
    - For group ProjectAdmin: ProjectAdmin CR, (optionally: Creator CR), ProjectMember D/M, KnownUser V, UnknownUser V
    - For group ProjectMember: ProjectAdmin CR, (optionally: Creator CR), ProjectMember D/M, KnownUser V, UnknownUser V
    """
    if len(project_doaps) != 2:
        return None
    admin_doaps = [x for x in project_doaps if x.get("forGroup", "").endswith("ProjectAdmin")]
    member_doaps = [x for x in project_doaps if x.get("forGroup", "").endswith("ProjectMember")]
    if len(admin_doaps) != 1 or len(member_doaps) != 1:
        return None

    admin_perms = admin_doaps[0]["hasPermissions"]
    member_perms = member_doaps[0]["hasPermissions"]
    if all([_is_legacy_private(admin_perms), _is_legacy_private(member_perms)]):
        return "private"
    if all([_is_legacy_public(admin_perms), _is_legacy_public(member_perms)]):
        return "public"

    return None


def _is_legacy_private(perms: list[dict[str, Any]]) -> bool:
    """
    Check if permissions match the legacy private pattern: ProjectAdmin CR, ProjectMember M/D

    Args:
        perms: List of permission objects
    """
    if len(perms) != 2:
        return False

    sorted_perms = sorted(perms, key=lambda x: x.get("name", ""))

    # First should be CR for ProjectAdmin
    if sorted_perms[0]["name"] != "CR" or not sorted_perms[0]["additionalInformation"].endswith("ProjectAdmin"):
        return False

    # Second should be D or M for ProjectMember
    if sorted_perms[1]["name"] not in ["D", "M"] or not sorted_perms[1]["additionalInformation"].endswith(
        "ProjectMember"
    ):
        return False

    return True


def _is_legacy_public(perms: list[dict[str, Any]]) -> bool:
    """
    Check if permissions match the public pattern:
    ProjectAdmin CR, (optionally: Creator CR), ProjectMember D/M, KnownUser V, UnknownUser V
    """
    # Should have exactly 4 permissions after filtering out Creator
    filtered_perms = [p for p in perms if not p["additionalInformation"].endswith("Creator")]
    if len(filtered_perms) != 4:
        return False

    sorted_perms = sorted(filtered_perms, key=lambda x: x.get("name", ""))

    # First should be CR for ProjectAdmin
    if sorted_perms[0]["name"] != "CR" or not sorted_perms[0]["additionalInformation"].endswith("ProjectAdmin"):
        return False

    # Second should be D or M for ProjectMember
    if sorted_perms[1]["name"] not in ["D", "M"] or not sorted_perms[1]["additionalInformation"].endswith(
        "ProjectMember"
    ):
        return False

    # Third/Fourth should be V for KnownUser
    if sorted_perms[2]["name"] != "V" or not sorted_perms[2]["additionalInformation"].endswith("nownUser"):
        return False

    # Third/Fourth should be V for UnknownUser
    if sorted_perms[3]["name"] != "V" or not sorted_perms[3]["additionalInformation"].endswith("nownUser"):
        return False

    return True
