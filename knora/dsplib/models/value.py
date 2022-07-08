import re
from typing import Optional, Any, Union

from pystrict import strict

from .helpers import IriTest, Actions, BaseError
from .langstring import LangString
from .listnode import ListNode
from .permission import PermissionValue, Permissions


@strict
class KnoraStandoffXml:
    """Used to handle XML strings for standoff markup"""

    __iriregexp = re.compile(r'IRI:[^:]*:IRI')
    __xmlstr: str

    def __init__(self, xmlstr: str) -> None:
        self.__xmlstr = str(xmlstr)

    def __str__(self) -> str:
        return self.__xmlstr

    def get_all_iris(self) -> Optional[list[str]]:
        return self.__iriregexp.findall(self.__xmlstr)

    def replace(self, fromStr: str, toStr: str) -> None:
        self.__xmlstr = self.__xmlstr.replace(fromStr, toStr)

    def regex_replace(self, pattern: str, repl: str) -> None:
        self.__xmlstr = re.sub(pattern=repr(pattern)[1:-1], repl=repl, string=self.__xmlstr)


@strict
class Value:
    """
    Represents a value
    """
    _iri: Optional[str]
    _comment: Optional[str]
    _permissions: Optional[Permissions]
    _upermission: Optional[PermissionValue]
    _ark_url: Optional[str]
    _vark_url: Optional[str]

    def __init__(self,
                 iri: Optional[str] = None,
                 comment: Optional[LangString] = None,
                 permissions: Optional[Permissions] = None,
                 upermission: Optional[PermissionValue] = None,
                 ark_url: Optional[str] = None,
                 vark_url: Optional[str] = None):
        self._iri = iri
        self._comment = comment
        self._permissions = permissions
        self._upermission = upermission
        self._ark_url = ark_url
        self._vark_url = vark_url

    def __str__(self):
        if self._iri:
            tmpstr = "(iri: " + self._iri
        else:
            tmpstr = ('(iri: -')
        if self._permissions:
            tmpstr = ", permissions: " + str(self._permissions)
        if self._comment:
            tmpstr += ", comment: " + self._comment
        tmpstr += ")"
        return tmpstr

    @property
    def iri(self) -> str:
        return self.iri

    @property
    def ark_url(self) -> str:
        return self._ark_url

    @property
    def vark_url(self) -> str:
        return self._vark_url

    @property
    def permissions(self) -> str:
        return self._permissions

    @property
    def upermission(self) -> str:
        return self._upermission

    @property
    def comment(self):
        return self._comment

    def toJsonLdObj(self, action: Actions) -> dict[str, Any]:
        tmp = {}
        if action == Actions.Create:
            if self._permissions:
                tmp["knora-api:hasPermissions"] = self.permissions.toJsonLdObj()
            if self._comment:
                tmp["knora-api:valueHasComment"] = str(self._comment)
        return tmp

    @staticmethod
    def get_typed_value(key: str, jsonld_obj: Any) -> Union[str, float]:
        try:
            tmp = jsonld_obj[key]
            if tmp.get("@type") == "xsd:decimal":
                result = float(tmp["@value"])
            elif tmp.get("@type") == "xsd:integer":
                result = int(tmp["@value"])
            elif tmp.get("@type") == "xsd:boolean":
                result = bool(tmp["@value"])
            elif tmp.get("@type") == "xsd:anyURI":
                result = str(tmp["@value"])
            elif tmp.get("@type") == "xsd:dateTimeStamp":
                result = str(tmp["@value"])
            elif tmp.get("@id"):
                result = tmp["@id"]
            else:
                raise BaseError("Invalid data type in JSON-LD: \"{}\"!".format(tmp["@type"]))
            return result
        except KeyError as kerr:
            raise BaseError("Error in JSON-LD returned!")

    @staticmethod
    def getFromJsonLd(jsonld_obj) -> dict[str, Union[str, float]]:

        return {
            'iri': jsonld_obj.get("@id"),
            'comment': jsonld_obj.get("knora-api:valueHasComment"),
            'ark_url': Value.get_typed_value("knora-api:arkUrl", jsonld_obj),
            'vark_url': Value.get_typed_value("knora-api:versionArkUrl", jsonld_obj),
            'permissions': Permissions.fromString(jsonld_obj.get("knora-api:hasPermissions")),
            'upermission': PermissionValue[jsonld_obj.get("knora-api:userHasPermission", jsonld_obj)]
        }


