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

"""
This model implements the handling of resource classes. It contains two classes that work closely together:
    * "HasProperty" deals with the association of Property-instances with the Resource-instances. This association
      is done using the "cardinality"-clause
    *  "ResourceClass" is the main class representing a knora resource class.
"""
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
    _resclass_id: str
    _cardinality: Cardinality
    _gui_order: int
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
                 gui_order: Optional[int] = None,
                 is_inherited: Optional[bool] = None,
                 ptype: Optional[Ptype] = None):
        if not isinstance(context, Context):
            raise BaseError('"context"-parameter must be an instance of Context')
        self.con = con
        self._context = context
        if ontology_id is not None and '#' not in ontology_id:
            self._ontology_id = context.iri_from_prefix(ontology_id)
        else:
            self._ontology_id = ontology_id
        self._property_id = property_id
        self._resclass_id = resclass_id
        self._cardinality = cardinality
        self._gui_order = gui_order
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
    def ontology_id(self, value: Optional[str]) -> None:
        self._ontology_id = value

    @property
    def property_id(self) -> Optional[str]:
        return self._property_id

    @property_id.setter
    def property_id(self, value: str) -> None:
        raise BaseError('"property_id" cannot be modified!')

    @property
    def resclass_id(self) -> Optional[str]:
        return self._resclass_id

    @resclass_id.setter
    def resclass_id(self, value: Optional[str]) -> None:
        self._resclass_id = value

    @property
    def cardinality(self) -> Optional[Cardinality]:
        return self._cardinality

    @cardinality.setter
    def cardinality(self, value: Optional[Cardinality]) -> None:
        self._cardinality = value
        self._changed.add('cardinality')

    @property
    def gui_order(self) -> Optional[int]:
        return self._gui_order

    @gui_order.setter
    def gui_order(self, value: int) -> None:
        self._gui_order = value

    @property
    def ptype(self) -> Ptype:
        return self._ptype

    @classmethod
    def fromJsonObj(cls, con: Connection, context: Context, jsonld_obj: Any) -> Tuple[str, 'HasProperty']:
        #pprint(jsonld_obj)
        if not isinstance(con, Connection):
            raise BaseError('"con"-parameter must be an instance of Connection')
        if not isinstance(context, Context):
            raise BaseError('"context"-parameter must be an instance of Context')

        rdf = context.prefix_from_iri("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        rdfs = context.prefix_from_iri("http://www.w3.org/2000/01/rdf-schema#")
        owl = context.prefix_from_iri("http://www.w3.org/2002/07/owl#")
        xsd = context.prefix_from_iri("http://www.w3.org/2001/XMLSchema#")
        knora_api = context.prefix_from_iri("http://api.knora.org/ontology/knora-api/v2#")
        salsah_gui = context.prefix_from_iri("http://api.knora.org/ontology/salsah-gui/v2#")

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
            ontology_id = context.iri_from_prefix(pp[0])
        property_id = p

        gui_order: int = None
        if jsonld_obj.get(salsah_gui + ':guiOrder') is not None:
            gui_order = jsonld_obj[salsah_gui + ':guiOrder']
        return property_id, cls(con=con,
                                context=context,
                                ontology_id=ontology_id,
                                property_id=property_id,
                                cardinality=cardinality,
                                gui_order=gui_order,
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
        # TODO: self._changed = str()
        return last_modification_date, ResourceClass.fromJsonObj(self.con, self._context, result['@graph'])

    def delete(self, last_modification_date: LastModificationDate) -> LastModificationDate:
        raise BaseError("Cannot remove a single property from a class!")
        # ToDo: Check with Ben if we could add this feature...

    def createDefinitionFileObj(self, context: Context, shortname: str):
        cardinality = {}
        if self._ptype == HasProperty.Ptype.other:
            cardinality["propname"] = context.reduce_iri(self._property_id, shortname)
            cardinality["cardinality"] = self._cardinality.value
            if self._gui_order:
                cardinality["gui_order"] = self._gui_order
        return cardinality

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
        print(f'{blank:>{offset + 2}}Resclass: {self._resclass_id}')


@strict
class ResourceClass:
    """
    This class represents a knora resource class

    Attributes
    ----------

    con : Connection
        A Connection instance to a Knora server

    id : str
        IRI of the ResourceClass [readonly, cannot be modified after creation of instance]

    name: str
        The name of the resource class, e.g. "Book", "Person", "Portait". Usually these names start
        with a capital letter

    ontology_id: str
        The IRI/Id of the ontology this resource class belongs to

    superlcasses: str, List[str]
        This is a list of superclasses for this resource class. Usually a project specific class must at least
        be a subclass of "Resource", but can be subclassed of any other valid resource class. In addition, external
        ontologies may be referenced:
        e.g.:
        ```
        "super": "Resource"

        "super": ":MySpecialTYpe"

        "super": [":MySpecialType", "dcterms:BibliographicResource"]
        ```

    label: language dependent string, that is a dict like {"en": "Biblography", "de": "Literaturverzeichnis"}
        A label (human readable name) for the resource

    comment: language dependent string, that is a dict like {"en": "a comment", "de": "Ein Kommentar"}
        A commentary to further explain what this resource class is used for

    permission: str
        The default permissions to be used if an instance of this resource class is being created

    has_properties: Dict[str, HasProperty]
        Holds a dict with the property names as keys and a HasProperty instance. HasProperty holds
        the information, how this resource class uses this property (basically the cardinality)

    changed: bool
        is set to True, if one of the fields has been chaned by the user (internal use only!)


    Methods
    -------

    addLabel: Add a new label to the resource
        addLabel(self, lang: Union[Languages, str], value: str) -> None

    getProperty: Get information about a property defined for this resource class
        getPropertery(prop_id: str) -> HasProperty
        returns a HasProperty-instance

    addProperty: Add a new property to the resource class
        addProperty(property_id: str, cardinality: Cardinality, last_modification_date: LastModificationDate)
        -> Optional[LastModificationDate]

    updateProperty: Updates the cardinality parameters of the given property with the resource class
        updateProperty(self, property_id: str, cardinality: Cardinality, last_modification_date: LastModificationDate)
        -> Optional[LastModificationDate]
        Please note that the cardinality usually can only be changed to be *less* restrictive!

    create: Create a new resource class on the connected server

    update: Update the information of a resource class on the connected server

    delete: Mark a resource class as deleted (on the connected server)

    createDefinitionFileObj: Create an object suitable for jsonification that conforms the the knora-py ontology tools

    print: Print the content of this class to the console

    """
    con: Connection
    __context: Context
    __id: str
    __name: str
    __ontology_id: str
    __superclasses: List[str]
    __label: LangString
    __comment: LangString
    __permissions: str
    ___has_properties: Dict[str, HasProperty]
    __changed: Set[str]

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
        """
        Create an instance of  ResourceClass

        :param con:
        :param context:
        :param id:
        :param name:
        :param ontology_id:
        :param superclasses:
        :param label:
        :param comment:
        :param permissions:
        :param has_properties:
        """
        if not isinstance(con, Connection):
            raise BaseError('"con"-parameter must be an instance of Connection')
        if not isinstance(context, Context):
            raise BaseError('"context"-parameter must be an instance of Context')
        self.con = con
        self.__context = context
        self.__id = id
        self.__name = name
        self.__ontology_id = ontology_id
        if isinstance(superclasses, ResourceClass):
            self.__superclasses = list(map(lambda a: a.id, superclasses))
        else:
            self.__superclasses = superclasses
        #
        # process label
        #
        if label is not None:
            if isinstance(label, str):
                self.__label = LangString(label)
            elif isinstance(label, LangString):
                self.__label = label
            else:
                raise BaseError('Invalid LangString for label!')
        else:
            self.__label = None
        #
        # process comment
        #
        if comment is not None:
            if isinstance(comment, str):
                self.__comment = LangString(comment)
            elif isinstance(comment, LangString):
                self.__comment = comment
            else:
                raise BaseError('Invalid LangString for comment!')
        else:
            self.__comment = None
        self.__permissions = permissions
        self.___has_properties = has_properties
        self.__changed = set()

    #
    # Here follows a list of getters/setters
    #
    @property
    def name(self) -> Optional[str]:
        return self.__name

    @name.setter
    def name(self, value: str) -> None:
        raise BaseError('"name" cannot be modified!')

    @property
    def id(self) -> Optional[str]:
        return self.__id

    @id.setter
    def id(self, value: str) -> None:
        raise BaseError('"id" cannot be modified!')

    @property
    def ontology_id(self) -> Optional[str]:
        return self.__ontology_id

    @ontology_id.setter
    def ontology_id(self, value: str) -> None:
        raise BaseError('"ontology_id" cannot be modified!')

    @property
    def superclasses(self) -> Optional[List[str]]:
        return self.__superclasses

    @superclasses.setter
    def superclasses(self, value: List[str]) -> None:
        raise BaseError('"superclasses" cannot be modified!')

    @property
    def label(self) -> Optional[LangString]:
        return self.__label

    @label.setter
    def label(self, value: Optional[Union[LangString, str]]) -> None:
        if value is None:
            self.__label.empty()  # clear all labels
        else:
            if isinstance(value, LangString):
                self.__label = value
            elif isinstance(value, str):
                self.__label = LangString(value)
            else:
                raise BaseError('Not a valid LangString')
        self.__changed.add('label')


    def addLabel(self, lang: Union[Languages, str], value: str) -> None:
        self.__label[lang] = value
        self.__changed.add('label')

    def rmLabel(self, lang: Union[Languages, str]) -> None:
        del self.__label[lang]
        self.__changed.add('label')

    @property
    def comment(self) -> Optional[LangString]:
        return self.__comment

    @comment.setter
    def comment(self, value: Optional[LangString]) -> None:
        if value is None:
            self.__comment.empty()  # clear all comments!
        else:
            if isinstance(value, LangString):
                self.__comment = value
            elif isinstance(value, str):
                self.__comment = LangString(value)
            else:
                raise BaseError('Not a valid LangString')
        self.__changed.add('comment')

    def addComment(self, lang: Union[Languages, str], value: str) -> None:
        self.__comment[lang] = value
        self.__changed.add('comment')

    def rmComment(self, lang: Union[Languages, str]) -> None:
        del self.__comment[lang]
        self.__changed.add('comment')

    @property
    def permissions(self) -> Optional[str]:
        return self.__permissions

    @permissions.setter
    def permissions(self, value: str) -> None:
        raise BaseError('"permissions" cannot be modified!')

    @property
    def has_property(self) -> Dict[str, HasProperty]:
        return self.___has_properties

    @has_property.setter
    def has_property(self, value: str) -> None:
        raise BaseError('"has_property" cannot be modified!')

    def getProperty(self, property_id) -> Optional[HasProperty]:
        if self.___has_properties is None:
            return None
        else:
            return self.___has_properties.get(self.__context.get_prefixed_iri(property_id))

    def addProperty(self, property_id: str, cardinality: Cardinality, last_modification_date: LastModificationDate) -> Optional[LastModificationDate]:
        if self.___has_properties.get(property_id) is None:
            latest_modification_date, resclass = HasProperty(con=self.con,
                                                             context=self.__context,
                                                             ontology_id=self.__ontology_id,
                                                             property_id=property_id,
                                                             resclass_id=self.id,
                                                             cardinality=cardinality).create(last_modification_date)
            hp = resclass.getProperty(property_id)
            hp.ontology_id = self.__context.iri_from_prefix(self.__ontology_id)
            hp.resclass_id = self.id
            self.___has_properties[hp.property_id] = hp
            return latest_modification_date
        else:
            raise BaseError("Property already has cardinality in this class!")

    def updateProperty(self, property_id: str, cardinality: Cardinality, last_modification_date: LastModificationDate) -> Optional[LastModificationDate]:
        property_id = self.__context.get_prefixed_iri(property_id)
        if self.___has_properties.get(property_id) is not None:
            has_properties = self.___has_properties[property_id]
            onto_id = has_properties.ontology_id  # save for later user
            rescl_id = has_properties.resclass_id  # save for later user
            has_properties.cardinality = cardinality
            latest_modification_date, resclass = has_properties.update(last_modification_date)
            hp = resclass.getProperty(property_id)
            hp.ontology_id = self.__context.iri_from_prefix(onto_id)  # restore value
            hp.resclass_id = rescl_id  # restore value
            self.___has_properties[hp.property_id] = hp
            return latest_modification_date
        else:
            return last_modification_date

    @classmethod
    def fromJsonObj(cls, con: Connection, context: Context, json_obj: Any) -> Any:
        if isinstance(json_obj, list):
            json_obj = json_obj[0]  # TODO: Is it possible to have more than one element in the list??
        if not isinstance(con, Connection):
            raise BaseError('"con"-parameter must be an instance of Connection')
        if not isinstance(context, Context):
            raise BaseError('"context"-parameter must be an instance of Context')
        rdf = context.prefix_from_iri("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        rdfs = context.prefix_from_iri("http://www.w3.org/2000/01/rdf-schema#")
        owl = context.prefix_from_iri("http://www.w3.org/2002/07/owl#")
        xsd = context.prefix_from_iri("http://www.w3.org/2001/XMLSchema#")
        knora_api = context.prefix_from_iri("http://api.knora.org/ontology/knora-api/v2#")
        salsah_gui = context.prefix_from_iri("http://api.knora.org/ontology/salsah-gui/v2#")

        if not (json_obj.get(knora_api + ':isResourceClass') or json_obj.get(knora_api + ':isStandoffClass')):
            raise BaseError("This is not a resource!")

        if json_obj.get('@id') is None:
            raise BaseError('Resource class has no "@id"!')
        tmp_id = json_obj.get('@id').split(':')
        id = context.iri_from_prefix(tmp_id[0]) + '#' + tmp_id[1]
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
                    return {"@id": self.__context.prefix_from_iri(self.__ontology_id) + ':' + tmp[1]}  # ":name" in current ontology
            else:
                return {"@id": "knora-api:" + resref}  # no ":", must be from knora-api!

        tmp = {}
        exp = re.compile('^http.*')  # It is already a fully IRI
        if exp.match(self.__ontology_id):
            resid = self.__context.prefix_from_iri(self.__ontology_id) + ":" + self.__name
            ontid = self.__ontology_id
        else:
            resid = self.__ontology_id + ":" + self.__name
            ontid = self.__context.iri_from_prefix(self.__ontology_id)
        if action == Actions.Create:
            if self.__name is None:
                raise BaseError("There must be a valid resource class name!")
            if self.__ontology_id is None:
                raise BaseError("There must be a valid ontology_id given!")
            if self.__superclasses is None:
                superclasses = [{"@id": "knora-api:Resource"}]
            else:
                superclasses = list(map(resolve_resref, self.__superclasses))
            if self.__comment is None or self.__comment.isEmpty():
                self.__comment = LangString("no comment available")
            if self.__label is None or self.__label.isEmpty():
                self.__label = LangString("no label available")
            tmp = {
                "@id": ontid,  # self._ontology_id,
                "@type": "owl:Ontology",
                "knora-api:lastModificationDate": lastModificationDate.toJsonObj(),
                "@graph": [{
                    "@id": resid,
                    "@type": "owl:Class",
                    "rdfs:label": self.__label.toJsonLdObj(),
                    "rdfs:comment": self.__comment.toJsonLdObj(),
                    "rdfs:subClassOf": superclasses
                }],
                "@context": self.__context.toJsonObj(),
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
                "@context": self.__context.toJsonObj(),
            }
            if what == 'label':
                if not self.__label.isEmpty() and 'label' in self.__changed:
                    tmp['@graph'][0]['rdfs:label'] = self.__label.toJsonLdObj()
            if what == 'comment':
                if not self.__comment.isEmpty() and 'comment' in self.__changed:
                    tmp['@graph'][0]['rdfs:comment'] = self.__comment.toJsonLdObj()
        return tmp

    def create(self, last_modification_date: LastModificationDate) -> Tuple[LastModificationDate, 'ResourceClass']:
        jsonobj = self.toJsonObj(last_modification_date, Actions.Create)
        jsondata = json.dumps(jsonobj)
        result = self.con.post('/v2/ontologies/classes', jsondata)
        last_modification_date = LastModificationDate(result['knora-api:lastModificationDate'])
        return last_modification_date, ResourceClass.fromJsonObj(self.con, self.__context, result['@graph'])

    def update(self, last_modification_date: LastModificationDate) -> Tuple[LastModificationDate, 'ResourceClass']:
        #
        # Note: Knora is able to change only one thing per call, either label or comment!
        #
        result = None
        something_changed = False
        if 'label' in self.__changed:
            jsonobj = self.toJsonObj(last_modification_date, Actions.Update, 'label')
            jsondata = json.dumps(jsonobj, cls=SetEncoder, indent=4)
            result = self.con.put('v2/ontologies/classes', jsondata)
            last_modification_date = LastModificationDate(result['knora-api:lastModificationDate'])
            something_changed = True
        if 'comment' in self.__changed:
            jsonobj = self.toJsonObj(last_modification_date, Actions.Update, 'comment')
            jsondata = json.dumps(jsonobj, cls=SetEncoder, indent=4)
            result = self.con.put('v2/ontologies/classes', jsondata)
            last_modification_date = LastModificationDate(result['knora-api:lastModificationDate'])
            something_changed = True
        if something_changed:
            return last_modification_date, ResourceClass.fromJsonObj(self.con, self.__context, result['@graph'])
        else:
            return last_modification_date, self

    def delete(self, last_modification_date: LastModificationDate) -> LastModificationDate:
        result = self.con.delete('v2/ontologies/classes/' + quote_plus(self.__id) + '?lastModificationDate=' + str(last_modification_date))
        return LastModificationDate(result['knora-api:lastModificationDate'])

    def createDefinitionFileObj(self, context: Context, shortname: str, skiplist: List[str]):
        resource = {
            "name": self.__name,
            "labels": self.__label.createDefinitionFileObj(),
        }
        if self.__comment:
            resource["comments"] = self.__comment.createDefinitionFileObj()
        if self.__superclasses:
            if len(self.__superclasses) > 1:
                superclasses = []
                for sc in self.__superclasses:
                    superclasses.append(context.reduce_iri(sc, shortname))
            else:
                superclasses = context.reduce_iri(self.__superclasses[0], shortname)
            resource["super"] = superclasses
        if self.___has_properties:
            cardinalities = []
            for pid, hp in self.___has_properties.items():
                if hp.property_id in skiplist:
                    print("Skip ", hp.property_id)
                    continue
                if hp.ptype == HasProperty.Ptype.other:
                    cardinalities.append(hp.createDefinitionFileObj(context, shortname))
            resource["cardinalities"] = cardinalities

        return resource

    def print(self, offset: int = 0):
        blank = ' '
        print(f'{blank:>{offset}}Resource Class Info')
        print(f'{blank:>{offset+2}}Name:            {self.__name}')
        print(f'{blank:>{offset+2}}Ontology prefix: {self.__ontology_id}')
        print(f'{blank:>{offset+2}}Superclasses:')
        if self.__superclasses is not None:
            for sc in self.__superclasses:
                print(f'{blank:>{offset + 4}}{sc}')
        if self.__label is not None:
            print(f'{blank:>{offset + 2}}Labels:')
            self.__label.print(offset + 4)
        if self.__comment is not None:
            print(f'{blank:>{offset + 2}}Comments:')
            self.__comment.print(offset + 4)
        if self.___has_properties is not None:
            print(f'{blank:>{offset + 2}}Has properties:')
            if self.___has_properties is not None:
                for pid, hp in self.___has_properties.items():
                    hp.print(offset + 4)





