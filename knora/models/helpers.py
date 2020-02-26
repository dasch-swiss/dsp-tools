from typing import List, Set, Dict, Tuple, Optional, Any, Union
from enum import Enum, unique

from pprint import pprint

class BaseError(Exception):
    message: str

    def __init__(self, message: str):
        super().__init__()
        self.message = message

@unique
class Languages(Enum):
    EN = 'en'
    DE = 'de'
    FR = 'fr'
    IT = 'it'


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

LangStringParam = Optional[Union[Dict[Union[Languages, str], str], str]]

class LangString:
    """
    This class holds a typical language-string pair as it is often used in JSON-LD as
    ```
    "some:thing" = [{
      '@language': 'xx',
      '@value': 'a string in language xx'
    },{…},…]
    ```

    or a simple string without language:
    ```
    "some:thing": "a string without language specificer"
    ```
    """
    _langstrs: Dict[Languages, str]
    _simplestring: str

    def __init__(self, initvalue: LangStringParam = None):

        def mymapper(p: Tuple[Union[Languages, str], str]) -> Tuple[Languages, str]:
            lmap = dict(map(lambda a: (a.value, a), Languages))
            if isinstance(p[0], str) and p[0] in lmap:
                lang = lmap[a[0].lower()]
            elif isinstance(p[0], Languages):
                lang = p[0]
            else:
                raise BaseError("No a valid language definition!")
            return lang, p[1]

        if initvalue is None:
            self._simplestring = None
            self._langstrs = {}
        elif isinstance(initvalue, str):
            self._simplestring = str
            self._langstrs = {}
        elif isinstance(initvalue, dict):
            self._simplestring = None
            self._langstrs = dict(map(mymapper, initvalue.items()))
        elif isinstance(initvalue, LangString):
            self._simplestring = None
            self._langstrs = dict(map(mymapper, initvalue.items()))
        else:
            raise BaseError("No a valid language definition!")

    def __getitem__(self, key: Optional[Union[Languages, str]] = None) -> str:
        #
        # First deal with simple strings (no language given). We return, if exsiting, the simple string
        # or just the first language dependent string
        #
        if key is None:
            if self._simplestring is not None:
                return self._simplestring
            else:
                try:
                    return list(self._langstrs)[0]
                except:
                    return None
        else:
            self._simplestring = None  # Let's delete the string without language if there is one...
        if isinstance(key, Enum):
            if self._langstrs.get(key) is None:
                for l in self._langstrs:
                    return self._langstrs[l]
                return  None
            else:
                return self._langstrs[key]
        else:
            lmap = dict(map(lambda a: (a.value, a), Languages))
            if lmap.get(key.lower()) is None:
                raise BaseError('Invalid language string "' + key + '"!')
            if self._langstrs.get(lmap[key.lower()]) is None:
                for l in self._langstrs:
                    return self._langstrs[l]
                return None
            else:
                return self._langstrs[lmap[key.lower()]]

    def __setitem__(self, key: Optional[Union[Languages, str]], value: str):
        if key is None:
            self._simplestring = value
            self._langstrs = {}  # Delete language dependent string! Needs Caution!!!
            return
        if isinstance(key, Languages):
            self._langstrs[key] = value
        else:
            lmap = dict(map(lambda a: (a.value, a), Languages))
            if lmap.get(key.lower()) is None:
                raise BaseError('Invalid language string "' + key  + '"!')
            self._langstrs[lmap[key.lower()]] = value

    def __delitem__(self, key: Union[Languages, str]):
        if isinstance(key, Languages):
            del self._langstrs[key]
        else:
            lmap = dict(map(lambda a: (a.value, a), Languages))
            if lmap.get(key.lower()) is None:
                raise BaseError('Invalid language string "' + key  + '"!')
            del self._langstrs[lmap[key.lower()]]

    def __str__(self):
        tmpstr = '{'
        for p in self._langstrs:
            tmpstr += '=' + p.value + ':' + self._langstrs[p]
        tmpstr += '}'
        return tmpstr

    def items(self):
        return self._langstrs.items()

    def isEmpty(self):
        return not (bool(self._langstrs) or bool(self._simplestring))

    def empty(self):
        self._simplestring = None
        self._langstrs = {}


    def toJsonObj(self):
        if self.isEmpty():
            return None
        if self._simplestring is not None:
            return self._simplestring
        else:
            return list(map(lambda a: {'language': a[0].value, 'value': a[1]}, self._langstrs.items()))

    def toJsonLdObj(self):
        if self.isEmpty():
            return None
        if self._simplestring is not None:
            return self._simplestring
        else:
            return list(map(lambda a: {'@language': a[0].value, '@value': a[1]}, self._langstrs.items()))

    @classmethod
    def fromJsonLdObj(cls, obj: Union[List[Dict[str, str]], str]) -> 'LangString':
        if isinstance(obj, str) or obj is None:
            return cls(obj)
        if isinstance(obj, list):
            objs = obj
        else:
            objs = [obj]
        lstrs: Dict[Languages, str] = {}
        for o in objs:
            lang = o.get('@language')
            if lang == 'en':
                lstrs[Languages.EN] = o.get('@value')
            elif lang == 'de':
                lstrs[Languages.DE] = o.get('@value')
            elif lang == 'fr':
                lstrs[Languages.FR] = o.get('@value')
            elif lang == 'it':
                lstrs[Languages.IT] = o.get('@value')
        return cls(lstrs)

    @classmethod
    def fromJsonObj(cls, obj: Optional[Any]) -> 'LangString':
        if isinstance(obj, str) or obj is None:
            return cls(obj)
        if isinstance(obj, list):
            objs = obj
        else:
            objs = [obj]
        lstrs: Dict[Languages, str] = {}
        for o in objs:
            lang = o.get('language')
            if lang == 'en':
                lstrs[Languages.EN] = o.get('value')
            elif lang == 'de':
                lstrs[Languages.DE] = o.get('value')
            elif lang == 'fr':
                lstrs[Languages.FR] = o.get('value')
            elif lang == 'it':
                lstrs[Languages.IT] = o.get('value')
        return cls(lstrs)

    def print(self, offset: Optional[int] = None):
        blank = ' '
        print(f'{blank:>{offset}}LangString:')
        if self._simplestring is not None:
            print(f'{blank:>{offset + 2}}{self._simplestring}')
        else:
            for p in self._langstrs.items():
                print(f'{blank:>{offset + 2}}{p[0]} : {p[1]}')

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

