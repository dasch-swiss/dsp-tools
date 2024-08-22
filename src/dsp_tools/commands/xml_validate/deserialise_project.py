import json
from typing import Any

from dsp_tools.commands.xml_validate.models.project_deserialised import LinkProperty
from dsp_tools.commands.xml_validate.models.project_deserialised import ListDeserialised
from dsp_tools.commands.xml_validate.models.project_deserialised import ListProperty
from dsp_tools.commands.xml_validate.models.project_deserialised import ProjectDeserialised
from dsp_tools.commands.xml_validate.models.project_deserialised import Property
from dsp_tools.commands.xml_validate.models.project_deserialised import ResourceDeserialised
from dsp_tools.commands.xml_validate.models.project_deserialised import SimpleTextProperty


def deserialise_project() -> ProjectDeserialised:
    onto = _get_project_ontology()
    deserialised_lists = _get_deserialised_lists()
    resources = _deserialise_resources(onto)
    props = _deserialise_properties(onto, deserialised_lists)
    return ProjectDeserialised(resources=resources, properties=props)


def _get_project_ontology() -> Any:
    with open("testdata/xml-validate/from_api/onto.jsonld", "r", encoding="utf-8") as file:
        return json.load(file)


def _get_deserialised_lists() -> ListDeserialised:
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


def _deserialise_resources(onto: dict[str, Any]) -> list[ResourceDeserialised]:
    pass


def _extract_resources(onto: dict[str, Any]) -> list[dict[str, Any]]:
    pass


def _deserialise_one_resource(res: dict[str, Any]) -> ResourceDeserialised:
    pass


def _deserialise_properties(onto: dict[str, Any], list_lookup: ListDeserialised) -> list[Property]:
    pass


def _extract_all_onto_properties(onto: dict[str, Any], list_lookup: ListDeserialised) -> list[dict[str, Any]]:
    pass


def _deserialise_one_property(prop: dict[str, Any], list_lookup: ListDeserialised) -> Property:
    pass


def _deserialise_list_prop(prop: dict[str, Any], list_lookup: ListDeserialised) -> ListProperty:
    pass


def _deserialise_link_prop(prop: dict[str, Any]) -> LinkProperty:
    pass


def _deserialise_simple_text_prop(prop: dict[str, Any]) -> SimpleTextProperty:
    pass
