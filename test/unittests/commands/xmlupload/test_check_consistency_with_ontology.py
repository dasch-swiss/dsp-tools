from pathlib import Path

import pytest
from lxml import etree
from pytest_unordered import unordered

from dsp_tools.commands.xmlupload.check_consistency_with_ontology import (
    _diagnose_all_classes,
    _diagnose_all_properties,
    _diagnose_class,
    _diagnose_property,
    _find_problems_in_classes_and_properties,
    _get_all_class_types_and_ids,
    _get_all_classes_and_properties,
    _get_all_property_names_and_resource_ids_one_resource,
    _get_prefix_and_prop_or_cls_identifier,
)
from dsp_tools.commands.xmlupload.models.ontology_diagnose_models import OntoCheckInformation, OntoInfo
from dsp_tools.models.exceptions import UserError


def test_get_all_classes_and_properties() -> None:
    test_ele = etree.fromstring(
        """<knora shortcode="4123" default-ontology="test">
                <resource label="resA" restype=":TestThing1" id="resA" permissions="res-default">
                    <resptr-prop name=":hasResource1">
                        <resptr permissions="prop-default">resB</resptr>
                    </resptr-prop>
                </resource>
                <resource label="resB" restype=":TestThing2" id="resB" permissions="res-default">
                </resource>
                <resource label="resC" restype=":TestThing2" id="resC" permissions="res-default">
                    <resptr-prop name=":hasResource2">
                        <resptr permissions="prop-default">resB</resptr>
                    </resptr-prop>
                    <resptr-prop name=":hasResource3">
                        <resptr permissions="prop-default">resA</resptr>
                    </resptr-prop>
                </resource>
        </knora>"""
    )
    expected_classes = {":TestThing1": ["resA"], ":TestThing2": ["resB", "resC"]}
    expected_properties = {
        ":hasResource1": ["resA"],
        ":hasResource2": ["resC"],
        ":hasResource3": ["resC"],
    }
    res_classes, res_properties = _get_all_classes_and_properties(test_ele)
    assert res_classes.keys() == expected_classes.keys()
    for k, v in res_classes.items():
        assert unordered(v) == expected_classes[k]
    assert res_properties.keys() == expected_properties.keys()
    for k, v in res_properties.items():
        assert unordered(v) == expected_properties[k]


def test_get_all_class_types_and_ids() -> None:
    test_ele = etree.fromstring(
        """<knora shortcode="4123" default-ontology="test">
                <resource label="resA" restype=":TestThing1" id="resA" permissions="res-default"/>
                <resource label="resB" restype=":TestThing2" id="resB" permissions="res-default"/>
                <resource label="resC" restype=":TestThing2" id="resC" permissions="res-default"/>
        </knora>"""
    )
    expected_classes = {":TestThing1": ["resA"], ":TestThing2": ["resB", "resC"]}
    res_classes = _get_all_class_types_and_ids(test_ele)
    assert res_classes.keys() == expected_classes.keys()
    for k, v in res_classes.items():
        assert unordered(v) == expected_classes[k]


def test_get_all_property_names_and_resource_ids_one_resouce() -> None:
    test_ele = etree.fromstring(
        """<resource label="resC" restype=":TestThing2" id="resC" permissions="res-default">
                <resptr-prop name=":hasResource2">
                    <resptr permissions="prop-default">resB</resptr>
                </resptr-prop>
                <resptr-prop name=":hasResource3">
                    <resptr permissions="prop-default">resA</resptr>
                </resptr-prop>
            </resource>"""
    )
    expected = {"a": ["a"], ":hasResource2": ["resC"], ":hasResource3": ["resC"]}
    res_dic = _get_all_property_names_and_resource_ids_one_resource(test_ele, {"a": ["a"]})
    assert res_dic.keys() == expected.keys()
    for k, v in res_dic.items():
        assert unordered(v) == expected[k]


def test_find_problems_in_classes_and_properties_all_good() -> None:
    onto_check_info = OntoCheckInformation(
        default_ontology_prefix="test",
        save_location=Path(""),
        onto_lookup={
            "test": OntoInfo(classes=["classA", "classB"], properties=["propA", "propB"]),
            "knora-api": OntoInfo(classes=["knoraClassA"], properties=["knoraPropA"]),
        },
    )
    classes = {"knoraClassA": ["idA"]}
    properties = {"knora-api:knoraPropA": ["idA"]}
    _find_problems_in_classes_and_properties(classes, properties, onto_check_info)