@strict
class TextValue(Value):
    _value: Union[str, KnoraStandoffXml]
    _mapping: str

    def __init__(self,
                 value: Union[str, KnoraStandoffXml],
                 mapping: Optional[str] = None,
                 comment: Optional[LangString] = None,
                 permissions: Optional[Permissions] = None,
                 upermission: Optional[PermissionValue] = None,
                 iri: Optional[str] = None,
                 ark_url: Optional[str] = None,
                 vark_url: Optional[str] = None):
        self._value = value
        self._mapping = mapping
        super().__init__(iri=iri,
                         comment=comment,
                         permissions=permissions,
                         upermission=upermission,
                         ark_url=ark_url,
                         vark_url=vark_url)

    @property
    def value(self) -> str:
        return self._value

    @property
    def mapping(self) -> str:
        return self._mapping

    @classmethod
    def fromJsonLdObj(cls, jsonld_obj: Any) -> dict[str, Any]:
        tmp = Value.getFromJsonLd(jsonld_obj)

        if jsonld_obj.get("knora-api:textValueAsXml") is not None:
            tmp['mapping'] = jsonld_obj.get("knora-api:textValueHasMapping")
            tmp['value'] = jsonld_obj.get("knora-api:textValueAsXml")
        else:
            tmp['mapping'] = None
            tmp['value'] = jsonld_obj.get("knora-api:valueAsString")
        return cls(**tmp)

    def toJsonLdObj(self, action: Actions) -> dict[str, Any]:
        tmp = super().toJsonLdObj(action)
        if action == Actions.Create:
            tmp['@type'] = 'knora-api:TextValue'
            if isinstance(self._value, KnoraStandoffXml):
                tmp['knora-api:textValueAsXml'] = self._value
                tmp['knora-api:textValueHasMapping'] = {
                    '@id': 'http://rdfh.ch/standoff/mappings/StandardMapping' if self._mapping is None else self._mapping
                }
            else:
                tmp['knora-api:valueAsString'] = str(self._value)
        return tmp

    def __str__(self) -> str:
        return str(self._value)


