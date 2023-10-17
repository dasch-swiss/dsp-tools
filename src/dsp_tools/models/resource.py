import json
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Optional, Type, Union
from urllib.parse import quote_plus

import regex

from dsp_tools.connection.connection import Connection
from dsp_tools.models.bitstream import Bitstream
from dsp_tools.models.exceptions import BaseError
from dsp_tools.models.helpers import Actions, Cardinality, Context, DateTimeStamp, OntoIri
from dsp_tools.models.listnode import ListNode
from dsp_tools.models.model import Model
from dsp_tools.models.ontology import Ontology
from dsp_tools.models.permission import Permissions, PermissionValue
from dsp_tools.models.project import Project
from dsp_tools.models.resourceclass import HasProperty
from dsp_tools.models.value import (
    BooleanValue,
    ColorValue,
    DateValue,
    DecimalValue,
    GeomValue,
    GeonameValue,
    IntervalValue,
    IntValue,
    KnoraStandoffXml,
    LinkValue,
    ListValue,
    TextValue,
    TimeValue,
    UriValue,
    Value,
    fromJsonLdObj,
)


class KnoraStandoffXmlEncoder(json.JSONEncoder):
    """Classes used as wrapper for DSP standoff-XML"""

    def default(self, o: Any) -> str:
        if isinstance(o, KnoraStandoffXml):
            return '<?xml version="1.0" encoding="UTF-8"?>\n<text>' + str(o) + "</text>"
        elif isinstance(o, OntoIri):
            return o.iri + "#" if o.hashtag else ""
        elif isinstance(o, DateTimeStamp):
            return str(o)
        return json.JSONEncoder.default(self, o)


@dataclass(frozen=True)
class Propinfo:
    valtype: Type
    cardinality: Cardinality
    gui_order: int
    attributes: Optional[str] = None


