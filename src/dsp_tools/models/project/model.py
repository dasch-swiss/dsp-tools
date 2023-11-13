from dsp_tools.connection.connection import Connection


class Model:  # pylint: disable=too-few-public-methods
    """Base class for other classes"""

    _con: Connection
    _changed: set[str]

    def __init__(self, con: Connection):
        self._con = con
        self._changed = set()
