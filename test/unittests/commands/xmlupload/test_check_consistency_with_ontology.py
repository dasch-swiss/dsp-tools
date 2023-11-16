import pytest

from dsp_tools.commands.xmlupload.check_consistency_with_ontology import (
    OntoRegEx,
    _diagnose_classes,
    _diagnose_properties,
    _identify_ontology,
)
from dsp_tools.commands.xmlupload.ontology_client import Ontology
from dsp_tools.models.exceptions import BaseError

# pylint: disable=missing-function-docstring

onto_regex = OntoRegEx(default_ontology_prefix="test")


def test_diagnose_classes_no_knora_prefix() -> None:
    onto_lookup = {
        "test": Ontology(classes=["classA", "classB"], properties=["propA", "propB"]),
        "knora-api": Ontology(classes=["knoraClassA"], properties=["knoraPropA"]),
    }
    assert _diagnose_classes("knoraClassA", onto_regex, onto_lookup)


def test_diagnose_classes_knora_prefix() -> None:
    onto_lookup = {
        "test": Ontology(classes=["classA", "classB"], properties=["propA", "propB"]),
        "knora-api": Ontology(classes=["knoraClassA"], properties=["knoraPropA"]),
    }
    assert _diagnose_classes("knora-api:knoraClassA", onto_regex, onto_lookup)


def test_diagnose_classes_no_default_prefix() -> None:
    onto_lookup = {
        "test": Ontology(classes=["classA", "classB"], properties=["propA", "propB"]),
        "knora-api": Ontology(classes=["knoraClassA"], properties=["knoraPropA"]),
    }
    assert _diagnose_classes(":classA", onto_regex, onto_lookup)


def test_diagnose_classes_default_prefix() -> None:
    onto_lookup = {
        "test": Ontology(classes=["classA", "classB"], properties=["propA", "propB"]),
        "knora-api": Ontology(classes=["knoraClassA"], properties=["knoraPropA"]),
    }
    assert _diagnose_classes("test:classB", onto_regex, onto_lookup)


def test_diagnose_properties_no_knora_prefix() -> None:
    onto_lookup = {
        "test": Ontology(classes=["classA", "classB"], properties=["propA", "propB"]),
        "knora-api": Ontology(classes=["knoraClassA"], properties=["knoraPropA"]),
    }
    assert _diagnose_properties("knoraPropA", onto_regex, onto_lookup)


def test_diagnose_properties_knora_prefix() -> None:
    onto_lookup = {
        "test": Ontology(classes=["classA", "classB"], properties=["propA", "propB"]),
        "knora-api": Ontology(classes=["knoraClassA"], properties=["knoraPropA"]),
    }
    assert _diagnose_properties("knora-api:knoraPropA", onto_regex, onto_lookup)


def test_diagnose_properties_no_default_prefix() -> None:
    onto_lookup = {
        "test": Ontology(classes=["classA", "classB"], properties=["propA", "propB"]),
        "knora-api": Ontology(classes=["knoraClassA"], properties=["knoraPropA"]),
    }
    assert _diagnose_properties(":propA", onto_regex, onto_lookup)


def test_diagnose_properties_default_prefix() -> None:
    onto_lookup = {
        "test": Ontology(classes=["classA", "classB"], properties=["propA", "propB"]),
        "knora-api": Ontology(classes=["knoraClassA"], properties=["knoraPropA"]),
    }
    assert _diagnose_properties("test:propB", onto_regex, onto_lookup)


def test_identify_ontology() -> None:
    assert _identify_ontology(":propA", onto_regex) == ("test", "propA")
    assert _identify_ontology("knora-api:knoraPropA", onto_regex) == ("knora-api", "knoraPropA")
    assert _identify_ontology("knoraPropB", onto_regex) == ("knora-api", "knoraPropB")
    assert _identify_ontology("test:propA", onto_regex) == ("test", "propA")


def test_identify_ontology_error() -> None:
    with pytest.raises(
        BaseError, match="The input property or class: '123654' does not follow a known ontology pattern."
    ):
        _identify_ontology("123654", onto_regex)
