from pathlib import Path

import pytest

from dsp_tools.commands.xmlupload.ontology_diagnose_models import UnknownOntologyElements
from dsp_tools.models.exceptions import UserError

# pylint: disable=missing-function-docstring,anomalous-backslash-in-string,protected-access


def test_not_empty_false() -> None:
    onto = UnknownOntologyElements(Path(""), [], [])
    assert not onto.not_empty()


def test_not_empty_true_cls() -> None:
    onto = UnknownOntologyElements(Path(""), [("a", "b")], [])
    assert onto.not_empty()


def test_not_empty_true_prop() -> None:
    onto = UnknownOntologyElements(Path(""), [], [("a", "b")])
    assert onto.not_empty()


def test_print_problem_string_cls() -> None:
    onto = UnknownOntologyElements(Path(""), [("idA", "clsA")], [])
    msg = onto._print_problem_string_cls()
    assert msg == (
        "The following resource(s) have an invalid resource type:\n\t- Resource ID: 'idA', Resource Type: 'clsA'"
    )


def test_print_problem_string_no_cls() -> None:
    onto = UnknownOntologyElements(Path(""), [], [])
    msg = onto._print_problem_string_cls()
    assert msg == ""


def test_print_problem_string_prop() -> None:
    onto = UnknownOntologyElements(Path(""), [], [("idA", "propA")])
    msg = onto._print_problem_string_props()
    assert msg == (
        "The following resource(s) have invalid property type(s):\n\t- Resource ID: 'idA', Property Name: 'propA'"
    )


def test_print_problem_string_no_prop() -> None:
    onto = UnknownOntologyElements(Path(""), [], [])
    msg = onto._print_problem_string_props()
    assert msg == ""


def test_execute_problem_protocol() -> None:
    onto = UnknownOntologyElements(Path(""), [("idB", "clsB")], [("idA", "propA")])
    expected_msg = (
        "Some property and or class type\(s\) used in the XML are unknown\:\n"
        "The following resource\(s\) have an invalid resource type:\n\t- Resource ID\: 'idB', Resource Type\: 'clsB'\n"
        "The following resource\(s\) have invalid property type\(s\):\n\t- Resource ID\: 'idA', Property Name\: 'propA'"
    )
    with pytest.raises(UserError, match=expected_msg):
        onto.execute_problem_protocol()
