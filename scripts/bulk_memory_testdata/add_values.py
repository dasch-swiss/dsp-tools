# ruff: noqa: S311 (seeded random numbers for test data, not for cryptography)
import random
from dataclasses import dataclass
from typing import Any

from lxml import etree

from scripts.bulk_memory_testdata.xml_ids import is_element
from scripts.bulk_memory_testdata.xml_ids import localname

NAMESPACE = "https://dasch.swiss/schema"
# Only optional cardinalities: filling an unused "1" or "1-n" property would remove a cardinality error.
_OPTIONAL_CARDINALITIES = {"0-n": None, "0-1": 1}
_PROP_ELEMENTS = {
    "TextValue": ("text-prop", "text"),
    "IntValue": ("integer-prop", "integer"),
    "DecimalValue": ("decimal-prop", "decimal"),
    "DateValue": ("date-prop", "date"),
    "BooleanValue": ("boolean-prop", "boolean"),
    "ColorValue": ("color-prop", "color"),
    "GeonameValue": ("geoname-prop", "geoname"),
    "GeolocationValue": ("geolocation-prop", "geolocation"),
    "ListValue": ("list-prop", "list"),
    "TimeValue": ("time-prop", "time"),
    "UriValue": ("uri-prop", "uri"),
}


@dataclass(frozen=True)
class PropertyInfo:
    """A property that can take generated values. `max_values` is None for no limit."""

    name: str
    object_type: str
    gui_element: str | None
    max_values: int | None
    list_nodes: tuple[str, ...]
    list_name: str = ""


def get_class_properties(project: dict[str, Any], default_ontology: str) -> dict[str, list[PropertyInfo]]:
    """
    Returns the optional properties of each class that can take generated values.
    Keys and property names use the XML form: `:Name` for the default ontology, `onto:Name` for the others.
    Values that need a target (links, region previews) are not supported.
    """
    ontologies = project["project"]["ontologies"]
    list_nodes = {x["name"]: tuple(_node_names(x)) for x in project["project"].get("lists", [])}
    properties = {(onto["name"], prop["name"]): prop for onto in ontologies for prop in onto["properties"]}
    classes: dict[str, list[PropertyInfo]] = {}
    for onto in ontologies:
        for res_class in onto["resources"]:
            infos = []
            for card in res_class.get("cardinalities", []):
                if card["cardinality"] not in _OPTIONAL_CARDINALITIES or ":" not in card["propname"]:
                    continue
                prefix, prop_name = card["propname"].split(":", 1)
                prop_onto = prefix or onto["name"]
                prop = properties.get((prop_onto, prop_name))
                if prop is None or prop["object"] not in _PROP_ELEMENTS:
                    continue
                infos.append(_make_info(prop, _xml_name(prop_onto, prop_name, default_ontology), card, list_nodes))
            classes[_xml_name(onto["name"], res_class["name"], default_ontology)] = infos
    return classes


def _make_info(
    prop: dict[str, Any], xml_name: str, card: dict[str, str], list_nodes: dict[str, tuple[str, ...]]
) -> PropertyInfo:
    max_values = _OPTIONAL_CARDINALITIES[card["cardinality"]]
    nodes: tuple[str, ...] = ()
    list_name = ""
    if prop["object"] == "ListValue":
        list_name = prop.get("gui_attributes", {}).get("hlist", "")
        nodes = list_nodes.get(list_name, ())
        max_values = len(nodes) if max_values is None else min(max_values, len(nodes))
    return PropertyInfo(xml_name, prop["object"], prop.get("gui_element"), max_values, nodes, list_name)


def _node_names(node: dict[str, Any]) -> list[str]:
    names = []
    for child in node.get("nodes", []):
        names.append(child["name"])
        names.extend(_node_names(child))
    return names


def _xml_name(ontology: str, name: str, default_ontology: str) -> str:
    return f":{name}" if ontology == default_ontology else f"{ontology}:{name}"


def make_value_element(prop: PropertyInfo, index: int) -> etree._Element:
    """Makes a valid value. Values with a different index are different."""
    _, value_tag = _PROP_ELEMENTS[prop.object_type]
    element = etree.Element(f"{{{NAMESPACE}}}{value_tag}")
    match prop.object_type:
        case "TextValue" if prop.gui_element == "Richtext":
            element.attrib["encoding"] = "xml"
            element.text = f"Rich text value {index}"
        case "TextValue":
            element.attrib["encoding"] = "utf8"
            element.text = f"Text value {index}"
        case "IntValue":
            element.text = str(index)
        case "DecimalValue":
            element.text = f"{index}.25"
        case "DateValue":
            element.text = f"GREGORIAN:CE:{1000 + index:04d}-01-01"
        case "BooleanValue":
            element.text = "true"
        case "ColorValue":
            element.text = f"#{index:06x}"
        case "GeonameValue":
            element.text = str(1_000_000 + index)
        case "GeolocationValue":
            element.attrib.update({"crs": "CRS84", "longitude": f"{8 + index / 1000:.3f}", "latitude": "47.370"})
        case "ListValue":
            element.text = prop.list_nodes[index]
        case "TimeValue":
            element.text = f"2019-10-23T{index // 3600 % 24:02d}:{index // 60 % 60:02d}:{index % 60:02d}Z"
        case "UriValue":
            element.text = f"https://example.org/value/{index}"
    return element


def add_values(resource: etree._Element, properties: list[PropertyInfo], count: int, rng: random.Random) -> int:
    """
    Adds up to `count` values to properties that the resource does not use yet.
    All values of one property go into one prop element, as the XSD requires.

    Returns:
        the number of values that were added
    """
    used = {x.attrib.get("name") for x in resource if is_element(x) and localname(x).endswith("-prop")}
    free = [x for x in properties if x.name not in used]
    added: dict[PropertyInfo, int] = {}
    for _ in range(count):
        open_props = [x for x in free if x.max_values is None or added.get(x, 0) < x.max_values]
        if not open_props:
            break
        prop = rng.choice(open_props)
        added[prop] = added.get(prop, 0) + 1
    for prop, number in added.items():
        prop_tag, _ = _PROP_ELEMENTS[prop.object_type]
        prop_element = etree.SubElement(resource, f"{{{NAMESPACE}}}{prop_tag}", name=prop.name)
        if prop.list_name:
            prop_element.attrib["list"] = prop.list_name
        prop_element.extend(make_value_element(prop, index) for index in range(number))
    return sum(added.values())


def fill_resources(
    root: etree._Element, class_properties: dict[str, list[PropertyInfo]], selected_classes: set[str], seed: int
) -> int:
    """
    Gives each `<resource>` of a selected class between 2 and 50 generated values, as far as its class allows.
    The number depends only on the seed and the resource id, so the output is the same on each run.

    Returns:
        the number of values that were added
    """
    added = 0
    for res in root:
        if not is_element(res) or localname(res) != "resource" or res.attrib["restype"] not in selected_classes:
            continue
        rng = random.Random(f"{seed}:{res.attrib['id']}")
        added += add_values(res, class_properties.get(res.attrib["restype"], []), rng.randint(2, 50), rng)
    return added
