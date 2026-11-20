from enum import Enum
from enum import unique
from typing import Any
from typing import Optional
from typing import Union

from dsp_tools.error.exceptions import BaseError


@unique
class Languages(Enum):
    """Languages supported by DSP"""

    EN = "en"
    DE = "de"
    FR = "fr"
    IT = "it"
    RM = "rm"


LangStringParam = Optional[Union[dict[Union[Languages, str], str], str]]


class LangStringIterator:
    """Iterator class for LangString class."""

    _langstring: "LangString"
    _index: int

    def __init__(self, langstring: "LangString"):
        self._langstring = langstring
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

    _langstrs: dict[Languages, str]
    _simplestring: str

    def __init__(self, initvalue: LangStringParam = None):
        def mymapper(p: tuple[Union[Languages, str], str]) -> tuple[Languages, str]:
            lmap = dict(map(lambda a: (a.value, a), Languages))
            if isinstance(p[0], str) and p[0] in lmap:
                lang = lmap[p[0].lower()]
            elif isinstance(p[0], Languages):
                lang = p[0]
            else:
                raise BaseError("Not a valid language definition!")
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
            raise BaseError("Not a valid language definition!")

    def __getitem__(self, key: Optional[Union[Languages, str]] = None) -> Optional[str]:
        match key:
            case None:
                return self.__getitem_nokey__()
            case Enum() if ls := self._langstrs.get(key):
                return ls
            case Enum():
                return self.__getitem_fallback__()
            case str():
                lmap = {a.value: a for a in Languages}
                lkey = lmap.get(key.lower())
                if lkey is None:
                    raise BaseError(f"Invalid language string '{key}'")
                if ls := self._langstrs.get(lkey):
                    return ls
                return self.__getitem_fallback__()

    def __getitem_nokey__(self) -> Optional[str]:
        if self._simplestring:
            return self._simplestring
        elif self._langstrs:
            return next(iter(self._langstrs)).value
        else:
            return None

    def __getitem_fallback__(self) -> Optional[str]:
        for lst in self._langstrs:
            if self._langstrs.get(lst) is not None:
                return self._langstrs[lst]
        if self._simplestring is not None:
            return self._simplestring
        return None

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
                raise BaseError('Invalid language string "' + key + '"!')
            self._langstrs[lmap[key.lower()]] = value

    def __delitem__(self, key: Union[Languages, str]):
        if isinstance(key, Languages):
            del self._langstrs[key]
        else:
            lmap = dict(map(lambda a: (a.value, a), Languages))
            if lmap.get(key.lower()) is None:
                raise BaseError('Invalid language string "' + key + '"!')
            del self._langstrs[lmap[key.lower()]]

    def __str__(self):
        tmpstr = "{"
        for p in self._langstrs:
            tmpstr += "=" + p.value + ":" + self._langstrs[p]
        tmpstr += "}"
        return tmpstr

    def __iter__(self):
        return LangStringIterator(self)

    def __eq__(self, other: "LangString"):
        equal = self._simplestring == other._simplestring
        if equal:
            for lang in Languages:
                equal = self._langstrs.get(lang) == other._langstrs.get(lang)
                if not equal:
                    break
        return equal

    def items(self):
        return self._langstrs.items()

    def isEmpty(self) -> bool:
        return not (bool(self._langstrs) or bool(self._simplestring))

    def empty(self) -> None:
        self._simplestring = None
        self._langstrs = {}

    def toJsonObj(self) -> Optional[Union[str, list[dict[str, str]]]]:
        if self.isEmpty():
            return None
        if self._simplestring is not None:
            return self._simplestring
        else:
            return list(map(lambda a: {"language": a[0].value, "value": a[1] if a[1] else "-"}, self._langstrs.items()))

    def toJsonLdObj(self) -> Optional[Union[str, list[dict[str, str]]]]:
        if self.isEmpty():
            return None
        if self._simplestring is not None:
            return self._simplestring
        else:
            return [{"@language": a[0].value, "@value": a[1]} for a in self._langstrs.items()]
            # return list(map(lambda a: {'@language': a[0].value, '@value': a[1]}, self._langstrs.items()))

    @classmethod
    def fromJsonLdObj(cls, obj: Optional[Union[list[dict[str, str]], str]]) -> "LangString":
        if obj is None:
            return None
        if isinstance(obj, str):
            return cls(obj)
        if isinstance(obj, list):
            objs = obj
        else:
            objs = [obj]
        lstrs: dict[Languages, str] = {}
        for o in objs:
            lang = o.get("@language")
            if lang == "en":
                lstrs[Languages.EN] = o.get("@value")
            elif lang == "de":
                lstrs[Languages.DE] = o.get("@value")
            elif lang == "fr":
                lstrs[Languages.FR] = o.get("@value")
            elif lang == "it":
                lstrs[Languages.IT] = o.get("@value")
            elif lang == "rm":
                lstrs[Languages.RM] = o.get("@value")
            elif o.get("@value") is not None:
                return cls(o.get("@value"))
        return cls(lstrs)

    @classmethod
    def fromJsonObj(cls, obj: Optional[Any]) -> "LangString":
        if obj is None:
            return None
        if isinstance(obj, str):
            return cls(obj)
        if isinstance(obj, list):
            objs = obj
        else:
            objs = [obj]
        lstrs: dict[Languages, str] = {}
        for o in objs:
            lang = o.get("language")
            if lang == "en":
                lstrs[Languages.EN] = o.get("value")
            elif lang == "de":
                lstrs[Languages.DE] = o.get("value")
            elif lang == "fr":
                lstrs[Languages.FR] = o.get("value")
            elif lang == "it":
                lstrs[Languages.IT] = o.get("value")
            elif lang == "rm":
                lstrs[Languages.RM] = o.get("value")
            elif o.get("value") is not None:
                return cls(o.get("value"))
        return cls(lstrs)

    def createDefinitionFileObj(self) -> Union[str, dict[str, str]]:
        if self._simplestring:
            return self._simplestring
        langstring = {}
        for p in self.items():
            langstring[p[0].value] = p[1]
        return langstring
