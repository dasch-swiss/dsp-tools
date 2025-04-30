from typing import Union

from rdflib import RDF
from rdflib import XSD
from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import LINK_PROP_TYPE_INFO
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import LIST_PROP_TYPE_INFO
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import RDF_LITERAL_PROP_TYPE_MAPPER
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import RICHTEXT_PROP_TYPE_INFO
from dsp_tools.commands.xmlupload.models.lookup_models import IRILookups
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedBoolean
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedColor
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedDate
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedDecimal
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedGeometry
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedGeoname
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedInt
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedInterval
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedLink
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedList
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedRichtext
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedSimpleText
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedTime
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedUri
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedValue
from dsp_tools.commands.xmlupload.models.rdf_models import RDFPropTypeInfo
from dsp_tools.config.logger_config import WARNINGS_SAVEPATH
from dsp_tools.error.exceptions import BaseError
from dsp_tools.error.exceptions import InputError
from dsp_tools.utils.data_formats.date_util import DayMonthYearEra
from dsp_tools.utils.data_formats.date_util import SingleDate
from dsp_tools.utils.data_formats.date_util import StartEnd
from dsp_tools.utils.data_formats.iri_util import is_resource_iri
from dsp_tools.utils.rdflib_constants import KNORA_API

type LiteralValueTypesAlias = Union[
    ProcessedBoolean,
    ProcessedColor,
    ProcessedDecimal,
    ProcessedGeoname,
    ProcessedGeometry,
    ProcessedInt,
    ProcessedSimpleText,
    ProcessedTime,
    ProcessedUri,
]


def make_values(values: list[ProcessedValue], res_node: BNode | URIRef, lookups: IRILookups) -> Graph:
    """
    Serialise the values of a resource.

    Args:
        values: list of ProcessedValues of the resource
        res_node: node of the resource
        lookups: lookups to resolve IRIs

    Returns:
        Graph with the values
    """
    properties_graph = Graph()
    for val in values:
        single_prop_graph = _make_one_value_graph(val=val, res_node=res_node, iri_lookups=lookups)
        properties_graph += single_prop_graph
    return properties_graph


def _make_one_value_graph(val: ProcessedValue, res_node: BNode | URIRef, iri_lookups: IRILookups) -> Graph:
    match val:
        case (
            ProcessedBoolean()
            | ProcessedColor()
            | ProcessedDecimal()
            | ProcessedGeometry()
            | ProcessedGeoname()
            | ProcessedInt()
            | ProcessedTime()
            | ProcessedUri()
            | ProcessedSimpleText()
        ):
            literal_info = RDF_LITERAL_PROP_TYPE_MAPPER[type(val)]
            properties_graph = _make_value_graph_with_literal_object(
                val=val,
                res_node=res_node,
                prop_type_info=literal_info,
            )
        case ProcessedList():
            properties_graph = _make_list_value_graph(val=val, res_node=res_node, prop_type_info=LIST_PROP_TYPE_INFO)
        case ProcessedLink():
            target_iri = _resolve_id_to_iri(val.value, iri_lookups.id_to_iri)
            properties_graph = make_link_value_graph(
                val=val,
                val_node=BNode(),
                res_node=res_node,
                target_iri=URIRef(target_iri),
            )
        case ProcessedRichtext():
            properties_graph = make_richtext_value_graph(
                val=val,
                val_node=BNode(),
                res_node=res_node,
                iri_resolver=iri_lookups.id_to_iri,
            )
        case ProcessedDate():
            properties_graph = _make_date_value_graph(
                val=val,
                res_node=res_node,
            )
        case ProcessedInterval():
            properties_graph = _make_interval_value_graph(
                val=val,
                res_node=res_node,
            )
        case _:
            raise InputError(f"Unknown value type: {type(val).__name__}")
    return properties_graph


def _make_base_value_graph(
    val: ProcessedValue,
    val_node: BNode | URIRef,
    prop_type_info: RDFPropTypeInfo,
    res_node: BNode | URIRef,
) -> Graph:
    g = _add_optional_triples(val_node, val.permissions, val.comment)
    g.add((res_node, URIRef(val.prop_iri), val_node))
    g.add((val_node, RDF.type, prop_type_info.knora_type))
    return g


def _add_optional_triples(val_bn: BNode | URIRef, permissions: Permissions | None, comment: str | None) -> Graph:
    g = Graph()
    if permissions:
        g.add((val_bn, KNORA_API.hasPermissions, Literal(str(permissions), datatype=XSD.string)))
    if comment:
        g.add((val_bn, KNORA_API.valueHasComment, Literal(comment, datatype=XSD.string)))
    return g


def _make_value_graph_with_literal_object(
    val: LiteralValueTypesAlias,
    prop_type_info: RDFPropTypeInfo,
    res_node: BNode | URIRef,
) -> Graph:
    val_bn = BNode()
    g = _make_base_value_graph(val=val, val_node=val_bn, prop_type_info=prop_type_info, res_node=res_node)
    g.add((val_bn, prop_type_info.knora_prop, Literal(val.value, datatype=prop_type_info.xsd_type)))
    return g


