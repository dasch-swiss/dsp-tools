from collections import defaultdict
from pathlib import Path

import pandas as pd

from dsp_tools.commands.validate_data.models.input_problems import InputProblem

LIST_SEPARATOR = "\n    - "
GRAND_SEPARATOR = "\n\n----------------------------\n"


def get_user_message(problems: list[InputProblem], file_path: Path) -> str:
    """
    Creates the string to communicate the user message.

    Args:
        problems: List of validation problems
        file_path: Path to the original data XML

    Returns:
        Problem message
    """
    if len(problems) > 50:
        specific_message = _save_problem_info_as_csv(problems, file_path)
    else:
        specific_message = _get_problem_print_message(problems)
    return f"\nDuring the validation of the data {len(problems)} errors were found:\n\n{specific_message}"


def _get_problem_print_message(problems: list[InputProblem]) -> str:
    grouped_problems = _group_problems_by_resource(problems)
    messages = [_get_message_for_one_resource(v) for v in grouped_problems.values()]
    return GRAND_SEPARATOR.join(messages)


def _group_problems_by_resource(problems: list[InputProblem]) -> dict[str : list[InputProblem]]:
    grouped_res = defaultdict(list)
    for prob in problems:
        grouped_res[prob.res_id].append(prob)
    return grouped_res


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
    if problem.actual_input:
        msg.append(f"Your input: '{_shorten_input(problem.actual_input)}'")
    if problem.actual_input_type:
        msg.append(f"Actual input type: '{problem.actual_input_type}'")
    if problem.expected:
        msg.append(f"Expected: '{problem.expected}'")
    return " | ".join(msg)


def _save_problem_info_as_csv(problems: list[InputProblem], file_path: Path) -> str:
    out_path = file_path.parent / f"{file_path.stem}_validation_errors.csv"
    all_problems = [_get_message_dict(x) for x in problems]
    df = pd.DataFrame.from_records(all_problems)
    df = df.sort_values(by=["Resource Type", "Resource ID", "Property"])
    df.to_csv(out_path, index=False)
    return f"Due to the large number or errors, the validation errors were saved at:\n{out_path}"


def _get_message_dict(problem: InputProblem) -> dict[str, str]:
    msg_dict = {
        "Resource ID": problem.res_id,
        "Resource Type": problem.res_type,
        "Property": problem.prop_name,
        "Problem": problem.message,
        "Your Input": _shorten_input(problem.actual_input),
        "Input Type": problem.actual_input_type,
        "Expected": problem.expected,
    }
    return {k: v for k, v in msg_dict.items() if v}


def _shorten_input(user_input: str | None) -> str | None:
    if not user_input or len(user_input) < 15:
        return user_input
    return f"{user_input[:15]}[...]"