@strict
class ColorValue(Value):
    _value: str

    def __init__(self,
                 value: str,
                 comment: Optional[LangString] = None,
                 permissions: Optional[Permissions] = None,
                 upermission: Optional[PermissionValue] = None,
                 iri: Optional[str] = None,
                 ark_url: Optional[str] = None,
                 vark_url: Optional[str] = None):
        #
        # a color value as used in HTML (e.g. "#aaccff"
        #
        m = re.match('^#(?:[0-9a-fA-F]{3}){1,2}$', str(value))
        if not m:
            raise BaseError("Invalid ColorValue format! " + str(value))
        self._value = str(value)
        super().__init__(iri=iri,
                         comment=comment,
                         permissions=permissions,
                         upermission=upermission,
                         ark_url=ark_url,
                         vark_url=vark_url)

    @property
    def value(self) -> str:
        return self._value

    @classmethod
    def fromJsonLdObj(cls, jsonld_obj: Any) -> dict[str, Any]:
        tmp = Value.getFromJsonLd(jsonld_obj)
        tmp['value'] = jsonld_obj.get("knora-api:colorValueAsColor")
        return cls(**tmp)

    def toJsonLdObj(self, action: Actions) -> dict[str, Any]:
        tmp = super().toJsonLdObj(action)
        if action == Actions.Create:
            tmp['@type'] = "knora-api:ColorValue"
            tmp['knora-api:colorValueAsColor'] = self._value
        return tmp

    def __str__(self) -> str:
        return self._value + ' ' + super().__str__()


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
                 permissions: Optional[Permissions] = None,
                 upermission: Optional[PermissionValue] = None,
                 iri: Optional[str] = None,
                 ark_url: Optional[str] = None,
                 vark_url: Optional[str] = None):
        #
        # A knora date value
        #
        m = re.match(
            '(GREGORIAN:|JULIAN:)?(CE:|BCE:)?(\\d{4})?(-\\d{1,2})?(-\\d{1,2})?(:CE|:BCE)?(:\\d{4})?(-\\d{1,2})?(-\\d{1,2})?',
            str(value))
        if not m:
            raise BaseError("Invalid date format: \"{}\"!".format(str(value)))
        dp = m.groups()
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

        super().__init__(iri=iri,
                         comment=comment,
                         permissions=permissions,
                         upermission=upermission,
                         ark_url=ark_url,
                         vark_url=vark_url)

    @property
    def value(self) -> str:
        datestr = ''
        if self._calendar:
            datestr += self._calendar + ':'
        if self._e1:
            datestr += self._e1 + ':'
        if self._y1:
            datestr += str(self._y1) + '-'
        if self._m1:
            datestr += str(self._m1) + '-'
        if self._d1:
            datestr += str(self._d1)
        if self._e2:
            datestr += ':' + str(self._e2)
        if self._y2:
            datestr += ':' + str(self._y2)
        if self._m2:
            datestr += '-' + str(self._m2)
        if self._d2:
            datestr += '-' + str(self._d2)
        return datestr

    @classmethod
    def fromJsonLdObj(cls, jsonld_obj: Any) -> dict[str, Any]:
        tmp = Value.getFromJsonLd(jsonld_obj)

        datestr = ""
        datestr += jsonld_obj.get("knora-api:dateValueHasCalendar") + ":" \
            if jsonld_obj.get("knora-api:dateValueHasCalendar") is not None else ""
        datestr += jsonld_obj.get("knora-api:dateValueHasStartEra") + ":" \
            if jsonld_obj.get("knora-api:dateValueHasStartEra") is not None else ""
        datestr += str(jsonld_obj.get("knora-api:dateValueHasStartYear")) \
            if jsonld_obj.get("knora-api:dateValueHasStartYear") is not None else ""
        datestr += "-" + str(jsonld_obj.get("knora-api:dateValueHasStartMonth")) \
            if jsonld_obj.get("knora-api:dateValueHasStartMonth") is not None else ""
        datestr += "-" + str(jsonld_obj.get("knora-api:dateValueHasStartDay")) \
            if jsonld_obj.get("knora-api:dateValueHasStartDay") is not None else ""
        datestr += ":" + jsonld_obj.get("knora-api:dateValueHasEndEra") \
            if jsonld_obj.get("knora-api:dateValueHasEndEra") is not None else ""
        datestr += ":" + str(jsonld_obj.get("knora-api:dateValueHasEndYear")) \
            if jsonld_obj.get("knora-api:dateValueHasEndYear") is not None else ""
        datestr += "-" + str(jsonld_obj.get("knora-api:dateValueHasEndMonth")) \
            if jsonld_obj.get("knora-api:dateValueHasEndMonth") is not None else ""
        datestr += "-" + str(jsonld_obj.get("knora-api:dateValueHasEndDay")) \
            if jsonld_obj.get("knora-api:dateValueHasEndDay") is not None else ""
        tmp['value'] = datestr
        return cls(**tmp)

    def toJsonLdObj(self, action: Actions) -> dict[str, Any]:
        tmp = super().toJsonLdObj(action)
        if action == Actions.Create:
            tmp['@type'] = "knora-api:DateValue"
            tmp["knora-api:dateValueHasCalendar"] = self._calendar
            tmp["knora-api:dateValueHasStartEra"] = self._e1
            tmp["knora-api:dateValueHasStartYear"] = self._y1
            if self._m1:
                tmp["knora-api:dateValueHasStartMonth"] = self._m1
            if self._d1:
                tmp["knora-api:dateValueHasStartDay"] = self._d1
            tmp["knora-api:dateValueHasEndEra"] = self._e2
            if self._y2:
                tmp["knora-api:dateValueHasEndYear"] = self._y2
            else:
                tmp["knora-api:dateValueHasEndYear"] = self._y1
            if self._m2:
                tmp["knora-api:dateValueHasEndMonth"] = self._m2
            if self._d2:
                tmp["knora-api:dateValueHasEndDay"] = self._d2
        return tmp

    def __str__(self):
        datestr = ''
        if self._calendar:
            datestr += self._calendar + ':'
        if self._e1:
            datestr += self._e1 + ':'
        if self._y1:
            datestr += str(self._y1) + '-'
        if self._m1:
            datestr += str(self._m1) + '-'
        if self._d1:
            datestr += str(self._d1)
        if self._e2:
            datestr += ':' + str(self._e2)
        if self._y2:
            datestr += ':' + str(self._y2)
        if self._m2:
            datestr += '-' + str(self._m2)
        if self._d2:
            datestr += '-' + str(self._d2)
        return datestr + ' ' + super().__str__()


