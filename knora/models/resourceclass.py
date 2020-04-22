import os
import sys
import json
import re
from pystrict import strict
from typing import List, Set, Dict, Tuple, Optional, Any, Union
from enum import Enum
from urllib.parse import quote_plus
from pprint import pprint

from models.helpers import Actions, BaseError, Context, Cardinality, LastModificationDate
from models.connection import Connection
from models.langstring import Languages, LangStringParam, LangString

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

    con: Connection
    _context: Context
    _ontology_id: str
    _property_id: str
    _reclass_id: str
    _cardinality: Cardinality
    _is_inherited: bool
    _ptype: Ptype
    _changed: Set

    def __init__(self,
                 con: Connection,
                 context: Context,
                 ontology_id: Optional[str] = None,
                 property_id: Optional[str] = None,
                 resclass_id: Optional[str] = None,
                 cardinality: Optional[Cardinality] = None,
                 is_inherited: Optional[bool] = None,
                 ptype: Optional[Ptype] = None):
        if not isinstance(context, Context):
            raise BaseError('"context"-parameter must be an instance of Context')
        self.con = con
        self._context = context
        if ontology_id is not None and '#' not in ontology_id:
            self._ontology_id = context.iriFromPrefix(ontology_id)
        else:
            self._ontology_id = ontology_id
        self._property_id = property_id
        self._resclass_id = resclass_id
        self._cardinality = cardinality
        self._is_inherited = is_inherited
        self._ptype = ptype
        self._changed = set()

    #
    # Here follows a list of getters/setters
    #
    @property
    def ontology_id(self) -> Optional[str]:
        return self._ontology_id

    @ontology_id.setter
    def ontology_id(self, value: str) -> None:
        raise BaseError('"ontology_id" cannot be modified!')

    @property
    def property_id(self) -> Optional[str]:
        return self._property_id

    @property_id.setter
    def property_id(self, value: str) -> None:
        raise BaseError('"property_id" cannot be modified!')

    @property
    def cardinality(self) -> Optional[Cardinality]:
        return self._cardinality

    @property_id.setter
    def cardinality(self, value: Cardinality) -> None:
        self._cardinality = value
        self._changed.append('cardinality')

    @classmethod
    def fromJsonObj(cls, con: Connection, context: Context, jsonld_obj: Any) -> Tuple[str, 'HasProperty']:
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
        cardinality: Cardinality
        if jsonld_obj.get(owl + ':cardinality') is not None:
            cardinality = Cardinality.C_1
        elif jsonld_obj.get(owl + ':maxCardinality') is not None:
            cardinality = Cardinality.C_0_1
        elif jsonld_obj.get(owl + ':minCardinality') is not None:
            if jsonld_obj.get(owl + ':minCardinality') == 0:
                cardinality = Cardinality.C_0_n
            elif jsonld_obj.get(owl + ':minCardinality') == 1:
                cardinality = Cardinality.C_1_n
            else:
                raise BaseError('Problem with cardinality')
        else:
            pprint(jsonld_obj)
            raise BaseError('Problem with cardinality')

        #
        # Now let's get the property IRI
        #
        property_id: str
        ptype: HasProperty.Ptype
        ontology_id: Optional[str] = None
        if jsonld_obj.get(owl + ':onProperty') is None:
            raise BaseError('No property IRI given')
        p = jsonld_obj[owl + ':onProperty'].get('@id')
        if p is None:
            raise BaseError('No property IRI given')
        pp = p.split(':')
        if pp[0] == rdf or pp[0] == rdfs or pp[0] == owl:
            ptype = HasProperty.Ptype.system
        elif pp[0] == knora_api:
            ptype = HasProperty.Ptype.knora
        else:
            ptype = HasProperty.Ptype.other
            ontology_id = context.iriFromPrefix(pp[0])
        property_id = p
        return property_id, cls(con=con,
                                context=context,
                                ontology_id=ontology_id,
                                property_id=property_id,
                                cardinality=cardinality,
                                is_inherited=is_inherited,
                                ptype=ptype)

    def toJsonObj(self, lastModificationDate: LastModificationDate, action: Actions) -> Any:
        tmp = {}
        switcher = {
            Cardinality.C_1: ("owl:cardinality", 1),
            Cardinality.C_0_1: ("owl:maxCardinality", 1),
            Cardinality.C_0_n: ("owl:minCardinality", 0),
            Cardinality.C_1_n: ("owl:minCardinality", 1)
        }
        occurrence = switcher.get(self._cardinality)
        if action == Actions.Create:
            tmp = {
                "@id": self._ontology_id,
                "@type": "owl:Ontology",
                "knora-api:lastModificationDate": lastModificationDate.toJsonObj(),
                "@graph": [{
                    "@id": self._resclass_id,
                    "@type": "owl:Class",
                    "rdfs:subClassOf": {
                        "@type": "owl:Restriction",
                        occurrence[0]: occurrence[1],
                        "owl:onProperty": {
                            "@id": self._property_id
                        }
                    }
                }],
                "@context": self._context.toJsonObj()
            }
        elif action == Actions.Update:
            tmp = {
                "@id": self._ontology_id,
                "@type": "owl:Ontology",
                "knora-api:lastModificationDate": lastModificationDate.toJsonObj(),
                "@graph": [{
                    "@id": self._resclass_id,
                    "@type": "owl:Class",
                    "rdfs:subClassOf": {
                        "@type": "owl:Restriction",
                        occurrence[0]: occurrence[1],
                        "owl:onProperty": {
                            "@id": self._property_id
                        }
                    }
                }],
                "@context": self._context.toJsonObj()
            }
        return tmp

    def create(self, last_modification_date: LastModificationDate) -> Tuple[LastModificationDate, 'ResourceClass']:
        if self._ontology_id is None:
            raise BaseError("Ontology id required")
        if self._property_id is None:
            raise BaseError("Property id required")
        if self._cardinality is None:
            raise BaseError("Cardinality id required")

        jsonobj = self.toJsonObj(last_modification_date, Actions.Create)
        jsondata = json.dumps(jsonobj, cls=SetEncoder, indent=2)
        result = self.con.post('/v2/ontologies/cardinalities', jsondata)
        last_modification_date = LastModificationDate(result['knora-api:lastModificationDate'])
        return last_modification_date, ResourceClass.fromJsonObj(self.con, self._context, result['@graph'])

    def update(self, last_modification_date: LastModificationDate) -> Tuple[LastModificationDate, 'ResourceClass']:
        if self._ontology_id is None:
            raise BaseError("Ontology id required")
        if self._property_id is None:
            raise BaseError("Property id required")
        if self._cardinality is None:
            raise BaseError("Cardinality id required")
        jsonobj = self.toJsonObj(last_modification_date, Actions.Update)
        jsondata = json.dumps(jsonobj, cls=SetEncoder)
        result = self.con.put('/v2/ontologies/cardinalities', jsondata)
        last_modification_date = LastModificationDate(result['knora-api:lastModificationDate'])
        return last_modification_date, ResourceClass.fromJsonObj(self.con, self._context, result['@graph'])

    def delete(self, last_modification_date: LastModificationDate) -> LastModificationDate:
        tmp = self._property_id.split(':')
        iri: str
        if len(tmp) > 1:
            iri = self._context.iriFromPrefix(tmp[0]) + '#' + tmp[1]
        else:
            iri = tmp[0]
        result = self.con.delete('/v2/ontologies/cardinalities/' + quote_plus(iri) + '?lastModificationDate=' + str(last_modification_date))
        return LastModificationDate(result['knora-api:lastModificationDate'])

    def print(self, offset: int = 0):
        blank = ' '
        if self._ptype == HasProperty.Ptype.system:
            print(f'{blank:>{offset}}Has Property (system)')
        elif self._ptype == HasProperty.Ptype.knora:
            print(f'{blank:>{offset}}Has Property (knora)')
        else:
            print(f'{blank:>{offset}}Has Property (project)')
        print(f'{blank:>{offset + 2}}Property: {self._property_id}')
        print(f'{blank:>{offset + 2}}Cardinality: {self._cardinality.value}')
        if self._ptype == HasProperty.Ptype.other:
            print(f'{blank:>{offset + 2}}Ontology_id: {self._ontology_id}')


