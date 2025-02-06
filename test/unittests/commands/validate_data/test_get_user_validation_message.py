import pytest

from dsp_tools.commands.validate_data.get_user_validation_message import _get_message_for_one_resource
from dsp_tools.commands.validate_data.models.input_problems import InputProblem
from dsp_tools.commands.validate_data.models.input_problems import ProblemType


@pytest.fixture
def generic_problem() -> InputProblem:
    return InputProblem(
        problem_type=ProblemType.GENERIC,
        res_id="res_id",
        res_type="onto:Class",
        prop_name="onto:hasGenericProblem",
        message="This is a generic problem.",
    )


def test_get_message_for_one_resource_generic(generic_problem: InputProblem) -> None:
    result = _get_message_for_one_resource([generic_problem])
    expected = (
        "Resource ID: res_id | Resource Type: onto:Class\nonto:hasGenericProblem\n    - This is a generic problem."
    )
    assert result == expected


@pytest.fixture
def file_value() -> InputProblem:
    return InputProblem(
        problem_type=ProblemType.FILE_VALUE,
        res_id="res_id",
        res_type="onto:Class",
        prop_name="bitstream / iiif-uri",
        expected="A MovingImageRepresentation requires a file with the extension 'mp4'.",
    )


def test_get_message_for_one_resource_file_value(file_value: InputProblem) -> None:
    result = _get_message_for_one_resource([file_value])
    expected = (
        "Resource ID: res_id | Resource Type: onto:Class\n"
        "bitstream / iiif-uri\n"
        "    - Expected : A MovingImageRepresentation requires a file with the extension 'mp4'."
    )
    assert result == expected


@pytest.fixture
def max_card() -> InputProblem:
    return InputProblem(
        problem_type=ProblemType.MAX_CARD,
        res_id="res_id",
        res_type="onto:Class",
        prop_name="onto:hasMaxCardProblem",
        expected="1",
    )


def test_get_message_for_one_resource_max_card(max_card: InputProblem) -> None:
    result = _get_message_for_one_resource([max_card])
    expected = (
        "Resource ID: res_id | Resource Type: onto:Class\n"
        "onto:hasMaxCardProblem\n"
        "    - Maximum Cardinality Violation | Expected Cardinality: '1'"
    )
    assert result == expected


@pytest.fixture
def min_card() -> InputProblem:
    return InputProblem(
        problem_type=ProblemType.MIN_CARD,
        res_id="res_id",
        res_type="onto:Class",
        prop_name="onto:hasMinCardProblem",
        expected="1-n",
    )


def test_get_message_for_one_resource_min_card(min_card: InputProblem) -> None:
    result = _get_message_for_one_resource([min_card])
    expected = (
        "Resource ID: res_id | Resource Type: onto:Class\n"
        "onto:hasMinCardProblem\n"
        "    - Minimum Cardinality Violation | Expected Cardinality: '1-n'"
    )
    assert result == expected


@pytest.fixture
def non_existing_card() -> InputProblem:
    return InputProblem(
        problem_type=ProblemType.NON_EXISTING_CARD,
        res_id="res_id",
        res_type="onto:Class",
        prop_name="onto:hasProp",
    )


def test_get_message_for_one_resource_non_existing_card(non_existing_card: InputProblem) -> None:
    result = _get_message_for_one_resource([non_existing_card])
    expected = (
        "Resource ID: res_id | Resource Type: onto:Class\n"
        "onto:hasProp\n"
        "    - The resource class does not have a cardinality for this property."
    )
    assert result == expected


@pytest.fixture
def file_value_prohibited() -> InputProblem:
    return InputProblem(
        problem_type=ProblemType.FILE_VALUE_PROHIBITED,
        res_id="res_id",
        res_type="onto:Class",
        prop_name="bitstream / iiif-uri",
    )


