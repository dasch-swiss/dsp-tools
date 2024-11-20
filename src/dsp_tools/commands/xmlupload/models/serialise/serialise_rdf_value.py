from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass

from rdflib import RDF
from rdflib import XSD
from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib import Namespace
from rdflib import URIRef

from dsp_tools.utils.date_util import Date
from dsp_tools.utils.date_util import DayMonthYearEra
from dsp_tools.utils.date_util import SingleDate
from dsp_tools.utils.date_util import StartEnd

KNORA_API = Namespace("http://api.knora.org/ontology/knora-api/v2#")


@dataclass
class TransformedValue:
    value: Literal | URIRef
    prop_name: URIRef
    permissions: str | None
    comment: str | None


@dataclass
class RDFPropTypeInfo:
    knora_type: URIRef
    knora_prop: URIRef


rdf_prop_type_mapper = {
    "boolean": RDFPropTypeInfo(KNORA_API.BooleanValue, KNORA_API.booleanValueAsBoolean),
    "color": RDFPropTypeInfo(KNORA_API.ColorValue, KNORA_API.colorValueAsColor),
    "decimal": RDFPropTypeInfo(KNORA_API.DecimalValue, KNORA_API.decimalValueAsDecimal),
    "geometry": RDFPropTypeInfo(KNORA_API.GeomValue, KNORA_API.geometryValueAsGeometry),
    "geoname": RDFPropTypeInfo(KNORA_API.GeonameValue, KNORA_API.geonameValueAsGeonameCode),
    "integer": RDFPropTypeInfo(KNORA_API.IntValue, KNORA_API.intValueAsInt),
    "link": RDFPropTypeInfo(KNORA_API.LinkValue, KNORA_API.linkValueHasTargetIri),
    "list": RDFPropTypeInfo(KNORA_API.ListValue, KNORA_API.listValueAsListNode),
    "simpletext": RDFPropTypeInfo(KNORA_API.TextValue, KNORA_API.valueAsString),
    "time": RDFPropTypeInfo(KNORA_API.TimeValue, KNORA_API.timeValueAsTimeStamp),
    "uri": RDFPropTypeInfo(KNORA_API.UriValue, KNORA_API.uriValueAsUri),
}
# date
# interval
# list
# resptr
# text


@dataclass(frozen=True)
class ValueRDF(ABC):
    resource_bn: BNode
    prop_name: URIRef
    value: Literal | URIRef
    permissions: Literal | None
    comment: Literal | None

    @abstractmethod
    def as_graph(self) -> Graph:
        """Creates the value as rdflib graph"""

    def _get_generic_graph(self, val_bn: BNode) -> Graph:
        g = Graph()
        g.add((self.resource_bn, self.prop_name, val_bn))
        if self.permissions:
            g.add((val_bn, KNORA_API.hasPermissions, self.permissions))
        if self.comment:
            g.add((val_bn, KNORA_API.valueHasComment, self.comment))
        return g


class DateValueRDF(ValueRDF):
    value: Date

    def as_graph(self) -> Graph:
        val_bn = BNode()
        g = self._get_generic_graph(val_bn)
        g.add((val_bn, RDF.type, KNORA_API.DateValue))
        if cal := self.value.calendar.value:
            g.add((val_bn, KNORA_API.dateValueHasCalendar, Literal(cal, datatype=XSD.string)))
        g += self._get_one_date_graph(val_bn, self.value.start, StartEnd.START)
        if self.value.end:
            g += self._get_one_date_graph(val_bn, self.value.end, StartEnd.END)
        return g

    def _get_one_date_graph(self, val_bn: BNode, date: SingleDate, start_end: StartEnd) -> Graph:
        def get_prop(precision: DayMonthYearEra) -> URIRef:
            return KNORA_API[f"dateValueHas{start_end.value}{precision.value}"]

        g = Graph()
        if yr := date.year:
            g.add((val_bn, get_prop(DayMonthYearEra.YEAR), Literal(yr, datatype=XSD.int)))
        if mnt := date.month:
            g.add((val_bn, get_prop(DayMonthYearEra.MONTH), Literal(mnt, datatype=XSD.int)))
        if day := date.day:
            g.add((val_bn, get_prop(DayMonthYearEra.DAY), Literal(day, datatype=XSD.int)))
        if era := date.era:
            g.add((val_bn, get_prop(DayMonthYearEra.ERA), Literal(era, datatype=XSD.string)))
        return g


class IntervalValueValueRDF(ValueRDF):
    """An IntervalValue to be serialised."""

    value: Interval

    def as_graph(self) -> Graph:
        val_bn = BNode()
        g = self._get_generic_graph(val_bn)
        g.add((val_bn, RDF.type, KNORA_API.IntervalValue))
        g.add((val_bn, KNORA_API.intervalValueHasStart, self.value.start))
        g.add((val_bn, KNORA_API.intervalValueHasEnd, self.value.end))
        return g


@dataclass
class Interval:
    start: Literal
    end: Literal
