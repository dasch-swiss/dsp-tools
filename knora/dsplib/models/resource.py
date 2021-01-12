import json
import re
from dataclasses import dataclass
from enum import Enum, unique
from urllib.parse import quote_plus

from pystrict import strict
from rfc3987 import parse
from typing import List, Set, Dict, Tuple, Optional, Any, Union, Type
from copy import deepcopy

from .group import Group
from .langstring import LangString
from .helpers import OntoInfo, Actions, BaseError, Cardinality, Context
from .connection import Connection
from .model import Model
from .project import Project
from .listnode import ListNode
from .ontology import Ontology
from .propertyclass import PropertyClass
from .resourceclass import ResourceClass, HasProperty
from .permission import PermissionValue, PermissionsIterator, Permissions
from .value import KnoraStandoffXml, Value, TextValue, ColorValue, DateValue, DecimalValue, GeomValue, GeonameValue, \
    IntValue, BooleanValue, UriValue, TimeValue, IntervalValue, ListValue, LinkValue, fromJsonLdObj


from pprint import pprint


class KnoraStandoffXmlEncoder(json.JSONEncoder):
    """Classes used as wrapper for knora standoff-XML"""
    def default(self, obj) -> str:
        if isinstance(obj, KnoraStandoffXml):
            return '<?xml version="1.0" encoding="UTF-8"?>\n<text>' + obj.getXml() + '</text>'
        elif isinstance(obj, OntoInfo):
            return obj.iri + "#" if obj.hashtag else ""
        return json.JSONEncoder.default(self, obj)

@dataclass
class Propinfo:
    valtype: Type
    cardinality: Cardinality
    gui_order: int
    attributes: Optional[str] = None


