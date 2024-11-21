from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.models.exceptions import PermissionNotExistsError


def resolve_permission(permissions: str | None, permissions_lookup: dict[str, Permissions]) -> str | None:
    """Resolve the permission into a string that can be sent to the API."""
    if permissions:
        if not (per := permissions_lookup.get(permissions)):
            raise PermissionNotExistsError(f"Could not find permissions for value: {permissions}")
        return str(per)
    return None
