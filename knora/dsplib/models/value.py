import json
import re
from pystrict import strict
from typing import List, Set, Dict, Tuple, Optional, Any, Union, Type

from .helpers import Actions, BaseError, Cardinality
from .langstring import LangString

from .listnode import ListNode


@strict
class KnoraStandoffXml:
    """Used to handle XML strings for standoff markup"""

    __iriregexp = re.compile(r'IRI:[^:]*:IRI')
    __xmlstr: str

    def __init__(self, xmlstr: str):
        self.__xmlstr = xmlstr

    def getXml(self):
        return self.__xmlstr

    def findall(self):
        return self.__iriregexp.findall(self.__xmlstr)

    def replace(self, fromStr: str, toStr: str):
        self.__xmlstr.replace(fromStr, toStr)


class KnoraStandoffXmlEncoder(json.JSONEncoder):
    """Classes used as wrapper for knora standoff-XML"""

    def default(self, obj):
        if isinstance(obj, KnoraStandoffXml):
            return obj.getXml()
        return json.JSONEncoder.default(self, obj)


@strict
class Value:
    _comment: Union[str, None]
    _permissions: Union[str, None]

    def __init__(self,
                 comment: Optional[LangString] = None,
                 permissions: Optional[str] = None):
        self._comment = comment
        self._permissions = permissions

    def toJsonLdObj(self, action: Actions) -> Dict[str, Any]:
        tmp = {}
        if action == Actions.Create:
            if self._permissions is not None:
                tmp["knora-api:hasPermissions"] = self._permissions

            if self._comment is not None:
                tmp["knora-api:valueHasComment"] = self._comment
            # jsonstr = json.dumps(self.__jsonld_obj, indent=3, separators=(',', ': '), cls=KnoraStandoffXmlEncoder)
            # return jsonstr
        else:
            pass
        return tmp


@strict
class TextValue(Value):
    _value: Union[str, KnoraStandoffXml]

    def __init__(self,
                 value: Union[str, KnoraStandoffXml],
                 comment: Optional[LangString] = None,
                 permissions: Optional[str] = None,
                 mapping: Optional[str] = None):
        super().__init__(comment, permissions)
        self._value = value

    def toJsonLdObj(self, action: Actions) -> Dict[str, Any]:
        tmp = super().toJsonLdObj(action)
        if action == Actions.Create:
            tmp['@type'] = 'knora-api:TextValue'
            if isinstance(self._value, KnoraStandoffXml):
                tmp['knora-api:textValueAsXml'] = self._value  # no conversion to string
                tmp['knora-api:textValueHasMapping'] = {
                    '@id': 'http://rdfh.ch/standoff/mappings/StandardMapping' if self._mapping is None else self._mapping
                }
            else:
                self.__jsonld_obj['knora-api:valueAsString'] = str(self._value)
        else:
            pass
        return tmp


@strict
class ColorValue(Value):
    _value: str

    def __init__(self,
                 value: str,
                 comment: Optional[LangString] = None,
                 permissions: Optional[str] = None):
        super().__init__(comment, permissions)
        #
        # a color value as used in HTML (e.g. "#aaccff"
        #
        res = re.match('^#(?:[0-9a-fA-F]{3}){1,2}$', str(value))
        if res is None:
            raise BaseError("Invalid ColorValue format! " + str(value))
        self._value = str(value)

    def toJsonLdObj(self, action: Actions) -> Dict[str, Any]:
        tmp = super().toJsonLdObj(action)
        if action == Actions.Create:
            tmp['knora-api:colorValueAsColor'] = self._value
        else:
            pass


