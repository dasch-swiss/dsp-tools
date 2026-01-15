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

    def items(self):
        return self._langstrs.items()

    def isEmpty(self) -> bool:
        return not (bool(self._langstrs) or bool(self._simplestring))

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
