from enum import Enum
from enum import auto


class Permissions(Enum):
    """
    _summary_
    """
    PROJECT_SPECIFIC_PERMISSIONS = ""
    OPEN = "open"
    RESTRICTED = "restricted"
    RESTRICTED_VIEW = "restricted-view"


class NewlineReplacement(Enum):
    """
    _summary_
    """
    NONE = auto()
    PARAGRAPH = auto()
    LINEBREAK = auto()