@strict
class DateValue(Value):
    _calendar: str
    _e1: str
    _y1: int
    _m1: int
    _d1: int
    _e2: str
    _y2: int
    _m2: int
    _d2: int

    def __init__(self,
                 value: str,
                 comment: Optional[LangString] = None,
                 permissions: Optional[str] = None):
        super().__init__(comment, permissions)
        #
        # A knora date value
        #
        res = re.match(
            '(GREGORIAN:|JULIAN:)?(CE:|BCE:)?(\d{4})?(-\d{1,2})?(-\d{1,2})?(:CE|:BCE)?(:\d{4})?(-\d{1,2})?(-\d{1,2})?',
            str(value))
        if res is None:
            raise BaseError("Invalid date format! " + str(value))
        dp = res.groups()
        self._calendar = 'GREGORIAN' if dp[0] is None else dp[0].strip('-: ')
        self._e1 = 'CE' if dp[1] is None else dp[1].strip('-: ')
        self._y1 = None if dp[2] is None else int(dp[2].strip('-: '))
        self._m1 = None if dp[3] is None else int(dp[3].strip('-: '))
        self._d1 = None if dp[4] is None else int(dp[4].strip('-: '))
        self._e2 = 'CE' if dp[5] is None else dp[5].strip('-: ')
        self._y2 = None if dp[6] is None else int(dp[6].strip('-: '))
        self._m2 = None if dp[7] is None else int(dp[7].strip('-: '))
        self._d2 = None if dp[8] is None else int(dp[8].strip('-: '))
        if self._y1 is None:
            raise BaseError("Invalid date format! " + str(value))
        if self._y2 is not None:
            date1 = self._y1 * 10000
            if self._m1 is not None:
                self._date1 += self._m1 * 100
            if self._d1 is not None:
                self._date1 += self._d1
            self._date2 = self._y2 * 10000
            if self._m2 is not None:
                self._date2 += self._m2 * 100
            if self._d2 is not None:
                self._date2 += self._d2
            if self._date1 > self._date2:
                self._y1, self._y2 = self._y2, self._y1
                self._m1, self._m2 = self._m2, self._m1
                self._d1, self._d2 = self._d2, self._d1

    def toJsonLdObj(self, action: Actions) -> Dict[str, Any]:
        tmp = super().toJsonLdObj(action)
        if action == Actions.Create:
            tmp["knora-api:dateValueHasCalendar"] = self._calendar
            tmp["knora-api:dateValueHasStartEra"] = self._e1
            tmp["knora-api:dateValueHasStartYear"] = self._y1
            if self._m1 is not None:
                tmp["knora-api:dateValueHasStartMonth"] = self._m1
            if self._d1 is not None:
                tmp["knora-api:dateValueHasStartDay"] = self._d1
            tmp["knora-api:dateValueHasEndEra"] = self._e2
            if self._y2 is not None:
                tmp["knora-api:dateValueHasEndYear"] = self._y2
            else:
                tmp["knora-api:dateValueHasEndYear"] = self._y1
            if self._m2 is not None:
                tmp["knora-api:dateValueHasEndMonth"] = self._m2
            if self._d2 is not None:
                tmp["knora-api:dateValueHasEndDay"] = self._d2
        else:
            pass
        return tmp


@strict
class DecimalValue(Value):
    _value: float

    def __init__(self,
                 value: Union[float, int, str],
                 comment: Optional[LangString] = None,
                 permissions: Optional[str] = None):
        super().__init__(comment, permissions)
        self._value = value
        if isinstance(value, str):
            if re.match('^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$', value):
                self._value = float(value)
            else:
                raise BaseError("String does not represent decimal/float number! \"" + value + "\"")
        elif isinstance(value, float):
            self._value = value
        elif isinstance(value, int):
            self._value = float(value)
        else:
            raise BaseError("String does not represent decimal/float number! \"" + value + "\"")

    def toJsonLdObj(self, action: Actions) -> Dict[str, Any]:
        tmp = super().toJsonLdObj(action)
        if action == Actions.Create:
            tmp['knora-api:decimalValueAsDecimal'] = {
                '@type': 'xsd:decimal',
                '@value': self._value
            }
        else:
            pass
        return tmp


@strict
class GeomValue(Value):
    _value: str

    def __init__(self,
                 value: str,
                 comment: Optional[LangString] = None,
                 permissions: Optional[str] = None):
        super().__init__(comment, permissions)
        self._value = str(value)

    def toJsonLdObj(self, action: Actions) -> Dict[str, Any]:
        tmp = super().toJsonLdObj(action)
        if action == Actions.Create:
            tmp['knora-api:geometryValueAsGeometry'] = self._value
        else:
            pass
        return tmp


@strict
class GeonameValue(Value):
    _value: str

    def __init__(self,
                 value: str,
                 comment: Optional[LangString] = None,
                 permissions: Optional[str] = None):
        super().__init__(comment, permissions)
        self._value = str(value)

    def toJsonLdObj(self, action: Actions) -> Dict[str, Any]:
        tmp = super().toJsonLdObj(action)
        if action == Actions.Create:
            tmp['knora-api:geonameValueAsGeonameCode'] = self._value
        else:
            pass
        return tmp


@strict
class IntValue(Value):
    _value: int

    def __init__(self,
                 value: Union[int, str],
                 comment: Optional[LangString] = None,
                 permissions: Optional[str] = None):
        super().__init__(comment, permissions)
        if isinstance(value, str):
            if re.match('^[-+]?[0-9]+$', value):
                self._value = int(value)
            else:
                raise BaseError("String does not represent integer number! \"" + value + "\"")
        elif isinstance(value, int):
            self._value = value

    def toJsonLdObj(self, action: Actions) -> Dict[str, Any]:
        tmp = super().toJsonLdObj(action)
        if action == Actions.Create:
            tmp['knora-api:intValueAsInt'] = self._value
        else:
            pass
        return tmp


@strict
class BooleanValue(Value):
    _value: bool

    def __init__(self,
                 value: Union[bool, int, str],
                 comment: Optional[LangString] = None,
                 permissions: Optional[str] = None):
        super().__init__(comment, permissions)
        if type(value) == bool:
            self.value = value

        elif type(value) == str:
            if value.upper() == 'TRUE':
                self._value = True
            elif value.upper() == 'FALSE':
                self._value = False
            else:
                raise BaseError("Invalid boolean format! " + str(value))
        elif type(value) == int:
            self._value = False if value == 0 else True

    def toJsonLdObj(self, action: Actions) -> Dict[str, Any]:
        tmp = super().toJsonLdObj(action)
        if action == Actions.Create:
            tmp['knora-api:booleanValueAsBoolean'] = self._value
        else:
            pass
        return tmp


