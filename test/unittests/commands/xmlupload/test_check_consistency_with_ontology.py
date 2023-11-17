from pathlib import Path

import pytest

from dsp_tools.commands.xmlupload.check_consistency_with_ontology import (
    _diagnose_class,
    _diagnose_properties,
    _get_prefix_and_prop_cls_identifier,
)
from dsp_tools.commands.xmlupload.models.ontology_diagnose_models import OntoCheckInformation, Ontology
from dsp_tools.models.exceptions import BaseError

# pylint: disable=missing-function-docstring


class TestDiagnoseClass:
    @staticmethod
    def test_no_knora_prefix() -> None:
        onto_tool = OntoCheckInformation(
            default_ontology_prefix="test",
            save_location=Path(""),
            onto_lookup={
                "test": Ontology(classes=["classA", "classB"], properties=["propA", "propB"]),
                "knora-api": Ontology(classes=["knoraClassA"], properties=["knoraPropA"]),
            },
        )
        assert _diagnose_class("knoraClassA", onto_tool)

    @staticmethod
    def test_knora_prefix() -> None:
        onto_tool = OntoCheckInformation(
            default_ontology_prefix="test",
            save_location=Path(""),
            onto_lookup={
                "test": Ontology(classes=["classA", "classB"], properties=["propA", "propB"]),
                "knora-api": Ontology(classes=["knoraClassA"], properties=["knoraPropA"]),
            },
        )

        assert _diagnose_class("knora-api:knoraClassA", onto_tool)

    @staticmethod
    def test_no_default_prefix() -> None:
        onto_tool = OntoCheckInformation(
            default_ontology_prefix="test",
            save_location=Path(""),
            onto_lookup={
                "test": Ontology(classes=["classA", "classB"], properties=["propA", "propB"]),
                "knora-api": Ontology(classes=["knoraClassA"], properties=["knoraPropA"]),
            },
        )
        assert _diagnose_class(":classA", onto_tool)

    @staticmethod
    def test_default_prefix() -> None:
        onto_tool = OntoCheckInformation(
            default_ontology_prefix="test",
            save_location=Path(""),
            onto_lookup={
                "test": Ontology(classes=["classA", "classB"], properties=["propA", "propB"]),
                "knora-api": Ontology(classes=["knoraClassA"], properties=["knoraPropA"]),
            },
        )
        assert _diagnose_class("test:classB", onto_tool)


class TestDiagnoseProperties:
    @staticmethod
    def test_no_knora_prefix() -> None:
        onto_tool = OntoCheckInformation(
            default_ontology_prefix="test",
            save_location=Path(""),
            onto_lookup={
                "test": Ontology(classes=["classA", "classB"], properties=["propA", "propB"]),
                "knora-api": Ontology(classes=["knoraClassA"], properties=["knoraPropA"]),
            },
        )
        assert _diagnose_properties("knoraPropA", onto_tool)

    @staticmethod
    def test_knora_prefix() -> None:
        onto_tool = OntoCheckInformation(
            default_ontology_prefix="test",
            save_location=Path(""),
            onto_lookup={
                "test": Ontology(classes=["classA", "classB"], properties=["propA", "propB"]),
                "knora-api": Ontology(classes=["knoraClassA"], properties=["knoraPropA"]),
            },
        )
        assert _diagnose_properties("knora-api:knoraPropA", onto_tool)

    @staticmethod
    def test_no_default_prefix() -> None:
        onto_tool = OntoCheckInformation(
            default_ontology_prefix="test",
            save_location=Path(""),
            onto_lookup={
                "test": Ontology(classes=["classA", "classB"], properties=["propA", "propB"]),
                "knora-api": Ontology(classes=["knoraClassA"], properties=["knoraPropA"]),
            },
        )
        assert _diagnose_properties(":propA", onto_tool)

    @staticmethod
    def test_default_prefix() -> None:
        onto_tool = OntoCheckInformation(
            default_ontology_prefix="test",
            save_location=Path(""),
            onto_lookup={
                "test": Ontology(classes=["classA", "classB"], properties=["propA", "propB"]),
                "knora-api": Ontology(classes=["knoraClassA"], properties=["knoraPropA"]),
            },
        )
        assert _diagnose_properties("test:propB", onto_tool)


def test_get_prefix_and_prop_cls_identifier() -> None:
    onto_tool = OntoCheckInformation(
        default_ontology_prefix="test",
        save_location=Path(""),
        onto_lookup={
            "test": Ontology(classes=["classA", "classB"], properties=["propA", "propB"]),
            "knora-api": Ontology(classes=["knoraClassA"], properties=["knoraPropA"]),
        },
    )
    assert _get_prefix_and_prop_cls_identifier(":propA", onto_tool) == ("test", "propA")
    assert _get_prefix_and_prop_cls_identifier("knora-api:knoraPropA", onto_tool) == ("knora-api", "knoraPropA")
    assert _get_prefix_and_prop_cls_identifier("knoraPropB", onto_tool) == ("knora-api", "knoraPropB")
    assert _get_prefix_and_prop_cls_identifier("test:propA", onto_tool) == ("test", "propA")


def test_get_prefix_and_prop_cls_identifier_error() -> None:
    onto_tool = OntoCheckInformation(
        default_ontology_prefix="test",
        save_location=Path(""),
        onto_lookup={
            "test": Ontology(classes=["classA", "classB"], properties=["propA", "propB"]),
            "knora-api": Ontology(classes=["knoraClassA"], properties=["knoraPropA"]),
        },
    )
    with pytest.raises(
        BaseError, match="The input property or class: '123654' does not follow a known ontology pattern."
    ):
        _get_prefix_and_prop_cls_identifier("123654", onto_tool)
