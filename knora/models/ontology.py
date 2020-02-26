import os
import sys
import json
from pystrict import strict
from typing import List, Set, Dict, Tuple, Optional, Any, Union
from urllib.parse import quote_plus
from pprint import pprint

path = os.path.abspath(os.path.dirname(__file__))
(head, tail)  = os.path.split(path)
if not head in sys.path:
    sys.path.append(head)
if not path in sys.path:
    sys.path.append(path)

from helpers import Languages, Actions, BaseError, Context
from connection import Connection
from resourceclass import ResourceClass, HasProperty

class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, Context):
            return obj.toJsonObj()
        return json.JSONEncoder.default(self, obj)


@strict
class Ontology:
    con: Connection
    _id: str
    _project: str
    _name: str
    _label: str
    _lastModificationDate: str
    _resource_classes: List[ResourceClass]
    _context: Context
    changed: Set[str]

    def __init__(self,
                 con:  Connection,
                 id: Optional[str] = None,
                 project: Optional[str] = None,
                 name: Optional[str] = None,
                 label: Optional[str] = None,
                 lastModificationDate: Optional[str] = None,
                 resource_classes: List[ResourceClass] = None,
                 context: Context = None):
        if not isinstance(con, Connection):
            raise BaseError('"con"-parameter must be an instance of Connection')
        self.con = con
        self._id = id
        self._project = project
        self._name = name
        self._label = label
        self._lastModificationDate = lastModificationDate
        self._resource_classes = resource_classes if isinstance(resource_classes, ResourceClass) else None
        self._context = context if context is not None else Context()
        self.changed = set()

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value: str):
        raise BaseError('Ontology id cannot be modified!')

    @property
    def project(self):
        return self._project

    @project.setter
    def project(self, value: str):
        raise BaseError("An ontology's project cannot be modified!")

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value: str):
        raise BaseError("An ontology's project cannot be modified!")

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, value: str):
        self._label = str(value)
        self.changed.add('label')

    @property
    def lastModificationDate(self):
        return self._lastModificationDate

    @lastModificationDate.setter
    def lastModificationDate(self, value: str):
        raise BaseError("An ontology's lastModificationDate cannot be modified!")

    @property
    def resource_classes(self):
        return self._resource_classes

    @resource_classes.setter
    def resource_classes(self, value: List[ResourceClass]):
        raise BaseError('"resource_classes cannot be set!')

    @classmethod
    def fromJsonObj(cls, con: Connection, json_obj: Any) -> Any:
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
        rdf = context.prefixFromIri("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        rdfs = context.prefixFromIri("http://www.w3.org/2000/01/rdf-schema#")
        owl = context.prefixFromIri("http://www.w3.org/2002/07/owl#")
        xsd = context.prefixFromIri("http://www.w3.org/2001/XMLSchema#")
        knora_api = context.prefixFromIri("http://api.knora.org/ontology/knora-api/v2#")
        salsah_gui = context.prefixFromIri("http://api.knora.org/ontology/salsah-gui/v2#")
        this_onto = context.prefixFromIri(id + "#")

        label = json_obj.get(rdfs + ':label')
        if label is None:
            raise BaseError('Ontology label is missing')
        if json_obj.get(knora_api + ':attachedToProject') is None:
            raise BaseError('Ontology not attached to a project')
        if json_obj[knora_api + ':attachedToProject'].get('@id') is None:
            raise BaseError('Ontology not attached to a project')
        project = json_obj[knora_api + ':attachedToProject']['@id']
        last_modification_date = json_obj.get(knora_api + ':lastModificationDate')
        if last_modification_date is None:
            raise BaseError('Ontology has no lastModificationDate!')
        if json_obj.get('@graph') is not None:
            resclasses_obj = list(filter(lambda a: a.get(knora_api + ':isResourceClass') is not None, json_obj.get('@graph')))
            resource_classes = list(map(lambda a: ResourceClass.fromJsonObj(con=con,
                                                                            context=context,
                                                                            json_obj=a), resclasses_obj))
        else:
            resource_classes = None
        return cls(con=con,
                   id=id,
                   label=label,
                   project=project,
                   lastModificationDate=last_modification_date,
                   resource_classes=resource_classes,
                   context=context)

    def toJsonObj(self, action: Actions) -> Any:
        rdf = self._context.prefixFromIri("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        rdfs = self._context.prefixFromIri("http://www.w3.org/2000/01/rdf-schema#")
        owl = self._context.prefixFromIri("http://www.w3.org/2002/07/owl#")
        xsd = self._context.prefixFromIri("http://www.w3.org/2001/XMLSchema#")
        knora_api = self._context.prefixFromIri("http://api.knora.org/ontology/knora-api/v2#")
        salsah_gui = self._context.prefixFromIri("http://api.knora.org/ontology/salsah-gui/v2#")
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
                "@context": self._context
            }
        elif action == Actions.Update:
            if self._label is not None and 'label' in self.changed:
                tmp = {
                    '@id': self._id,
                    rdfs + ':label': self._label,
                    # ToDo: Change to dateTimeStamp in version 12 of Knora API!!!
                    #knora_api + ':lastModificationDate': {
                    #    "@type": xsd + ":dateTimeStamp",
                    #    "@value": self._lastModificationDate
                    #},
                    knora_api + ':lastModificationDate': self._lastModificationDate,
                    "@context": self._context.toJsonObj()
                }
        return tmp

    def create(self) -> 'Ontology':
        jsonobj = self.toJsonObj(Actions.Create)
        jsondata = json.dumps(jsonobj, cls=SetEncoder)
        result = self.con.post('/v2/ontologies', jsondata)
        return Ontology.fromJsonObj(self.con, result)

    def update(self) -> Union['Ontology', None]:
        jsonobj = self.toJsonObj(Actions.Update)
        if jsonobj:
            jsondata = json.dumps(jsonobj, cls=SetEncoder)
            result = self.con.put('/v2/ontologies/metadata', jsondata, 'application/ld+json')
            return Ontology.fromJsonObj(self.con, result)
        else:
            return None

    def read(self) -> 'Ontology':
        result = self.con.get('/v2/ontologies/allentities/' + quote_plus(self._id))
        return Ontology.fromJsonObj(self.con, result)

    def delete(self) -> Optional[str]:
        result = self.con.delete('/v2/ontologies/' + quote_plus(self._id), params={'lastModificationDate': self._lastModificationDate})
        return result.get('knora-api:result')

    @staticmethod
    def getProjectOntologies(con: Connection, project_id: str) -> List['Ontology']:
        if project_id is None:
            raise BaseError('Project ID must be defined!')
        result = con.get('/v2/ontologies/metadata/' + quote_plus(project_id))
        ontos = []
        if '@graph' in result:  # multiple ontologies
            ontos = list(map(lambda a: Ontology.fromJsonObj(con, a), result['@graph']))
        elif '@id' in result:  # single ontology
            ontos[Ontology.fromJsonObj(con, result)]
        else:
            raise BaseError('Something went wrong....!')
        return ontos

    def print(self) -> None:
        print('Ontology Info:')
        print('  Id:                   {}'.format(self._id))
        print('  Label:                {}'.format(self._label))
        print('  Project:              {}'.format(self._project))
        print('  LastModificationDate: {}'.format(self._lastModificationDate))