def test_get_message_for_one_resource_file_value_prohibited(file_value_prohibited: InputProblem) -> None:
    result = _get_message_for_one_resource([file_value_prohibited])
    expected = (
        "Resource ID: res_id | Resource Type: onto:Class\n"
        "bitstream / iiif-uri\n"
        "    - A file was added to the resource. This resource type must not have a file."
    )
    assert result == expected


@pytest.fixture
def value_type_mismatch() -> InputProblem:
    return InputProblem(
        problem_type=ProblemType.VALUE_TYPE_MISMATCH,
        res_id="res_id",
        res_type="onto:Class",
        prop_name="onto:hasProp",
        actual_input_type="LinkValue",
        expected="ListValue",
    )


def test_get_message_for_one_resource_value_type_mismatch(value_type_mismatch: InputProblem) -> None:
    result = _get_message_for_one_resource([value_type_mismatch])
    expected = (
        "Resource ID: res_id | Resource Type: onto:Class\n"
        "onto:hasProp\n"
        "    - Value Type Mismatch | Actual input type: 'LinkValue' | Expected: 'ListValue'"
    )
    assert result == expected


@pytest.fixture
def input_regex() -> InputProblem:
    return InputProblem(
        problem_type=ProblemType.INPUT_REGEX,
        res_id="res_id",
        res_type="onto:Class",
        prop_name="onto:hasProp",
        actual_input="wrong input",
        expected="Expected format information",
    )


def test_get_message_for_one_resource_input_regex(input_regex: InputProblem) -> None:
    result = _get_message_for_one_resource([input_regex])
    expected = (
        "Resource ID: res_id | Resource Type: onto:Class\n"
        "onto:hasProp\n"
        "    - Wrong Format of Input | Your input: 'wrong input' | "
        "Expected Input Format: Expected format information"
    )
    assert result == expected


@pytest.fixture
def link_target_mismatch() -> InputProblem:
    return InputProblem(
        problem_type=ProblemType.LINK_TARGET_TYPE_MISMATCH,
        res_id="res_id",
        res_type="onto:Class",
        prop_name="onto:hasProp",
        actual_input="link_target_id",
        actual_input_type="onto:Class",
        expected="onto:File",
    )


def test_get_message_for_one_resource_link_target_mismatch(link_target_mismatch: InputProblem) -> None:
    result = _get_message_for_one_resource([link_target_mismatch])
    expected = (
        "Resource ID: res_id | Resource Type: onto:Class\n"
        "onto:hasProp\n"
        "    - Linked Resource Type Mismatch | Your input: 'link_target_id' "
        "Actual Type: 'onto:Class' | Expected Resource Type: : onto:File or a subclass."
    )
    assert result == expected


@pytest.fixture
def inexistent_linked_resource() -> InputProblem:
    return InputProblem(
        problem_type=ProblemType.INEXISTENT_LINKED_RESOURCE,
        res_id="res_id",
        res_type="onto:Class",
        prop_name="onto:hasProp",
        actual_input="link_target_id",
    )


def test_get_message_for_one_resource_inexistent_linked_resource(inexistent_linked_resource: InputProblem) -> None:
    result = _get_message_for_one_resource([inexistent_linked_resource])
    expected = (
        "Resource ID: res_id | Resource Type: onto:Class\n"
        "onto:hasProp\n"
        "    - Linked Resource does not Exist, Target Resource ID: 'link_target_id'"
    )
    assert result == expected


@pytest.fixture
def duplicate_value() -> InputProblem:
    return InputProblem(
        problem_type=ProblemType.DUPLICATE_VALUE,
        res_id="res_id",
        res_type="onto:Class",
        prop_name="onto:hasProp",
        actual_input="Text",
    )


def test_get_message_for_one_resource_duplicate_value(duplicate_value: InputProblem) -> None:
    result = _get_message_for_one_resource([duplicate_value])
    expected = (
        "Resource ID: res_id | Resource Type: onto:Class\nonto:hasProp\n    - Value is duplicated, Your Input: 'Text'"
    )
    assert result == expected
