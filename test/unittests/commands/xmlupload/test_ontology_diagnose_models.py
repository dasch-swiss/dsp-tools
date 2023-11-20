from pathlib import Path

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from dsp_tools.commands.xmlupload.models.ontology_diagnose_models import InvalidOntologyElements
from dsp_tools.models.exceptions import UserError

# pylint: disable=missing-function-docstring,anomalous-backslash-in-string,protected-access


def test_print_problem_string_cls() -> None:
    onto = InvalidOntologyElements(Path(""), [["idA", "clsA", "wrong"]], [])
    msg = onto._print_problem_string_cls()
    assert msg == (
        "The following resource(s) have an invalid resource type:\n\n"
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
        "The following resource(s) have invalid property type(s):\n\n"
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
        "\n\n----------------------------\n\n"
        "The following resource\(s\) have an invalid resource type\:\n\n"
        "\tResource ID\: 'idA'\n"
        "\tResource Type\: 'clsA'\n"
        "\tProblem\: 'wrong'"
        "\n\n----------------------------\n\n"
        "The following resource\(s\) have invalid property type\(s\)\:\n\n"
        "\tResource ID\: 'idA'\n"
        "\tProperty Name\: 'propA'\n"
        "\tProblem\: 'wrong'"
    )
    with pytest.raises(UserError, match=expected_msg):
        onto.execute_problem_protocol()


def test_get_problems_as_df() -> None:
    onto = InvalidOntologyElements(
        Path(""), [["idA", "clsA", "wrongA"], ["idC", "clsC", "wrongC"]], [["idB", "propB", "wrongB"]]
    )
    expected_df = pd.DataFrame(
        {
            "resource id": ["idA", "idC", "idB"],
            "problematic type": ["clsA", "clsC", "propB"],
            "problem": ["wrongA", "wrongC", "wrongB"],
        }
    )
    res_df = onto._get_problems_as_df()
    assert_frame_equal(res_df, expected_df)