def _make_list_value_graph(
    val: ProcessedList,
    res_node: BNode | URIRef,
    prop_type_info: RDFPropTypeInfo,
) -> Graph:
    val_bn = BNode()
    g = _make_base_value_graph(val=val, val_node=val_bn, prop_type_info=prop_type_info, res_node=res_node)
    g.add((val_bn, prop_type_info.knora_prop, URIRef(val.value)))
    return g


def make_link_value_graph(
    val: ProcessedLink,
    val_node: BNode | URIRef,
    res_node: BNode | URIRef,
    target_iri: URIRef,
) -> Graph:
    """Make a LinkValue Graph"""
    g = _make_base_value_graph(val=val, val_node=val_node, prop_type_info=LINK_PROP_TYPE_INFO, res_node=res_node)
    g.add((val_node, LINK_PROP_TYPE_INFO.knora_prop, target_iri))
    return g


def _resolve_id_to_iri(value: str, iri_resolver: IriResolver) -> URIRef:
    if is_resource_iri(value):
        return URIRef(value)
    elif resolved_iri := iri_resolver.get(value):
        return URIRef(resolved_iri)
    msg = (
        f"Could not find the ID {value} in the id2iri mapping. "
        f"This is probably because the resource '{value}' could not be created. "
        f"See {WARNINGS_SAVEPATH} for more information."
    )
    raise BaseError(msg)


def _make_date_value_graph(
    val: ProcessedDate,
    res_node: BNode | URIRef,
) -> Graph:
    val_bn = BNode()
    date = val.value
    g = _add_optional_triples(val_bn, val.permissions, val.comment)
    g.add((res_node, URIRef(val.prop_iri), val_bn))
    g.add((val_bn, RDF.type, KNORA_API.DateValue))
    if cal := date.calendar:
        g.add((val_bn, KNORA_API.dateValueHasCalendar, Literal(cal.value, datatype=XSD.string)))
    g += _make_single_date_graph(val_bn, date.start, StartEnd.START)
    if date.end:
        g += _make_single_date_graph(val_bn, date.end, StartEnd.END)
    return g


def _make_single_date_graph(val_bn: BNode, date: SingleDate, start_end: StartEnd) -> Graph:
    def get_prop(precision: DayMonthYearEra) -> URIRef:
        return KNORA_API[f"dateValueHas{start_end.value}{precision.value}"]

    g = Graph()
    if yr := date.year:
        g.add((val_bn, get_prop(DayMonthYearEra.YEAR), Literal(yr, datatype=XSD.integer)))
    if mnt := date.month:
        g.add((val_bn, get_prop(DayMonthYearEra.MONTH), Literal(mnt, datatype=XSD.integer)))
    if day := date.day:
        g.add((val_bn, get_prop(DayMonthYearEra.DAY), Literal(day, datatype=XSD.integer)))
    if era := date.era:
        g.add((val_bn, get_prop(DayMonthYearEra.ERA), Literal(era.value, datatype=XSD.string)))
    return g


def _make_interval_value_graph(
    val: ProcessedInterval,
    res_node: BNode | URIRef,
) -> Graph:
    val_bn = BNode()
    g = _add_optional_triples(val_bn, val.permissions, val.comment)
    g.add((res_node, URIRef(val.prop_iri), val_bn))
    g.add((val_bn, RDF.type, KNORA_API.IntervalValue))
    g.add((val_bn, KNORA_API.intervalValueHasStart, Literal(val.value.start, datatype=XSD.decimal)))
    g.add((val_bn, KNORA_API.intervalValueHasEnd, Literal(val.value.end, datatype=XSD.decimal)))
    return g


def make_richtext_value_graph(
    val: ProcessedRichtext,
    val_node: BNode | URIRef,
    res_node: BNode | URIRef,
    iri_resolver: IriResolver,
) -> Graph:
    """
    Creates an rdflib graph for a richtext value.

    Args:
        val: Richtext value
        val_node: IRI or blank node of the value
        res_node: IRI or blank node of the resource
        iri_resolver: id to IRI resolver

    Returns:
        Graph
    """
    g = _make_base_value_graph(val=val, val_node=val_node, prop_type_info=RICHTEXT_PROP_TYPE_INFO, res_node=res_node)
    xml_with_iris = val.value.with_iris(iri_resolver)
    val_str = xml_with_iris.as_xml()
    g.add((val_node, RICHTEXT_PROP_TYPE_INFO.knora_prop, Literal(val_str, datatype=XSD.string)))
    g.add((val_node, KNORA_API.textValueHasMapping, URIRef("http://rdfh.ch/standoff/mappings/StandardMapping")))
    return g
