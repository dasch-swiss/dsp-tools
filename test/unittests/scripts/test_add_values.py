# ruff: noqa: S311 (seeded random numbers for test data, not for cryptography)
import random
from collections import Counter

from lxml import etree

from scripts.bulk_memory_testdata.add_values import PropertyInfo
from scripts.bulk_memory_testdata.add_values import add_values
from scripts.bulk_memory_testdata.add_values import fill_resources
from scripts.bulk_memory_testdata.add_values import get_class_properties
from scripts.bulk_memory_testdata.add_values import make_value_element

NS = "https://dasch.swiss/schema"

PROJECT = {
    "project": {
        "lists": [{"name": "firstList", "nodes": [{"name": "n1", "nodes": [{"name": "n1.1"}]}]}],
        "ontologies": [
            {
                "name": "onto",
                "properties": [
                    {"name": "testText", "object": "TextValue", "gui_element": "SimpleText"},
                    {"name": "testRich", "object": "TextValue", "gui_element": "Richtext"},
                    {"name": "testInt", "object": "IntValue", "gui_element": "Spinbox"},
                    {"name": "testBool", "object": "BooleanValue", "gui_element": "Checkbox"},
                    {
                        "name": "testList",
                        "object": "ListValue",
                        "gui_element": "List",
                        "gui_attributes": {"hlist": "firstList"},
                    },
                    {"name": "testRequired", "object": "IntValue", "gui_element": "Spinbox"},
                    {"name": "testLink", "object": "Resource", "gui_element": "Searchbox"},
                ],
                "resources": [
                    {
                        "name": "Thing",
                        "cardinalities": [
                            {"propname": ":testText", "cardinality": "0-n"},
                            {"propname": ":testRich", "cardinality": "0-n"},
                            {"propname": ":testInt", "cardinality": "0-n"},
                            {"propname": ":testBool", "cardinality": "0-1"},
                            {"propname": ":testList", "cardinality": "0-n"},
                            {"propname": ":testRequired", "cardinality": "1"},
                            {"propname": ":testLink", "cardinality": "0-n"},
                        ],
                    }
                ],
            },
            {"name": "in-built", "properties": [], "resources": [{"name": "Other"}]},
        ],
    }
}


def _resource(body: str = "", restype: str = ":Thing") -> etree._Element:
    xml = f'<knora xmlns="{NS}"><resource label="a" restype="{restype}" id="a">{body}</resource></knora>'
    return etree.fromstring(xml)[0]


def _values_by_property(resource: etree._Element) -> dict[str, list[str]]:
    return {
        prop.attrib["name"]: [(v.text or "") + str(dict(v.attrib)) for v in prop]
        for prop in resource
        if isinstance(prop.tag, str)
    }


class TestGetClassProperties:
    def test_default_ontology_gets_the_empty_prefix(self) -> None:
        classes = get_class_properties(PROJECT, default_ontology="onto")
        assert set(classes) == {":Thing", "in-built:Other"}

    def test_keeps_only_optional_supported_properties(self) -> None:
        props = get_class_properties(PROJECT, default_ontology="onto")[":Thing"]
        assert [x.name for x in props] == [":testText", ":testRich", ":testInt", ":testBool", ":testList"]

    def test_capacity(self) -> None:
        props = {x.name: x for x in get_class_properties(PROJECT, default_ontology="onto")[":Thing"]}
        assert props[":testBool"].max_values == 1
        assert props[":testList"].max_values == 2
        assert props[":testList"].list_nodes == ("n1", "n1.1")
        assert props[":testText"].max_values is None


class TestMakeValueElement:
    def test_values_differ_by_index(self) -> None:
        prop = PropertyInfo(":testText", "TextValue", "SimpleText", None, ())
        first = make_value_element(prop, 0)
        second = make_value_element(prop, 1)
        assert first.text != second.text
        assert first.attrib["encoding"] == "utf8"

    def test_richtext_encoding(self) -> None:
        prop = PropertyInfo(":testRich", "TextValue", "Richtext", None, ())
        assert make_value_element(prop, 0).attrib["encoding"] == "xml"

    def test_list_node(self) -> None:
        prop = PropertyInfo(":testList", "ListValue", "List", 2, ("n1", "n1.1"), "firstList")
        assert [make_value_element(prop, i).text for i in (0, 1)] == ["n1", "n1.1"]


