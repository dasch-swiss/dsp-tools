import os
import sys
import json
import copy
from pystrict import strict
from typing import List, Set, Dict, Tuple, Optional, Any, Union
from urllib.parse import quote_plus
from pprint import pprint

from knora.models.helpers import Actions, BaseError, Context, LastModificationDate, OntoInfo
from knora.models.connection import Connection
from knora.models.resourceclass import ResourceClass, HasProperty
from knora.models.propertyclass import PropertyClass
from knora.models.project import Project

class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, Context):
            return obj.toJsonObj()
        elif isinstance(obj, OntoInfo):
            return {"iri": obj.iri, "hashtag": obj.hashtag}
        return json.JSONEncoder.default(self, obj)


"""
This model implements the handling of ontologies. It is to note that ResourceClasses, PropertyClasses
as well as the assignment of PropertyCLasses to the ResourceClasses (with a given cardinality)
is handeld in "cooperation" with the propertyclass.py (PropertyClass) and resourceclass.py (ResourceClass
and HasProperty) modules.

_Note_: All modifications to an ontology

CREATE:
    * Instantiate a new object of the Ontology class with all required parameters
    * Call the ``create``-method on the instance to create the ontology withing the backend

READ:
    * Instantiate a new object with ``id``(IRI of ontology) given
    * Call the ``read``-method on the instance. Reading the ontology also reads all
      associated PropertyClasses and ResourceClasses as well as the assignments.
    * Access the information that has been provided to the instance

UPDATE:
    * You need an instance of an existing Ontology by reading an instance
    * Change the attributes by assigning the new values
    * Call the ``update```method on the instance

DELETE
    * Instantiate a new objects with ``id``(IRI of group) given, or use any instance that has the id set,
      that is, that You've read before
    * Call the ``delete``-method on the instance

"""
@strict
class Ontology:
    con: Connection
    _id: str
    _project: str
    _name: str
    _label: str
    _comment: str
    _lastModificationDate: LastModificationDate
    _resource_classes: List[ResourceClass]
    _property_classes: List[PropertyClass]
    _context: Context
    _skiplist: List[str]
    changed: Set[str]

    def __init__(self,
                 con:  Connection,
                 id: Optional[str] = None,
                 project: Optional[Union[str, Project]] = None,
                 name: Optional[str] = None,
                 label: Optional[str] = None,
                 comment: Optional[str] = None,
                 lastModificationDate: Optional[Union[str, LastModificationDate]] = None,
                 resource_classes: List[ResourceClass] = None,
                 property_classes: List[PropertyClass] = None,
                 context: Context = None):
        if not isinstance(con, Connection):
            raise BaseError('"con"-parameter must be an instance of Connection')
        self.con = con
        self._id = id
        if isinstance(project, Project):
            self._project = project.id
        else:
            self._project = project
        self._name = name
        self._label = label
        self._comment = comment
        if lastModificationDate is None:
            self._lastModificationDate = None
        elif isinstance(lastModificationDate, LastModificationDate):
            self._lastModificationDate = lastModificationDate
        else:
            self._lastModificationDate = LastModificationDate(lastModificationDate)
        self._resource_classes = resource_classes
        self._property_classes = property_classes
        self._context = context if context is not None else Context()
        self.changed = set()
        self._skiplist = []

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, value: str):
        raise BaseError('Ontology id cannot be modified!')

    @property
    def project(self) -> str:
        return self._project

    @project.setter
    def project(self, value: str):
        raise BaseError("An ontology's project cannot be modified!")

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        raise BaseError("An ontology's name cannot be modified!")

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, value: str):
        self._label = str(value)
        self.changed.add('label')

    @property
    def comment(self):
        return self._comment

    @comment.setter
    def comment(self, value: str):
        self._comment = str(value)
        self.changed.add('comment')

    @property
    def lastModificationDate(self) -> LastModificationDate:
        return self._lastModificationDate

    @lastModificationDate.setter
    def lastModificationDate(self, value: Union[str, LastModificationDate]):
        self._lastModificationDate = LastModificationDate(value)

    @property
    def resource_classes(self) -> List[ResourceClass]:
        return self._resource_classes

    @resource_classes.setter
    def resource_classes(self, value: List[ResourceClass]) -> None:
        self._resource_classes = value

    def addResourceClass(self, resourceclass: ResourceClass, create: bool = False) -> Tuple[int, ResourceClass]:
        if create:
            lmd, resourceclass = resourceclass.create(self._lastModificationDate)
            self.lastModificationDate = lmd
        self._resource_classes.append(resourceclass)
        index = len(self._resource_classes) - 1
        return index, resourceclass

    def updateResourceClass(self, index: int, resourceclass: ResourceClass) -> ResourceClass:
        lmd, resourceclass = resourceclass.update(self._lastModificationDate)
        self._lastModificationDate = lmd
        self._resource_classes[index] = resourceclass
        return resourceclass

    def removeResourceClass(self, index: int, erase: bool = False) -> None:
        if erase:
            lmd = self._resource_classes[index].delete(self._lastModificationDate)
            self._lastModificationDate = lmd
        del self._resource_classes[index]


    @property
    def property_classes(self):
        return self._property_classes

    @property_classes.setter
    def property_classes(self, value: List[PropertyClass]):
        self._property_classes = value

    def addPropertyClass(self, propclass: PropertyClass):
        self._property_classes.append(propclass)

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, value: Context):
        raise BaseError('"Context" cannot be set!')

    @classmethod
    def fromJsonObj(cls, con: Connection, json_obj: Any) -> Tuple[LastModificationDate, 'Ontology']:
        #
        # First let's get the ID (IRI) of the ontology
        #
        id = json_obj.get('@id')
        if id is None:
            raise BaseError('Ontology id is missing')

        #
        # evaluate the JSON-LD context to get the proper prefixes
        #
        context = Context(json_obj.get('@context'))
        onto_name = id.split('/')[-2]
        context.add_context(onto_name, id + '#')
        rdf = context.prefix_from_iri("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        rdfs = context.prefix_from_iri("http://www.w3.org/2000/01/rdf-schema#")
        owl = context.prefix_from_iri("http://www.w3.org/2002/07/owl#")
        xsd = context.prefix_from_iri("http://www.w3.org/2001/XMLSchema#")
        knora_api = context.prefix_from_iri("http://api.knora.org/ontology/knora-api/v2#")
        salsah_gui = context.prefix_from_iri("http://api.knora.org/ontology/salsah-gui/v2#")
        this_onto = context.prefix_from_iri(id + "#")

        label = json_obj.get(rdfs + ':label')
        if label is None:
            raise BaseError('Ontology label is missing')
        comment = json_obj.get(rdfs + ':comment')
        if json_obj.get(knora_api + ':attachedToProject') is None:
            raise BaseError('Ontology not attached to a project')
        if json_obj[knora_api + ':attachedToProject'].get('@id') is None:
            raise BaseError('Ontology not attached to a project')
        project = json_obj[knora_api + ':attachedToProject']['@id']
        tmp = json_obj.get(knora_api + ':lastModificationDate')
        if tmp is not None:
            last_modification_date = LastModificationDate(json_obj.get(knora_api + ':lastModificationDate'))
        else:
            last_modification_date = None
        resource_classes = None
        property_classes = None
        if json_obj.get('@graph') is not None:
            resclasses_obj = list(filter(lambda a: a.get(knora_api + ':isResourceClass') is not None, json_obj.get('@graph')))
            resource_classes = list(map(lambda a: ResourceClass.fromJsonObj(con=con,
                                                                            context=context,
                                                                            json_obj=a), resclasses_obj))
            standoffclasses_obj = list(filter(lambda a: a.get(knora_api + ':isStandoffClass') is not None, json_obj.get('@graph')))
            # ToDo: parse standoff classes

            properties_obj = list(filter(lambda a: a.get(knora_api + ':isResourceProperty') is not None, json_obj.get('@graph')))
            property_classes = list(map(lambda a: PropertyClass.fromJsonObj(con=con,
                                                                            context=context,
                                                                            json_obj=a), properties_obj))
        return last_modification_date, cls(con=con,
                                           id=id,
                                           label=label,
                                           project=project,
                                           name=this_onto,  # TODO: corresponds the prefix always to the ontology name?
                                           comment=comment,
                                           lastModificationDate=last_modification_date,
                                           resource_classes=resource_classes,
                                           property_classes=property_classes,
                                           context=context)

    @classmethod
    def __oneOntologiesFromJsonObj(cls, con: Connection, json_obj: Any, context: Context) -> 'Ontology':
        rdf = context.prefix_from_iri("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        rdfs = context.prefix_from_iri("http://www.w3.org/2000/01/rdf-schema#")
        owl = context.prefix_from_iri("http://www.w3.org/2002/07/owl#")
        xsd = context.prefix_from_iri("http://www.w3.org/2001/XMLSchema#")
        knora_api = context.prefix_from_iri("http://api.knora.org/ontology/knora-api/v2#")
        salsah_gui = context.prefix_from_iri("http://api.knora.org/ontology/salsah-gui/v2#")
        if json_obj.get('@type') != owl + ':Ontology':
            return None
        id = json_obj.get('@id')
        if id is None:
            raise BaseError('Ontology id is missing')
        if json_obj.get(knora_api + ':attachedToProject') is None:
            raise BaseError('Ontology not attached to a project (1)')
        if json_obj[knora_api + ':attachedToProject'].get('@id') is None:
            raise BaseError('Ontology not attached to a project (2)')
        project = json_obj[knora_api + ':attachedToProject']['@id']
        tmp = json_obj.get(knora_api + ':lastModificationDate')
        if tmp is not None:
            last_modification_date = LastModificationDate(json_obj.get(knora_api + ':lastModificationDate'))
        else:
            last_modification_date = None
        label = json_obj.get(rdfs + ':label')
        if label is None:
            raise BaseError('Ontology label is missing')
        comment = json_obj.get(rdfs + ':comment')
        this_onto = id.split('/')[-2]
        context2 = copy.deepcopy(context)
        context2.add_context(this_onto, id)
        return cls(con=con,
                   id=id,
                   label=label,
                   project=project,
                   name=this_onto,
                   comment=comment,
                   lastModificationDate=last_modification_date,
                   context=context2)

    @classmethod
    def allOntologiesFromJsonObj(cls, con: Connection, json_obj: Any) -> List['Ontology']:
        context = Context(json_obj.get('@context'))
        rdf = context.prefix_from_iri("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        rdfs = context.prefix_from_iri("http://www.w3.org/2000/01/rdf-schema#")
        owl = context.prefix_from_iri("http://www.w3.org/2002/07/owl#")
        xsd = context.prefix_from_iri("http://www.w3.org/2001/XMLSchema#")
        knora_api = context.prefix_from_iri("http://api.knora.org/ontology/knora-api/v2#")
        salsah_gui = context.prefix_from_iri("http://api.knora.org/ontology/salsah-gui/v2#")
        ontos: List['Ontology'] = []
        if json_obj.get('@graph') is not None:
            for o in json_obj['@graph']:
                ontos.append(Ontology.__oneOntologiesFromJsonObj(con, o, context))
        else:
            onto = Ontology.__oneOntologiesFromJsonObj(con, json_obj, context)
            if onto is not None:
                ontos.append(onto)
        return ontos

    def toJsonObj(self, action: Actions, last_modification_date: Optional[LastModificationDate] = None) -> Any:
        rdf = self._context.prefix_from_iri("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        rdfs = self._context.prefix_from_iri("http://www.w3.org/2000/01/rdf-schema#")
        owl = self._context.prefix_from_iri("http://www.w3.org/2002/07/owl#")
        xsd = self._context.prefix_from_iri("http://www.w3.org/2001/XMLSchema#")
        knora_api = self._context.prefix_from_iri("http://api.knora.org/ontology/knora-api/v2#")
        salsah_gui = self._context.prefix_from_iri("http://api.knora.org/ontology/salsah-gui/v2#")
        # this_onto = self._context.prefixFromIri(self._id + "#")
        tmp = {}
        if action == Actions.Create:
            if self._name is None:
                raise BaseError('There must be a valid name given!')
            if self._label is None:
                raise BaseError('There must be a valid label given!')
            if self._project is None:
                raise BaseError('There must be a valid project given!')
            tmp = {
                knora_api + ":ontologyName": self._name,
                knora_api + ":attachedToProject": {
                    "@id": self._project
                },
                rdfs + ":label": self._label,
                "@context": self._context.toJsonObj()
            }
            if self._comment is not None:
                tmp[rdfs + ":comment"] = self._comment
        elif action == Actions.Update:
            if last_modification_date is None:
                raise BaseError("'last_modification_date' must be given!")
            if isinstance(last_modification_date, str):
                last_modification_date = LastModificationDate(last_modification_date)
            elif not isinstance(last_modification_date, LastModificationDate):
                raise BaseError("Must be string or LastModificationClass instance!")
            tmp = {
                '@id': self._id,
                rdfs + ':label': self._label,
                knora_api + ':lastModificationDate': last_modification_date.toJsonObj(),
                "@context": self._context.toJsonObj()
            }
            if self._label is not None and 'label' in self.changed:
                tmp[rdfs + ':label'] = self._label
            if self._comment is not None and 'comment in self.changed:':
                tmp[rdfs + ':comment'] = self._comment
        return tmp

    def create(self) -> Tuple[LastModificationDate, 'Ontology']:
        jsonobj = self.toJsonObj(Actions.Create)
        jsondata = json.dumps(jsonobj, cls=SetEncoder)
        result = self.con.post('/v2/ontologies', jsondata)
        return Ontology.fromJsonObj(self.con, result)

    def update(self, last_modification_date: LastModificationDate) -> Tuple[LastModificationDate, 'Ontology']:
        jsonobj = self.toJsonObj(Actions.Update, last_modification_date)
        jsondata = json.dumps(jsonobj, cls=SetEncoder)
        result = self.con.put('/v2/ontologies/metadata', jsondata, 'application/ld+json')
        return Ontology.fromJsonObj(self.con, result)

    def read(self) -> Tuple[LastModificationDate, 'Ontology']:
        result = self.con.get('/v2/ontologies/allentities/' + quote_plus(self._id) + '?allLanguages=true')
        return Ontology.fromJsonObj(self.con, result)

    def delete(self, last_modification_date: LastModificationDate) -> Optional[str]:
        result = self.con.delete('/v2/ontologies/' + quote_plus(self._id), params={'lastModificationDate': str(last_modification_date)})
        return result.get('knora-api:result')

    @staticmethod
    def getAllOntologies(con: Connection) -> List['Ontology']:
        result = con.get('/v2/ontologies/metadata/')
        return Ontology.allOntologiesFromJsonObj(con, result)

    @staticmethod
    def getProjectOntologies(con: Connection, project_id: str) -> List['Ontology']:
        if project_id is None:
            raise BaseError('Project ID must be defined!')
        result = con.get('/v2/ontologies/metadata/' + quote_plus(project_id) + '?allLanguages=true')
        return Ontology.allOntologiesFromJsonObj(con, result)

    @staticmethod
    def getOntologyFromServer(con: Connection, shortcode: str, name: str):
        result = con.get("/ontology/" + shortcode + "/" + name + "/v2")
        return Ontology.fromJsonObj(con, result)

    def createDefinitionFileObj(self):
        ontology = {
            "name": self._name,
            "label": self._label,
            "properties": [],
            "resources": []
        }
        if self._comment is not None:
            ontology["comment"] = self._comment
        for prop in self._property_classes:
            if "knora-api:hasLinkToValue" in prop.superproperties:
                self._skiplist.append(self._name + ":" + prop.name)
                continue
            ontology["properties"].append(prop.createDefinitionFileObj(self.context, self._name))

        for res in self._resource_classes:
            ontology["resources"].append(res.createDefinitionFileObj(self.context, self._name, self._skiplist))

        return ontology

    def print(self) -> None:
        print('Ontology Info:')
        print('  Id:                   {}'.format(self._id))
        print('  Label:                {}'.format(self._label))
        print('  Name:                 {}'.format(self._name))
        print('  Project:              {}'.format(self._project))
        print('  LastModificationDate: {}'.format(str(self._lastModificationDate)))
        print('  Property Classes:')
        if self._property_classes is not None:
            for pc in self._property_classes:
                pc.print(4)
        print('  Resource Classes:')
        if self._resource_classes is not None:
            for rc in self._resource_classes:
                rc.print(4)

