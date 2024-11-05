from enum import Enum
from enum import auto


class Permissions(Enum):
    """
    Options of permissions for resources and values:

    - `PROJECT_SPECIFIC_PERMISSIONS`: the permissions defined for the project will be applied
    - `OPEN`: the resource or value is openly accessible
    - `RESTRICTED`: the resource of value is only accessible for project members
    - `RESTRICTED_VIEW`: the image file has a restricted view
    """

    PROJECT_SPECIFIC_PERMISSIONS = ""
    OPEN = "open"
    RESTRICTED = "restricted"
    RESTRICTED_VIEW = "restricted-view"


class NewlineReplacement(Enum):
    """
    Options to replace '\\n' with XML formatting

    - `NONE`: The text is returned without changes
    - `PARAGRAPH`: Replaces `Start Text\\nEnd Text` with `<p>Start Text</p><p>End Text</p>`
    - `LINEBREAK`: Replaces `Start Text\\nEnd Text` with `Start Text<br/>End Text`
    """

    NONE = auto()
    PARAGRAPH = auto()
    LINEBREAK = auto()
