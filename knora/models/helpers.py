from typing import List, Set, Dict, Tuple, Optional, Any, Union
from enum import Enum, unique

from pprint import pprint

class BaseError(Exception):
    message: str

    def __init__(self, message: str):
        super().__init__()
        self.message = message


class Actions(Enum):
    Create = 1
    Read = 2
    Update = 3
    Delete = 4

@unique
class Cardinality(Enum):
    C_1 = "1",
    C_0_1 = "0-1",
    C_1_n = "1-n",
    C_0_n = "0-n"


class Context:
    _context: Dict[str, str]
    _rcontext: Dict[str, str]

    def __init__(self, context: Optional[Dict[str, str]] = None):
        if context is not None:
            self._context = context
        else:
            self._context = {
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "owl": "http://www.w3.org/2002/07/owl#",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
                "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
                "salsah-gui": "http://api.knora.org/ontology/salsah-gui/v2#"
            }
        self._rcontext = dict(map(lambda x: (x[1], x[0]), self._context.items()))

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, value: Dict[str, str]):
        if value is not None and isinstance(value, dict):
            self._context = value

    def addContext(self, prefix: str, iri: str):
        self._context[prefix] = iri
        self._rcontext[iri] = prefix

    def iriFromPrefix(self, prefix: str) -> Optional[str]:
        return self._context.get(prefix)

    def prefixFromIri(self, iri: str) -> Optional[str]:
        return self._rcontext.get(iri)

    def toJsonObj(self) -> Dict[str, str]:
        return self._context

