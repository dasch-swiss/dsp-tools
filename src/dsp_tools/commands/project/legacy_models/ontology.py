"""
This model implements the handling of ontologies. It is to note that ResourceClasses, PropertyClasses
as well as the assignment of PropertyCLasses to the ResourceClasses (with a given cardinality)
is handled in "cooperation" with the propertyclass.py (PropertyClass) and resourceclass.py (ResourceClass
and HasProperty) modules.

CREATE:
    * Instantiate a new object of the Ontology class with all required parameters
    * Call the ``create``-method on the instance to create the ontology withing the backend

READ:
    * Instantiate a new object with ``iri``(IRI of ontology) given
    * Call the ``read``-method on the instance. Reading the ontology also reads all
      associated PropertyClasses and ResourceClasses as well as the assignments.
    * Access the information that has been provided to the instance

"""

from __future__ import annotations

import copy
from typing import Any
from typing import Optional
from typing import Union
from urllib.parse import quote_plus

import regex

from dsp_tools.clients.connection import Connection
from dsp_tools.commands.project.legacy_models.context import Context
from dsp_tools.commands.project.legacy_models.helpers import WithId
from dsp_tools.commands.project.legacy_models.model import Model
from dsp_tools.commands.project.legacy_models.project import Project
from dsp_tools.commands.project.legacy_models.propertyclass import PropertyClass
from dsp_tools.commands.project.legacy_models.resourceclass import ResourceClass
from dsp_tools.error.exceptions import BaseError
from dsp_tools.legacy_models.datetimestamp import DateTimeStamp


