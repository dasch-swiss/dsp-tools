# mypy: disable-error-code="method-assign,no-untyped-def"

import pytest

from dsp_tools.commands.validate_data.models.input_problems import AllProblems
from dsp_tools.commands.validate_data.models.input_problems import DuplicateFileWarning
from dsp_tools.commands.validate_data.models.input_problems import InputProblem
from dsp_tools.commands.validate_data.models.input_problems import ProblemType
from dsp_tools.commands.validate_data.models.input_problems import Severity
from dsp_tools.commands.validate_data.models.validation import UnexpectedComponent
from dsp_tools.commands.validate_data.process_validation_report.get_user_validation_message import (
    _get_message_for_one_resource,
)
from dsp_tools.commands.validate_data.process_validation_report.get_user_validation_message import _shorten_input
from dsp_tools.commands.validate_data.process_validation_report.get_user_validation_message import sort_user_problems


@pytest.fixture
def generic_problem() -> InputProblem:
    return InputProblem(
        problem_type=ProblemType.GENERIC,
        res_id="res_id",
        res_type="onto:Class",
        prop_name="onto:hasGenericProblem",
        severity=Severity.VIOLATION,
        message="This is a generic problem.",
    )


@pytest.fixture
def file_value() -> InputProblem:
    return InputProblem(
        problem_type=ProblemType.FILE_VALUE_MISSING,
        res_id="res_id",
        res_type="onto:Class",
        prop_name="bitstream / iiif-uri",
        severity=Severity.VIOLATION,
        expected="A MovingImageRepresentation requires a file with the extension 'mp4'.",
    )


@pytest.fixture
def max_card() -> InputProblem:
    return InputProblem(
        problem_type=ProblemType.MAX_CARD,
        res_id="res_id",
        res_type="onto:Class",
        prop_name="onto:hasMaxCardProblem",
        severity=Severity.VIOLATION,
        expected="Cardinality 1",
    )


@pytest.fixture
def min_card() -> InputProblem:
    return InputProblem(
        problem_type=ProblemType.MIN_CARD,
        res_id="res_id",
        res_type="onto:Class",
        prop_name="onto:hasMinCardProblem",
        severity=Severity.VIOLATION,
        expected="Cardinality 1-n",
    )


@pytest.fixture
def non_existing_card() -> InputProblem:
    return InputProblem(
        problem_type=ProblemType.NON_EXISTING_CARD,
        res_id="res_id",
        res_type="onto:Class",
        prop_name="onto:hasProp",
        severity=Severity.VIOLATION,
    )


@pytest.fixture
def file_value_prohibited() -> InputProblem:
    return InputProblem(
        problem_type=ProblemType.FILE_VALUE_PROHIBITED,
        res_id="res_id",
        res_type="onto:Class",
        prop_name="bitstream / iiif-uri",
        severity=Severity.VIOLATION,
    )


@pytest.fixture
def link_value_type_mismatch() -> InputProblem:
    return InputProblem(
        problem_type=ProblemType.VALUE_TYPE_MISMATCH,
        res_id="res_id",
        res_type="onto:Class",
        prop_name="onto:hasProp",
        severity=Severity.VIOLATION,
        input_type="LinkValue",
        expected="ListValue",
    )


@pytest.fixture
def input_regex() -> InputProblem:
    return InputProblem(
        problem_type=ProblemType.INPUT_REGEX,
        res_id="res_id",
        res_type="onto:Class",
        prop_name="onto:hasProp",
        severity=Severity.VIOLATION,
        input_value="wrong input",
        expected="Expected format information",
    )


@pytest.fixture
def link_target_mismatch() -> InputProblem:
    return InputProblem(
        problem_type=ProblemType.LINK_TARGET_TYPE_MISMATCH,
        res_id="res_id",
        res_type="onto:Class",
        prop_name="onto:hasProp",
        severity=Severity.VIOLATION,
        input_value="link_target_id",
        input_type="onto:Class",
        expected="onto:File or a subclass",
    )


