import json
import re
from dataclasses import dataclass

from pystrict import strict
from rfc3987 import parse
from typing import List, Set, Dict, Tuple, Optional, Any, Union, Type

from .langstring import LangString
from .helpers import Actions, BaseError, Cardinality
from .connection import Connection
from .model import Model
from .project import Project
from .listnode import ListNode
from .ontology import Ontology
from .propertyclass import PropertyClass
from .resourceclass import ResourceClass, HasProperty
from .value import Value, TextValue, ColorValue, DateValue, DecimalValue, GeomValue, GeonameValue, IntValue, \
    BooleanValue, UriValue, TimeValue, IntervalValue, ListValue, LinkValue

from pprint import pprint

#############################################################################################



@dataclass
class Propinfo:
    valtype: Type
    cardinality: Cardinality
    gui_order: int
    attributes: Optional[str] = None


@strict
class ResourceInstance(Model):
    _label: str

    def __init__(self,
                 con: Connection,
                 label: str,
                 values: Dict[str, Union[str, List[str], Value, List[Value]]]):
        super().__init__(con)
        self._label = label
        self._values: Dict[str, List[Value]] = {}
        for propname, propinfo in self.properties.items():
            vals = values.get(propname)
            if vals is not None:
                self._values = []
                valcnt: int = 0
                if type(vals) is list:  # we do have several values for this properties
                    for val in vals:
                        if valcnt > 0 and (propinfo.cardinality == Cardinality.C_0_1 or propinfo.cardinality == Cardinality.C_1):
                            raise BaseError("Cardinality does not allow multiple values for \"{}\"!".format(propname))
                        if type(val) is tuple:
                            self._values[propname] = propinfo.valtype(*val)
                        else:
                            self._values[propname] = propinfo.valtype(val)
                        valcnt = valcnt + 1
                else:  # we do have only one value for this property
                    if type(vals) is tuple:
                        self._values[propname] = propinfo.valtype(*vals)
                    else:
                        self._values[propname] = propinfo.valtype(vals)
            else:
                if propinfo.cardinality == Cardinality.C_1 or propinfo.cardinality == Cardinality.C_1_n:
                    raise BaseError("Cardinality does require at least one value for \"{}\"!".format(propname))

    def create(self):
        pass

    def read(self):
        pass

    def update(self):
        pass

    def delete(self):
        pass


@strict
class ResourceInstanceFactory:
    _con: Connection
    _project: Project
    _lists = List[ListNode]
    _ontologies = Dict[str, Ontology]

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

        self._lists = ListNode.getAllLists(con=self._con, project_iri=self._project.id)

        tmp_ontologies = Ontology.getProjectOntologies(con, self._project.id)
        # ToDo tmp_ontologies = Ontology.getProjectOntologies(con, --SHARED-ONTOLOGY-PROJECT-ID--)
        # ToDo merge...
        ontology_ids = [x.id for x in tmp_ontologies]
        self._ontologies = {}
        self._properties = {}
        for onto in ontology_ids:
            oparts = onto.split("/")
            name = oparts[len(oparts) - 2]
            shortcode = oparts[len(oparts) - 3]
            self._ontologies[name] = Ontology.getOntologyFromServer(con=con, shortcode=shortcode, name=name)
            self._properties.update({name + ':' + x.name: x for x in self._ontologies[name].property_classes})

    def get_resclass_names(self) -> List[str]:
        resclass_names: List[str] = []
        for name, onto in self._ontologies.items():
            for resclass in onto.resource_classes:
                resclass_names.append(onto.context.get_prefixed_iri(resclass.id))
        return resclass_names

    def get_resclass(self, resclass: str) -> Type:
        prefix, resclass_name = resclass.split(':')
        resclass = [x for x in self._ontologies[prefix]._resource_classes if x.name == resclass_name][0]
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
                    return type(resclass_name, (ResourceInstance,), {'properties': props})
                else:
                    props[propname] = Propinfo(valtype=valtype,
                                               cardinality=has_property.cardinality,
                                               gui_order=has_property.gui_order)
        return type(resclass_name, (ResourceInstance,), {'properties': props})



# Lexicon = ResourceInstanceFactory.create_class(project=project, resclass="mls:Lexicon")


