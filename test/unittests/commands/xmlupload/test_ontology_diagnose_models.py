import pandas as pd
from pandas.testing import assert_frame_equal

from dsp_tools.commands.xmlupload.models.ontology_diagnose_models import InvalidOntologyElements

# pylint: disable=missing-function-docstring,protected-access


def test_print_problem_string_cls() -> None:
    onto = InvalidOntologyElements([("clsA", ["idA"], "wrong")], [], ontos_on_server=["test"])
    msg = onto._compose_problem_string_cls()
    assert msg == (
        "The following resource(s) have an invalid resource type:\n\n"
        "    Resource Type: 'clsA'\n"
        "    Problem: 'wrong'\n"
        "    Resource ID(s):\n"
        "    - idA"
    )


def test_print_problem_string_no_cls() -> None:
    onto = InvalidOntologyElements([], [], [])
    assert not onto._compose_problem_string_cls()


def test_print_problem_string_prop() -> None:
    onto = InvalidOntologyElements([], [("propA", ["idA"], "wrong")], ["test"])
    msg = onto._compose_problem_string_props()
    assert msg == (
        "The following resource(s) have invalid property type(s):\n\n"
        "    Property Name: 'propA'\n"
        "    Problem: 'wrong'\n"
        "    Resource ID(s):\n"
        "    - idA"
    )


def test_print_problem_string_no_prop() -> None:
    onto = InvalidOntologyElements([], [], [])
    assert not onto._compose_problem_string_props()


def test_execute_problem_protocol() -> None:
    onto = InvalidOntologyElements(
        [("clsA", ["idA"], "wrong")],
        [("propA", ["idA"], "wrong"), ("propB", ["idB", "idC"], "wrong")],
        ["test1", "test2"],
    )
    expected_msg = (
        "\nSome property and/or class type(s) used in the XML are unknown.\n"
        "The ontologies for your project on the server are:\n"
        "    - test1\n"
        "    - test2"
        "\n\n---------------------------------------\n\n"
        "The following resource(s) have an invalid resource type:\n\n"
        "    Resource Type: 'clsA'\n"
        "    Problem: 'wrong'\n"
        "    Resource ID(s):\n"
        "    - idA"
        "\n\n---------------------------------------\n\n"
        "The following resource(s) have invalid property type(s):\n\n"
        "    Property Name: 'propA'\n"
        "    Problem: 'wrong'\n"
        "    Resource ID(s):\n"
        "    - idA"
        "\n----------------------------\n"
        "    Property Name: 'propB'\n"
        "    Problem: 'wrong'\n"
        "    Resource ID(s):\n"
        "    - idB\n"
        "    - idC"
    )
    msg, df = onto.execute_problem_protocol()
    assert not df
    assert msg == expected_msg


def test_get_problems_as_df() -> None:
    onto = InvalidOntologyElements(
        [("clsA", ["idA"], "wrongA")], [("propB", ["idB"], "wrongB"), ("propC", ["idC1", "idC2"], "wrongC")], ["test"]
    )
    expected_df = pd.DataFrame(
        {
            "problematic type": ["clsA", "propB", "propC", "propC"],
            "resource id": ["idA", "idB", "idC1", "idC2"],
            "problem": ["wrongA", "wrongB", "wrongC", "wrongC"],
        }
    )
    res_df = onto._get_problems_as_df()
    assert_frame_equal(res_df, expected_df)
