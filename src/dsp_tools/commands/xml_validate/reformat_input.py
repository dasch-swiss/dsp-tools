from typing import Callable
from typing import Sequence

from lxml import etree
from rdflib import XSD
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.commands.xml_validate.models.data_rdf import BooleanValueRDF
from dsp_tools.commands.xml_validate.models.data_rdf import ColorValueRDF
from dsp_tools.commands.xml_validate.models.data_rdf import DataRDF
from dsp_tools.commands.xml_validate.models.data_rdf import DateValueRDF
from dsp_tools.commands.xml_validate.models.data_rdf import DecimalValueRDF
from dsp_tools.commands.xml_validate.models.data_rdf import GeonameValueRDF
from dsp_tools.commands.xml_validate.models.data_rdf import IntValueRDF
from dsp_tools.commands.xml_validate.models.data_rdf import LinkValueRDF
from dsp_tools.commands.xml_validate.models.data_rdf import ListValueRDF
from dsp_tools.commands.xml_validate.models.data_rdf import ResourceRDF
from dsp_tools.commands.xml_validate.models.data_rdf import RichtextRDF
from dsp_tools.commands.xml_validate.models.data_rdf import SimpleTextRDF
from dsp_tools.commands.xml_validate.models.data_rdf import TimeValueRDF
from dsp_tools.commands.xml_validate.models.data_rdf import UriValueRDF
from dsp_tools.commands.xml_validate.models.data_rdf import ValueRDF


def to_data_rdf(root: etree._Element) -> DataRDF:
    """
    Takes the root of an XML
    Extracts the data of the project and transforms all its resources.

    Args:
        root: root of an xml with qnames and comments removed

    Returns:
        Class instance with the information reformatted
    """
    shortcode = root.attrib["shortcode"]
    default_ontology = root.attrib["default-ontology"]
    resources = _deserialise_all_resources(root)
    return DataRDF(shortcode=shortcode, default_onto=default_ontology, resources=resources)


def _deserialise_all_resources(root: etree._Element) -> list[ResourceRDF]:
    all_res = []
    for res in root.iterchildren():
        match res.tag:
            case "resource":
                all_res.append(_deserialise_one_resource(res))
            case "annotation" | "region" | "link" | "video-segment" | "audio-segment":
                all_res.append(_deserialise_dsp_base_resource(res))
            case _:
                pass
    return all_res


def _deserialise_dsp_base_resource(resource: etree._Element) -> ResourceRDF:
    return ResourceRDF(
        res_id=URIRef(resource.attrib["id"]),
        res_class=URIRef(resource.attrib["restype"]),
        label=Literal(resource.attrib["label"], datatype=XSD.string),
        values=[],
    )


def _deserialise_one_resource(resource: etree._Element) -> ResourceRDF:
    values: list[ValueRDF] = []
    for val in resource.iterchildren():
        values.extend(_deserialise_one_property(val))
    return ResourceRDF(
        res_id=URIRef(resource.attrib["id"]),
        res_class=URIRef(resource.attrib["restype"]),
        label=Literal(resource.attrib["label"], datatype=XSD.string),
        values=values,
    )


def _deserialise_one_property(prop_ele: etree._Element) -> Sequence[ValueRDF]:  # noqa: PLR0911 (too-many-branches, return statements)
    match prop_ele.tag:
        case "boolean-prop":
            return _deserialise_bool_prop(prop_ele)
        case "color-prop":
            return _deserialise_into_xsd_string(prop_ele, ColorValueRDF)
        case "date-prop":
            return _deserialise_into_xsd_string(prop_ele, DateValueRDF)
        case "decimal-prop":
            return _deserialise_decimal_prop(prop_ele)
        case "geoname-prop":
            return _deserialise_into_xsd_int(prop_ele, GeonameValueRDF)
        case "list-prop":
            return _deserialise_list_prop(prop_ele)
        case "integer-prop":
            return _deserialise_into_xsd_int(prop_ele, IntValueRDF)
        case "resptr-prop":
            return _deserialise_link_prop(prop_ele)
        case "text-prop":
            return _deserialise_text_prop(prop_ele)
        case "time-prop":
            return _deserialise_time_prop(prop_ele)
        case "uri-prop":
            return _deserialise_uri_prop(prop_ele)
        case _:
            return []


