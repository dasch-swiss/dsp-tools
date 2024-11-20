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


class BooleanValueRDF(ValueRDF):
    value: Literal

    def as_graph(self) -> Graph:
        val_bn = BNode()
        g = self._get_generic_graph(val_bn)
        g.add((val_bn, RDF.type, KNORA_API.BooleanValue))
        g.add((val_bn, KNORA_API.booleanValueAsBoolean, self.value))
        return g


class ColorValueRDF(ValueRDF):
    value: Literal

    def as_graph(self) -> Graph:
        val_bn = BNode()
        g = self._get_generic_graph(val_bn)
        g.add((val_bn, RDF.type, KNORA_API.ColorValue))
        g.add((val_bn, KNORA_API.colorValueAsColor, self.value))
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


class DecimalValueRDF(ValueRDF):
    value: Literal

    def as_graph(self) -> Graph:
        val_bn = BNode()
        g = self._get_generic_graph(val_bn)
        g.add((val_bn, RDF.type, KNORA_API.DecimalValue))
        g.add((val_bn, KNORA_API.decimalValueAsDecimal, self.value))
        return g


class GeomValueRDF(ValueRDF):
    value: Literal

    def as_graph(self) -> Graph:
        val_bn = BNode()
        g = self._get_generic_graph(val_bn)
        g.add((val_bn, RDF.type, KNORA_API.GeomValue))
        g.add((val_bn, KNORA_API.geometryValueAsGeometry, self.value))
        return g


class GeonameValueRDF(ValueRDF):
    value: Literal

    def as_graph(self) -> Graph:
        val_bn = BNode()
        g = self._get_generic_graph(val_bn)
        g.add((val_bn, RDF.type, KNORA_API.GeonameValue))
        g.add((val_bn, KNORA_API.geonameValueAsGeonameCode, self.value))
        return g


class IntValueRDF(ValueRDF):
    value: Literal

    def as_graph(self) -> Graph:
        val_bn = BNode()
        g = self._get_generic_graph(val_bn)
        g.add((val_bn, RDF.type, KNORA_API.IntValue))
        g.add((val_bn, KNORA_API.intValueAsInt, self.value))
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


class ListValueRDF(ValueRDF):
    value: URIRef

    def as_graph(self) -> Graph:
        val_bn = BNode()
        g = self._get_generic_graph(val_bn)
        g.add((val_bn, RDF.type, KNORA_API.ListValue))
        g.add((val_bn, KNORA_API.listValueAsListNode, self.value))
        return g


class LinkValueRDF(ValueRDF):
    value: URIRef

    def as_graph(self) -> Graph:
        val_bn = BNode()
        g = self._get_generic_graph(val_bn)
        g.add((val_bn, RDF.type, KNORA_API.LinkValue))
        g.add((val_bn, KNORA_API.linkValueHasTargetIri, self.value))
        return g


class SimpletextRDF(ValueRDF):
    value: Literal

    def as_graph(self) -> Graph:
        val_bn = BNode()
        g = self._get_generic_graph(val_bn)
        g.add((val_bn, RDF.type, KNORA_API.TextValue))
        g.add((val_bn, KNORA_API.valueAsString, self.value))
        return g


class RichtextRDF(ValueRDF):
    value: Literal

    def as_graph(self) -> Graph:
        val_bn = BNode()
        g = self._get_generic_graph(val_bn)
        g.add((val_bn, RDF.type, KNORA_API.TextValue))
        g.add((val_bn, KNORA_API.textValueAsXml, self.value))
        g.add((val_bn, KNORA_API.textValueHasMapping, URIRef("http://rdfh.ch/standoff/mappings/StandardMapping")))
        return g


class TimeValueRDF(ValueRDF):
    value: Literal

    def as_graph(self) -> Graph:
        val_bn = BNode()
        g = self._get_generic_graph(val_bn)
        g.add((val_bn, RDF.type, KNORA_API.TimeValue))
        g.add((val_bn, KNORA_API.timeValueAsTimeStamp, self.value))
        return g


class UriValueRDF(ValueRDF):
    value: Literal

    def as_graph(self) -> Graph:
        val_bn = BNode()
        g = self._get_generic_graph(val_bn)
        g.add((val_bn, RDF.type, KNORA_API.UriValue))
        g.add((val_bn, KNORA_API.uriValueAsUri, self.value))
        return g
