from pathlib import Path

import pytest
from lxml import etree
from pytest_unordered import unordered

from dsp_tools.commands.xmlupload.check_consistency_with_ontology import (
    _diagnose_all_classes,
    _diagnose_all_properties,
    _diagnose_class,
    _diagnose_properties,
    _find_problems_in_classes_and_properties,
    _get_all_class_types_and_ids,
    _get_all_classes_and_properties,
    _get_all_property_names_and_resource_ids,
    _get_prefix_and_prop_cls_identifier,
)
from dsp_tools.commands.xmlupload.models.ontology_diagnose_models import OntoCheckInformation, Ontology
from dsp_tools.models.exceptions import BaseError

# pylint: disable=missing-function-docstring,missing-class-docstring


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
    expected_classes = [["resA", ":TestThing1"], ["resB", ":TestThing2"], ["resC", ":TestThing2"]]
    expected_properties = [["resA", ":hasResource1"], ["resC", ":hasResource2"], ["resC", ":hasResource3"]]
    res_classes, res_properties = _get_all_classes_and_properties(test_ele)
    assert unordered(res_classes) == expected_classes
    assert unordered(res_properties) == expected_properties


def test_get_all_class_types_and_ids() -> None:
    test_ele = etree.fromstring(
        """<knora shortcode="4123" default-ontology="test">
                <resource label="resA" restype=":TestThing1" id="resA" permissions="res-default">
                </resource>
                <resource label="resB" restype=":TestThing2" id="resB" permissions="res-default">
                </resource>
                <resource label="resC" restype=":TestThing2" id="resC" permissions="res-default">
                </resource>
        </knora>"""
    )
    expected = [["resA", ":TestThing1"], ["resB", ":TestThing2"], ["resC", ":TestThing2"]]
    assert unordered(_get_all_class_types_and_ids(test_ele)) == expected


def test_get_all_property_names_and_resource_ids() -> None:
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
    expected = [["resC", ":hasResource2"], ["resC", ":hasResource3"]]
    assert unordered(_get_all_property_names_and_resource_ids(test_ele)) == expected


def test_find_problems_in_classes_and_properties() -> None:
    onto_check_info = OntoCheckInformation(
        default_ontology_prefix="test",
        save_location=Path(""),
        onto_lookup={
            "test": Ontology(classes=["classA", "classB"], properties=["propA", "propB"]),
            "knora-api": Ontology(classes=["knoraClassA"], properties=["knoraPropA"]),
        },
    )
    classes = [["idA", "knoraClassA"]]
    properties = [["idA", "knora-api:knoraPropA"]]
    assert not _find_problems_in_classes_and_properties(
        classes, properties, onto_check_info
    )  # type: ignore[func-returns-value]


class TestDiagnoseClass:
    @staticmethod
    def test_no_knora_prefix() -> None:
        onto_check_info = OntoCheckInformation(
            default_ontology_prefix="test",
            save_location=Path(""),
            onto_lookup={
                "test": Ontology(classes=["classA", "classB"], properties=[]),
                "knora-api": Ontology(classes=["knoraClassA"], properties=[]),
            },
        )
        assert not _diagnose_class(["idA", "knoraClassA"], onto_check_info)

    @staticmethod
    def test_knora_prefix() -> None:
        onto_check_info = OntoCheckInformation(
            default_ontology_prefix="test",
            save_location=Path(""),
            onto_lookup={
                "test": Ontology(classes=["classA", "classB"], properties=[]),
                "knora-api": Ontology(classes=["knoraClassA"], properties=[]),
            },
        )

        assert not _diagnose_class(["idA", "knora-api:knoraClassA"], onto_check_info)

    @staticmethod
    def test_no_default_prefix() -> None:
        onto_check_info = OntoCheckInformation(
            default_ontology_prefix="test",
            save_location=Path(""),
            onto_lookup={
                "test": Ontology(classes=["classA", "classB"], properties=[]),
                "knora-api": Ontology(classes=["knoraClassA"], properties=[]),
            },
        )
        assert not _diagnose_class(["idA", ":classA"], onto_check_info)

    @staticmethod
    def test_default_prefix() -> None:
        onto_check_info = OntoCheckInformation(
            default_ontology_prefix="test",
            save_location=Path(""),
            onto_lookup={
                "test": Ontology(classes=["classA", "classB"], properties=[]),
                "knora-api": Ontology(classes=["knoraClassA"], properties=[]),
            },
        )
        assert not _diagnose_class(["idB", "test:classB"], onto_check_info)

    @staticmethod
    def test_unknown_class() -> None:
        onto_check_info = OntoCheckInformation(
            default_ontology_prefix="test",
            save_location=Path(""),
            onto_lookup={
                "test": Ontology(classes=["classA", "classB"], properties=[]),
                "knora-api": Ontology(classes=["knoraClassA"], properties=[]),
            },
        )
        expected = ["idC", "test:classC", "Invalid Class Type"]
        assert _diagnose_class(["idC", "test:classC"], onto_check_info) == expected

    @staticmethod
    def test_unknown_prefix() -> None:
        onto_check_info = OntoCheckInformation(
            default_ontology_prefix="test",
            save_location=Path(""),
            onto_lookup={
                "test": Ontology(classes=["classA", "classB"], properties=[]),
                "knora-api": Ontology(classes=["knoraClassA"], properties=[]),
            },
        )
        expected = ["idC", "other:classC", "Unknown ontology prefix"]
        assert _diagnose_class(["idC", "other:classC"], onto_check_info) == expected

    @staticmethod
    def test_diagnose_all_classes_no_problems() -> None:
        onto_check_info = OntoCheckInformation(
            default_ontology_prefix="test",
            save_location=Path(""),
            onto_lookup={
                "test": Ontology(classes=["classA", "classB"], properties=[]),
                "knora-api": Ontology(classes=["knoraClassA"], properties=[]),
            },
        )
        test_classes = [["idA", "knora-api:knoraClassA"], ["idB", ":classB"]]
        assert not _diagnose_all_classes(test_classes, onto_check_info)

    @staticmethod
    def test_diagnose_all_classes_problems() -> None:
        onto_check_info = OntoCheckInformation(
            default_ontology_prefix="test",
            save_location=Path(""),
            onto_lookup={
                "test": Ontology(classes=["classA", "classB"], properties=[]),
                "knora-api": Ontology(classes=["knoraClassA"], properties=[]),
            },
        )
        test_classes = [["idA", "knoraClassA"], ["idD", ":classD"]]
        assert _diagnose_all_classes(test_classes, onto_check_info) == [["idD", ":classD", "Invalid Class Type"]]