@strict
class ResourceClass:
    con: Connection
    _context: Context
    _id: str
    _name: str
    _ontology_id: str
    _superclasses: List[str]
    _label: LangString
    _comment: LangString
    _permissions: str
    _has_properties: Dict[str, HasProperty]
    _changed: Set[str]

    def __init__(self,
                 con: Connection,
                 context: Context,
                 id: Optional[str] = None,
                 name: Optional[str] = None,
                 ontology_id: Optional[str] = None,
                 superclasses: Optional[List[Union['ResourceClass', str]]] = None,
                 label: Optional[Union[LangString, str]] = None,
                 comment: Optional[Union[LangString, str]] = None,
                 permissions: Optional[str] = None,
                 has_properties: Optional[Dict[str, HasProperty]] = None):
        if not isinstance(con, Connection):
            raise BaseError('"con"-parameter must be an instance of Connection')
        if not isinstance(context, Context):
            raise BaseError('"context"-parameter must be an instance of Context')
        self.con = con
        self._context = context
        self._id = id
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
    def id(self) -> Optional[str]:
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        raise BaseError('"id" cannot be modified!')

    @property
    def ontology_id(self) -> Optional[str]:
        return self._ontology_id

    @ontology_id.setter
    def ontology_id(self, value: str) -> None:
        raise BaseError('"ontology_id" cannot be modified!')

    @property
    def superclasses(self) -> Optional[List[str]]:
        return self._superclasses

    @superclasses.setter
    def superclasses(self, value: List[str]) -> None:
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
        self._comment[lang] = value
        self._changed.add('comment')

    def rmComment(self, lang: Union[Languages, str]) -> None:
        del self._comment[lang]
        self._changed.add('comment')

    @property
    def permissions(self) -> Optional[str]:
        return self._permissions

    @permissions.setter
    def permissions(self, value: str) -> None:
        raise BaseError('"permissions" cannot be modified!')

    @property
    def has_property(self) -> Dict[str, HasProperty]:
        return self._has_properties

    @has_property.setter
    def has_property(self, value: str) -> None:
        raise BaseError('"has_property" cannot be modified!')

    def getProperty(self, property_id) -> Optional[HasProperty]:
        if self._has_properties is None:
            return None
        else:
            return self._has_properties.get(self._context.getPrefixIri(property_id))

    def addProperty(self, property_id: str, cardinality: Cardinality, last_modification_date: LastModificationDate) -> Optional[LastModificationDate]:
        if self._has_properties.get(property_id) is None:
            latest_modification_date, resclass = HasProperty(con=self.con,
                                                           context=self._context,
                                                           ontology_id=self._ontology_id,
                                                           property_id=property_id,
                                                           resclass_id=self.id,
                                                           cardinality=cardinality).create(last_modification_date)
            hp = resclass.getProperty(property_id)
            self._has_properties[hp.property_id] = hp
            return latest_modification_date
        else:
            return None

    def rmProperty(self, property_id: str, last_modification_date: LastModificationDate):
        HasProperty(con=self.con,
                    context=self._context,
                    ontology_id=self._ontology_id,
                    property_id=property_id,
                    resclass_id=self.id).delete(last_modification_date)

    @classmethod
    def fromJsonObj(cls, con: Connection, context: Context, json_obj: Any) -> Any:
        if isinstance(json_obj, list):
            json_obj = json_obj[0]  # TODO: Is it possible to have more than one element in the list??
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
            raise BaseError("This is not a resource!")

        if json_obj.get('@id') is None:
            raise BaseError('Resource class has no "@id"!')
        tmp_id = json_obj.get('@id').split(':')
        id = context.iriFromPrefix(tmp_id[0]) + '#' + tmp_id[1]
        ontology_id = tmp_id[0]
        name = tmp_id[1]
        superclasses_obj = json_obj.get(rdfs + ':subClassOf')
        if superclasses_obj is not None:
            supercls: List[Any] = list(filter(lambda a: a.get('@id') is not None, superclasses_obj))
            superclasses: List[str] = list(map(lambda a: a['@id'], supercls))
            has_props: List[Any] = list(filter(lambda a: a.get('@type') == (owl + ':Restriction'), superclasses_obj))
            has_properties: Dict[HasProperty] = dict(map(lambda a: HasProperty.fromJsonObj(con, context, a), has_props))
        else:
            superclasses = None
            has_properties = None

        label = LangString.fromJsonLdObj(json_obj.get(rdfs + ':label'))
        comment = LangString.fromJsonLdObj(json_obj.get(rdfs + ':comment'))
        return cls(con=con,
                   context=context,
                   name=name,
                   id=id,
                   ontology_id=ontology_id,
                   superclasses=superclasses,
                   label=label,
                   comment=comment,
                   has_properties=has_properties)

    def toJsonObj(self, lastModificationDate: LastModificationDate, action: Actions, what: Optional[str] = None) -> Any:

        def resolve_resref(resref: str):
            tmp = resref.split(':')
            if len(tmp) > 1:
                if tmp[0]:
                    return {"@id": resref}  # fully qualified name in the form "prefix:name"
                else:
                    return {"@id": self._context.prefixFromIri(self._ontology_id) + ':' + tmp[1]}  # ":name" in current ontology
            else:
                return {"@id": "knora-api:" + resref}  # no ":", must be from knora-api!

        tmp = {}
        exp = re.compile('^http.*')  # It is already a fully IRI
        if exp.match(self._ontology_id):
            resid = self._context.prefixFromIri(self._ontology_id) + ":" + self._name
            ontid = self._ontology_id
        else:
            resid = self._ontology_id + ":" + self._name
            ontid = self._context.iriFromPrefix(self._ontology_id)
        if action == Actions.Create:
            if self._name is None:
                raise BaseError("There must be a valid resource class name!")
            if self._ontology_id is None:
                raise BaseError("There must be a valid ontology_id given!")
            if self._superclasses is None:
                superclasses = [{"@id": "knora-api:Resource"}]
            else:
                superclasses = list(map(resolve_resref, self._superclasses))

            tmp = {
                "@id": ontid,  # self._ontology_id,
                "@type": "owl:Ontology",
                "knora-api:lastModificationDate": lastModificationDate.toJsonObj(),
                "@graph": [{
                    "@id": resid,
                    "@type": "owl:Class",
                    "rdfs:label": self._label.toJsonLdObj(),
                    "rdfs:comment": self._comment.toJsonLdObj(),
                    "rdfs:subClassOf": superclasses
                }],
                "@context": self._context.toJsonObj(),
            }
        elif action == Actions.Update:
            tmp = {
                "@id": ontid,  # self._ontology_id,
                "@type": "owl:Ontology",
                "knora-api:lastModificationDate": lastModificationDate.toJsonObj(),
                "@graph": [{
                    "@id": resid,
                    "@type": "owl:Class",
                }],
                "@context": self._context.toJsonObj(),
            }
            if what == 'label':
                if not self._label.isEmpty() and 'label' in self._changed:
                    tmp['@graph'][0]['rdfs:label'] = self._label.toJsonLdObj()
            if what == 'comment':
                if not self._comment.isEmpty() and 'comment' in self._changed:
                    tmp['@graph'][0]['rdfs:comment'] = self._comment.toJsonLdObj()
        return tmp

    def create(self, last_modification_date: LastModificationDate) -> Tuple[LastModificationDate, 'ResourceClass']:
        jsonobj = self.toJsonObj(last_modification_date, Actions.Create)
        jsondata = json.dumps(jsonobj)
        result = self.con.post('/v2/ontologies/classes', jsondata)
        last_modification_date = LastModificationDate(result['knora-api:lastModificationDate'])
        return last_modification_date, ResourceClass.fromJsonObj(self.con, self._context, result['@graph'])

    def update(self, last_modification_date: LastModificationDate) -> Tuple[LastModificationDate, 'ResourceClass']:
        #
        # Note: Knora is able to change only one thing per call, either label or comment!
        #
        result = None
        something_changed = False
        if 'label' in self._changed:
            jsonobj = self.toJsonObj(last_modification_date, Actions.Update, 'label')
            jsondata = json.dumps(jsonobj, cls=SetEncoder, indent=4)
            result = self.con.put('v2/ontologies/classes', jsondata)
            last_modification_date = LastModificationDate(result['knora-api:lastModificationDate'])
            something_changed = True
        if 'comment' in self._changed:
            jsonobj = self.toJsonObj(last_modification_date, Actions.Update, 'comment')
            jsondata = json.dumps(jsonobj, cls=SetEncoder, indent=4)
            result = self.con.put('v2/ontologies/classes', jsondata)
            last_modification_date = LastModificationDate(result['knora-api:lastModificationDate'])
            something_changed = True
        if something_changed:
            return last_modification_date, ResourceClass.fromJsonObj(self.con, self._context, result['@graph'])
        else:
            return last_modification_date, self

    def delete(self, last_modification_date: LastModificationDate) -> LastModificationDate:
        result = self.con.delete('v2/ontologies/classes/' + quote_plus(self._id) + '?lastModificationDate=' + str(last_modification_date))
        return LastModificationDate(result['knora-api:lastModificationDate'])


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
                for pid, hp in self._has_properties.items():
                    hp.print(offset + 4)