@strict
class DecimalValue(Value):
    _value: float

    def __init__(self,
                 value: Union[float, int, str],
                 comment: Optional[LangString] = None,
                 permissions: Optional[Permissions] = None,
                 upermission: Optional[PermissionValue] = None,
                 iri: Optional[str] = None,
                 ark_url: Optional[str] = None,
                 vark_url: Optional[str] = None):
        self._value = value
        if isinstance(value, str):
            m = re.match(r'^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$', value)
            if m:
                self._value = float(value)
            else:
                raise BaseError("String does not represent decimal/float number! \"" + value + "\"")
        elif isinstance(value, float):
            self._value = value
        elif isinstance(value, int):
            self._value = float(value)
        else:
            raise BaseError("String does not represent decimal/float number! \"" + value + "\"")
        super().__init__(iri=iri,
                         comment=comment,
                         permissions=permissions,
                         upermission=upermission,
                         ark_url=ark_url,
                         vark_url=vark_url)

    @property
    def value(self) -> float:
        return self._value

    @classmethod
    def fromJsonLdObj(cls, jsonld_obj: Any) -> dict[str, Any]:
        tmp = Value.getFromJsonLd(jsonld_obj)
        tmp['value'] = Value.get_typed_value("knora-api:decimalValueAsDecimal", jsonld_obj)
        return cls(**tmp)

    def toJsonLdObj(self, action: Actions) -> dict[str, Any]:
        tmp = super().toJsonLdObj(action)
        if action == Actions.Create:
            tmp['@type'] = "knora-api:DecimalValue"
            tmp['knora-api:decimalValueAsDecimal'] = {
                '@type': 'xsd:decimal',
                '@value': str(self._value)
            }
        return tmp

    def __str__(self) -> str:
        return str(self._value) + ' ' + super().__str__()


@strict
class GeomValue(Value):
    _value: str

    def __init__(self,
                 value: str,
                 comment: Optional[LangString] = None,
                 permissions: Optional[Permissions] = None,
                 upermission: Optional[PermissionValue] = None,
                 iri: Optional[str] = None,
                 ark_url: Optional[str] = None,
                 vark_url: Optional[str] = None):
        self._value = str(value)
        super().__init__(iri=iri,
                         comment=comment,
                         permissions=permissions,
                         upermission=upermission,
                         ark_url=ark_url,
                         vark_url=vark_url)

    @property
    def value(self) -> str:
        return self._value

    @classmethod
    def fromJsonLdObj(cls, jsonld_obj: Any) -> dict[str, Any]:
        tmp = Value.getFromJsonLd(jsonld_obj)
        tmp['value'] = jsonld_obj.get('knora-api:geometryValueAsGeometry')
        return cls(**tmp)

    def toJsonLdObj(self, action: Actions) -> dict[str, Any]:
        tmp = super().toJsonLdObj(action)
        if action == Actions.Create:
            tmp['@type'] = "knora-api:GeomValue"
            tmp['knora-api:geometryValueAsGeometry'] = self._value
        return tmp

    def __str__(self) -> str:
        return self._value + ' ' + super().__str__()