@pytest.fixture
def inexistent_linked_resource() -> InputProblem:
    return InputProblem(
        problem_type=ProblemType.INEXISTENT_LINKED_RESOURCE,
        res_id="res_id",
        res_type="onto:Class",
        prop_name="onto:hasProp",
        severity=Severity.VIOLATION,
        input_value="link_target_id",
    )


@pytest.fixture
def duplicate_value() -> InputProblem:
    return InputProblem(
        problem_type=ProblemType.DUPLICATE_VALUE,
        res_id="res_id",
        res_type="onto:Class",
        prop_name="onto:hasProp",
        severity=Severity.VIOLATION,
        input_value="Text",
    )


@pytest.fixture
def missing_legal_warning() -> InputProblem:
    return InputProblem(
        problem_type=ProblemType.GENERIC,
        res_id="image_no_legal_info",
        res_type="onto:TestStillImageRepresentation",
        prop_name="bitstream / iiif-uri",
        severity=Severity.WARNING,
        expected="Files and IIIF-URIs require a reference to a license.",
    )


def test_sort_user_problems_with_iris(duplicate_value, link_value_type_mismatch, missing_legal_warning):
    references_iri = InputProblem(
        problem_type=ProblemType.INEXISTENT_LINKED_RESOURCE,
        res_id="references_iri",
        res_type="onto:Class",
        prop_name="onto:hasProp",
        severity=Severity.VIOLATION,
        input_value="http://rdfh.ch/4123/DiAmYQzQSzC7cdTo6OJMYA",
    )
    inexistent_license_iri = InputProblem(
        problem_type=ProblemType.GENERIC,
        res_id="inexistent_license_iri",
        res_type="onto:TestStillImageRepresentation",
        prop_name="bitstream / iiif-uri",
        severity=Severity.VIOLATION,
        input_value="http://rdfh.ch/licenses/this-iri-does-not-exist",
        message="Files and IIIF-URIs require a reference to a license.",
    )
    duplicate_file = InputProblem(
        problem_type=ProblemType.FILE_DUPLICATE,
        res_id=None,
        res_type=None,
        prop_name="bitstream / iiif-uri",
        severity=Severity.WARNING,
        message="msg",
        input_value="fil.jpg",
    )
    result = sort_user_problems(
        AllProblems(
            [duplicate_value, link_value_type_mismatch, references_iri, inexistent_license_iri, missing_legal_warning],
            [],
        ),
        duplicate_file_warnings=DuplicateFileWarning([duplicate_file]),
    )
    assert len(result.unique_violations) == 3
    assert set([x.res_id for x in result.unique_violations]) == {"res_id", "inexistent_license_iri"}
    assert len(result.user_warnings) == 2
    warning_ids = {x.res_id for x in result.user_warnings}
    assert warning_ids == {None, "image_no_legal_info"}
    assert len(result.user_info) == 1
    assert result.user_info[0].res_id == "references_iri"
    assert not result.unexpected_shacl_validation_components


def test_sort_user_problems_with_duplicate(duplicate_value, link_value_type_mismatch):
    should_remain = InputProblem(
        problem_type=ProblemType.VALUE_TYPE_MISMATCH,
        res_id="text_value_id",
        res_type="",
        prop_name="onto:hasProp",
        severity=Severity.VIOLATION,
        expected="TextValue without formatting",
    )
    should_be_removed = InputProblem(
        problem_type=ProblemType.VALUE_TYPE_MISMATCH,
        res_id="text_value_id",
        res_type="",
        prop_name="onto:hasProp",
        severity=Severity.VIOLATION,
        expected="This property requires a TextValue",
    )
    result = sort_user_problems(
        AllProblems(
            [duplicate_value, link_value_type_mismatch, should_remain, should_be_removed],
            [UnexpectedComponent("sh:unexpected"), UnexpectedComponent("sh:unexpected")],
        ),
        duplicate_file_warnings=None,
    )
    assert len(result.unique_violations) == 3
    assert not result.user_info
    assert len(result.unexpected_shacl_validation_components) == 1
    assert set([x.res_id for x in result.unique_violations]) == {"text_value_id", "res_id"}