@strict
class ResourceInstance(Model):
    baseclasses_with_bitstream: Set[str] = {
        'StillImageRepresentation',
        'AudioRepresentation',
        'DocumentRepresentation',
        'MovingImageRepresentation',
        'DDDRepresentation',
        'TextRepresentation'}
    _iri: Union[str, None]
    _ark: Union[str, None]
    _vark: Union[str, None]
    _label: Union[str, None]
    _permissions: Union[Permissions, None]
    _upermission: Union[PermissionValue, None]
    _bitstream: Union[str, None]
    _values: Union[Dict[Value, List[Value]], None]

    def __init__(self,
                 con: Connection,
                 iri: Optional[str] = None,
                 ark: Optional[str] = None,
                 vark: Optional[str] = None,
                 label: Optional[str] = None,
                 permissions: Optional[Permissions] = None,
                 upermission: Optional[PermissionValue] = None,
                 bitstream: Optional[str] = None,
                 values: Optional[Dict[str, Union[str, List[str], Dict[str, str], List[Dict[str,str]], Value, List[Value]]]] = None):
        super().__init__(con)
        self._iri = iri
        self._label = label
        self._ark = ark
        self._vark = vark
        self._permissions = permissions
        self._upermission = upermission

        if self.baseclass in self.baseclasses_with_bitstream and bitstream is None:
            raise BaseError("The baseclass \"{}\" requires a bitstream value!".format(self.baseclass))
        if self.baseclass not in self.baseclasses_with_bitstream and bitstream is not None:
            raise BaseError("The baseclass \"{}\" does not allow a bitstream value!".format(self.baseclass))
        if self.baseclass in self.baseclasses_with_bitstream and bitstream is not None:
            self._bitstream = bitstream
        else:
            self._bitstream = None

        self._values = {}
        if values:
            self._values = {}
            for propname, propinfo in self.properties.items():
                # if propinfo.valtype is LinkValue:
                vals = values.get(propname)
                if vals is not None:
                    valcnt: int = 0
                    if type(vals) is list:  # we do have several values for this properties
                        self._values[propname] = []
                        for val in vals:
                            if valcnt > 0 and (propinfo.cardinality == Cardinality.C_0_1 or propinfo.cardinality == Cardinality.C_1):
                                raise BaseError("Cardinality does not allow multiple values for \"{}\"!".format(propname))
                            if type(val) is Value:
                                self._values[propname].append(val)
                            elif type(val) is dict:
                                if propinfo.valtype is ListValue:
                                    val['lists'] = self.lists
                                self._values[propname].append(propinfo.valtype(**val))
                            else:
                                if propinfo.valtype is ListValue:
                                    val = {'value': val, 'lists': self.list}
                                self._values[propname].append(propinfo.valtype(val))
                            valcnt = valcnt + 1
                    else:  # we do have only one value for this property
                        if type(vals) is Value:
                            self._values[propname] = vals
                        elif type(vals) is dict:
                            if propinfo.valtype is ListValue:
                                vals['lists'] = self.lists
                            self._values[propname] = propinfo.valtype(**vals)
                        else:
                            if propinfo.valtype is ListValue:
                                vals = {'value': val, 'lists': self.list}
                            self._values[propname] = propinfo.valtype(vals)
                else:
                    if propinfo.cardinality == Cardinality.C_1 or propinfo.cardinality == Cardinality.C_1_n:
                        raise BaseError("Cardinality does require at least one value for \"{}\"!".format(propname))
            for propname in values:
                if self.properties.get(propname) is None:
                    raise BaseError("Property \"{}\" is not part of data model!".format(propname))

    @property
    def iri(self) -> str:
        return self._iri

    @property
    def ark(self) -> str:
        return self._ark

    @property
    def vark(self) -> str:
        return self._vark

    def clone(self) -> 'ResourceInstance':
        return deepcopy(self)

    def fromJsonLdObj(self, con: Connection, jsonld_obj: Any) -> 'ResourceInstance':
        newinstance = self.clone()
        newinstance._iri = jsonld_obj.get('@id')
        resclass = jsonld_obj.get('@type')
        context = Context(jsonld_obj.get('@context'))
        newinstance._label = jsonld_obj.get("rdfs:label")
        newinstance._ark = Value.get_typed_value("knora-api:arkUrl", jsonld_obj)
        newinstance._vark = Value.get_typed_value("knora-api:versionArkUrl", jsonld_obj)
        newinstance._permissions = Permissions.fromString(jsonld_obj.get("knora-api:hasPermissions"))
        newinstance._upermission = PermissionValue[jsonld_obj.get("knora-api:userHasPermission", jsonld_obj)]
        creation_date = Value.get_typed_value("knora-api:creationDate", jsonld_obj)
        user = Value.get_typed_value("knora-api:attachedToUser", jsonld_obj)
        project = Value.get_typed_value("knora-api:attachedToProject", jsonld_obj)
        to_be_ignored = [
            '@id', '@type', '@context', "rdfs:label", "knora-api:arkUrl", "knora-api:versionArkUrl",
            "knora-api:creationDate", "knora-api:attachedToUser", "knora-api:attachedToProject",
            "knora-api:hasPermissions", "knora-api:userHasPermission"
        ]
        if id is None:
            raise BaseError('Resource "id" is missing in JSON-LD from DSP-API')
        type = jsonld_obj.get('@type')
        newinstance._values: Dict[str, Union[Value, List[Value]]] = {}
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
                raise BaseError("Invalid data in JSON-LD: \"{}\" has value class \"{}\"!".format(key, obj.get("@type")))
        return newinstance

    def toJsonLdObj(self, action: Actions) -> Any:
        tmp = {}
        if action == Actions.Create:
            tmp['@type'] = self.classname
            tmp["knora-api:attachedToProject"] = {
                "@id": self.project
            }
            tmp['rdfs:label'] = self._label
            if self._permissions:
                tmp["knora-api:hasPermissions"] = self._permissions.toJsonLdObj()
            if self._bitstream:
                tmp["knora-api:hasStillImageFileValue"] = {
                    "@type": "knora-api:StillImageFileValue",
                    "knora-api:fileValueHasFilename": self._bitstream
                }
            for propname, valtype in self._values.items():
                if type(valtype) is list:
                    if type(valtype[0]) is LinkValue:
                        propname += 'Value'
                    tmp[propname] = []
                    for vt in valtype:
                        tmp[propname].append(vt.toJsonLdObj(action))
                    pass
                else:
                    if type(valtype) is LinkValue:
                        propname += 'Value'
                    tmp[propname] = valtype.toJsonLdObj(action)
            tmp['@context'] = self.context
        else:
            pass
        return tmp

    def create(self):
        jsonobj = self.toJsonLdObj(Actions.Create)
        jsondata = json.dumps(jsonobj, indent=4, separators=(',', ': '), cls=KnoraStandoffXmlEncoder)
        # print(jsondata)
        result = self._con.post('/v2/resources', jsondata)
        newinstance = self.clone()
        newinstance._iri = result['@id']
        newinstance._ark = result['knora-api:arkUrl']['@value']
        newinstance._vark = result['knora-api:versionArkUrl']['@value']
        return newinstance

    def read(self) -> 'ResourceInstance':
        result = self._con.get('/v2/resources/' + quote_plus(self._iri))
        return self.fromJsonLdObj(con=self._con, jsonld_obj=result)


    def update(self):
        pass

    def delete(self):
        pass

    def print(self):
        print('Iri:', self._iri)
        print('Ark:', self._ark)
        print('Vark:', self._vark)
        print('Label:', self._label)
        print('Permissions:', str(self._permissions))
        print('Userpermission:', str(self._upermission))
        for name, val in self._values.items():
            if isinstance(val, list):
                tmp = [str(x) for x in val]
                print(name, ':', " | ".join(tmp))
                pass
            else:
                print(name, ':', str(val))


