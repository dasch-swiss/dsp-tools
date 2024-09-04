from rdflib import Literal
from rdflib import Namespace

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
from dsp_tools.commands.xml_validate.models.data_rdf import ProjectNamespaces
from dsp_tools.commands.xml_validate.models.data_rdf import ResourceRDF
from dsp_tools.commands.xml_validate.models.data_rdf import SimpleTextRDF
from dsp_tools.commands.xml_validate.models.data_rdf import ValueRDF
from dsp_tools.models.exceptions import InputError


def create_project_rdf(project: DataDeserialised) -> DataRDF:
    """Transform the deserialised data into models that can serialise as RDF."""
    proj_namespaces = ProjectNamespaces(
        onto=Namespace("http://0.0.0.0:3333/ontology/9999/onto/v2#"),
        data=Namespace(f"http://validation-{project.shortcode}/data/"),
    )
    return DataRDF(resources=[_create_resource_rdf(x, proj_namespaces) for x in project.resources])


def _create_resource_rdf(resource: ResourceData, namespaces: ProjectNamespaces) -> ResourceRDF:
    all_values = [_create_one_value(x, namespaces) for x in resource.values]
    return ResourceRDF(
        res_iri=namespaces.data[resource.res_id],
        res_class=namespaces.onto[resource.res_class.lstrip(":")],
        label=Literal(resource.label),
        values=all_values,
    )


def _create_one_value(value: ValueData, namespaces: ProjectNamespaces) -> ValueRDF:
    match value:
        case SimpleTextData():
            return _create_simple_text_value_rdf(value, namespaces)
        case IntValueData():
            return _create_int_value_rdf(value, namespaces)
        case ListValueData():
            return _create_list_value_rdf(value, namespaces)
        case LinkValueData():
            return _create_link_value_rdf(value, namespaces)
        case _:
            raise InputError(f"The value type is not known: {type(value)}")


def _create_simple_text_value_rdf(value: SimpleTextData, namespaces: ProjectNamespaces) -> SimpleTextRDF:
    return SimpleTextRDF(prop_name=namespaces.onto[value.prop_name.lstrip(":")], object_value=Literal(value.prop_value))


def _create_int_value_rdf(value: IntValueData, namespaces: ProjectNamespaces) -> IntValueRDF:
    return IntValueRDF(prop_name=namespaces.onto[value.prop_name.lstrip(":")], object_value=Literal(value.prop_value))


def _create_list_value_rdf(value: ListValueData, namespaces: ProjectNamespaces) -> ListValueRDF:
    return ListValueRDF(
        prop_name=namespaces.onto[value.prop_name.lstrip(":")],
        object_value=Literal(value.prop_value),
        list_name=Literal(value.list_name),
    )


def _create_link_value_rdf(value: LinkValueData, namespaces: ProjectNamespaces) -> LinkValueRDF:
    return LinkValueRDF(
        prop_name=namespaces.onto[value.prop_name.lstrip(":")], object_value=namespaces.data[value.prop_value]
    )
