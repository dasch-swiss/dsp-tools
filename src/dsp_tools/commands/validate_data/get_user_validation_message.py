from collections import defaultdict
from pathlib import Path

import pandas as pd

from dsp_tools.commands.validate_data.models.input_problems import InputProblem
from dsp_tools.commands.validate_data.models.input_problems import ProblemType

LIST_SEPARATOR = "\n    - "
GRAND_SEPARATOR = "\n\n----------------------------\n"


PROBLEM_TYPES_IGNORE_STR_ENUM_INFO = {ProblemType.GENERIC, ProblemType.FILE_VALUE}


def get_user_message(problems: list[InputProblem], file_path: Path) -> str:
    """
    Creates the string to communicate the user message.

    Args:
        problems: List of validation problems
        file_path: Path to the original data XML

    Returns:
        Problem message
    """
    duplicates_removed = _filter_out_duplicate_problems(problems)
    num_unique_problems = sum([len(x) for x in duplicates_removed])
    if num_unique_problems > 50:
        specific_message = _save_problem_info_as_csv(duplicates_removed, file_path)
    else:
        specific_message = _get_problem_print_message(duplicates_removed)
    return f"\nDuring the validation of the data {num_unique_problems} errors were found:\n\n{specific_message}"


def _filter_out_duplicate_problems(problems: list[InputProblem]) -> list[list[InputProblem]]:
    grouped = _group_problems_by_resource(problems)
    filtered = {k: _filter_out_duplicate_text_value_problem(v) for k, v in grouped.items()}
    return list(filtered.values())


def _filter_out_duplicate_text_value_problem(problems: list[InputProblem]) -> list[InputProblem]:
    filtered_problems = [x for x in problems if x.problem_type != ProblemType.VALUE_TYPE_MISMATCH]
    type_problems = [x for x in problems if x.problem_type == ProblemType.VALUE_TYPE_MISMATCH]

    grouped_dict = defaultdict(list)
    for prob in type_problems:
        grouped_dict[prob.prop_name].append(prob)

    for problem_list in grouped_dict.values():
        messages = [x.expected for x in problem_list]
        # Is there a chance of a duplicate (only possible for TextValue)?
        if "This property requires a TextValue" not in messages:
            filtered_problems.extend(problem_list)
            continue
        # Is there a more precise message about the type of TextValue?
        if "TextValue without formatting" not in messages and "TextValue with formatting" not in messages:
            # If there is not a more precise message, then the generic one is communicated to the user
            filtered_problems.extend(problem_list)
            continue
        # We remove the generic message and leave the specific one
        inx = messages.index("This property requires a TextValue")
        problem_list.pop(inx)
        filtered_problems.extend(problem_list)

    return filtered_problems


def _group_problems_by_resource(problems: list[InputProblem]) -> dict[str, list[InputProblem]]:
    grouped_res = defaultdict(list)
    for prob in problems:
        grouped_res[prob.res_id].append(prob)
    return grouped_res


def _get_problem_print_message(problems: list[list[InputProblem]]) -> str:
    messages = [_get_message_for_one_resource(v) for v in sorted(problems, key=lambda x: x[0].res_id)]
    return GRAND_SEPARATOR.join(messages)


def _get_message_for_one_resource(problems: list[InputProblem]) -> str:
    start_msg = f"Resource ID: {problems[0].res_id} | Resource Type: {problems[0].res_type}"
    prop_messages = _get_message_with_properties(problems)
    return f"{start_msg}\n{prop_messages}"


def _get_message_with_properties(problems: list[InputProblem]) -> str:
    messages = defaultdict(list)
    for prob in problems:
        messages[prob.prop_name].append(_get_message_detail_str(prob))

    def format_msg(propname: str, msg: list[str]) -> str:
        return f"{propname}{LIST_SEPARATOR}{LIST_SEPARATOR.join(msg)}"

    return "\n".join([format_msg(k, v) for k, v in messages.items()])


def _get_message_detail_str(problem: InputProblem) -> str:
    msg = []
    if problem.message:
        msg.append(problem.message)
    if problem.problem_type not in PROBLEM_TYPES_IGNORE_STR_ENUM_INFO:
        msg.append(str(problem.problem_type))
    if problem.input_value:
        msg.append(f"Your input: '{_shorten_input(problem.input_value)}'")
    if problem.input_type:
        msg.append(f"Actual input type: '{problem.input_type}'")
    if problem.expected:
        msg.append(f"Expected{_get_expected_prefix(problem.problem_type)}: {problem.expected}")
    return " | ".join(msg)


def _get_expected_prefix(problem_type: ProblemType) -> str | None:
    match problem_type:
        case ProblemType.VALUE_TYPE_MISMATCH:
            return " Value Type"
        case ProblemType.INPUT_REGEX:
            return " Input Format"
        case ProblemType.LINK_TARGET_TYPE_MISMATCH:
            return " Resource Type"
        case _:
            return ""


def _save_problem_info_as_csv(problems: list[list[InputProblem]], file_path: Path) -> str:
    out_path = file_path.parent / f"{file_path.stem}_validation_errors.csv"
    all_problems = []
    for resource_problems in problems:
        all_problems.extend([_get_message_dict(x) for x in resource_problems])
    df = pd.DataFrame.from_records(all_problems)
    df = df.sort_values(by=["Resource Type", "Resource ID", "Property"])
    df.to_csv(out_path, index=False)
    return f"Due to the large number or errors, the validation errors were saved at:\n{out_path}"


def _get_message_dict(problem: InputProblem) -> dict[str, str]:
    msg_dict = {
        "Resource ID": problem.res_id,
        "Resource Type": problem.res_type,
        "Property": problem.prop_name,
        "Your Input": _shorten_input(problem.input_value),
        "Input Type": problem.input_type,
    }
    non_empty_dict = {k: v for k, v in msg_dict.items() if v}
    expected_and_message = _get_expected_message_dict(problem)
    non_empty_dict.update(expected_and_message)
    if problem.problem_type not in PROBLEM_TYPES_IGNORE_STR_ENUM_INFO:
        non_empty_dict["Problem"] = str(problem.problem_type)
    return non_empty_dict


def _get_expected_message_dict(problem: InputProblem) -> dict[str, str]:
    out_dict = {}
    if problem.expected:
        msg_str = problem.expected
        if prefix := _get_expected_prefix(problem.problem_type):
            msg_str = f"{prefix.strip()}: {msg_str}"
        out_dict["Expected"] = msg_str
    if problem.message:
        if problem.expected:
            out_dict["Message"] = problem.message
        else:
            out_dict["Expected"] = problem.message
    return out_dict


def _shorten_input(user_input: str | None) -> str | None:
    if not user_input:
        return None
    if len(user_input) < 41:
        return user_input
    return f"{user_input[:40]}[...]"
