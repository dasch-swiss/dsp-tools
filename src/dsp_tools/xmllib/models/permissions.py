from __future__ import annotations

from enum import Enum


class Permissions(Enum):
    """
    Options of permissions for resources and values:

    - `PROJECT_SPECIFIC_PERMISSIONS`: the permissions defined on project level will be applied
    - `PUBLIC`: the resource/value is visible for everyone
    - `PRIVATE`: the resource/value is only visible for project members
    - `LIMITED_VIEW`: the resource/value is visible for everyone,
      but images are blurred/watermarked for non-project members

    Deprecated terms:

    - `OPEN`: use `PUBLIC` instead
    - `RESTRICTED`: use `PRIVATE` instead
    - `RESTRICTED_VIEW`: use `LIMITED_VIEW` instead

    Examples:
        ```python
        resource = xmllib.Resource.create_new(
            res_id="ID",
            restype=":ResourceType",
            label="label",
            permissions=xmllib.Permissions.PRIVATE,
        )
        ```
    """

    PROJECT_SPECIFIC_PERMISSIONS = ""
    PUBLIC = "public"
    PRIVATE = "private"
    LIMITED_VIEW = "limited_view"

    # Deprecated terminology
    OPEN = "open"
    RESTRICTED = "restricted"
    RESTRICTED_VIEW = "restricted-view"
