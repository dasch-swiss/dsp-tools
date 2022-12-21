class XmlError(Exception):
    """Represents an error raised in the context of the XML import"""
    _message: str

    def __init__(self, msg: str):
        self._message = msg

    def __str__(self) -> str:
        return 'XML-ERROR: ' + self._message
