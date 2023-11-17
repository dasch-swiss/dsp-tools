from pathlib import Path

import pytest

from dsp_tools.commands.xmlupload.models.ontology_diagnose_models import InvalidOntologyElements
from dsp_tools.models.exceptions import UserError

# pylint: disable=missing-function-docstring,anomalous-backslash-in-string,protected-access


def test_print_problem_string_cls() -> None:
    onto = InvalidOntologyElements(Path(""), [["idA", "clsA", "wrong"]], [])
    msg = onto._print_problem_string_cls()
    assert msg == (
        "The following resource(s) have an invalid resource type:\n"
        "\tResource ID: 'idA'\n"
        "\tResource Type: 'clsA'\n"
        "\tProblem: 'wrong'"
    )


def test_print_problem_string_no_cls() -> None:
    onto = InvalidOntologyElements(Path(""), [], [])
    msg = onto._print_problem_string_cls()
    assert msg == ""


def test_print_problem_string_prop() -> None:
    onto = InvalidOntologyElements(Path(""), [], [["idA", "propA", "wrong"]])
    msg = onto._print_problem_string_props()
    assert msg == (
        "The following resource(s) have invalid property type(s):\n"
        "\tResource ID: 'idA'\n"
        "\tProperty Name: 'propA'\n"
        "\tProblem: 'wrong'"
    )


def test_print_problem_string_no_prop() -> None:
    onto = InvalidOntologyElements(Path(""), [], [])
    msg = onto._print_problem_string_props()
    assert msg == ""


def test_execute_problem_protocol() -> None:
    onto = InvalidOntologyElements(Path(""), [["idA", "clsA", "wrong"]], [["idA", "propA", "wrong"]])
    expected_msg = (
        "Some property and or class type\(s\) used in the XML are unknown\:"
        "\n----------------------------"
        "The following resource\(s\) have an invalid resource type\:\n"
        "\tResource ID\: 'idA'\n"
        "\tResource Type\: 'clsA'\n"
        "\tProblem\: 'wrong'"
        "\n----------------------------"
        "The following resource\(s\) have invalid property type\(s\)\:\n"
        "\tResource ID\: 'idA'\n"
        "\tProperty Name\: 'propA'\n"
        "\tProblem\: 'wrong'"
    )
    with pytest.raises(UserError, match=expected_msg):
        onto.execute_problem_protocol()
