import os
import sys
import json
from pystrict import strict
from typing import List, Set, Dict, Tuple, Optional, Any, Union
from enum import Enum
from urllib.parse import quote_plus
from pprint import pprint

path = os.path.abspath(os.path.dirname(__file__))
(head, tail)  = os.path.split(path)
if not head in sys.path:
    sys.path.append(head)
if not path in sys.path:
    sys.path.append(path)

from helpers import Actions, BaseError, Context, Cardinality
from connection import Connection
from langstring import Languages, LangStringParam, LangString

class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


@strict
class PropertyClass:
    _name: str
    _ontology_id: str
    _superproperties: List[str]
    _object: str
    _subject: str
    _guielement: str
    _gui_attribute: Dict[str, str]
    _label: LangString
    _comment: LangString
    _editable: bool
    _linkvalue: bool
    _changed: Set[str]

    def __init__(self,
                 con: Connection,
                 context: Context,
                 name: Optional[str] = None,
                 ontology_id: Optional[str] = None,
                 superproperties: Optional[List[Union['PropertyClass', str]]] = None,
                 object: Optional[str] = None,
                 subject: Optional[str] = None,
                 guielement: Optional[str] = None,
                 gui_attribute: Optional[Dict[str, str]] = None,
                 label: Optional[Union[LangString, str]] = None,
                 comment: Optional[Union[LangString, str]] = None,
                 editable: Optional[bool] = None,
                 linkvalue: Optional[bool] = None):
        if not isinstance(con, Connection):
            raise BaseError('"con"-parameter must be an instance of Connection')
        if not isinstance(context, Context):
            raise BaseError('"context"-parameter must be an instance of Context')
        self.con = con
        self._name = name
        self._ontology_id = ontology_id
        if isinstance(superproperties, PropertyClass):
            self._superproperties = list(map(lambda a: a.id, superproperties))
        else:
            self._superproperties = superproperties
        self._object = object
        self._subject = subject
        self._guielement = guielement
        self._gui_attribute = gui_attribute
        #
        # process label
        #
        if label is not None:
            if isinstance(label, str):
                self._label = LangString(label)
            elif isinstance(label, LangString):
                self._label = label
            else:
                raise BaseError('Invalid LangString for label!')
        else:
            self._label = None
        #
        # process comment
        #
        if comment is not None:
            if isinstance(comment, str):
                self._comment = LangString(comment)
            elif isinstance(comment, LangString):
                self._comment = comment
            else:
                raise BaseError('Invalid LangString for comment!')
        else:
            self._comment = None

        self._editable = editable
        self._linkvalue = linkvalue
        self._changed = set()

    #
    # Here follows a list of getters/setters
    #
    @property
    def name(self) -> Optional[str]:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        raise BaseError('"name" cannot be modified!')

    @property
    def ontology_id(self) -> Optional[str]:
        return self._ontology_id

    @ontology_id.setter
    def ontology_id(self, value: str) -> None:
        raise BaseError('"ontology_id" cannot be modified!')

    @property
    def superproperties(self) -> Optional[str]:
        return self._superproperties

    @superproperties.setter
    def superproperties(self, value: str) -> None:
        raise BaseError('"superproperties" cannot be modified!')

    @property
    def object(self) -> Optional[str]:
        return self._object

    @object.setter
    def object(self, value: Any):
        raise BaseError('"object" cannot be modified!')

    @property
    def subject(self) -> Optional[str]:
        return self._subject

    @subject.setter
    def subject(self, value: Any):
        raise BaseError('"subject" cannot be modified!')

    @property
    def guielement(self) -> Optional[str]:
        return self._guielement

    @guielement.setter
    def guielement(self, value: str) -> None:
        self._guielement = value
        self._changed.append('guielement')

    @property
    def gui_attribute(self) -> Optional[Dict[str, str]]:
        return self._gui_attribute

    @gui_attribute.setter
    def gui_attribute(self, value: List[Dict[str, str]]) -> None:
        self._gui_attribute = value
        self._changed.append('gui_attribute')

    def addGuiAttribute(self, key: str, value: str) -> None:
        self._gui_attribute[key] = value
        self._changed.append('gui_attribute')

    def rmGuiAttribute(self, key: str) -> None:
        if self._gui_attribute.get(key) is not None:
            del self._gui_attribute[key]
            self._changed.append('gui_attribute')

    @property
    def label(self) -> Optional[LangString]:
        return self._label

    @label.setter
    def label(self, value: Optional[Union[LangString, str]]) -> None:
        if value is None:
            self._label.empty()  # clear all labels
        else:
            if isinstance(value, LangString):
                self._label = value
            elif isinstance(value, str):
                self._label = LangString(value)
            else:
                raise BaseError('Not a valid LangString')
        self._changed.add('label')


    def addLabel(self, lang: Union[Languages, str], value: str) -> None:
        self._label[lang] = value
        self._changed.add('label')

    def rmLabel(self, lang: Union[Languages, str]) -> None:
        del self._label[lang]
        self._changed.add('label')

    @property
    def comment(self) -> Optional[LangString]:
        return self._comment

    @comment.setter
    def comment(self, value: Optional[LangString]) -> None:
        if value is None:
            self._comment.empty()  # clear all comments!
        else:
            if isinstance(value, LangString):
                self._comment = value
            elif isinstance(value, str):
                self._comment = LangString(value)
            else:
                raise BaseError('Not a valid LangString')
        self._changed.add('comment')

    def addComment(self, lang: Union[Languages, str], value: str) -> None:
        self._commant[lang] = value
        self._changed.add('comment')

    def rmComment(self, lang: Union[Languages, str]) -> None:
        del self._comment[lang]
        self._changed.add('comment')

    @property
    def editable(self) -> bool:
        return self._editable

    @editable.setter
    def editable(self, value: bool) -> None:
        raise BaseError('"editable" cannot be modified!')

    @property
    def linkvalue(self) -> bool:
        return self._linkvalue

    @linkvalue.setter
    def linkvalue(self) -> None:
        raise BaseError('"linkvalue" cannot be modified!')

    @classmethod
    def fromJsonObj(cls, con: Connection, context: Context, json_obj: Any) -> Any:
        if not isinstance(con, Connection):
            raise BaseError('"con"-parameter must be an instance of Connection')
        if not isinstance(context, Context):
            raise BaseError('"context"-parameter must be an instance of Context')
        rdf = context.prefixFromIri("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        rdfs = context.prefixFromIri("http://www.w3.org/2000/01/rdf-schema#")
        owl = context.prefixFromIri("http://www.w3.org/2002/07/owl#")
        xsd = context.prefixFromIri("http://www.w3.org/2001/XMLSchema#")
        knora_api = context.prefixFromIri("http://api.knora.org/ontology/knora-api/v2#")
        salsah_gui = context.prefixFromIri("http://api.knora.org/ontology/salsah-gui/v2#")

        if not (json_obj.get(knora_api + ':isResourceProperty')):
            raise BaseError("This is not a property!")