def test_sort_user_problems_different_props():
    one = InputProblem(
        problem_type=ProblemType.VALUE_TYPE_MISMATCH,
        res_id="res_id",
        res_type="",
        prop_name="onto:prop2",
        severity=Severity.VIOLATION,
        expected="TextValue without formatting",
    )
    two = InputProblem(
        problem_type=ProblemType.VALUE_TYPE_MISMATCH,
        res_id="res_id",
        res_type="",
        prop_name="onto:prop1",
        severity=Severity.VIOLATION,
        expected="This property requires a TextValue",
    )
    result = sort_user_problems(AllProblems([one, two], []), duplicate_file_warnings=None)
    assert len(result.unique_violations) == 2
    assert not result.user_info
    assert not result.unexpected_shacl_validation_components
    assert [x.res_id for x in result.unique_violations] == ["res_id", "res_id"]


def test_get_message_for_one_resource_generic(generic_problem):
    result = _get_message_for_one_resource([generic_problem])
    expected = (
        "Resource ID: res_id | Resource Type: onto:Class\nonto:hasGenericProblem\n    - This is a generic problem."
    )
    assert result == expected


def test_get_message_for_one_resource_file_value(file_value):
    result = _get_message_for_one_resource([file_value])
    expected = (
        "Resource ID: res_id | Resource Type: onto:Class\n"
        "bitstream / iiif-uri\n"
        "    - Expected: A MovingImageRepresentation requires a file with the extension 'mp4'."
    )
    assert result == expected


def test_get_message_for_one_resource_max_card(max_card):
    result = _get_message_for_one_resource([max_card])
    expected = (
        "Resource ID: res_id | Resource Type: onto:Class\n"
        "onto:hasMaxCardProblem\n"
        "    - Maximum Cardinality Violation | Expected: Cardinality 1"
    )
    assert result == expected


def test_get_message_for_one_resource_min_card(min_card):
    result = _get_message_for_one_resource([min_card])
    expected = (
        "Resource ID: res_id | Resource Type: onto:Class\n"
        "onto:hasMinCardProblem\n"
        "    - Minimum Cardinality Violation | Expected: Cardinality 1-n"
    )
    assert result == expected


def test_get_message_for_one_resource_non_existing_card(non_existing_card):
    result = _get_message_for_one_resource([non_existing_card])
    expected = (
        "Resource ID: res_id | Resource Type: onto:Class\n"
        "onto:hasProp\n"
        "    - The resource class does not have a cardinality for this property."
    )
    assert result == expected


def test_get_message_for_one_resource_file_value_prohibited(file_value_prohibited):
    result = _get_message_for_one_resource([file_value_prohibited])
    expected = (
        "Resource ID: res_id | Resource Type: onto:Class\n"
        "bitstream / iiif-uri\n"
        "    - A file was added to the resource. This resource type must not have a file."
    )
    assert result == expected


def test_get_message_for_one_resource_value_type_mismatch(link_value_type_mismatch):
    result = _get_message_for_one_resource([link_value_type_mismatch])
    expected = (
        "Resource ID: res_id | Resource Type: onto:Class\n"
        "onto:hasProp\n"
        "    - Value Type Mismatch | Actual input type: 'LinkValue' | Expected Value Type: ListValue"
    )
    assert result == expected


def test_get_message_for_one_resource_input_regex(input_regex):
    result = _get_message_for_one_resource([input_regex])
    expected = (
        "Resource ID: res_id | Resource Type: onto:Class\n"
        "onto:hasProp\n"
        "    - Wrong Format of Input | Your input: 'wrong input' | "
        "Expected Input Format: Expected format information"
    )
    assert result == expected