class ResourceInstance(Model):
    """
    Represents a resource instance
    """

    ROUTE: str = "/v2/resources"

    baseclasses_with_bitstream: set[str] = {
        "StillImageRepresentation",
        "AudioRepresentation",
        "DocumentRepresentation",
        "MovingImageRepresentation",
        "ArchiveRepresentation",
        "DDDRepresentation",
        "TextRepresentation",
    }
    knora_properties: set[str] = {
        "knora-api:hasLinkTo",
        "knora-api:hasColor",
        "knora-api:hasComment",
        "knora-api:hasGeometry",
        "knora-api:isPartOf",
        "knora-api:isRegionOf",
        "knora-api:isAnnotationOf",
        "knora-api:seqnum",
        "knora-api:isSequenceOf",
        "knora-api:hasSequenceBounds",
    }
    _iri: Optional[str]
    _ark: Optional[str]
    _version_ark: Optional[str]
    _creation_date: Optional[DateTimeStamp]
    _label: Optional[str]
    _permissions: Optional[Permissions]
    _user_permission: Optional[PermissionValue]
    _bitstream: Optional[Bitstream]
    _values: Optional[dict[Value, list[Value]]]

    def __init__(
        self,
        con: Connection,
        iri: Optional[str] = None,
        ark: Optional[str] = None,
        version_ark: Optional[str] = None,
        creation_date: Optional[DateTimeStamp] = None,
        label: Optional[str] = None,
        permissions: Optional[Permissions] = None,
        user_permission: Optional[PermissionValue] = None,
        bitstream: Optional[str] = None,
        values: Optional[
            dict[str, Union[str, list[str], dict[str, str], list[dict[str, str]], Value, list[Value]]]
        ] = None,
    ):
        super().__init__(con)
        self._iri = iri
        self._ark = ark
        self._version_ark = version_ark
        self._creation_date = creation_date
        self._label = label
        self._permissions = permissions
        self._user_permission = user_permission

        if self.baseclass in self.baseclasses_with_bitstream and bitstream is None:
            raise BaseError(
                f"ERROR in resource with label '{self._label}': Baseclass '{self.baseclass}' requires a bitstream value"
            )
        if self.baseclass not in self.baseclasses_with_bitstream and bitstream:
            raise BaseError(
                f"ERROR in resource with label '{self._label}': "
                f"Baseclass '{self.baseclass}' does not allow a bitstream value"
            )
        if self.baseclass in self.baseclasses_with_bitstream and bitstream:
            self._bitstream = bitstream
        else:
            self._bitstream = None

        self._values = {}
        if values:
            for property_name, property_info in self.properties.items():
                cardinality = property_info.cardinality
                value_type = property_info.valtype
                value = values.get(property_name)
                if value:
                    # property has multiple values
                    if isinstance(value, list):
                        self._values[property_name] = []
                        for val in value:
                            # check if cardinality allows multiple values for a property
                            if cardinality == Cardinality.C_0_1 or cardinality == Cardinality.C_1:
                                raise BaseError(
                                    f"ERROR in resource with label '{self._label}': "
                                    f"Ontology does not allow multiple values for '{property_name}'"
                                )

                            if isinstance(val, Value):
                                self._values[property_name].append(val)

                            elif isinstance(val, dict):
                                if value_type is ListValue:
                                    val["lists"] = self.lists
                                self._values[property_name].append(value_type(**val))

                            else:
                                if value_type is ListValue:
                                    val = {"value": val, "lists": self.lists}
                                self._values[property_name].append(value_type(val))
                    # property has one value
                    else:
                        if isinstance(value, Value):
                            self._values[property_name] = value

                        elif isinstance(value, dict):
                            if value_type is ListValue:
                                value["lists"] = self.lists
                            self._values[property_name] = value_type(**value)

                        else:
                            if value_type is ListValue:
                                value = {"value": value, "lists": self.lists}
                                self._values[property_name] = value_type(**value)
                            else:
                                self._values[property_name] = value_type(value)
                else:
                    if cardinality == Cardinality.C_1 or cardinality == Cardinality.C_1_n:
                        raise BaseError(
                            f"ERROR in resource with label '{self._label}': "
                            f"The ontology requires at least one value for '{property_name}'"
                        )

            for property_name in values:
                if property_name not in self.knora_properties and not self.properties.get(property_name):
                    raise BaseError(
                        f"ERROR in resource with label '{self._label}': "
                        f"Property '{property_name}' is not part of ontology"
                    )

    def value(self, item: Any) -> Optional[list[Value]]:
        if self._values.get(item):
            value = self._values[item]

            # value has multiple values
            if isinstance(value, list):
                return [x.value for x in value]
            else:
                return value.value
        else:
            return None

    @property
    def label(self) -> str:
        return self._label

    @property
    def iri(self) -> str:
        return self._iri

    @property
    def ark(self) -> str:
        return self._ark

    @property
    def creation_date(self) -> Optional[DateTimeStamp]:
        return self._creation_date

    def clone(self) -> "ResourceInstance":
        return deepcopy(self)

    def fromJsonLdObj(self, jsonld_obj: dict[str, Any]) -> "ResourceInstance":
        newinstance = self.clone()
        newinstance._iri = jsonld_obj.get("@id")
        newinstance._label = jsonld_obj.get("rdfs:label")
        newinstance._ark = Value.get_typed_value("knora-api:arkUrl", jsonld_obj)
        newinstance._version_ark = Value.get_typed_value("knora-api:versionArkUrl", jsonld_obj)
        newinstance._permissions = Permissions.fromString(jsonld_obj.get("knora-api:hasPermissions"))
        newinstance._user_permission = PermissionValue[jsonld_obj.get("knora-api:userHasPermission", jsonld_obj)]
        to_be_ignored = [
            "@id",
            "@type",
            "@context",
            "rdfs:label",
            "knora-api:arkUrl",
            "knora-api:versionArkUrl",
            "knora-api:creationDate",
            "knora-api:attachedToUser",
            "knora-api:attachedToProject",
            "knora-api:hasPermissions",
            "knora-api:userHasPermission",
        ]
        if id is None:
            raise BaseError('Resource "id" is missing in JSON-LD from DSP-API')
        newinstance._values: dict[str, Union[Value, list[Value]]] = {}
        for key, obj in jsonld_obj.items():
            if key in to_be_ignored:
                continue
            try:
                if isinstance(obj, list):
                    newinstance._values[key] = []
                    for o in obj:
                        newinstance._values[key].append(fromJsonLdObj(o))
                else:
                    newinstance._values[key] = fromJsonLdObj(obj)
            except KeyError as kerr:
                raise BaseError(f'Invalid data in JSON-LD: "{key}" has value class "{obj.get("@type")}"!') from kerr
        return newinstance

    def toJsonLdObj(self, action: Actions) -> Any:
        tmp = {}
        if action == Actions.Create:
            # if a custom IRI is provided, use it
            if self._iri:
                tmp["@id"] = self._iri
            tmp["@type"] = self.classname
            tmp["knora-api:attachedToProject"] = {"@id": self.project}
            tmp["rdfs:label"] = self._label

            if self._permissions:
                tmp["knora-api:hasPermissions"] = self._permissions.toJsonLdObj()

            if self._bitstream:
                bitstream_attributes = {"knora-api:fileValueHasFilename": self._bitstream["internal_file_name"]}

                permissions = self._bitstream.get("permissions")
                if permissions:
                    bitstream_attributes["knora-api:hasPermissions"] = permissions.toJsonLdObj()

                if self.baseclass == "StillImageRepresentation":
                    bitstream_attributes["@type"] = "knora-api:StillImageFileValue"
                    tmp["knora-api:hasStillImageFileValue"] = bitstream_attributes
                elif self.baseclass == "DocumentRepresentation":
                    bitstream_attributes["@type"] = "knora-api:DocumentFileValue"
                    tmp["knora-api:hasDocumentFileValue"] = bitstream_attributes
                elif self.baseclass == "TextRepresentation":
                    bitstream_attributes["@type"] = "knora-api:TextFileValue"
                    tmp["knora-api:hasTextFileValue"] = bitstream_attributes
                elif self.baseclass == "AudioRepresentation":
                    bitstream_attributes["@type"] = "knora-api:AudioFileValue"
                    tmp["knora-api:hasAudioFileValue"] = bitstream_attributes
                elif self.baseclass == "ArchiveRepresentation":
                    bitstream_attributes["@type"] = "knora-api:ArchiveFileValue"
                    tmp["knora-api:hasArchiveFileValue"] = bitstream_attributes
                elif self.baseclass == "MovingImageRepresentation":
                    bitstream_attributes["@type"] = "knora-api:MovingImageFileValue"
                    tmp["knora-api:hasMovingImageFileValue"] = bitstream_attributes
                else:
                    raise BaseError(f"Baseclass '{self.baseclass}' not yet supported!")

            for property_name, value in self._values.items():
                # if the property has several values
                if isinstance(value, list):
                    if isinstance(value[0], LinkValue):
                        property_name += "Value"
                    # append all values to that property
                    tmp[property_name] = []
                    for vt in value:
                        tmp[property_name].append(vt.toJsonLdObj(action))
                # if property is a link
                elif isinstance(value, LinkValue):
                    property_name += "Value"
                    tmp[property_name] = value.toJsonLdObj(action)
                else:
                    tmp[property_name] = value.toJsonLdObj(action)

            tmp["@context"] = self.context

            if self._creation_date:
                tmp["knora-api:creationDate"] = {"@type": "xsd:dateTimeStamp", "@value": self._creation_date}
        return tmp

    def create(self) -> "ResourceInstance":
        jsonobj = self.toJsonLdObj(Actions.Create)
        jsondata = json.dumps(jsonobj, indent=4, separators=(",", ": "), cls=KnoraStandoffXmlEncoder)
        result = self._con.post(ResourceInstance.ROUTE, jsondata)
        newinstance = self.clone()
        newinstance._iri = result["@id"]
        newinstance._ark = result["knora-api:arkUrl"]["@value"]
        newinstance._version_ark = result["knora-api:versionArkUrl"]["@value"]
        return newinstance

    def read(self) -> "ResourceInstance":
        result = self._con.get(ResourceInstance.ROUTE + "/" + quote_plus(self._iri))
        return self.fromJsonLdObj(result)

    def update(self):
        pass

    def delete(self):
        pass