class TestDiagnoseProperties:
    @staticmethod
    def test_no_knora_prefix() -> None:
        onto_check_info = OntoCheckInformation(
            default_ontology_prefix="test",
            save_location=Path(""),
            onto_lookup={
                "test": Ontology(classes=[], properties=["propA", "propB"]),
                "knora-api": Ontology(classes=[], properties=["knoraPropA"]),
            },
        )
        assert not _diagnose_properties(["idA", "knoraPropA"], onto_check_info)

    @staticmethod
    def test_knora_prefix() -> None:
        onto_check_info = OntoCheckInformation(
            default_ontology_prefix="test",
            save_location=Path(""),
            onto_lookup={
                "test": Ontology(classes=[], properties=["propA", "propB"]),
                "knora-api": Ontology(classes=[], properties=["knoraPropA"]),
            },
        )
        assert not _diagnose_properties(["idA", "knora-api:knoraPropA"], onto_check_info)

    @staticmethod
    def test_no_default_prefix() -> None:
        onto_check_info = OntoCheckInformation(
            default_ontology_prefix="test",
            save_location=Path(""),
            onto_lookup={
                "test": Ontology(classes=[], properties=["propA", "propB"]),
                "knora-api": Ontology(classes=[], properties=["knoraPropA"]),
            },
        )
        assert not _diagnose_properties(["idA", ":propA"], onto_check_info)

    @staticmethod
    def test_default_prefix() -> None:
        onto_check_info = OntoCheckInformation(
            default_ontology_prefix="test",
            save_location=Path(""),
            onto_lookup={
                "test": Ontology(classes=[], properties=["propA", "propB"]),
                "knora-api": Ontology(classes=[], properties=["knoraPropA"]),
            },
        )
        assert not _diagnose_properties(["idB", "test:propB"], onto_check_info)

    @staticmethod
    def test_unknown_prefix() -> None:
        onto_check_info = OntoCheckInformation(
            default_ontology_prefix="test",
            save_location=Path(""),
            onto_lookup={
                "test": Ontology(classes=[], properties=["propA", "propB"]),
                "knora-api": Ontology(classes=[], properties=["knoraPropA"]),
            },
        )
        res = _diagnose_properties(["idB", "other:propB"], onto_check_info)
        assert unordered(res) == ["idB", "other:propB", "Unknown ontology prefix"]

    @staticmethod
    def test_unknown_property() -> None:
        onto_check_info = OntoCheckInformation(
            default_ontology_prefix="test",
            save_location=Path(""),
            onto_lookup={
                "test": Ontology(classes=[], properties=["propA", "propB"]),
                "knora-api": Ontology(classes=[], properties=["knoraPropA"]),
            },
        )
        expected = ["id", "test:propC", "Invalid Property"]
        assert _diagnose_properties(["id", "test:propC"], onto_check_info) == expected

    @staticmethod
    def test_diagnose_all_properties_problems() -> None:
        onto_check_info = OntoCheckInformation(
            default_ontology_prefix="test",
            save_location=Path(""),
            onto_lookup={
                "test": Ontology(classes=[], properties=["propA", "propB"]),
                "knora-api": Ontology(classes=[], properties=["knoraPropA"]),
            },
        )
        test_properties = [["idB", "test:propB"], ["idB", "other:propB"], ["idD", "test:propD"]]
        expected = [["idB", "other:propB", "Unknown ontology prefix"], ["idD", "test:propD", "Invalid Property"]]
        assert unordered(_diagnose_all_properties(test_properties, onto_check_info)) == expected

    @staticmethod
    def test_diagnose_all_properties_no_problems() -> None:
        onto_check_info = OntoCheckInformation(
            default_ontology_prefix="test",
            save_location=Path(""),
            onto_lookup={
                "test": Ontology(classes=[], properties=["propA", "propB"]),
                "knora-api": Ontology(classes=[], properties=["knoraPropA"]),
            },
        )
        test_properties = [["idB", "test:propB"], ["idA", "knoraPropA"]]
        assert not unordered(_diagnose_all_properties(test_properties, onto_check_info))


def test_get_prefix_and_prop_cls_identifier() -> None:
    assert _get_prefix_and_prop_cls_identifier(":propA", "test") == ("test", "propA")
    assert _get_prefix_and_prop_cls_identifier("knora-api:knoraPropA", "test") == ("knora-api", "knoraPropA")
    assert _get_prefix_and_prop_cls_identifier("knoraPropB", "test") == ("knora-api", "knoraPropB")
    assert _get_prefix_and_prop_cls_identifier("test:propA", "test") == ("test", "propA")


def test_get_prefix_and_prop_cls_identifier_error() -> None:
    with pytest.raises(
        BaseError, match="The input property or class: '123654' does not follow a known ontology pattern."
    ):
        _get_prefix_and_prop_cls_identifier("123654", "test")
