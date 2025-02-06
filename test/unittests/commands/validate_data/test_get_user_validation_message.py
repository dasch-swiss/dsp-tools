import pytest

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


@pytest.fixture
def file_value() -> InputProblem:
    return InputProblem(
        problem_type=ProblemType.FILE_VALUE,
        res_id="res_id",
        res_type="onto:Class",
        prop_name="onto:hasFileProblem",
        expected="A MovingImageRepresentation requires a file with the extension 'mp4'.",
    )


@pytest.fixture
def max_card() -> InputProblem:
    return InputProblem(
        problem_type=ProblemType.MAX_CARD,
        res_id="res_id",
        res_type="onto:Class",
        prop_name="onto:hasMaxCardProblem",
        expected="1",
    )


@pytest.fixture
def min_card() -> InputProblem:
    return InputProblem(
        problem_type=ProblemType.MIN_CARD,
        res_id="res_id",
        res_type="onto:Class",
        prop_name="onto:hasMinCardProblem",
        expected="1-n",
    )


@pytest.fixture
def non_existing_card() -> InputProblem:
    return InputProblem(
        problem_type=ProblemType.NON_EXISTING_CARD,
        res_id="res_id",
        res_type="onto:Class",
        prop_name="onto:hasProp",
    )


@pytest.fixture
def file_value_prohibited() -> InputProblem:
    return InputProblem(
        problem_type=ProblemType.FILE_VALUE_PROHIBITED,
        res_id="res_id",
        res_type="onto:Class",
        prop_name="bitstream / iiif-uri",
    )


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


@pytest.fixture
def inexistent_linked_resource() -> InputProblem:
    return InputProblem(
        problem_type=ProblemType.INEXISTENT_LINKED_RESOURCE,
        res_id="res_id",
        res_type="onto:Class",
        prop_name="onto:hasProp",
        actual_input="link_target_id",
    )


@pytest.fixture
def duplicate_value() -> InputProblem:
    return InputProblem(
        problem_type=ProblemType.DUPLICATE_VALUE,
        res_id="res_id",
        res_type="onto:Class",
        prop_name="onto:hasProp",
        actual_input="Duplicate input",
    )