class Ontology(Model):
    ROUTE: str = "/v2/ontologies"
    METADATA: str = "/metadata/"
    ALL_LANGUAGES: str = "?allLanguages=true"

    _iri: str
    _project: str
    _name: str
    _label: str
    _comment: str
    _lastModificationDate: DateTimeStamp
    _resource_classes: list[ResourceClass]
    _property_classes: list[PropertyClass]
    _context: Context
    _skiplist: list[str]

    def __init__(
        self,
        con: Connection,
        iri: Optional[str] = None,
        project: Optional[Union[str, Project]] = None,
        name: Optional[str] = None,
        label: Optional[str] = None,
        comment: Optional[str] = None,
        lastModificationDate: Optional[Union[str, DateTimeStamp]] = None,
        resource_classes: Optional[list[ResourceClass]] = None,
        property_classes: Optional[list[PropertyClass]] = None,
        context: Context = None,
    ):
        super().__init__(con)
        self._iri = iri
        if isinstance(project, Project):
            self._project = project.iri
        else:
            self._project = project
        self._name = name
        self._label = label
        self._comment = comment
        if lastModificationDate is None:
            self._lastModificationDate = None
        elif isinstance(lastModificationDate, DateTimeStamp):
            self._lastModificationDate = lastModificationDate
        else:
            self._lastModificationDate = DateTimeStamp(lastModificationDate)
        self._resource_classes = resource_classes or []
        self._property_classes = property_classes or []
        self._context = context if context is not None else Context()
        self._skiplist = []

    @property
    def iri(self) -> str:
        return self._iri

    @property
    def project(self) -> str:
        return self._project

    @property
    def name(self) -> str:
        return self._name

    @property
    def label(self) -> str:
        return self._label

    @label.setter
    def label(self, value: str) -> None:
        self._label = str(value)
        self._changed.add("label")

    @property
    def comment(self) -> str:
        return self._comment

    @comment.setter
    def comment(self, value: str) -> None:
        self._comment = str(value)
        self._changed.add("comment")

    @property
    def lastModificationDate(self) -> DateTimeStamp:
        return self._lastModificationDate

    @lastModificationDate.setter
    def lastModificationDate(self, value: Union[str, DateTimeStamp]) -> None:
        self._lastModificationDate = DateTimeStamp(value)

    @property
    def resource_classes(self) -> list[ResourceClass]:
        return self._resource_classes

    @resource_classes.setter
    def resource_classes(self, value: list[ResourceClass]) -> None:
        self._resource_classes = value

    @property
    def property_classes(self) -> list[PropertyClass]:
        return self._property_classes

    @property_classes.setter
    def property_classes(self, value: list[PropertyClass]) -> None:
        self._property_classes = value

    @property
    def context(self) -> Context:
        return self._context

    @classmethod
    def fromJsonObj(cls, con: Connection, json_obj: Any) -> Ontology:
        #
        # First let's get the ID (IRI) of the ontology
        #
        iri = json_obj.get("@id")
        if iri is None:
            raise BaseError("Ontology iri is missing")

        #
        # evaluate the JSON-LD context to get the proper prefixes
        #
        context = Context(json_obj.get("@context"))
        onto_name = iri.split("/")[-2]
        context.add_context(onto_name, iri + "#")
        rdfs = context.prefix_from_iri("http://www.w3.org/2000/01/rdf-schema#")
        knora_api = context.prefix_from_iri("http://api.knora.org/ontology/knora-api/v2#")
        this_onto = context.prefix_from_iri(iri + "#")

        label = json_obj.get(rdfs + ":label")
        if label is None:
            raise BaseError("Ontology label is missing")
        comment = json_obj.get(rdfs + ":comment")
        if json_obj.get(knora_api + ":attachedToProject") is None:
            raise BaseError("Ontology not attached to a project")
        if json_obj[knora_api + ":attachedToProject"].get("@id") is None:
            raise BaseError("Ontology not attached to a project")
        project = json_obj[knora_api + ":attachedToProject"]["@id"]
        tmp = json_obj.get(knora_api + ":lastModificationDate")
        if tmp is not None:
            last_modification_date = DateTimeStamp(json_obj.get(knora_api + ":lastModificationDate"))
        else:
            last_modification_date = None
        resource_classes = None
        property_classes = None
        if json_obj.get("@graph") is not None:
            resclasses_obj = list(
                filter(lambda a: a.get(knora_api + ":isResourceClass") is not None, json_obj.get("@graph"))
            )
            resource_classes = list(
                map(lambda a: ResourceClass.fromJsonObj(con=con, context=context, json_obj=a), resclasses_obj)
            )

            properties_obj = list(
                filter(lambda a: a.get(knora_api + ":isResourceProperty") is not None, json_obj.get("@graph"))
            )
            property_classes = [
                PropertyClass.fromJsonObj(con=con, context=context, json_obj=a)
                for a in properties_obj
                if WithId(a.get(knora_api + ":objectType")).to_string() != "knora-api:LinkValue"
            ]
        return cls(
            con=con,
            iri=iri,
            label=label,
            project=project,
            name=this_onto,
            comment=comment,
            lastModificationDate=last_modification_date,
            resource_classes=resource_classes,
            property_classes=property_classes,
            context=context,
        )

    @classmethod
    def __oneOntologiesFromJsonObj(cls, con: Connection, json_obj: Any, context: Context) -> Ontology:
        rdfs = context.prefix_from_iri("http://www.w3.org/2000/01/rdf-schema#")
        owl = context.prefix_from_iri("http://www.w3.org/2002/07/owl#")
        knora_api = context.prefix_from_iri("http://api.knora.org/ontology/knora-api/v2#")
        if json_obj.get("@type") != owl + ":Ontology":
            return None
        iri = json_obj.get("@id")
        if iri is None:
            raise BaseError("Ontology iri is missing")
        if json_obj.get(knora_api + ":attachedToProject") is None:
            raise BaseError("Ontology not attached to a project (1)")
        if json_obj[knora_api + ":attachedToProject"].get("@id") is None:
            raise BaseError("Ontology not attached to a project (2)")
        project = json_obj[knora_api + ":attachedToProject"]["@id"]
        tmp = json_obj.get(knora_api + ":lastModificationDate")
        if tmp is not None:
            last_modification_date = DateTimeStamp(json_obj.get(knora_api + ":lastModificationDate"))
        else:
            last_modification_date = None
        label = json_obj.get(rdfs + ":label")
        if label is None:
            raise BaseError("Ontology label is missing")
        comment = json_obj.get(rdfs + ":comment")
        this_onto = iri.split("/")[-2]
        context2 = copy.deepcopy(context)
        context2.add_context(this_onto, iri)
        return cls(
            con=con,
            iri=iri,
            label=label,
            project=project,
            name=this_onto,
            comment=comment,
            lastModificationDate=last_modification_date,
            context=context2,
        )

    @classmethod
    def allOntologiesFromJsonObj(cls, con: Connection, json_obj: Any) -> list[Ontology]:
        context = Context(json_obj.get("@context"))
        ontos: list[Ontology] = []
        if json_obj.get("@graph") is not None:
            for o in json_obj["@graph"]:
                ontos.append(Ontology.__oneOntologiesFromJsonObj(con, o, context))
        else:
            onto = Ontology.__oneOntologiesFromJsonObj(con, json_obj, context)
            if onto is not None:
                ontos.append(onto)
        return ontos

    def create(self) -> Ontology:
        jsonobj = self._toJsonObj_create()
        result = self._con.post(Ontology.ROUTE, jsonobj)
        return Ontology.fromJsonObj(self._con, result)

    def _toJsonObj_create(self):
        rdfs = self._context.prefix_from_iri("http://www.w3.org/2000/01/rdf-schema#")
        knora_api = self._context.prefix_from_iri("http://api.knora.org/ontology/knora-api/v2#")
        if self._name is None:
            raise BaseError("There must be a valid name given!")
        if self._label is None:
            raise BaseError("There must be a valid label given!")
        if self._project is None:
            raise BaseError("There must be a valid project given!")
        tmp = {
            knora_api + ":ontologyName": self._name,
            knora_api + ":attachedToProject": {"@id": self._project},
            rdfs + ":label": self._label,
            "@context": self._context.toJsonObj(),
        }
        if self._comment is not None:
            tmp[rdfs + ":comment"] = self._comment
        return tmp

    def read(self) -> Ontology:
        result = self._con.get(Ontology.ROUTE + "/allentities/" + quote_plus(self._iri) + Ontology.ALL_LANGUAGES)
        return Ontology.fromJsonObj(self._con, result)

    @staticmethod
    def getProjectOntologies(con: Connection, project_id: str) -> list[Ontology]:
        if project_id is None:
            raise BaseError("Project ID must be defined!")
        result = con.get(Ontology.ROUTE + Ontology.METADATA + quote_plus(project_id) + Ontology.ALL_LANGUAGES)
        return Ontology.allOntologiesFromJsonObj(con, result)

    @staticmethod
    def getOntologyFromServer(con: Connection, shortcode: str, name: str) -> Ontology:
        if regex.search(r"[0-9A-F]{4}", shortcode):
            result = con.get("/ontology/" + shortcode + "/" + name + "/v2" + Ontology.ALL_LANGUAGES)
        else:
            result = con.get("/ontology/" + name + "/v2" + Ontology.ALL_LANGUAGES)
        return Ontology.fromJsonObj(con, result)

    def createDefinitionFileObj(self) -> dict[str, Any]:
        ontology = {
            "name": self.name,
            "label": self.label,
            "comment": self.comment,
            "properties": [],
            "resources": [],
        }
        if not self.comment:
            ontology.pop("comment")
        for prop in self.property_classes:
            if "knora-api:hasLinkToValue" in prop.superproperties:
                self._skiplist.append(self.name + ":" + prop.name)
                continue
            ontology["properties"].append(prop.createDefinitionFileObj(self.context, self.name))

        for res in self.resource_classes:
            ontology["resources"].append(res.createDefinitionFileObj(self.context, self.name, self._skiplist))

        return ontology
