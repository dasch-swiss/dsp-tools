from dsp_tools.clients.connection import Connection


class Model:
    """Base class for other classes"""

    _con: Connection
    _changed: set[str]

    def __init__(self, con: Connection):
        self._con = con
        self._changed = set()
