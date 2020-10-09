from typing import List, Set, Dict, Tuple, Optional, Any, Union

from .helpers import Actions, BaseError
from .connection import Connection

class Model:
    _con: Connection
    _changed: Set[str]

    def __init__(self, con: Connection):
        if not isinstance(con, Connection):
            raise BaseError('"con"-parameter must be an instance of Connection')
        self._con = con
        self._changed = set()

    def has_changed(self) -> bool:
        if self._changed:
            return True
        else:
            return False