@strict
class GeonameValue(Value):
    _value: str

    def __init__(self,
                 value: str,
                 comment: Optional[LangString] = None,
                 permissions: Optional[Permissions] = None,
                 upermission: Optional[PermissionValue] = None,
                 iri: Optional[str] = None,
                 ark_url: Optional[str] = None,
                 vark_url: Optional[str] = None):
        self._value = str(value)
        super().__init__(iri=iri,
                         comment=comment,
                         permissions=permissions,
                         upermission=upermission,
                         ark_url=ark_url,
                         vark_url=vark_url)

    @property
    def value(self) -> str:
        return self._value

    @classmethod
    def fromJsonLdObj(cls, jsonld_obj: Any) -> dict[str, Any]:
        tmp = Value.getFromJsonLd(jsonld_obj)
        tmp['value'] = jsonld_obj.get('knora-api:geonameValueAsGeonameCode')
        return cls(**tmp)

    def toJsonLdObj(self, action: Actions) -> dict[str, Any]:
        tmp = super().toJsonLdObj(action)
        if action == Actions.Create:
            tmp['@type'] = "knora-api:GeonameValue"
            tmp['knora-api:geonameValueAsGeonameCode'] = self._value
        return tmp

    def __str__(self) -> str:
        return self._value + ' ' + super().__str__()


@strict
class IntValue(Value):
    _value: int

    def __init__(self,
                 value: Union[int, str],
                 comment: Optional[LangString] = None,
                 permissions: Optional[Permissions] = None,
                 upermission: Optional[PermissionValue] = None,
                 iri: Optional[str] = None,
                 ark_url: Optional[str] = None,
                 vark_url: Optional[str] = None):
        if isinstance(value, str):
            m = re.match('^[-+]?[0-9]+$', value)
            if m and m.span()[1] == len(str(value)):
                self._value = int(value)
            else:
                raise BaseError("String does not represent integer number! \"" + value + "\"")
        elif isinstance(value, int):
            self._value = value
        super().__init__(iri=iri,
                         comment=comment,
                         permissions=permissions,
                         upermission=upermission,
                         ark_url=ark_url,
                         vark_url=vark_url)

    @property
    def value(self) -> int:
        return self._value

    @classmethod
    def fromJsonLdObj(cls, jsonld_obj: Any) -> dict[str, Any]:
        tmp = Value.getFromJsonLd(jsonld_obj)
        tmp['value'] = jsonld_obj.get("knora-api:intValueAsInt")
        return cls(**tmp)

    def toJsonLdObj(self, action: Actions) -> dict[str, Any]:
        tmp = super().toJsonLdObj(action)
        if action == Actions.Create:
            tmp['@type'] = "knora-api:IntValue"
            tmp['knora-api:intValueAsInt'] = self._value
        return tmp

    def __str__(self) -> str:
        return str(self._value) + ' ' + super().__str__()


@strict
class BooleanValue(Value):
    _value: bool

    def __init__(self,
                 value: Union[bool, int, str],
                 comment: Optional[LangString] = None,
                 permissions: Optional[Permissions] = None,
                 upermission: Optional[PermissionValue] = None,
                 iri: Optional[str] = None,
                 ark_url: Optional[str] = None,
                 vark_url: Optional[str] = None):

        if type(value) is bool:
            self._value = value
        else:
            if value == 1 or value.upper() == 'TRUE' or value == '1':
                self._value = True
            elif value == 0 or value.upper() == 'FALSE' or value == '0':
                self._value = False
            else:
                raise BaseError(f"ERROR Invalid boolean format {value}!")

        super().__init__(iri=iri,
                         comment=comment,
                         permissions=permissions,
                         upermission=upermission,
                         ark_url=ark_url,
                         vark_url=vark_url)

    @property
    def value(self) -> bool:
        return self._value

    @classmethod
    def fromJsonLdObj(cls, jsonld_obj: Any) -> dict[str, Any]:
        tmp = Value.getFromJsonLd(jsonld_obj)
        tmp['value'] = jsonld_obj.get("knora-api:booleanValueAsBoolean")
        return cls(**tmp)

    def toJsonLdObj(self, action: Actions) -> dict[str, Any]:
        tmp = super().toJsonLdObj(action)
        if action == Actions.Create:
            tmp['@type'] = "knora-api:BooleanValue"
            tmp['knora-api:booleanValueAsBoolean'] = self._value
        return tmp

    def __str__(self) -> str:
        return str(self._value) + ' ' + super().__str__()


