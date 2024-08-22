import json
from collections import defaultdict
from copy import deepcopy
from typing import Any

from dsp_tools.commands.xml_validate.models.project_deserialised import Cardinality
from dsp_tools.commands.xml_validate.models.project_deserialised import CardinalityOne
from dsp_tools.commands.xml_validate.models.project_deserialised import CardinalityZeroToN
from dsp_tools.commands.xml_validate.models.project_deserialised import LinkProperty
from dsp_tools.commands.xml_validate.models.project_deserialised import ListDeserialised
from dsp_tools.commands.xml_validate.models.project_deserialised import ListProperty
from dsp_tools.commands.xml_validate.models.project_deserialised import ProjectDeserialised
from dsp_tools.commands.xml_validate.models.project_deserialised import Property
from dsp_tools.commands.xml_validate.models.project_deserialised import ResourceDeserialised
from dsp_tools.commands.xml_validate.models.project_deserialised import SimpleTextProperty


def deserialise_project() -> ProjectDeserialised:
    """Deserializes an ontology."""
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


def _deserialise_resources(onto: list[dict[str, Any]]) -> list[ResourceDeserialised]:
    only_res = _extract_resources(onto)
    return [_deserialise_one_resource(x) for x in only_res]


def _extract_resources(onto: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [x for x in onto if x.get("knora-api:isResourceClass")]


def _deserialise_one_resource(res: dict[str, Any]) -> ResourceDeserialised:
    cards = _deserialise_restrictions(res["rdfs:subClassOf"])
    return ResourceDeserialised(cls_id=res["@id"], restrictions=cards)


def _deserialise_restrictions(sub_class_bns: list[dict[str, Any]]) -> dict[str, Cardinality]:
    only_restrct = [x for x in sub_class_bns if x.get("salsah-gui:guiOrder") is not None]
    all_cards: list[Cardinality] = []
    for bn in only_restrct:
        prp = bn["owl:onProperty"]["@id"]
        if bn.get("owl:cardinality") == 1:
            all_cards.append(CardinalityOne(prp))
        elif bn.get("owl:minCardinality") == 0:
            all_cards.append(CardinalityZeroToN(prp))
    return {x.onProperty: x for x in all_cards}


def _deserialise_properties(onto: list[dict[str, Any]], list_lookup: ListDeserialised) -> list[Property]:
    all_props = _extract_all_onto_properties(onto)
    deserialised_props: list[Property] = []

    supers = _get_subclasses(onto)
    link_props = [x for x in all_props if x.get("knora-api:isLinkProperty")]
    deserialised_props.extend([_deserialise_link_prop(x, supers) for x in link_props])

    list_props = [x for x in all_props if x["knora-api:objectType"]["@id"] == "knora-api:ListValue"]
    deserialised_props.extend([_deserialise_list_prop(x, list_lookup) for x in list_props])

    for prop in all_props:
        if des := _deserialise_other_property(prop):
            deserialised_props.append(des)
    return deserialised_props


def _extract_all_onto_properties(onto: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [x for x in onto if x.get("knora-api:isResourceProperty") and not x.get("knora-api:isLinkValueProperty")]


def _get_subclasses(onto: list[dict[str, Any]]) -> dict[str, set[str]]:
    # This is only implemented for one level of sub-classing
    resources = _extract_resources(onto)
    sub_dict = defaultdict(list)
    for r in resources:
        for subclasses in r["rdfs:subClassOf"]:
            if supr := subclasses.get("@id"):
                sub_dict[supr].append(r["@id"])
    extended_sub = deepcopy(sub_dict)
    for sub_list in sub_dict.values():
        for sub in sub_list:
            if sub in extended_sub:
                extended_sub[sub].append(sub)
            else:
                extended_sub[sub] = [sub]
    extended_sub["knora-api:Resource"].extend(extended_sub.keys())
    return {k: set(v) for k, v in extended_sub.items()}


def _deserialise_other_property(prop: dict[str, Any]) -> Property | None:
    match prop["knora-api:objectType"]["@id"]:
        case "knora-api:TextValue":
            return _deserialise_simple_text_prop(prop)
        case _:
            return None


def _deserialise_simple_text_prop(prop: dict[str, Any]) -> SimpleTextProperty:
    return SimpleTextProperty(prop_name=prop["@id"])


def _deserialise_list_prop(prop: dict[str, Any], list_lookup: ListDeserialised) -> ListProperty:
    # This is written as if only one list exists. The lookup would have to be designed to hold several lists.
    hlist = prop["salsah-gui:guiAttribute"].replace("hlist=<", "").rstrip(">")
    if not hlist == list_lookup.iri:
        return ListProperty(prop_name=prop["@id"], list_name=None, nodes=[])
    return ListProperty(prop_name=prop["@id"], list_name=list_lookup.list_name, nodes=list_lookup.nodes)


def _deserialise_link_prop(prop: dict[str, Any], supers: dict[str, set[str]]) -> LinkProperty:
    return LinkProperty(prop_name=prop["@id"], objectType=supers[prop["knora-api:objectType"]["@id"]])
