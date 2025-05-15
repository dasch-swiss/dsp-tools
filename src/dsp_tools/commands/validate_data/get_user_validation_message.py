from collections import defaultdict
from pathlib import Path

import pandas as pd

from dsp_tools.commands.validate_data.models.input_problems import AllProblems
from dsp_tools.commands.validate_data.models.input_problems import InputProblem
from dsp_tools.commands.validate_data.models.input_problems import MessageStrings
from dsp_tools.commands.validate_data.models.input_problems import ProblemType
from dsp_tools.commands.validate_data.models.input_problems import Severity
from dsp_tools.commands.validate_data.models.input_problems import SortedProblems
from dsp_tools.commands.validate_data.models.input_problems import UserPrintMessages

LIST_SEPARATOR = "\n    - "
GRAND_SEPARATOR = "\n\n----------------------------\n"


PROBLEM_TYPES_IGNORE_STR_ENUM_INFO = {ProblemType.GENERIC, ProblemType.FILE_VALUE}


def sort_user_problems(all_problems: AllProblems) -> SortedProblems:
    iris_removed, problems_with_iris = _separate_link_value_missing_if_reference_is_an_iri(all_problems.problems)
    filtered_problems = _filter_out_duplicate_problems(iris_removed)
    violations, warnings = _separate_according_to_severity(filtered_problems)
    unique_unexpected = list(set(x.component_type for x in all_problems.unexpected_results or []))
    return SortedProblems(
        unique_violations=violations,
        user_warnings=warnings,
        user_info=problems_with_iris,
        unexpected_shacl_validation_components=unique_unexpected,
    )


def _separate_according_to_severity(problems: list[InputProblem]) -> tuple[list[InputProblem], list[InputProblem]]:
    violations = [x for x in problems if x.severity == Severity.VIOLATION]
    warnings = [x for x in problems if x.severity == Severity.WARNING]
    return violations, warnings


def _separate_link_value_missing_if_reference_is_an_iri(
    problems: list[InputProblem],
) -> tuple[list[InputProblem], list[InputProblem]]:
    iris_referenced = []
    no_iris_referenced = []
    for prblm in problems:
        if prblm.problem_type != ProblemType.INEXISTENT_LINKED_RESOURCE:
            no_iris_referenced.append(prblm)
            continue
        if not prblm.input_value:
            no_iris_referenced.append(prblm)
        elif prblm.input_value.startswith("http://rdfh.ch/"):
            iris_referenced.append(prblm)
        else:
            no_iris_referenced.append(prblm)
    return no_iris_referenced, iris_referenced


def _filter_out_duplicate_problems(problems: list[InputProblem]) -> list[InputProblem]:
    grouped = _group_problems_by_resource(problems)
    filtered = []
    for problems_per_resource in grouped.values():
        filtered.extend(_filter_out_duplicate_text_value_problem(problems_per_resource))
    return filtered


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


def get_user_message(sorted_problems: SortedProblems, file_path: Path) -> UserPrintMessages:
    """
    Creates the string to communicate the user message.

    Args:
        sorted_problems: validation problems
        file_path: Path to the original data XML

    Returns:
        Problem message
    """
    violation_message, warning_message, info_message, unexpected_violations = None, None, None, None
    if sorted_problems.unique_violations:
        if len(sorted_problems.unique_violations) > 50:
            violation_body = _save_problem_info_as_csv(sorted_problems.unique_violations, file_path)
        else:
            violation_body = _get_problem_print_message(sorted_problems.unique_violations)
        violation_header = (
            f"During the validation of the data {len(sorted_problems.unique_violations)} errors were found."
        )
        violation_message = MessageStrings(violation_header, violation_body)
    if sorted_problems.user_warnings:
        if len(sorted_problems.unique_violations) > 50:
            warning_body = _save_problem_info_as_csv(sorted_problems.user_warnings, file_path, "warnings")
        else:
            warning_body = _get_problem_print_message(sorted_problems.user_warnings)
        warning_header = (
            f"During the validation of the data {len(sorted_problems.user_warnings)} "
            f"problems were found. While they currently do not impede an xmlupload they may do so in the future."
        )
        warning_message = MessageStrings(warning_header, warning_body)
    if sorted_problems.user_info:
        info_message = _get_referenced_iri_info(sorted_problems.user_info)
    if sorted_problems.unexpected_shacl_validation_components:
        unexpected_header = "The following unknown violation types were found!"
        unexpected_body = LIST_SEPARATOR + LIST_SEPARATOR.join(sorted_problems.unexpected_shacl_validation_components)
        unexpected_violations = MessageStrings(unexpected_header, unexpected_body)
    return UserPrintMessages(violation_message, warning_message, info_message, unexpected_violations)


def _get_referenced_iri_info(problems: list[InputProblem]) -> MessageStrings:
    user_info_str = [
        f"Resource ID: {x.res_id} | Property: {x.prop_name} | Referenced Database IRI: {x.input_value}"
        for x in problems
    ]
    iri_msg = (
        "Your data references absolute IRIs of resources. "
        "If these resources do not exist in the database or are not of the expected resource type, then "
        "the xmlupload will fail. Below you find a list of the references."
    )
    return MessageStrings(iri_msg, LIST_SEPARATOR + LIST_SEPARATOR.join(user_info_str))


def _get_problem_print_message(problems: list[InputProblem]) -> str:
    grouped = list(_group_problems_by_resource(problems).values())
    messages = [_get_message_for_one_resource(v) for v in sorted(grouped, key=lambda x: x[0].res_id)]
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


def _save_problem_info_as_csv(problems: list[InputProblem], file_path: Path, severity: str = "errors") -> str:
    out_path = file_path.parent / f"{file_path.stem}_validation_{severity}.csv"
    problem_dicts = [_get_message_dict(x) for x in problems]
    df = pd.DataFrame.from_records(problem_dicts)
    df = df.sort_values(by=["Resource Type", "Resource ID", "Property"])
    df.to_csv(out_path, index=False)
    return f"Due to the large number of {severity}, the validation {severity} were saved at:\n{out_path}"


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
