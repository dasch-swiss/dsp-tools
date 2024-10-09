from enum import Enum
from enum import auto


class Permissions(Enum):
    DOAP = ""
    OPEN = "open"
    RESTRICTED = "restricted"
    RESTRICTED_VIEW = "restricted-view"


class NewlineReplacement(Enum):
    NONE = auto()
    PARAGRAPH = auto()
    LINEBREAK = auto()