@strict
class UriValue(Value):
    _value: str

    def __init__(self,
                 value: str,
                 comment: Optional[LangString] = None,
                 permissions: Optional[Permissions] = None,
                 upermission: Optional[PermissionValue] = None,
                 iri: Optional[str] = None,
                 ark_url: Optional[str] = None,
                 vark_url: Optional[str] = None):
        m = re.match("^(http)s?://([\\w\\.\\-~]+)?(:\\d{,6})?(/[\\w\\-~]+)*(#[\\w\\-~]*)?", str(value))
        if m:
            self._value = str(value)
        else:
            raise BaseError("Invalid IRI/URI! \"" + value + "\"")
        super().__init__(iri=iri,
                         comment=comment,
                         permissions=permissions,
                         upermission=upermission,
                         ark_url=ark_url,
                         vark_url=vark_url)

    @property
    def value(self) -> str:
        return self._value

    @classmethod
    def fromJsonLdObj(cls, jsonld_obj: Any) -> dict[str, Any]:
        tmp = Value.getFromJsonLd(jsonld_obj)
        tmp['value'] = Value.get_typed_value("knora-api:uriValueAsUri", jsonld_obj)
        return cls(**tmp)

    def toJsonLdObj(self, action: Actions) -> dict[str, Any]:
        tmp = super().toJsonLdObj(action)
        if action == Actions.Create:
            tmp['@type'] = "knora-api:UriValue"
            tmp['knora-api:uriValueAsUri'] = {
                "@type": "xsd:anyURI",
                "@value": self._value
            }
        return tmp

    def __str__(self) -> str:
        return self._value + ' ' + super().__str__()


@strict
class TimeValue(Value):
    _value: str

    @property
    def value(self) -> str:
        return self._value

    def __init__(self,
                 value: str,
                 comment: Optional[LangString] = None,
                 permissions: Optional[Permissions] = None,
                 upermission: Optional[PermissionValue] = None,
                 iri: Optional[str] = None,
                 ark_url: Optional[str] = None,
                 vark_url: Optional[str] = None):
        m = re.match("^([+-])?(\\d{4}-[0-1]\\d-[0-3]\\dT[0-2]\\d:[0-5]\\d:[0-5]\\d)(.\\d+)?(Z|[+-][0-2]\\d:[0-5]\\d)$",
                     str(value))
        if m:
            self._value = str(value)
        else:
            raise BaseError("Invalid time value! \"" + value + "\"")
        super().__init__(iri=iri,
                         comment=comment,
                         permissions=permissions,
                         upermission=upermission,
                         ark_url=ark_url,
                         vark_url=vark_url)

    @property
    def value(self) -> str:
        return self._value

    @classmethod
    def fromJsonLdObj(cls, jsonld_obj: Any) -> dict[str, Any]:
        tmp = Value.getFromJsonLd(jsonld_obj)
        tmp['value'] = Value.get_typed_value("knora-api:timeValueAsTimeStamp", jsonld_obj)
        return cls(**tmp)

    def toJsonLdObj(self, action: Actions) -> dict[str, Any]:
        tmp = super().toJsonLdObj(action)
        if action == Actions.Create:
            tmp['@type'] = "knora-api:TimeValue"
            tmp['knora-api:timeValueAsTimeStamp'] = {
                "@type": "xsd:dateTimeStamp",
                "@value": self._value
            }
        return tmp

    def __str__(self) -> str:
        return self._value + ' ' + super().__str__()


