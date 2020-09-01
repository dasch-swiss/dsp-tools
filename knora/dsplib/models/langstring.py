from typing import List, Set, Dict, Tuple, Optional, Any, Union
from enum import Enum, unique

from ..models.helpers import BaseError


@unique
class Languages(Enum):
    EN = 'en'
    DE = 'de'
    FR = 'fr'
    IT = 'it'

LangStringParam = Optional[Union[Dict[Union[Languages, str], str], str]]


class LangStringIterator:
    """Iterator class for LangString class."""

    _langstring: 'LangString'
    _index: int

    def __init__(self, langstring: 'LangString'):
        self._langstring = langstring;
        self._langlist = list(map(lambda a: a[0], self._langstring.items()))
        self._index = 0

    def __next__(self):
        if len(self._langlist) == 0 and self._index == 0:
            return None, self._langstring[None]
        elif self._index < len(self._langlist):
            tmp = self._langlist[self._index]
            self._index += 1
            return tmp, self._langstring[tmp]
        else:
            raise StopIteration


class LangString:
    """
    This class holds a typical language-string pair as it is often used in JSON-LD as
    ```
    "some:thing" = [{
      '@language': 'xx',
      '@value': 'a string in language xx'
    },
    {…},…]
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
                lang = lmap[p[0].lower()]
            elif isinstance(p[0], Languages):
                lang = p[0]
            else:
                raise BaseError("No a valid language definition!")
            return lang, p[1]

        if initvalue is None:
            self._simplestring = None
            self._langstrs = {}
        elif isinstance(initvalue, str):
            self._simplestring = initvalue
            self._langstrs = {}
        elif isinstance(initvalue, dict):
            self._simplestring = None
            self._langstrs = dict(map(mymapper, initvalue.items()))
        elif isinstance(initvalue, LangString):
            self._simplestring = initvalue._simplestring
            self._langstrs = initvalue._langstrs
        else:
            raise BaseError("No a valid language definition!")

    def __getitem__(self, key: Optional[Union[Languages, str]] = None) -> str:
        #
        # First deal with simple strings (no language given). We return, if existing, the simple string
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
            pass
            # self._simplestring = None  # Let's delete the string without language if there is one...
        if isinstance(key, Enum):
            if self._langstrs.get(key) is None:
                for l in self._langstrs:
                    if self._langstrs.get(l) is not None:
                        return self._langstrs[l]
                if self._simplestring is not None:
                    return self._simplestring
                return None
            else:
                return self._langstrs[key]
        else:
            lmap = dict(map(lambda a: (a.value, a), Languages))
            if lmap.get(key.lower()) is None:
                raise BaseError('Invalid language string "' + key + '"!')
            if self._langstrs.get(lmap[key.lower()]) is None:
                for l in self._langstrs:
                    if self._langstrs.get(l) is not None:
                        return self._langstrs[l]
                if self._simplestring is not None:
                    return self._simplestring
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

    def __iter__(self):
        return LangStringIterator(self)

    def __eq__(self, other: 'LangString'):
        equal = self._simplestring == other._simplestring
        if equal:
            for lang in Languages:
                equal = self._langstrs.get(lang) == other._langstrs.get(lang)
                if not equal:
                    break
        return equal


    def get_by_lang(self, key: Optional[Union[Languages, str]] = None) -> Optional[str]:
        if key is None:
            return self._simplestring
        else:
            if isinstance(key, Enum):
                return self._langstrs.get(key)
            else:
                lmap = dict(map(lambda a: (a.value, a), Languages))
                if lmap.get(key.lower()) is None:
                    raise BaseError('Invalid language string "' + key + '"!')
                return self._langstrs.get(lmap[key.lower()])

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
    def fromJsonLdObj(cls, obj: Optional[Union[List[Dict[str, str]], str]]) -> 'LangString':
        if obj is None:
            return None
        if isinstance(obj, str):
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
            else:
                if o.get('@value') is not None:
                    return cls(o.get('@value'))
        return cls(lstrs)

    @classmethod
    def fromJsonObj(cls, obj: Optional[Any]) -> 'LangString':
        if obj is None:
            return None
        if isinstance(obj, str):
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
            else:
                if o.get('value') is not None:
                    return cls(o.get('value'))
        return cls(lstrs)

    def print(self, offset: Optional[int] = None):
        blank = ' '
        #print(f'{blank:>{offset}}LangString:')
        if self._simplestring is not None:
            print(f'{blank:>{offset + 2}}{self._simplestring}')
        else:
            for p in self._langstrs.items():
                print(f'{blank:>{offset + 2}}{p[0]} : {p[1]}')

    @property
    def langstrs(self):
        return self._langstrs

    def createDefinitionFileObj(self) -> Union[str, Dict[str, str]]:
        if self._simplestring is not None:
            return self._simplestring
        langstring = {}
        for p in self.items():
            langstring[p[0].value] = p[1]
        return langstring
