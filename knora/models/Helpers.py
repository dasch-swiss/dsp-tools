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

class LangString:
    langstrs: Dict[Languages,str]

    def __init__(self,
                 initvalue: Optional[Dict[Languages,str]] = None):
        if initvalue is not None:
            self.langstrs = initvalue
        else:
            self.langstrs = {}

    def __getitem__(self, key: Union[Languages,str]):
        if isinstance(key, Enum):
            if self.langstrs.get(key) is None:
                for l in self.langstrs:
                    return self.langstrs[l]
                return  None
            else:
                return self.langstrs[key]
        else:
            lmap = dict(map(lambda a: (a.value, a), Languages))
            if lmap.get(key) is None:
                raise BaseError('Invalid language string "' + key  + '"!')
            if self.langstrs.get(lmap[key]) is None:
                for l in self.langstrs:
                    return self.langstrs[l]
                return None
            else:
                return self.langstrs[lmap[key]]

    def __setitem__(self, key: Union[Languages,str], value: str):
        if isinstance(key, Languages):
            self.langstrs[key] = value
        else:
            lmap = dict(map(lambda a: (a.value, a), Languages))
            if lmap.get(key) is None:
                raise BaseError('Invalid language string "' + key  + '"!')
            self.langstrs[lmap[key]] = value

    def __delitem__(self, key: Union[Languages,str]):
        if isinstance(key, Languages):
            del self.langstrs[key]
        else:
            lmap = dict(map(lambda a: (a.value, a), Languages))
            if lmap.get(key) is None:
                raise BaseError('Invalid language string "' + key  + '"!')
            del self.langstrs[lmap[key]]

    def __str__(self):
        tmpstr = '{'
        for p in self.langstrs:
            tmpstr += '=' + p.value + ':' + self.langstrs[p]
        tmpstr += '}'
        return tmpstr

    def items(self):
        return self.langstrs.items()

    def isEmpty(self):
        return not bool(self.langstrs)

    def toJsonObj(self):
        return list(map(lambda a: { 'language': a[0].value, 'value': a[1]}, self.langstrs.items()))