class TestAddValues:
    def _props(self) -> list[PropertyInfo]:
        return get_class_properties(PROJECT, default_ontology="onto")[":Thing"]

    def test_adds_the_requested_number(self) -> None:
        res = _resource()
        added = add_values(res, self._props(), 20, random.Random(1))
        assert added == 20
        assert sum(len(x) for x in _values_by_property(res).values()) == 20

    def test_one_prop_element_per_property_and_no_duplicate_values(self) -> None:
        res = _resource()
        add_values(res, self._props(), 40, random.Random(2))
        names = [x.attrib["name"] for x in res if isinstance(x.tag, str)]
        assert len(names) == len(set(names))
        for values in _values_by_property(res).values():
            assert len(values) == len(set(values))

    def test_respects_capacity(self) -> None:
        res = _resource()
        add_values(res, self._props(), 50, random.Random(3))
        counts = Counter({k: len(v) for k, v in _values_by_property(res).items()})
        assert counts[":testBool"] <= 1
        assert counts[":testList"] <= 2

    def test_skips_properties_the_resource_uses(self) -> None:
        res = _resource('<integer-prop name=":testInt"><integer>abc</integer></integer-prop>')
        add_values(res, self._props(), 30, random.Random(4))
        assert _values_by_property(res)[":testInt"] == ["abc{}"]

    def test_stops_when_no_property_is_left(self) -> None:
        bool_only = [PropertyInfo(":testBool", "BooleanValue", "Checkbox", 1, ())]
        res = _resource()
        assert add_values(res, bool_only, 10, random.Random(5)) == 1

    def test_list_prop_names_its_list(self) -> None:
        props = [x for x in self._props() if x.name == ":testList"]
        res = _resource()
        add_values(res, props, 2, random.Random(6))
        assert res[0].attrib["list"] == "firstList"


class TestFillResources:
    def _root(self) -> etree._Element:
        xml = (
            f'<knora xmlns="{NS}">'
            '<resource label="a" restype=":Thing" id="a"/>'
            '<resource label="b" restype=":Thing" id="b"/>'
            '<resource label="c" restype="in-built:Other" id="c"/>'
            '<region label="r" id="r"/>'
            "</knora>"
        )
        return etree.fromstring(xml)

    def test_only_selected_classes_get_values(self) -> None:
        root = self._root()
        classes = get_class_properties(PROJECT, default_ontology="onto")
        fill_resources(root, classes, {":Thing"}, seed=1)
        counts = {x.attrib["id"]: len(x) for x in root}
        assert counts["a"] > 0
        assert counts["b"] > 0
        assert counts["c"] == 0
        assert counts["r"] == 0

    def test_is_deterministic(self) -> None:
        classes = get_class_properties(PROJECT, default_ontology="onto")
        first, second = self._root(), self._root()
        fill_resources(first, classes, {":Thing"}, seed=1)
        fill_resources(second, classes, {":Thing"}, seed=1)
        assert etree.tostring(first) == etree.tostring(second)

    def test_count_is_between_2_and_50(self) -> None:
        many = {":Big": [PropertyInfo(":t", "TextValue", "SimpleText", None, ())]}
        root = etree.fromstring(
            f'<knora xmlns="{NS}">'
            + "".join(f'<resource label="x" restype=":Big" id="r{i}"/>' for i in range(40))
            + "</knora>"
        )
        added = fill_resources(root, many, {":Big"}, seed=7)
        counts = [len(x[0]) for x in root]
        assert min(counts) >= 2
        assert max(counts) <= 50
        assert len(set(counts)) > 5
        assert added == sum(counts)
