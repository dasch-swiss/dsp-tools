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
from dsp_tools.commands.xmlupload.make_rdf_graph.helpers import get_absolute_iri
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
from dsp_tools.commands.xmlupload.models.lookup_models import IRILookup
from dsp_tools.commands.xmlupload.models.rdf_models import RDFPropTypeInfo
from dsp_tools.models.exceptions import BaseError
from dsp_tools.models.exceptions import UserError
from dsp_tools.utils.date_util import DayMonthYearEra
from dsp_tools.utils.date_util import SingleDate
from dsp_tools.utils.date_util import StartEnd
from dsp_tools.utils.iri_util import is_resource_iri
from dsp_tools.utils.logger_config import WARNINGS_SAVEPATH


def make_values(values: list[IntermediaryValue], res_bnode: BNode, lookups: IRILookup) -> tuple[Graph, URIRef | None]:
    """
    Serialise the values of a resource.

    Args:
        values: list of IntermediaryValues of the resource
        res_bnode: blank node of the resource
        lookups: lookups to resolve IRIs

    Returns:
        Graph with the values and the last property name
    """
    properties_graph = Graph()
    # To frame the json-ld correctly, we need one property used in the graph. It does not matter which.
    last_prop_name = None

    for prop in values:
        single_prop_graph, last_prop_name = _make_one_prop_graph(val=prop, res_bnode=res_bnode, iri_lookup=lookups)
        properties_graph += single_prop_graph

    return properties_graph, last_prop_name


def _make_one_prop_graph(val: IntermediaryValue, res_bnode: BNode, iri_lookup: IRILookup) -> tuple[Graph, URIRef]:
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
            | IntermediarySimpleText() as val_type
        ):
            literal_info = RDF_LITERAL_PROP_TYPE_MAPPER[val_type]
            properties_graph = _make_value_graph_with_object_literals(
                val=val,
                res_bn=res_bnode,
                prop_type_info=literal_info,
            )
        case IntermediaryList():
            properties_graph = _make_prop_graph_with_object_iri(
                val=val, res_bn=res_bnode, prop_type_info=LIST_PROP_TYPE_INFO
            )
        case IntermediaryLink():
            prop_name = get_absolute_iri(f"{val.name}Value", iri_lookup.namespaces)
            properties_graph = _make_link_prop_graph(
                val=val,
                res_bn=res_bnode,
                prop_type_info=LINK_PROP_TYPE_INFO,
                iri_resolver=iri_lookup.id_to_iri,
            )
        case IntermediaryRichtext():
            properties_graph = _make_richtext_value_graph(
                val=val,
                res_bn=res_bnode,
                prop_type_info=RICHTEXT_PROP_TYPE_INFO,
                iri_resolver=iri_lookup.id_to_iri,
            )
        case IntermediaryDate():
            properties_graph = _make_date_value_graph(
                val=val,
                res_bn=res_bnode,
            )
        case IntermediaryInterval():
            properties_graph = _make_interval_value_graph(
                val=val,
                res_bn=res_bnode,
            )
        case _:
            raise UserError(f"Unknown value type: {val.valtype}")
    return properties_graph, prop_name


def _make_base_value_graph(
    val: IntermediaryValue,
    prop_type_info: RDFPropTypeInfo,
    res_bn: BNode,
) -> tuple[BNode, Graph]:
    val_bn = BNode()
    g = _add_optional_triples(val_bn, val.permissions, val.comment)
    g.add((res_bn, URIRef(val.prop_iri), val_bn))
    g.add((val_bn, RDF.type, prop_type_info.knora_type))
    return val_bn, g


def _add_optional_triples(val_bn: BNode, permissions: str | None, comment: str | None) -> Graph:
    g = Graph()
    if permissions:
        g.add((val_bn, KNORA_API.hasPermissions, Literal(permissions, datatype=XSD.string)))
    if comment:
        g.add((val_bn, KNORA_API.valueHasComment, Literal(comment, datatype=XSD.string)))
    return g


def _make_value_graph_with_object_literals(
    val: IntermediaryValue,
    prop_type_info: RDFPropTypeInfo,
    res_bn: BNode,
) -> Graph:
    val_bn, g = _make_base_value_graph(val, prop_type_info, res_bn)
    g.add((val_bn, prop_type_info.knora_prop, Literal(val.value, datatype=prop_type_info.xsd_type)))
    return g


def _make_prop_graph_with_object_iri(
    val: IntermediaryValue,
    res_bn: BNode,
    prop_type_info: RDFPropTypeInfo,
) -> Graph:
    val_bn, g = _make_base_value_graph(val, prop_type_info, res_bn)
    g.add((val_bn, prop_type_info.knora_prop, URIRef(val.value)))
    return g


def _make_link_prop_graph(
    val: IntermediaryValue,
    prop_type_info: RDFPropTypeInfo,
    res_bn: BNode,
    iri_resolver: IriResolver,
) -> Graph:
    val_bn, g = _make_base_value_graph(val, prop_type_info, res_bn)
    iri_str = _resolve_id_to_iri(val.value, iri_resolver)
    g.add((val_bn, prop_type_info.knora_prop, URIRef(iri_str)))
    return g


def _resolve_id_to_iri(value: str, iri_resolver: IriResolver) -> str:
    if is_resource_iri(value):
        iri_str = value
    elif resolved_iri := iri_resolver.get(value):
        iri_str = resolved_iri
    else:
        msg = (
            f"Could not find the ID {value} in the id2iri mapping. "
            f"This is probably because the resource '{value}' could not be created. "
            f"See {WARNINGS_SAVEPATH} for more information."
        )
        raise BaseError(msg)
    return iri_str


def _make_date_value_graph(
    val: IntermediaryValue,
    res_bn: BNode,
) -> Graph:
    val_bn = BNode()
    date = val.value
    g = _add_optional_triples(val_bn, val.permissions, val.comment)
    g.add((res_bn, URIRef(val.prop_iri), val_bn))
    g.add((val_bn, RDF.type, KNORA_API.DateValue))
    if cal := date.calendar.value:
        g.add((val_bn, KNORA_API.dateValueHasCalendar, Literal(cal, datatype=XSD.string)))
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
    val: IntermediaryValue,
    res_bn: BNode,
) -> Graph:
    val_bn = BNode()
    g = _add_optional_triples(val_bn, val.permissions, val.comment)
    g.add((res_bn, URIRef(val.prop_iri), val_bn))
    g.add((val_bn, RDF.type, KNORA_API.IntervalValue))
    g.add((val_bn, KNORA_API.intervalValueHasStart, Literal(val.value.start, datatype=XSD.float)))
    g.add((val_bn, KNORA_API.intervalValueHasEnd, Literal(val.value.end, datatype=XSD.float)))
    return g


def _make_richtext_value_graph(
    val: IntermediaryValue,
    prop_type_info: RDFPropTypeInfo,
    res_bn: BNode,
    iri_resolver: IriResolver,
) -> Graph:
    val_bn, g = _make_base_value_graph(val, prop_type_info, res_bn)
    xml_with_iris = val.value.with_iris(iri_resolver)
    val_str = xml_with_iris.as_xml()
    g.add((val_bn, prop_type_info.knora_prop, Literal(val_str, datatype=XSD.string)))
    g.add((val_bn, KNORA_API.textValueHasMapping, URIRef("http://rdfh.ch/standoff/mappings/StandardMapping")))
    return g