def test_get_message_for_one_resource_link_target_mismatch(link_target_mismatch):
    result = _get_message_for_one_resource([link_target_mismatch])
    expected = (
        "Resource ID: res_id | Resource Type: onto:Class\n"
        "onto:hasProp\n"
        "    - Linked Resource Type Mismatch | Your input: 'link_target_id' | "
        "Actual input type: 'onto:Class' | Expected Resource Type: onto:File or a subclass"
    )
    assert result == expected


def test_get_message_for_one_resource_inexistent_linked_resource(inexistent_linked_resource):
    result = _get_message_for_one_resource([inexistent_linked_resource])
    expected = (
        "Resource ID: res_id | Resource Type: onto:Class\n"
        "onto:hasProp\n"
        "    - Linked Resource does not exist | Your input: 'link_target_id'"
    )
    assert result == expected


def test_get_message_for_one_resource_duplicate_value(duplicate_value):
    result = _get_message_for_one_resource([duplicate_value])
    expected = (
        "Resource ID: res_id | Resource Type: onto:Class\n"
        "onto:hasProp\n"
        "    - Your input is duplicated | Your input: 'Text'"
    )
    assert result == expected


def test_get_message_for_one_resource_several_problems(file_value, inexistent_linked_resource):
    result = _get_message_for_one_resource([file_value, inexistent_linked_resource])
    expected = (
        "Resource ID: res_id | Resource Type: onto:Class\n"
        "bitstream / iiif-uri\n"
        "    - Expected: A MovingImageRepresentation requires a file with the extension 'mp4'.\n"
        "onto:hasProp\n"
        "    - Linked Resource does not exist | Your input: 'link_target_id'"
    )
    assert result == expected


def test_get_message_duplicate_files_no_res_id():
    file1 = InputProblem(
        problem_type=ProblemType.FILE_DUPLICATE,
        res_id=None,
        res_type=None,
        prop_name="bitstream / iiif-uri",
        severity=Severity.WARNING,
        message="msg",
        input_value="file1.jpg",
    )
    file2 = InputProblem(
        problem_type=ProblemType.FILE_DUPLICATE,
        res_id=None,
        res_type=None,
        prop_name="bitstream / iiif-uri",
        severity=Severity.WARNING,
        message="msg",
        input_value="file2.jpg",
    )
    result = _get_message_for_one_resource([file1, file2])
    expected = "\nbitstream / iiif-uri\n    - msg | Your input: 'file1.jpg'\n    - msg | Your input: 'file2.jpg'"
    assert result == expected


@pytest.mark.parametrize(
    ("user_input", "problem_type", "expected"),
    [
        (
            "this/is/a/very/very/very/very/long/filepath/but/should/remain/intact/file.csv",
            ProblemType.FILE_VALUE_MISSING,
            "this/is/a/very/very/very/very/long/filepath/but/should/remain/intact/file.csv",
        ),
        (
            "http://rdfh.ch/lists/0000/a6XOoBsrT3ma6XOoBsrT3ma6XOoBsrT3ma6XOoBsrT3m",
            ProblemType.GENERIC,
            "http://rdfh.ch/lists/0000/a6XOoBsrT3ma6XOoBsrT3ma6XOoBsrT3ma6XOoBsrT3m",
        ),
        (
            " / http://rdfh.ch/lists/0000/a6XOoBsrT3ma6XOoBsrT3ma6XOoBsrT3ma6XOoBsrT3m-D8Q",
            ProblemType.VALUE_TYPE_MISMATCH,
            " / http://rdfh.ch/lists/0000/a6XOoBsrT3ma6XOoBsrT3ma6XOoBsrT3ma6XOoBsrT3m-D8Q",
        ),
        (
            "This is a very, very long sentence and should be shortened.",
            ProblemType.GENERIC,
            "This is a very, very long sentence and should be s[...]",
        ),
        ("So short, nothing happens", ProblemType.VALUE_TYPE_MISMATCH, "So short, nothing happens"),
        (None, ProblemType.GENERIC, None),
    ],
)
def test_shorten_input(user_input, problem_type, expected):
    result = _shorten_input(user_input, problem_type)
    assert result == expected