@strict
class UriValue(Value):
    _value: str

    def __init__(self,
                 value: str,
                 comment: Optional[LangString] = None,
                 permissions: Optional[str] = None):
        super().__init__(comment, permissions)
        m = re.match("^(http)s?://([\\w\\.\\-~]+:?\\d{,4})(/[\\w\\-~]+)+(#[\\w\\-~]*)?", str(value))
        if m and m.span()[1] == len(str(value)):
            self._value = str(value)
        else:
            raise BaseError("Invalid IRI/URI! \"" + value + "\"")

    def toJsonLdObj(self, action: Actions) -> Dict[str, Any]:
        tmp = super().toJsonLdObj(action)
        if action == Actions.Create:
            tmp['knora-api:uriValueAsUri'] = {
                "@type": "xsd:anyURI",
                "@value": self._value
            }
        else:
            pass
        return tmp


@strict
class TimeValue(Value):
    _value: str

    def __init__(self,
                 value: str,
                 comment: Optional[LangString] = None,
                 permissions: Optional[str] = None):
        super().__init__(comment, permissions)
        m = re.match("^[0-2]\d:[0-5]\d:[0-5]\d(?:\.\d+)?Z?$", str(value))
        if m and m.span()[1] == len(value):
            self._value = str(value)
        else:
            raise BaseError("Invalid time value! \"" + value + "\"")

    def toJsonLdObj(self, action: Actions) -> Dict[str, Any]:
        tmp = super().toJsonLdObj(action)
        if action == Actions.Create:
            tmp['knora-api:timeValueAsTime'] = {
                "@type": "xsd:dateTime",
                "@value": self._value
            }
        else:
            pass
        return tmp


@strict
class IntervalValue(Value):
    def __init__(self,
                 value: str,
                 comment: Optional[LangString] = None,
                 permissions: Optional[str] = None):
        super().__init__(comment, permissions)
        iv = value.split(':')
        self.__jsonld_obj["knora-api:intervalValueHasEnd"] = {
            "@type": "xsd:decimal",
            "@value": str(iv[0])
        }
        self.__jsonld_obj["knora-api:intervalValueHasStart"] = {
            "@type": "xsd:decimal",
            "@value": str(iv[1])
        }


@strict
class ListValue(Value):
    _value: str

    def __init__(self,
                 value: str,
                 comment: Optional[LangString] = None,
                 permissions: Optional[str] = None,
                 lists: List[ListNode] = None, ):

        def find_listnode(nodes: List[ListNode], name: str) -> Union[str, None]:
            for node in nodes:
                if node.name == name:
                    return node.id
                else:
                    node_id = find_listnode(node.children, name)
                    if node_id is not None:
                        return node_id
            return None

        super().__init__(comment, permissions)
        iriparts = parse(str(value), rule='IRI')
        if iriparts['scheme'] == 'http' or iriparts['scheme'] == 'https':
            self._value = str(value)
        else:
            if iriparts['authority'] is not None:
                raise BaseError("Invalid list node: \"" + str(value) + "\" !")
            listname = iriparts['scheme']
            nodename = iriparts['path']
            if lists is None:
                raise BaseError("Lists from ResourceInstanceFactory must be provided!")
            node_iri = None
            for list in lists:
                if list.name == listname:
                    node_iri = find_listnode(list.children, str(value))
            if node_iri is not None:
                self._value = node_iri
            else:
                raise BaseError("Listnode \"{}\" not found".format(value))

    def toJsonLdObj(self, action: Actions) -> Dict[str, Any]:
        tmp = super().toJsonLdObj(action)
        if action == Actions.Create:
            tmp['knora-api:listValueAsListNode'] = {
                '@id': self._value
            }
        else:
            pass
        return tmp


@strict
class LinkValue(Value):
    _value: str

    def __init__(self,
                 value: str,
                 comment: Optional[LangString] = None,
                 permissions: Optional[str] = None):
        super().__init__(comment, permissions)
        m = re.match("^(http)s?://([\\w\\.\\-~]+:?\\d{,4})(/[\\w\\-~]+)+(#[\\w\\-~]*)?", str(value))
        if m and m.span()[1] == len(value):
            self._value = str(value)
        else:
            raise BaseError("Target of link is not a IRI: \"" + str(value) + "\"")

    def toJsonLdObj(self, action: Actions) -> Dict[str, Any]:
        tmp = super().toJsonLdObj(action)
        if action == Actions.Create:
            tmp['knora-api:linkValueHasTargetIri'] = {
                '@id': self._value
            }
        else:
            pass
        return tmp

