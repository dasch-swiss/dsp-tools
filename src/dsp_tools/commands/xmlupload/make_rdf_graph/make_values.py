from typing import TypeAlias
from typing import Union

from rdflib import RDF
from rdflib import XSD
from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import KNORA_API
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import LINK_PROP_TYPE_INFO
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import LIST_PROP_TYPE_INFO
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import RDF_LITERAL_PROP_TYPE_MAPPER
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import RICHTEXT_PROP_TYPE_INFO
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryBoolean
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryColor
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryDate
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryDecimal
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryGeometry
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryGeoname
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryInt
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryInterval
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryLink
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryList
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryRichtext
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediarySimpleText
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryTime
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryUri
from dsp_tools.commands.xmlupload.models.intermediary.values import IntermediaryValue
from dsp_tools.commands.xmlupload.models.lookup_models import IRILookups
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.rdf_models import RDFPropTypeInfo
from dsp_tools.models.exceptions import BaseError
from dsp_tools.models.exceptions import UserError
from dsp_tools.utils.date_util import DayMonthYearEra
from dsp_tools.utils.date_util import SingleDate
from dsp_tools.utils.date_util import StartEnd
from dsp_tools.utils.iri_util import is_resource_iri
from dsp_tools.utils.logger_config import WARNINGS_SAVEPATH

LiteralValueTypesAlias: TypeAlias = Union[
    IntermediaryBoolean,
    IntermediaryColor,
    IntermediaryDecimal,
    IntermediaryGeoname,
    IntermediaryGeometry,
    IntermediaryInt,
    IntermediarySimpleText,
    IntermediaryTime,
    IntermediaryUri,
]


def make_values(values: list[IntermediaryValue], res_node: BNode | URIRef, lookups: IRILookups) -> Graph:
    """
    Serialise the values of a resource.

    Args:
        values: list of IntermediaryValues of the resource
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


def _make_one_value_graph(val: IntermediaryValue, res_node: BNode | URIRef, iri_lookups: IRILookups) -> Graph:
    match val:
        case (
            IntermediaryBoolean()
            | IntermediaryColor()
            | IntermediaryDecimal()
            | IntermediaryGeometry()
            | IntermediaryGeoname()
            | IntermediaryInt()
            | IntermediaryTime()
            | IntermediaryUri()
            | IntermediarySimpleText()
        ):
            literal_info = RDF_LITERAL_PROP_TYPE_MAPPER[type(val)]
            properties_graph = _make_value_graph_with_literal_object(
                val=val,
                res_node=res_node,
                prop_type_info=literal_info,
            )
        case IntermediaryList():
            properties_graph = _make_list_value_graph(val=val, res_node=res_node, prop_type_info=LIST_PROP_TYPE_INFO)
        case IntermediaryLink():
            properties_graph = _make_link_value_graph(
                val=val,
                res_node=res_node,
                prop_type_info=LINK_PROP_TYPE_INFO,
                iri_resolver=iri_lookups.id_to_iri,
            )
        case IntermediaryRichtext():
            properties_graph = _make_richtext_value_graph(
                val=val,
                res_node=res_node,
                prop_type_info=RICHTEXT_PROP_TYPE_INFO,
                iri_resolver=iri_lookups.id_to_iri,
            )
        case IntermediaryDate():
            properties_graph = _make_date_value_graph(
                val=val,
                res_node=res_node,
            )
        case IntermediaryInterval():
            properties_graph = _make_interval_value_graph(
                val=val,
                res_node=res_node,
            )
        case _:
            raise UserError(f"Unknown value type: {type(val).__name__}")
    return properties_graph


def _make_base_value_graph(
    val: IntermediaryValue,
    prop_type_info: RDFPropTypeInfo,
    res_node: BNode | URIRef,
) -> tuple[BNode, Graph]:
    val_bn = BNode()
    g = _add_optional_triples(val_bn, val.permissions, val.comment)
    g.add((res_node, URIRef(val.prop_iri), val_bn))
    g.add((val_bn, RDF.type, prop_type_info.knora_type))
    return val_bn, g


def _add_optional_triples(val_bn: BNode, permissions: Permissions | None, comment: str | None) -> Graph:
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
    val_bn, g = _make_base_value_graph(val, prop_type_info, res_node)
    g.add((val_bn, prop_type_info.knora_prop, Literal(val.value, datatype=prop_type_info.xsd_type)))
    return g


def _make_list_value_graph(
    val: IntermediaryList,
    res_node: BNode | URIRef,
    prop_type_info: RDFPropTypeInfo,
) -> Graph:
    val_bn, g = _make_base_value_graph(val, prop_type_info, res_node)
    g.add((val_bn, prop_type_info.knora_prop, URIRef(val.value)))
    return g


def _make_link_value_graph(
    val: IntermediaryLink,
    prop_type_info: RDFPropTypeInfo,
    res_node: BNode | URIRef,
    iri_resolver: IriResolver,
) -> Graph:
    val_bn, g = _make_base_value_graph(val, prop_type_info, res_node)
    iri_str = _resolve_id_to_iri(val.value, iri_resolver)
    g.add((val_bn, prop_type_info.knora_prop, URIRef(iri_str)))
    return g


def _resolve_id_to_iri(value: str, iri_resolver: IriResolver) -> str:
    if is_resource_iri(value):
        return value
    elif resolved_iri := iri_resolver.get(value):
        return resolved_iri
    msg = (
        f"Could not find the ID {value} in the id2iri mapping. "
        f"This is probably because the resource '{value}' could not be created. "
        f"See {WARNINGS_SAVEPATH} for more information."
    )
    raise BaseError(msg)


def _make_date_value_graph(
    val: IntermediaryDate,
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
    val: IntermediaryInterval,
    res_node: BNode | URIRef,
) -> Graph:
    val_bn = BNode()
    g = _add_optional_triples(val_bn, val.permissions, val.comment)
    g.add((res_node, URIRef(val.prop_iri), val_bn))
    g.add((val_bn, RDF.type, KNORA_API.IntervalValue))
    g.add((val_bn, KNORA_API.intervalValueHasStart, Literal(val.value.start, datatype=XSD.decimal)))
    g.add((val_bn, KNORA_API.intervalValueHasEnd, Literal(val.value.end, datatype=XSD.decimal)))
    return g


def _make_richtext_value_graph(
    val: IntermediaryRichtext,
    prop_type_info: RDFPropTypeInfo,
    res_node: BNode | URIRef,
    iri_resolver: IriResolver,
) -> Graph:
    val_bn, g = _make_base_value_graph(val, prop_type_info, res_node)
    xml_with_iris = val.value.with_iris(iri_resolver)
    val_str = xml_with_iris.as_xml()
    g.add((val_bn, prop_type_info.knora_prop, Literal(val_str, datatype=XSD.string)))
    g.add((val_bn, KNORA_API.textValueHasMapping, URIRef("http://rdfh.ch/standoff/mappings/StandardMapping")))
    return g
