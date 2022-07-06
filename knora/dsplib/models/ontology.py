import copy
import json
import re
from typing import Tuple, Optional, Any, Union
from urllib.parse import quote_plus

from pystrict import strict

from .connection import Connection
from .helpers import Actions, BaseError, Context, LastModificationDate, OntoIri, WithId
from .model import Model
from .project import Project
from .propertyclass import PropertyClass
from .resourceclass import ResourceClass


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, Context):
            return obj.toJsonObj()
        elif isinstance(obj, OntoIri):
            return {"iri": obj.iri, "hashtag": obj.hashtag}
        return json.JSONEncoder.default(self, obj)


"""
This model implements the handling of ontologies. It is to note that ResourceClasses, PropertyClasses
as well as the assignment of PropertyCLasses to the ResourceClasses (with a given cardinality)
is handled in "cooperation" with the propertyclass.py (PropertyClass) and resourceclass.py (ResourceClass
and HasProperty) modules.

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
class Ontology(Model):
    ROUTE: str = '/v2/ontologies'
    METADATA: str = '/metadata/'
    ALL_LANGUAGES: str = '?allLanguages=true'

    _id: str
    _project: str
    _name: str
    _label: str
    _comment: str
    _lastModificationDate: LastModificationDate
    _resource_classes: list[ResourceClass]
    _property_classes: list[PropertyClass]
    _context: Context
    _skiplist: list[str]

    def __init__(self,
                 con: Connection,
                 id: Optional[str] = None,
                 project: Optional[Union[str, Project]] = None,
                 name: Optional[str] = None,
                 label: Optional[str] = None,
                 comment: Optional[str] = None,
                 lastModificationDate: Optional[Union[str, LastModificationDate]] = None,
                 resource_classes: list[ResourceClass] = [],
                 property_classes: list[PropertyClass] = [],
                 context: Context = None):
        super().__init__(con)
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
        self._changed.add('label')

    @property
    def comment(self):
        return self._comment

    @comment.setter
    def comment(self, value: str):
        self._comment = str(value)
        self._changed.add('comment')

    @property
    def lastModificationDate(self) -> LastModificationDate:
        return self._lastModificationDate

    @lastModificationDate.setter
    def lastModificationDate(self, value: Union[str, LastModificationDate]):
        self._lastModificationDate = LastModificationDate(value)

    @property
    def resource_classes(self) -> list[ResourceClass]:
        return self._resource_classes

    @resource_classes.setter
    def resource_classes(self, value: list[ResourceClass]) -> None:
        self._resource_classes = value

    def addResourceClass(self, resourceclass: ResourceClass, create: bool = False) -> Tuple[int, ResourceClass]:
        if create:
            print('Calling resourceclass.create in Ontology.addResourceClass')
            lmd, resourceclass = resourceclass.create(self._lastModificationDate)
            self._lastModificationDate = lmd
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
    def property_classes(self) -> list[PropertyClass]:
        return self._property_classes

    @property_classes.setter
    def property_classes(self, value: list[PropertyClass]):
        self._property_classes = value

    def addPropertyClass(self, propclass: PropertyClass, create: bool = False) -> Tuple[int, ResourceClass]:
        if create:
            lmd, resourceclass = propclass.create(self._lastModificationDate)
            self._lastModificationDate = lmd
        self._property_classes.append(resourceclass)
        index = len(self._property_classes) - 1
        return index, propclass

    def updatePropertyClass(self, index: int, propclass: PropertyClass) -> PropertyClass:
        lmd, propclass = propclass.update(self._lastModificationDate)
        self._lastModificationDate = lmd
        self._property_classes[index] = propclass
        return propclass

    def removePropertyClass(self, index: int, erase: bool = False) -> None:
        if erase:
            lmd = self._property_classes[index].delete(self._lastModificationDate)
            self._lastModificationDate = lmd
        del self._property_classes[index]

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, value: Context):
        raise BaseError('"Context" cannot be set!')

    @classmethod
    def fromJsonObj(cls, con: Connection, json_obj: Any) -> 'Ontology':
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
            resclasses_obj = list(
                filter(lambda a: a.get(knora_api + ':isResourceClass') is not None, json_obj.get('@graph')))
            resource_classes = list(map(lambda a: ResourceClass.fromJsonObj(con=con,
                                                                            context=context,
                                                                            json_obj=a), resclasses_obj))
            standoffclasses_obj = list(
                filter(lambda a: a.get(knora_api + ':isStandoffClass') is not None, json_obj.get('@graph')))
            # ToDo: parse standoff classes

            properties_obj = list(
                filter(lambda a: a.get(knora_api + ':isResourceProperty') is not None, json_obj.get('@graph')))
            # property_classes = list(map(lambda a: PropertyClass.fromJsonObj(con=con,
            #                                                                context=context,
            #                                                                json_obj=a), properties_obj))
            property_classes = [PropertyClass.fromJsonObj(con=con, context=context, json_obj=a) for a in properties_obj
                                if WithId(a.get(knora_api + ':objectType')).str() != "knora-api:LinkValue"]
        return cls(con=con,
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
    def allOntologiesFromJsonObj(cls, con: Connection, json_obj: Any) -> list['Ontology']:
        context = Context(json_obj.get('@context'))
        rdf = context.prefix_from_iri("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        rdfs = context.prefix_from_iri("http://www.w3.org/2000/01/rdf-schema#")
        owl = context.prefix_from_iri("http://www.w3.org/2002/07/owl#")
        xsd = context.prefix_from_iri("http://www.w3.org/2001/XMLSchema#")
        knora_api = context.prefix_from_iri("http://api.knora.org/ontology/knora-api/v2#")
        salsah_gui = context.prefix_from_iri("http://api.knora.org/ontology/salsah-gui/v2#")
        ontos: list['Ontology'] = []
        if json_obj.get('@graph') is not None:
            for o in json_obj['@graph']:
                ontos.append(Ontology.__oneOntologiesFromJsonObj(con, o, context))
        else:
            onto = Ontology.__oneOntologiesFromJsonObj(con, json_obj, context)
            if onto is not None:
                ontos.append(onto)
        return ontos

    def toJsonObj(self, action: Actions) -> Any:
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
            if self._lastModificationDate is None:
                raise BaseError("'last_modification_date' must be in ontology!")
            tmp = {
                '@id': self._id,
                rdfs + ':label': self._label,
                knora_api + ':lastModificationDate': self._lastModificationDate.toJsonObj(),
                "@context": self._context.toJsonObj()
            }
            if self._label is not None and 'label' in self._changed:
                tmp[rdfs + ':label'] = self._label
            if self._comment is not None and 'comment' in self._changed:
                tmp[rdfs + ':comment'] = self._comment
        return tmp

    def create(self, dumpjson: Optional[str] = None) -> 'Ontology':
        jsonobj = self.toJsonObj(Actions.Create)
        jsondata = json.dumps(jsonobj, cls=SetEncoder, indent=4)
        result = self._con.post(Ontology.ROUTE, jsondata)
        return Ontology.fromJsonObj(self._con, result)

    def update(self) -> 'Ontology':
        jsonobj = self.toJsonObj(Actions.Update)
        jsondata = json.dumps(jsonobj, cls=SetEncoder, indent=4)
        result = self._con.put(Ontology.ROUTE + '/metadata', jsondata, 'application/ld+json')
        return Ontology.fromJsonObj(self._con, result)

    def read(self) -> 'Ontology':
        result = self._con.get(Ontology.ROUTE + '/allentities/' + quote_plus(self._id) + Ontology.ALL_LANGUAGES)
        return Ontology.fromJsonObj(self._con, result)

    def delete(self) -> Optional[str]:
        result = self._con.delete(Ontology.ROUTE + '/' + quote_plus(self._id),
                                  params={'lastModificationDate': str(self._lastModificationDate)})
        return result.get('knora-api:result')

    @staticmethod
    def getAllOntologies(con: Connection) -> list['Ontology']:
        result = con.get(Ontology.ROUTE + Ontology.METADATA)
        return Ontology.allOntologiesFromJsonObj(con, result)

    @staticmethod
    def getProjectOntologies(con: Connection, project_id: str) -> list['Ontology']:
        if project_id is None:
            raise BaseError('Project ID must be defined!')
        result = con.get(Ontology.ROUTE + Ontology.METADATA + quote_plus(project_id) + Ontology.ALL_LANGUAGES)
        return Ontology.allOntologiesFromJsonObj(con, result)

    @staticmethod
    def getOntologyFromServer(con: Connection, shortcode: str, name: str) -> 'Ontology':
        if re.search(r'[0-9A-F]{4}', shortcode):
            result = con.get("/ontology/" + shortcode + "/" + name + "/v2" + Ontology.ALL_LANGUAGES)
        else:
            result = con.get("/ontology/" + name + "/v2" + Ontology.ALL_LANGUAGES)
        return Ontology.fromJsonObj(con, result)

    def createDefinitionFileObj(self):
        ontology = {
            "name": self.name,
            "label": self.label,
            "properties": [],
            "resources": []
        }
        if self.comment:
            ontology["comment"] = self.comment
        for prop in self.property_classes:
            if "knora-api:hasLinkToValue" in prop.superproperties:
                self.skiplist.append(self.name + ":" + prop.name)
                continue
            ontology["properties"].append(prop.createDefinitionFileObj(self.context, self.name))

        for res in self.resource_classes:
            ontology["resources"].append(res.createDefinitionFileObj(self.context, self.name, self._skiplist))

        return ontology

    def print(self, short: bool = True) -> None:
        print('Ontology Info:')
        print('  Id:                   {}'.format(self._id))
        print('  Label:                {}'.format(self._label))
        print('  Name:                 {}'.format(self._name))
        print('  Project:              {}'.format(self._project))
        print('  LastModificationDate: {}'.format(str(self._lastModificationDate)))
        if not short:
            print('  Property Classes:')
            if self._property_classes:
                for pc in self._property_classes:
                    pc.print(4)
            print('  Resource Classes:')
            if self._resource_classes:
                for rc in self._resource_classes:
                    rc.print(4)
