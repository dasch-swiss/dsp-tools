from dsp_tools.models.connection import Connection
from dsp_tools.models.exceptions import BaseError


class Model:
    _con: Connection
    _changed: set[str]

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
