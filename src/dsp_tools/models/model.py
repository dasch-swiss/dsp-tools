from dsp_tools.models.connection import Connection
from dsp_tools.models.exceptions import BaseError


class Model:  # pylint: disable=too-few-public-methods
    """Base class for other classes"""

    _con: Connection
    _changed: set[str]

    def __init__(self, con: Connection):
        if not isinstance(con, Connection):
            raise BaseError('"con"-parameter must be an instance of Connection')
        self._con = con
        self._changed = set()