class ResourceInstanceFactory:
    _con: Connection
    _project: Project
    _lists = list[ListNode]
    _ontologies = dict[str, Ontology]
    _context: Context

    def __init__(self, con: Connection, projident: str) -> None:
        self._con = con
        if regex.match("^[0-9a-fA-F]{4}$", projident):
            project = Project(con=con, shortcode=projident)
        elif regex.match("^[\\w-]+$", projident):
            project = Project(con=con, shortname=projident)
        elif regex.match("^(http)s?://([\\w\\.\\-~]+:?\\d{,4})(/[\\w\\-~]+)+$", projident):
            project = Project(con=con, shortname=projident)
        else:
            raise BaseError("Invalid project identification!")
        self._project = project.read()

        self._lists = [x.getAllNodes() for x in ListNode.getAllLists(con=con, project_iri=self._project.iri)]

        tmp_ontologies = Ontology.getProjectOntologies(con=con, project_id=self._project.iri)
        shared_project = Project(con=con, shortcode="0000").read()
        shared_ontologies = Ontology.getProjectOntologies(con=con, project_id=shared_project.iri)
        tmp_ontologies.extend(shared_ontologies)
        knora_api_onto = [x for x in Ontology.getAllOntologies(con=con) if x.name == "knora-api"][0]
        tmp_ontologies.append(knora_api_onto)

        ontology_ids = [x.iri for x in tmp_ontologies]
        self._ontologies = {}
        self._properties = {}
        self._context = {}
        for onto in ontology_ids:
            oparts = onto.split("/")
            name = oparts[len(oparts) - 2]
            shortcode = oparts[len(oparts) - 3]
            self._ontologies[name] = Ontology.getOntologyFromServer(con=con, shortcode=shortcode, name=name)
            self._properties.update({name + ":" + x.name: x for x in self._ontologies[name].property_classes})
            self._context.update(self._ontologies[name].context)

    @property
    def lists(self) -> list[ListNode]:
        return self._lists

    def get_resclass_names(self) -> list[str]:
        resclass_names: list[str] = []
        for _, onto in self._ontologies.items():
            for resclass in onto.resource_classes:
                resclass_names.append(onto.context.get_prefixed_iri(resclass.iri))
        return resclass_names

    def _get_baseclass(self, superclasses: list[str]) -> Union[str, None]:
        for sc in superclasses:
            ontoname, classname = sc.split(":")
            if ontoname == "knora-api":
                return classname
            o = self._ontologies.get(ontoname)
            if o is None:
                continue
            gaga = [x for x in o.resource_classes if x.name == classname][0]
            return self._get_baseclass(gaga.superclasses)
        return None

    def get_resclass_type(self, prefixedresclass: str) -> Type:
        prefix, resclass_name = prefixedresclass.split(":")
        resclass = [x for x in self._ontologies[prefix].resource_classes if x.name == resclass_name][0]
        baseclass = self._get_baseclass(resclass.superclasses)
        props: dict[str, Propinfo] = {}
        switcher = {
            "knora-api:TextValue": TextValue,
            "knora-api:ColorValue": ColorValue,
            "knora-api:DateValue": DateValue,
            "knora-api:DecimalValue": DecimalValue,
            "knora-api:GeomValue": GeomValue,
            "knora-api:GeonameValue": GeonameValue,
            "knora-api:IntValue": IntValue,
            "knora-api:BooleanValue": BooleanValue,
            "knora-api:UriValue": UriValue,
            "knora-api:TimeValue": TimeValue,
            "knora-api:IntervalValue": IntervalValue,
            "knora-api:ListValue": ListValue,
            "knora-api:LinkValue": LinkValue,
        }
        for propname, has_property in resclass.has_properties.items():
            if propname in [
                "knora-api:isAnnotationOf",
                "knora-api:isRegionOf",
                "knora-api:isPartOf",
                "knora-api:hasLinkTo",
                "knora-api:isSequenceOf",
            ]:
                valtype = LinkValue
                props[propname] = Propinfo(
                    valtype=valtype, cardinality=has_property.cardinality, gui_order=has_property.gui_order
                )

            elif propname == "knora-api:hasGeometry":
                valtype = GeomValue
                props[propname] = Propinfo(
                    valtype=valtype, cardinality=has_property.cardinality, gui_order=has_property.gui_order
                )
            elif propname == "knora-api:hasColor":
                valtype = ColorValue
                props[propname] = Propinfo(
                    valtype=valtype, cardinality=has_property.cardinality, gui_order=has_property.gui_order
                )
            elif propname == "knora-api:seqnum":
                valtype = IntValue
                props[propname] = Propinfo(
                    valtype=valtype, cardinality=has_property.cardinality, gui_order=has_property.gui_order
                )
            elif propname == "knora-api:hasComment":
                valtype = TextValue
                props[propname] = Propinfo(
                    valtype=valtype, cardinality=has_property.cardinality, gui_order=has_property.gui_order
                )
            elif propname == "knora-api:hasSequenceBounds":
                valtype = IntervalValue
                props[propname] = Propinfo(
                    valtype=valtype, cardinality=has_property.cardinality, gui_order=has_property.gui_order
                )
            elif has_property.ptype == HasProperty.Ptype.other:
                valtype = switcher.get(self._properties[propname].rdf_object)
                if valtype == LinkValue:
                    continue  # we have the Link to the LinkValue which we do not use
                if valtype is None:
                    valtype = LinkValue
                    props[propname] = Propinfo(
                        valtype=valtype,
                        cardinality=has_property.cardinality,
                        gui_order=has_property.gui_order,
                        attributes=self._properties[propname].rdf_object,
                    )
                else:
                    props[propname] = Propinfo(
                        valtype=valtype, cardinality=has_property.cardinality, gui_order=has_property.gui_order
                    )
        return type(
            resclass_name,
            (ResourceInstance,),
            {
                "project": self._project.iri,
                "classname": prefixedresclass,
                "baseclass": baseclass,
                "context": self._context,
                "properties": props,
                "lists": self._lists,
            },
        )
