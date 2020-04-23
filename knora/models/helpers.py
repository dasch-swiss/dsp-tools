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
            self._context = dict(map(lambda x: (x[0], x[1].strip()), context.items()))
            if "salsah-gui" not in self._context:
                self._context["salsah-gui"] = "http://api.knora.org/ontology/salsah-gui/v2#"
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
        if iri[-1] != '#':
            iri = iri + '#'
        self._context[prefix] = iri
        self._rcontext[iri] = prefix

    def iriFromPrefix(self, prefix: str) -> Optional[str]:
        if self._context.get(prefix) is not None:
            return self._context.get(prefix)[:-1]
        else:
            return None

    def prefixFromIri(self, iri: str) -> Optional[str]:
        if iri[-1] != '#':
            iri = iri + '#'
        return self._rcontext.get(iri)

    def getQualifiedIri(self, val: Optional[str]) -> Optional[str]:
        if val is None:
            return None
        tmp = val.split('#')
        if len(tmp) > 1:
            return val
        else:
            return self.iriFromPrefix(tmp[0]) + '#' + tmp[1]

    def getPrefixIri(self, val: Optional[str]) -> Optional[str]:
        if val is None:
            return None
        tmp = val.split('#')
        if len(tmp) > 1:
            return self.prefixFromIri(tmp[0]) + ':' + tmp[1]
        else:
            return val

    def toJsonObj(self) -> Dict[str, str]:
        return self._context

    def print(self):
        for a in self._context.items():
            print(a[0] + ': "' + a[1] + '"')


class LastModificationDate:
    _last_modification_date: str;

    def __init__(self, val: Any):
        if isinstance(val, str):
            self._last_modification_date = val;
        elif isinstance(val, LastModificationDate):
            self._last_modification_date = str(val)
        else:
            if val.get("@type") is not None and val.get("@type") == "xsd:dateTimeStamp":
                self._last_modification_date = val["@value"]
            else:
                raise BaseError("Invalid LastModificationDate")

    def __eq__(self, other: Union[str, 'LastModificationDate']) -> bool:
        if isinstance(other, str):
            other = LastModificationDate(other)
        return self._last_modification_date == other._last_modification_date

    def __lt__(self, other: 'LastModificationDate') -> bool:
        if isinstance(other, str):
            other = LastModificationDate(other)
        return self._last_modification_date < other._last_modification_date

    def __le__(self, other: 'LastModificationDate') -> bool:
        if isinstance(other, str):
            other = LastModificationDate(other)
        return self._last_modification_date <= other._last_modification_date

    def __gt__(self, other: 'LastModificationDate') -> bool:
        if isinstance(other, str):
            other = LastModificationDate(other)
        return self._last_modification_date > other._last_modification_date

    def __ge__(self, other: 'LastModificationDate') -> bool:
        if isinstance(other, str):
            other = LastModificationDate(other)
        return self._last_modification_date >= other._last_modification_date

    def __ne__(self, other: 'LastModificationDate') -> bool:
        if isinstance(other, str):
            other = LastModificationDate(other)
        return self._last_modification_date != other._last_modification_date

    def __str__(self: 'LastModificationDate') -> Union[None, str]:
        return self._last_modification_date

    def toJsonObj(self):
        return {
            "@type": "xsd:dateTimeStamp",
            "@value": self._last_modification_date
        }


class WithId:
    _tmp: str = None

    def __init__(self, obj: Optional[Dict[str, str]]):
        if obj is None:
            return
        self._tmp = obj.get('@id')

    def str(self) -> Optional[str]:
        return self._tmp
