from enum import Enum
from enum import auto


class Permissions(Enum):
    PROJECT_SPECIFIC_PERMISSIONS = ""
    OPEN = "open"
    RESTRICTED = "restricted"
    RESTRICTED_VIEW = "restricted-view"


class NewlineReplacement(Enum):
    NONE = auto()
    PARAGRAPH = auto()
    LINEBREAK = auto()
