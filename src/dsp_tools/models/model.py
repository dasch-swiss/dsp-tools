from dsp_tools.models.connection_live import ConnectionLive
from dsp_tools.models.exceptions import BaseError


class Model:  # pylint: disable=too-few-public-methods
    """Base class for other classes"""

    _con: ConnectionLive
    _changed: set[str]

    def __init__(self, con: ConnectionLive):
        if not isinstance(con, ConnectionLive):
            raise BaseError('"con"-parameter must be an instance of Connection')
        self._con = con
        self._changed = set()