@strict
class IntervalValue(Value):
    _iv_start: str
    _iv_end: str

    def __init__(self,
                 value: Optional[str] = None,
                 iv_start: Optional[float] = None,
                 iv_end: Optional[float] = None,
                 comment: Optional[LangString] = None,
                 permissions: Optional[Permissions] = None,
                 upermission: Optional[PermissionValue] = None,
                 iri: Optional[str] = None,
                 ark_url: Optional[str] = None,
                 vark_url: Optional[str] = None):
        if value is not None:
            startval, endval = value.split(':')
            self._iv_start = float(startval)
            self._iv_end = float(endval)
        else:
            if iv_start is None or iv_end is None:
                raise BaseError("\"value\" or \"iv_start\" and \"iv_end\" must be given to constructor!")
            self._iv_start = iv_start
            self._iv_end = iv_end
        super().__init__(iri=iri,
                         comment=comment,
                         permissions=permissions,
                         upermission=upermission,
                         ark_url=ark_url,
                         vark_url=vark_url)

    @property
    def value(self) -> str:
        return str(self._iv_start) + ':' + str(self._iv_end)

    @property
    def iv_start(self) -> float:
        return self._iv_start

    @property
    def iv_end(self) -> float:
        return self._iv_end

    @classmethod
    def fromJsonLdObj(cls, jsonld_obj: Any) -> dict[str, Any]:
        tmp = Value.getFromJsonLd(jsonld_obj)
        start = Value.get_typed_value("knora-api:intervalValueHasStart", jsonld_obj)
        end = Value.get_typed_value("knora-api:intervalValueHasEnd", jsonld_obj)
        tmp['value'] = str(start) + ":" + str(end)
        return cls(**tmp)

    def toJsonLdObj(self, action: Actions) -> dict[str, Any]:
        tmp = super().toJsonLdObj(action)
        if action == Actions.Create:
            tmp['@type'] = "knora-api:IntervalValue"
            tmp["knora-api:intervalValueHasStart"] = {
                "@type": "xsd:decimal",
                "@value": str(self._iv_start)
            }
            tmp["knora-api:intervalValueHasEnd"] = {
                "@type": "xsd:decimal",
                "@value": str(self._iv_end)
            }
        return tmp

    def __str__(self) -> str:
        interval = str(self._iv_start) + ':' + str(self._iv_end)
        return interval + ' ' + super().__str__()


@strict
class ListValue(Value):
    _value: str

    def __init__(self,
                 value: str,
                 lists: list[ListNode] = None,
                 comment: Optional[LangString] = None,
                 permissions: Optional[Permissions] = None,
                 upermission: Optional[PermissionValue] = None,
                 iri: Optional[str] = None,
                 ark_url: Optional[str] = None,
                 vark_url: Optional[str] = None):

        def find_listnode(nodes: list[ListNode], name: str) -> Optional[str]:
            for node in nodes:
                if node.name == name:
                    return node.id
                else:
                    if node.children is not None:
                        node_id = find_listnode(node.children, name)
                        if node_id is not None:
                            return node_id
            return None

        if IriTest.test(str(value)):
            self._value = str(value)
        else:
            tmp = str(value).split(':')
            if len(tmp) > 1:
                if tmp[0]:
                    listname = tmp[0]
                    nodename = tmp[1]
                else:
                    raise BaseError("Invalid list node: \"" + str(value) + "\" !")
            else:
                raise BaseError("Invalid list node: \"" + str(value) + "\" !")
            if lists is None:
                raise BaseError("Lists from ResourceInstanceFactory must be provided!")
            node_iri = None
            for list_item in lists:
                if list_item.name == listname:
                    node_iri = find_listnode(list_item.children, nodename)
            if node_iri is not None:
                self._value = node_iri
            else:
                raise BaseError("Listnode \"{}\" not found".format(value))
        super().__init__(iri=iri,
                         comment=comment,
                         permissions=permissions,
                         upermission=upermission,
                         ark_url=ark_url,
                         vark_url=vark_url)

    def print(self, offset: int = 0):
        blank = ' '
        print(f'{blank:>{offset}}{self._value}')

    @property
    def value(self) -> str:
        return self._value

    @classmethod
    def fromJsonLdObj(cls, jsonld_obj: Any) -> dict[str, Any]:
        tmp = Value.getFromJsonLd(jsonld_obj)
        tmp['value'] = Value.get_typed_value("knora-api:listValueAsListNode", jsonld_obj)
        return cls(**tmp)

    def toJsonLdObj(self, action: Actions) -> dict[str, Any]:
        tmp = super().toJsonLdObj(action)
        if action == Actions.Create:
            tmp['@type'] = "knora-api:ListValue"
            tmp['knora-api:listValueAsListNode'] = {
                '@id': self._value
            }
        return tmp

    def __str__(self) -> str:
        return self._value + ' ' + super().__str__()


