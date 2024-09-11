import pandas as pd
from pandas.testing import assert_frame_equal

from dsp_tools.commands.xmlupload.models.ontology_lookup_models import TextValueData
from dsp_tools.commands.xmlupload.models.ontology_problem_models import InvalidOntologyElementsInData
from dsp_tools.commands.xmlupload.models.ontology_problem_models import InvalidTextValueEncodings
from dsp_tools.commands.xmlupload.models.ontology_problem_models import _make_msg_for_one_resource
from dsp_tools.commands.xmlupload.models.ontology_problem_models import _make_msg_from_df


class TestInvalidOntologyElementsInData:
    def test_print_problem_string_cls(self) -> None:
        onto = InvalidOntologyElementsInData([("clsA", ["idA"], "wrong")], [], ontos_on_server=["test"])
        msg = onto._compose_problem_string_for_cls()
        assert msg == (
            "The following resource(s) have an invalid resource type:\n\n"
            "    Resource Type: 'clsA'\n"
            "    Problem: 'wrong'\n"
            "    Resource ID(s):\n"
            "    - idA\n"
        )

    def test_print_problem_string_no_cls(self) -> None:
        onto = InvalidOntologyElementsInData([], [], [])
        assert not onto._compose_problem_string_for_cls()

    def test_print_problem_string_prop(self) -> None:
        onto = InvalidOntologyElementsInData([], [("propA", ["idA"], "wrong")], ["test"])
        msg = onto._compose_problem_string_for_props()
        assert msg == (
            "The following resource(s) have invalid property type(s):\n\n"
            "    Property Name: 'propA'\n"
            "    Problem: 'wrong'\n"
            "    Resource ID(s):\n"
            "    - idA\n"
        )

    def test_print_problem_string_no_prop(self) -> None:
        onto = InvalidOntologyElementsInData([], [], [])
        assert not onto._compose_problem_string_for_props()

    def test_execute_problem_protocol(self) -> None:
        onto = InvalidOntologyElementsInData(
            [("clsA", ["idA"], "wrong")],
            [("propA", ["idA"], "wrong"), ("propB", ["idB", "idC"], "wrong")],
            ["test1", "test2"],
        )
        expected_msg = (
            "\nSome property and/or class type(s) used in the XML are unknown.\n"
            "The ontologies for your project on the server are:\n"
            "    - test1\n"
            "    - test2"
            "\n\n"
            "The following resource(s) have an invalid resource type:\n\n"
            "    Resource Type: 'clsA'\n"
            "    Problem: 'wrong'\n"
            "    Resource ID(s):\n"
            "    - idA"
            "\n\n"
            "The following resource(s) have invalid property type(s):\n\n"
            "    Property Name: 'propA'\n"
            "    Problem: 'wrong'\n"
            "    Resource ID(s):\n"
            "    - idA"
            "\n\n"
            "    Property Name: 'propB'\n"
            "    Problem: 'wrong'\n"
            "    Resource ID(s):\n"
            "    - idB\n"
            "    - idC"
            "\n\n"
        )
        msg, df = onto.execute_problem_protocol()
        assert not df
        assert msg == expected_msg

    def test_get_problems_as_df(self) -> None:
        onto = InvalidOntologyElementsInData(
            [("clsA", ["idA"], "wrongA")],
            [("propB", ["idB"], "wrongB"), ("propC", ["idC1", "idC2"], "wrongC")],
            ["test"],
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


class TestInvalidTextValueEncodings:
    def test_get_problems_as_df(self) -> None:
        problems = InvalidTextValueEncodings(
            [
                TextValueData("id1", ":restype", ":simple", "xml"),
                TextValueData("id1", ":restype", ":rich", "utf8"),
                TextValueData("id2", ":restype", ":rich", "utf8"),
            ]
        )
        expected_df = pd.DataFrame(
            {
                "Resource ID": ["id1", "id1", "id2"],
                "Resource Type": [":restype", ":restype", ":restype"],
                "Property Name": [":rich", ":simple", ":rich"],
                "Encoding Used": ["utf8", "xml", "utf8"],
            }
        )
        res_df = problems._get_problems_as_df()
        assert_frame_equal(res_df, expected_df)

    def test_make_msg_for_one_resource(self) -> None:
        test_df = pd.DataFrame(
            {
                "Resource ID": ["id1", "id1"],
                "Resource Type": [":restype", ":restype"],
                "Property Name": [":rich", ":simple"],
                "Encoding Used": ["utf8", "xml"],
            }
        )
        res = _make_msg_for_one_resource("id1", test_df)
        expected = (
            "Resource ID: 'id1' | Resource Type: ':restype'\n"
            "    - Property Name: ':rich' -> Encoding Used: 'utf8'\n"
            "    - Property Name: ':simple' -> Encoding Used: 'xml'"
        )
        assert res == expected

    def test_make_msg_from_df(self) -> None:
        test_df = pd.DataFrame(
            {
                "Resource ID": ["id1", "id1", "id2"],
                "Resource Type": [":restype", ":restype", ":restype"],
                "Property Name": [":rich", ":simple", ":rich"],
                "Encoding Used": ["utf8", "xml", "utf8"],
            }
        )
        res = _make_msg_from_df(test_df)
        expected = (
            "Resource ID: 'id1' | Resource Type: ':restype'\n"
            "    - Property Name: ':rich' -> Encoding Used: 'utf8'\n"
            "    - Property Name: ':simple' -> Encoding Used: 'xml'"
            "\n\n"
            "Resource ID: 'id2' | Resource Type: ':restype'\n"
            "    - Property Name: ':rich' -> Encoding Used: 'utf8'"
        )
        assert res == expected