def _deserialise_into_xsd_string(
    prop: etree._Element, func: Callable[[URIRef, Literal], ValueRDF]
) -> Sequence[ValueRDF]:
    prop_name = URIRef(prop.attrib["name"])
    all_vals: list[ValueRDF] = []
    for val in prop.iterchildren():
        txt = val.text if val.text is not None else ""
        all_vals.append(func(prop_name, Literal(txt, datatype=XSD.string)))
    return all_vals


def _deserialise_into_xsd_int(prop: etree._Element, func: Callable[[URIRef, Literal], ValueRDF]) -> Sequence[ValueRDF]:
    prop_name = URIRef(prop.attrib["name"])
    all_vals: list[ValueRDF] = []
    for val in prop.iterchildren():
        txt = Literal(val.text, datatype=XSD.integer) if val.text is not None else Literal("", datatype=XSD.string)
        all_vals.append(func(prop_name, txt))
    return all_vals


def _deserialise_bool_prop(prop: etree._Element) -> Sequence[BooleanValueRDF]:
    prop_name = URIRef(prop.attrib["name"])
    all_vals: list[BooleanValueRDF] = []
    for val in prop.iterchildren():
        txt = Literal(val.text, datatype=XSD.boolean) if val.text is not None else Literal("", datatype=XSD.string)
        all_vals.append(BooleanValueRDF(prop_name=prop_name, object_value=txt))
    return all_vals


def _deserialise_decimal_prop(prop: etree._Element) -> Sequence[DecimalValueRDF]:
    prop_name = URIRef(prop.attrib["name"])
    all_vals: list[DecimalValueRDF] = []
    for val in prop.iterchildren():
        txt = Literal(val.text, datatype=XSD.decimal) if val.text is not None else Literal("", datatype=XSD.string)
        all_vals.append(DecimalValueRDF(prop_name=prop_name, object_value=txt))
    return all_vals


def _deserialise_link_prop(prop: etree._Element) -> Sequence[LinkValueRDF]:
    prop_name = URIRef(prop.attrib["name"])
    all_vals: list[LinkValueRDF] = []
    for val in prop.iterchildren():
        txt = val.text if val.text is not None else ""
        all_vals.append(LinkValueRDF(prop_name=prop_name, object_value=URIRef(txt)))
    return all_vals


def _deserialise_list_prop(prop: etree._Element) -> Sequence[ListValueRDF]:
    prop_name = URIRef(prop.attrib["name"])
    list_name = Literal(prop.attrib["list"], datatype=XSD.string)
    all_vals: list[ListValueRDF] = []
    for val in prop.iterchildren():
        txt = val.text if val.text is not None else ""
        all_vals.append(
            ListValueRDF(prop_name=prop_name, object_value=Literal(txt, datatype=XSD.string), list_name=list_name)
        )
    return all_vals


def _deserialise_text_prop(prop: etree._Element) -> Sequence[SimpleTextRDF | RichtextRDF]:
    prop_name = URIRef(prop.attrib["name"])
    all_vals: list[SimpleTextRDF | RichtextRDF] = []
    for val in prop.iterchildren():
        txt = val.text if val.text is not None else ""
        match val.attrib["encoding"]:
            case "utf8":
                all_vals.append(SimpleTextRDF(prop_name, Literal(txt, datatype=XSD.string)))
            case "xml":
                all_vals.append(RichtextRDF(prop_name, Literal(txt, datatype=XSD.string)))
    return all_vals


def _deserialise_time_prop(prop: etree._Element) -> Sequence[TimeValueRDF]:
    prop_name = URIRef(prop.attrib["name"])
    all_vals: list[TimeValueRDF] = []
    for val in prop.iterchildren():
        txt = (
            Literal(val.text, datatype=XSD.dateTimeStamp) if val.text is not None else Literal("", datatype=XSD.string)
        )
        all_vals.append(TimeValueRDF(prop_name=prop_name, object_value=txt))
    return all_vals


def _deserialise_uri_prop(prop: etree._Element) -> Sequence[UriValueRDF]:
    prop_name = URIRef(prop.attrib["name"])
    all_vals: list[UriValueRDF] = []
    for val in prop.iterchildren():
        txt = Literal(val.text, datatype=XSD.anyURI) if val.text is not None else Literal("", datatype=XSD.string)
        all_vals.append(UriValueRDF(prop_name=prop_name, object_value=txt))
    return all_vals