def test_find_problems_in_classes_and_properties_problem() -> None:
    onto_check_info = OntoCheckInformation(
        default_ontology_prefix="test",
        save_location=Path(""),
        onto_lookup={
            "test": OntoInfo(classes=["classA", "classB"], properties=["propA", "propB"]),
            "knora-api": OntoInfo(classes=["knoraClassA"], properties=["knoraPropA"]),
        },
    )
    classes = {"knora": ["idA"]}
    properties = {"knora-api:knoraPropA": ["idA"]}
    with pytest.raises(UserError):
        _find_problems_in_classes_and_properties(classes, properties, onto_check_info)


class TestDiagnoseClass:
    def test_no_knora_prefix(self) -> None:
        onto_check_info = OntoCheckInformation(
            default_ontology_prefix="test",
            save_location=Path(""),
            onto_lookup={
                "test": OntoInfo(classes=["classA", "classB"], properties=[]),
                "knora-api": OntoInfo(classes=["knoraClassA"], properties=[]),
            },
        )
        assert not _diagnose_class("knoraClassA", onto_check_info)

    def test_knora_prefix(self) -> None:
        onto_check_info = OntoCheckInformation(
            default_ontology_prefix="test",
            save_location=Path(""),
            onto_lookup={
                "test": OntoInfo(classes=["classA", "classB"], properties=[]),
                "knora-api": OntoInfo(classes=["knoraClassA"], properties=[]),
            },
        )
        assert not _diagnose_class("knora-api:knoraClassA", onto_check_info)

    def test_no_default_prefix(self) -> None:
        onto_check_info = OntoCheckInformation(
            default_ontology_prefix="test",
            save_location=Path(""),
            onto_lookup={
                "test": OntoInfo(classes=["classA", "classB"], properties=[]),
                "knora-api": OntoInfo(classes=["knoraClassA"], properties=[]),
            },
        )
        assert not _diagnose_class(":classA", onto_check_info)

    def test_default_prefix(self) -> None:
        onto_check_info = OntoCheckInformation(
            default_ontology_prefix="test",
            save_location=Path(""),
            onto_lookup={
                "test": OntoInfo(classes=["classA", "classB"], properties=[]),
                "knora-api": OntoInfo(classes=["knoraClassA"], properties=[]),
            },
        )
        assert not _diagnose_class("test:classB", onto_check_info)

    def test_unknown_class(self) -> None:
        onto_check_info = OntoCheckInformation(
            default_ontology_prefix="test",
            save_location=Path(""),
            onto_lookup={
                "test": OntoInfo(classes=["classA", "classB"], properties=[]),
                "knora-api": OntoInfo(classes=["knoraClassA"], properties=[]),
            },
        )
        assert _diagnose_class("test:classC", onto_check_info) == "Invalid Class Type"

    def test_unknown_prefix(self) -> None:
        onto_check_info = OntoCheckInformation(
            default_ontology_prefix="test",
            save_location=Path(""),
            onto_lookup={
                "test": OntoInfo(classes=["classA", "classB"], properties=[]),
                "knora-api": OntoInfo(classes=["knoraClassA"], properties=[]),
            },
        )
        assert _diagnose_class("other:classC", onto_check_info) == "Unknown ontology prefix"

    def test_diagnose_all_classes_no_problems(self) -> None:
        onto_check_info = OntoCheckInformation(
            default_ontology_prefix="test",
            save_location=Path(""),
            onto_lookup={
                "test": OntoInfo(classes=["classA", "classB"], properties=[]),
                "knora-api": OntoInfo(classes=["knoraClassA"], properties=[]),
            },
        )
        test_classes = {"knora-api:knoraClassA": ["idA"], ":classB": ["idB"]}
        assert not _diagnose_all_classes(test_classes, onto_check_info)

    def test_diagnose_all_classes_problems(self) -> None:
        onto_check_info = OntoCheckInformation(
            default_ontology_prefix="test",
            save_location=Path(""),
            onto_lookup={
                "test": OntoInfo(classes=["classA", "classB"], properties=[]),
                "knora-api": OntoInfo(classes=["knoraClassA"], properties=[]),
            },
        )
        test_classes = {"knoraClassA": ["idA"], ":classD": ["idD"]}
        assert _diagnose_all_classes(test_classes, onto_check_info) == [(":classD", ["idD"], "Invalid Class Type")]


