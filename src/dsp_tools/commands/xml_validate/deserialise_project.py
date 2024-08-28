import json
from typing import Any

from rdflib import BNode
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
from dsp_tools.commands.xml_validate.models.data_rdf import ResourceRDF
from dsp_tools.commands.xml_validate.models.data_rdf import SimpleTextRDF
from dsp_tools.commands.xml_validate.models.data_rdf import ValueRDF
from dsp_tools.commands.xml_validate.models.project_deserialised import ListDeserialised
from dsp_tools.models.exceptions import InputError


def _get_project_ontology() -> Any:
    with open("testdata/xml-validate/from_api/onto.jsonld", "r", encoding="utf-8") as file:
        return json.load(file)


def get_deserialised_lists() -> ListDeserialised:
    """Get objects which contain the pertinent information of the lists from the API."""
    with open("testdata/xml-validate/from_api/onlyList.json", "r", encoding="utf-8") as file:
        data: dict[str, Any] = json.load(file)
    return _deserialise_one_list(data)


def _deserialise_one_list(list_response: dict[str, Any]) -> ListDeserialised:
    all_children = []
    for child in list_response["list"]["children"]:
        all_children.extend(_process_child_nodes(child))
    return ListDeserialised(
        list_name=list_response["list"]["listinfo"]["name"],
        iri=list_response["list"]["listinfo"]["id"],
        nodes=all_children,
    )


def _process_child_nodes(node: dict[str, Any]) -> list[str]:
    children = []
    all_nodes = [node]
    while all_nodes:
        current_node = all_nodes.pop(0)
        children.append(current_node["name"])
        all_nodes.extend(current_node.get("children", []))
    return children


def create_project_rdf(project: DataDeserialised) -> DataRDF:
    """Transform the deserialised data into models that can serialise as RDF."""
    onto = Namespace(f"http://validation-{project.shortcode}/{project.default_onto}#")
    return DataRDF(resources=[_create_resource_rdf(x, onto) for x in project.resources])


def _create_resource_rdf(resource: ResourceData, onto: Namespace) -> ResourceRDF:
    all_values = [_create_one_value(x, onto) for x in resource.values]
    return ResourceRDF(
        res_bn=BNode(resource.res_id),
        res_class=onto[resource.res_class],
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
    return SimpleTextRDF(prop_name=onto[value.prop_name], object_value=Literal(value.prop_value))


def _create_int_value_rdf(value: IntValueData, onto: Namespace) -> IntValueRDF:
    return IntValueRDF(prop_name=onto[value.prop_name], object_value=Literal(value.prop_value))


def _create_list_value_rdf(value: ListValueData, onto: Namespace) -> ListValueRDF:
    return ListValueRDF(
        prop_name=onto[value.prop_name], object_value=Literal(value.prop_value), list_name=Literal(value.list_name)
    )


def _create_link_value_rdf(value: LinkValueData, onto: Namespace) -> LinkValueRDF:
    return LinkValueRDF(prop_name=onto[value.prop_name], object_value=BNode(value.prop_value))
