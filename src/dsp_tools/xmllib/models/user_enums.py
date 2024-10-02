from enum import Enum
from enum import auto


class Permissions(Enum):
    open = auto()
    restricted = auto()
    restricted_view = auto()
