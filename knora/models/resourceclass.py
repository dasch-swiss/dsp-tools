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
class HasProperty:
    class Ptype(Enum):
        system = 1
        knora = 2
        other = 3

    property: str
    cardinality: Cardinality
    is_inherited: bool
    ptype: Ptype

    def __init__(self, context: Context, jsonld_obj: Any):
        if not isinstance(context, Context):
            raise BaseError('"context"-parameter must be an instance of Context')

        rdf = context.prefixFromIri("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        rdfs = context.prefixFromIri("http://www.w3.org/2000/01/rdf-schema#")
        owl = context.prefixFromIri("http://www.w3.org/2002/07/owl#")
        xsd = context.prefixFromIri("http://www.w3.org/2001/XMLSchema#")
        knora_api = context.prefixFromIri("http://api.knora.org/ontology/knora-api/v2#")
        salsah_gui = context.prefixFromIri("http://api.knora.org/ontology/salsah-gui/v2#")

        if jsonld_obj.get('@type') is None or jsonld_obj.get('@type') != owl + ":Restriction":
            raise BaseError('Expected restriction type')

        #
        # let's get the inherited field...
        #
        tmp = jsonld_obj.get(knora_api + ':isInherited')
        is_inherited = tmp if tmp is not None else False

        #
        # let's get the cardinality
        #
        if jsonld_obj.get(owl + ':cardinality') is not None:
            self.cardinality = Cardinality.C_1
        elif jsonld_obj.get(owl + ':maxCardinality') is not None:
            self.cardinality = Cardinality.C_0_1
        elif jsonld_obj.get(owl + ':minCardinality') is not None:
            if jsonld_obj.get(owl + ':minCardinality') == 0:
                self.cardinality = Cardinality.C_0_n
            elif jsonld_obj.get(owl + ':minCardinality') == 1:
                self.cardinality = Cardinality.C_1_n
            else:
                raise BaseError('Problem with cardinality')
        else:
            pprint(jsonld_obj)
            raise BaseError('Problem with cardinality')

        #
        # Now let's get the property IRI
        #
        if jsonld_obj.get(owl + ':onProperty') is None:
            raise BaseError('No property IRI given')
        p = jsonld_obj[owl + ':onProperty'].get('@id')
        if p is None:
            raise BaseError('No property IRI given')
        pp = p.split(':')
        if pp[0] == rdf or pp[0] == rdfs or pp[0] == owl:
            self.ptype = self.Ptype.system
        elif pp[0] == knora_api:
            self.ptype = self.Ptype.knora
        else:
            self.ptype = self.Ptype.other
        self.property = p

    def print(self, offset: int = 0):
        blank = ' '
        if self.ptype == self.Ptype.system:
            print(f'{blank:>{offset}}Has Property (system)')
        elif self.ptype == self.Ptype.knora:
            print(f'{blank:>{offset}}Has Property (knora)')
        else:
            print(f'{blank:>{offset}}Has Property (project)')
        print(f'{blank:>{offset + 2}}Property: {self.property}')
        print(f'{blank:>{offset + 2}}Cardinality: {self.cardinality.value}')





@strict
class ResourceClass:
    _name: str
    _ontology_id: str
    _superclasses: List[str]
    _label: LangString
    _comment: LangString
    _permissions: str
    _has_properties: [str]
    changed: Set[str]

    def __init__(self,
                 con: Connection,
                 context: Context,
                 name: Optional[str] = None,
                 ontology_id: Optional[str] = None,
                 superclasses: Optional[List[Union['ResourceClass', str]]] = None,
                 label: Optional[Union[LangString, str]] = None,
                 comment: Optional[Union[LangString, str]] = None,
                 permissions: Optional[str] = None,
                 has_properties: Optional[List[str]] = None):
        if not isinstance(con, Connection):
            raise BaseError('"con"-parameter must be an instance of Connection')
        if not isinstance(context, Context):
            raise BaseError('"context"-parameter must be an instance of Context')
        self.con = con
        self._name = name
        self._ontology_id = ontology_id
        if isinstance(superclasses, ResourceClass):
            self._superclasses = list(map(lambda a: a.id, superclasses))
        else:
            self._superclasses = superclasses
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
        self._permissions = permissions
        self._has_properties = has_properties

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
    def superclasses(self) -> Optional[str]:
        return self._superclasses

    @superclasses.setter
    def superclasses(self, value: str) -> None:
        raise BaseError('"superclasses" cannot be modified!')

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
        self.changed.add('label')


    def addLabel(self, lang: Union[Languages, str], value: str) -> None:
        self._label[lang] = value
        self.changed.add('label')

    def rmLabel(self, lang: Union[Languages, str]) -> None:
        del self._label[lang]
        self.changed.add('label')

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
        self.changed.add('comment')

    def addComment(self, lang: Union[Languages, str], value: str) -> None:
        self._commant[lang] = value
        self.changed.add('comment')

    def rmComment(self, lang: Union[Languages, str]) -> None:
        del self._comment[lang]
        self.changed.add('comment')

    @property
    def permissions(self) -> Optional[str]:
        return self._permissions

    @permissions.setter
    def permissions(self, value: str) -> None:
        raise BaseError('"permissions" cannot be modified!')

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

        if not (json_obj.get(knora_api + ':isResourceClass') or json_obj.get(knora_api + ':isStandoffClass')):
            pprint(json_obj)
            raise BaseError("This is not a resource!")

        if json_obj.get('@id') is None:
            raise BaseError('Resource class has no "@id"!')
        tmp_id = json_obj.get('@id').split(':')
        ontology_id = tmp_id[0]
        name = tmp_id[1]
        superclasses_obj = json_obj.get(rdfs + ':subClassOf')
        if superclasses_obj is not None:
            supercls: List[Any] = list(filter(lambda a: a.get('@id') is not None, superclasses_obj))
            superclasses: List[str] = list(map(lambda a: a['@id'], supercls))
            has_props: List[Any] = list(filter(lambda a: a.get('@type') == (owl + ':Restriction'), superclasses_obj))
            has_properties: List[HasProperty] = list(map(lambda a: HasProperty(context, a), has_props))
        else:
            superclasses = None
            has_properties = None

        label = LangString.fromJsonLdObj(json_obj.get(rdfs + ':label'))
        comment = LangString.fromJsonLdObj(json_obj.get(rdfs + ':comment'))
        return cls(con=con,
                   context=context,
                   name=name,
                   ontology_id=ontology_id,
                   superclasses=superclasses,
                   label=label,
                   comment=comment,
                   has_properties=has_properties)

    def print(self, offset: int = 0):
        blank = ' '
        print(f'{blank:>{offset}}Resource Class Info')
        print(f'{blank:>{offset+2}}Name:            {self._name}')
        print(f'{blank:>{offset+2}}Ontology prefix: {self._ontology_id}')
        print(f'{blank:>{offset+2}}Superclasses:')
        if self._superclasses is not None:
            for sc in self._superclasses:
                print(f'{blank:>{offset + 4}}{sc}')
        if self._label is not None:
            print(f'{blank:>{offset + 2}}Labels:')
            self._label.print(offset + 4)
        if self._comment is not None:
            print(f'{blank:>{offset + 2}}Comments:')
            self._comment.print(offset + 4)
        if self._has_properties is not None:
            print(f'{blank:>{offset + 2}}Has properties:')
            if self._has_properties is not None:
                for hp in self._has_properties:
                    hp.print(offset + 4)