@strict
class ResourceInstanceFactory:
    _con: Connection
    _project: Project
    _lists = List[ListNode]
    _ontologies = Dict[str, Ontology]
    _ontoname2iri = Dict[str, str]
    _context: Context

    def __init__(self,
                 con: Connection,
                 projident: str):
        self._con = con
        if re.match("^[0-9aAbBcCdDeEfF]{4}$", projident):
            project = Project(con=self._con, shortcode=projident)
        elif re.match("^[\\w-]+$", projident):
            project = Project(con=self._con, shortname=projident)
        elif re.match("^(http)s?://([\\w\\.\\-~]+:?\\d{,4})(/[\\w\\-~]+)+$", projident):
            project = Project(con=self._con, shortname=projident)
        else:
            raise BaseError("Invalid project identification!")
        self._project = project.read()

        tmp = ListNode.getAllLists(con=self._con, project_iri=self._project.id)
        self._lists = []
        for rnode in tmp:
            self._lists.append(rnode.getAllNodes())

        tmp_ontologies = Ontology.getProjectOntologies(con, self._project.id)
        shared_project = Project(con=self._con, shortcode="0000").read()
        shared_ontologies = Ontology.getProjectOntologies(con, shared_project.id)
        tmp_ontologies.extend(shared_ontologies)
        self._ontoname2iri = {x.name: x.id for x in tmp_ontologies}

        ontology_ids = [x.id for x in tmp_ontologies]
        self._ontologies = {}
        self._properties = {}
        self._context = {}
        for onto in ontology_ids:
            oparts = onto.split("/")
            name = oparts[len(oparts) - 2]
            shortcode = oparts[len(oparts) - 3]
            self._ontologies[name] = Ontology.getOntologyFromServer(con=con, shortcode=shortcode, name=name)
            self._properties.update({name + ':' + x.name: x for x in self._ontologies[name].property_classes})
            self._context.update(self._ontologies[name].context)

    @property
    def lists(self) -> List[ListNode]:
        return self._lists

    def get_resclass_names(self) -> List[str]:
        resclass_names: List[str] = []
        for name, onto in self._ontologies.items():
            for resclass in onto.resource_classes:
                resclass_names.append(onto.context.get_prefixed_iri(resclass.id))
        return resclass_names

    def _get_baseclass(self, superclasses: List[str]) -> Union[str, None]:
        for sc in superclasses:
            ontoname, classname = sc.split(':')
            if ontoname == 'knora-api':
                return classname
            o = self._ontologies.get(ontoname)
            if o is None:
                continue
            gaga = [x for x in o.resource_classes if x.name == classname][0]
            return self._get_baseclass(gaga.superclasses)
        return None

    def get_resclass(self, prefixedresclass: str) -> Type:
        prefix, resclass_name = prefixedresclass.split(':')
        resclass = [x for x in self._ontologies[prefix].resource_classes if x.name == resclass_name][0]
        baseclass = self._get_baseclass(resclass.superclasses)
        props: Dict[str, Propinfo] = {}
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
        for propname, has_property in resclass.has_properties.items():
            if has_property.ptype == HasProperty.Ptype.other:
                valtype = switcher.get(self._properties[propname].object)
                if valtype == LinkValue:
                    continue  # we have the Link to the LinkValue which we do not use
                if valtype is None:
                    valtype = LinkValue
                    props[propname] = Propinfo(valtype=valtype,
                                               cardinality=has_property.cardinality,
                                               gui_order=has_property.gui_order,
                                               attributes=self._properties[propname].object)
                else:
                    props[propname] = Propinfo(valtype=valtype,
                                               cardinality=has_property.cardinality,
                                               gui_order=has_property.gui_order)
        return type(resclass_name, (ResourceInstance,), {'project': self._project.id,
                                                         'classname': prefixedresclass,
                                                         'baseclass': baseclass,
                                                         'context': self._context,
                                                         'properties': props,
                                                         'lists': self._lists})