class TestDiagnoseProperties:
    def test_no_knora_prefix(self) -> None:
        onto_check_info = OntoCheckInformation(
            default_ontology_prefix="test",
            save_location=Path(""),
            onto_lookup={
                "test": OntoInfo(classes=[], properties=["propA", "propB"]),
                "knora-api": OntoInfo(classes=[], properties=["knoraPropA"]),
            },
        )
        assert not _diagnose_property("knoraPropA", onto_check_info)

    def test_knora_prefix(self) -> None:
        onto_check_info = OntoCheckInformation(
            default_ontology_prefix="test",
            save_location=Path(""),
            onto_lookup={
                "test": OntoInfo(classes=[], properties=["propA", "propB"]),
                "knora-api": OntoInfo(classes=[], properties=["knoraPropA"]),
            },
        )
        assert not _diagnose_property("knora-api:knoraPropA", onto_check_info)

    def test_no_default_prefix(self) -> None:
        onto_check_info = OntoCheckInformation(
            default_ontology_prefix="test",
            save_location=Path(""),
            onto_lookup={
                "test": OntoInfo(classes=[], properties=["propA", "propB"]),
                "knora-api": OntoInfo(classes=[], properties=["knoraPropA"]),
            },
        )
        assert not _diagnose_property(":propA", onto_check_info)

    def test_default_prefix(self) -> None:
        onto_check_info = OntoCheckInformation(
            default_ontology_prefix="test",
            save_location=Path(""),
            onto_lookup={
                "test": OntoInfo(classes=[], properties=["propA", "propB"]),
                "knora-api": OntoInfo(classes=[], properties=["knoraPropA"]),
            },
        )
        assert not _diagnose_property("test:propB", onto_check_info)

    def test_unknown_prefix(self) -> None:
        onto_check_info = OntoCheckInformation(
            default_ontology_prefix="test",
            save_location=Path(""),
            onto_lookup={
                "test": OntoInfo(classes=[], properties=["propA", "propB"]),
                "knora-api": OntoInfo(classes=[], properties=["knoraPropA"]),
            },
        )
        assert _diagnose_property("other:propB", onto_check_info) == "Unknown ontology prefix"

    def test_unknown_property(self) -> None:
        onto_check_info = OntoCheckInformation(
            default_ontology_prefix="test",
            save_location=Path(""),
            onto_lookup={
                "test": OntoInfo(classes=[], properties=["propA", "propB"]),
                "knora-api": OntoInfo(classes=[], properties=["knoraPropA"]),
            },
        )
        assert _diagnose_property("test:propC", onto_check_info) == "Invalid Property"

    def test_diagnose_all_properties_problems(self) -> None:
        onto_check_info = OntoCheckInformation(
            default_ontology_prefix="test",
            save_location=Path(""),
            onto_lookup={
                "test": OntoInfo(classes=[], properties=["propA", "propB"]),
                "knora-api": OntoInfo(classes=[], properties=["knoraPropA"]),
            },
        )
        test_properties = {"test:propB": ["idB"], "other:propB": ["idB"], "test:propD": ["idD"]}
        expected = [("other:propB", ["idB"], "Unknown ontology prefix"), ("test:propD", ["idD"], "Invalid Property")]
        assert unordered(_diagnose_all_properties(test_properties, onto_check_info)) == expected

    def test_diagnose_all_properties_no_problems(self) -> None:
        onto_check_info = OntoCheckInformation(
            default_ontology_prefix="test",
            save_location=Path(""),
            onto_lookup={
                "test": OntoInfo(classes=[], properties=["propA", "propB"]),
                "knora-api": OntoInfo(classes=[], properties=["knoraPropA"]),
            },
        )
        test_properties = {"test:propB": ["idB"], "knoraPropA": ["idA"]}
        assert not unordered(_diagnose_all_properties(test_properties, onto_check_info))


def test_get_prefix_and_prop_cls_identifier() -> None:
    assert _get_prefix_and_prop_or_cls_identifier(":propA", "test") == ("test", "propA")
    assert _get_prefix_and_prop_or_cls_identifier("knora-api:knoraPropA", "test") == ("knora-api", "knoraPropA")
    assert _get_prefix_and_prop_or_cls_identifier("knoraPropB", "test") == ("knora-api", "knoraPropB")
    assert _get_prefix_and_prop_or_cls_identifier("test:propA", "test") == ("test", "propA")


def test_get_prefix_and_prop_cls_identifier_error() -> None:
    assert _get_prefix_and_prop_or_cls_identifier("123654/", "test") == (None, None)
