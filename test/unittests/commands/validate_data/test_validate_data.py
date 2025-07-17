# mypy: disable-error-code="method-assign,no-untyped-def"

import pytest

from dsp_tools.commands.validate_data.models.api_responses import OneList
from dsp_tools.commands.validate_data.models.api_responses import OneNode
from dsp_tools.commands.validate_data.models.input_problems import InputProblem
from dsp_tools.commands.validate_data.models.input_problems import ProblemType
from dsp_tools.commands.validate_data.models.input_problems import Severity
from dsp_tools.commands.validate_data.models.input_problems import SortedProblems
from dsp_tools.commands.validate_data.prepare_data.prepare_data import _make_list_lookup
from dsp_tools.commands.validate_data.validate_data import _get_validation_status


def test_make_list_lookup():
    all_lists = [
        OneList("IRI1", "list1", [OneNode("l1n1", "IRIl1n1"), OneNode("l1n2", "IRIl1n2")]),
        OneList("IRI2", "list2", [OneNode("l2n1", "IRIl2n1")]),
    ]
    result = _make_list_lookup(all_lists)
    expected_lookup = {
        ("", "IRIl1n1"): "IRIl1n1",
        ("", "IRIl1n2"): "IRIl1n2",
        ("", "IRIl2n1"): "IRIl2n1",
        ("list1", "l1n1"): "IRIl1n1",
        ("list1", "l1n2"): "IRIl1n2",
        ("list2", "l2n1"): "IRIl2n1",
    }
    assert result.lists == expected_lookup


class TestGetValidationStatus:
    def test_not_prod_problems(self):
        problems = SortedProblems([InputProblem(ProblemType.GENERIC, "", "", "", Severity.VIOLATION)], [], [], [])
        validation_passed = _get_validation_status(problems, is_on_prod=False)
        assert not validation_passed

    def test_not_prod_problems_and_unexpected(self):
        problems = SortedProblems([InputProblem(ProblemType.GENERIC, "", "", "", Severity.VIOLATION)], [], [], ["unex"])
        validation_passed = _get_validation_status(problems, is_on_prod=False)
        assert not validation_passed

    def test_not_prod_warnings(self):
        problems = SortedProblems([], [InputProblem(ProblemType.GENERIC, "", "", "", Severity.VIOLATION)], [], [])
        validation_passed = _get_validation_status(problems, is_on_prod=False)
        assert validation_passed

    def test_not_prod_info(self):
        problems = SortedProblems([], [], [InputProblem(ProblemType.GENERIC, "", "", "", Severity.VIOLATION)], [])
        validation_passed = _get_validation_status(problems, is_on_prod=False)
        assert validation_passed

    def test_not_prod_unexpected(self):
        problems = SortedProblems([], [], [], ["unexpected"])
        validation_passed = _get_validation_status(problems, is_on_prod=False)
        assert not validation_passed


if __name__ == "__main__":
    pytest.main([__file__])
