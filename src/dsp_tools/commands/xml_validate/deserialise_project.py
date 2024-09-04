from rdflib import Literal
from rdflib import Namespace
from rdflib import URIRef

from dsp_tools.commands.xml_validate.models.data_deserialised import DataDeserialised
from dsp_tools.commands.xml_validate.models.data_deserialised import IntValueData
from dsp_tools.commands.xml_validate.models.data_deserialised import LinkValueData
from dsp_tools.commands.xml_validate.models.data_deserialised import ListValueData
from dsp_tools.commands.xml_validate.models.data_deserialised import ResourceData
from dsp_tools.commands.xml_validate.models.data_deserialised import SimpleTextData
from dsp_tools.commands.xml_validate.models.data_deserialised import ValueData
from dsp_tools.commands.xml_validate.models.data_rdf import DataRDF
from dsp_tools.commands.xml_validate.models.data_rdf import IntValueRDF
from dsp_tools.commands.xml_validate.models.data_rdf import LinkValueRDF
from dsp_tools.commands.xml_validate.models.data_rdf import ListValueRDF
from dsp_tools.commands.xml_validate.models.data_rdf import ResourceRDF
from dsp_tools.commands.xml_validate.models.data_rdf import SimpleTextRDF
from dsp_tools.commands.xml_validate.models.data_rdf import ValueRDF
from dsp_tools.models.exceptions import InputError


def create_project_rdf(project: DataDeserialised) -> DataRDF:
    """Transform the deserialised data into models that can serialise as RDF."""
    onto_namespace = Namespace("http://0.0.0.0:3333/ontology/9999/onto/v2#")
    return DataRDF(resources=[_create_resource_rdf(x, onto_namespace) for x in project.resources])


def _create_resource_rdf(resource: ResourceData, onto: Namespace) -> ResourceRDF:
    all_values = [_create_one_value(x, onto) for x in resource.values]
    return ResourceRDF(
        res_iri=URIRef(resource.res_id),
        res_class=onto[resource.res_class.lstrip(":")],
        label=Literal(resource.label),
        values=all_values,
    )


def _create_one_value(value: ValueData, onto: Namespace) -> ValueRDF:
    match value:
        case SimpleTextData():
            return _create_simple_text_value_rdf(value, onto)
        case IntValueData():
            return _create_int_value_rdf(value, onto)
        case ListValueData():
            return _create_list_value_rdf(value, onto)
        case LinkValueData():
            return _create_link_value_rdf(value, onto)
        case _:
            raise InputError(f"The value type is not known: {type(value)}")


def _create_simple_text_value_rdf(value: SimpleTextData, onto: Namespace) -> SimpleTextRDF:
    return SimpleTextRDF(prop_name=onto[value.prop_name.lstrip(":")], object_value=Literal(value.prop_value))


def _create_int_value_rdf(value: IntValueData, onto: Namespace) -> IntValueRDF:
    return IntValueRDF(prop_name=onto[value.prop_name.lstrip(":")], object_value=Literal(value.prop_value))


def _create_list_value_rdf(value: ListValueData, onto: Namespace) -> ListValueRDF:
    return ListValueRDF(
        prop_name=onto[value.prop_name.lstrip(":")],
        object_value=Literal(value.prop_value),
        list_name=Literal(value.list_name),
    )


def _create_link_value_rdf(value: LinkValueData, onto: Namespace) -> LinkValueRDF:
    return LinkValueRDF(prop_name=onto[value.prop_name.lstrip(":")], object_value=URIRef(value.prop_value))