@strict
class LinkValue(Value):
    _value: str
    _restype: str
    _reslabel: str

    def __init__(self,
                 value: str,
                 restype: Optional[str] = None,
                 reslabel: Optional[str] = None,
                 comment: Optional[LangString] = None,
                 permissions: Optional[Permissions] = None,
                 upermission: Optional[PermissionValue] = None,
                 iri: Optional[str] = None,
                 ark_url: Optional[str] = None,
                 vark_url: Optional[str] = None):
        m = re.match("^(http)s?://([\\w\\.\\-~]+)?(:\\d{,6})?(/[\\w\\-~]+)*(#[\\w\\-~]*)?", str(value))
        if m:
            self._value = str(value)
        else:
            raise BaseError("Target of link is not a IRI: \"" + str(value) + "\"")
        self._restype = restype
        self._reslabel = reslabel
        super().__init__(iri=iri,
                         comment=comment,
                         permissions=permissions,
                         upermission=upermission,
                         ark_url=ark_url,
                         vark_url=vark_url)

    @property
    def value(self) -> str:
        return self._value

    @property
    def restype(self) -> str:
        return self._restype

    @property
    def reslabel(self) -> str:
        return self._reslabel

    @classmethod
    def fromJsonLdObj(cls, jsonld_obj: Any) -> dict[str, Any]:
        tmp = Value.getFromJsonLd(jsonld_obj)
        linked_resource = jsonld_obj.get("knora-api:linkValueHasTarget")
        if linked_resource is not None:
            tmp['value'] = linked_resource['@id']
            tmp['restype'] = linked_resource["@type"]
            tmp['reslabel'] = linked_resource["rdfs:label"]
        return cls(**tmp)

    def toJsonLdObj(self, action: Actions) -> dict[str, Any]:
        tmp = super().toJsonLdObj(action)
        if action == Actions.Create:
            tmp['@type'] = "knora-api:LinkValue"
            tmp['knora-api:linkValueHasTargetIri'] = {
                '@id': self._value
            }
        return tmp

    def __str__(self) -> str:
        return self._value + ' ' + super().__str__()


def fromJsonLdObj(jsonld_obj: str) -> Value:
    switcher = {
        'knora-api:TextValue': TextValue,
        'knora-api:ColorValue': ColorValue,
        'knora-api:DateValue': DateValue,
        'knora-api:DecimalValue': DecimalValue,
        'knora-api:GeomValue': GeomValue,
        'knora-api:GeonameValue': GeonameValue,
        'knora-api:IntValue': IntValue,
        'knora-api:BooleanValue': BooleanValue,
        'knora-api:UriValue': UriValue,
        'knora-api:TimeValue': TimeValue,
        'knora-api:IntervalValue': IntervalValue,
        'knora-api:ListValue': ListValue,
        'knora-api:LinkValue': LinkValue,
    }
    return switcher[jsonld_obj.get('@type')].fromJsonLdObj(jsonld_obj)


def make_value(value: Value,
               comment: Optional[str] = None,
               permissions: Optional[Permissions] = None):
    res = {}
    res['value'] = value
    if comment:
        res['comment'] = comment
    if permissions:
        res['permissions'] = permissions
    return res
