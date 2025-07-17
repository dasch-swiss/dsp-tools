from collections import defaultdict

import pandas as pd

from dsp_tools.cli.args import ValidationSeverity
from dsp_tools.commands.validate_data.models.input_problems import AllProblems
from dsp_tools.commands.validate_data.models.input_problems import DuplicateFileWarning
from dsp_tools.commands.validate_data.models.input_problems import InputProblem
from dsp_tools.commands.validate_data.models.input_problems import MessageComponents
from dsp_tools.commands.validate_data.models.input_problems import ProblemType
from dsp_tools.commands.validate_data.models.input_problems import Severity
from dsp_tools.commands.validate_data.models.input_problems import SortedProblems
from dsp_tools.commands.validate_data.models.input_problems import UserPrintMessages

LIST_SEPARATOR = "\n    - "
GRAND_SEPARATOR = "\n\n----------------------------\n"


PROBLEM_TYPES_IGNORE_STR_ENUM_INFO = {ProblemType.GENERIC, ProblemType.FILE_VALUE_MISSING, ProblemType.FILE_DUPLICATE}


def sort_user_problems(
    all_problems: AllProblems, duplicate_file_warnings: DuplicateFileWarning | None
) -> SortedProblems:
    iris_removed, problems_with_iris = _separate_link_value_missing_if_reference_is_an_iri(all_problems.problems)
    filtered_problems = _filter_out_duplicate_problems(iris_removed)
    violations, warnings, info = _separate_according_to_severity(filtered_problems)
    if duplicate_file_warnings:
        warnings.extend(duplicate_file_warnings.problems)
    info.extend(problems_with_iris)
    unique_unexpected = list(set(x.component_type for x in all_problems.unexpected_results or []))
    return SortedProblems(
        unique_violations=violations,
        user_warnings=warnings,
        user_info=info,
        unexpected_shacl_validation_components=unique_unexpected,
    )


def _separate_according_to_severity(
    problems: list[InputProblem],
) -> tuple[list[InputProblem], list[InputProblem], list[InputProblem]]:
    violations = [x for x in problems if x.severity == Severity.VIOLATION]
    warnings = [x for x in problems if x.severity == Severity.WARNING]
    info = [x for x in problems if x.severity == Severity.INFO]
    return violations, warnings, info


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
            prblm.message = (
                "You used an absolute IRI to reference an existing resource in the DB. "
                "If this resource does not exist or is not of the correct type, an xmlupload will fail."
            )
            iris_referenced.append(prblm)
        else:
            no_iris_referenced.append(prblm)
    return no_iris_referenced, iris_referenced


def _filter_out_duplicate_problems(problems: list[InputProblem]) -> list[InputProblem]:
    grouped, without_res_id = _group_problems_by_resource(problems)
    filtered = without_res_id
    for problems_per_resource in grouped.values():
        text_value_filtered = _filter_out_duplicate_text_value_problem(problems_per_resource)
        file_value_corrected = _filter_out_duplicate_wrong_file_type_problems(text_value_filtered)
        filtered.extend(file_value_corrected)
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


def _filter_out_duplicate_wrong_file_type_problems(problems: list[InputProblem]) -> list[InputProblem]:
    # If a class is for example, an AudioRepresentation, but a jpg file is used,
    # the created value is of type StillImageFileValue.
    # This creates a min cardinality (because the audio file is missing)
    # and a closed constraint violation (because it is not permissible to add an image)
    # However, we only want to give one message to the user
    idx_missing = next((i for i, x in enumerate(problems) if x.problem_type == ProblemType.FILE_VALUE_MISSING), None)
    idx_prohibited = next(
        (i for i, x in enumerate(problems) if x.problem_type == ProblemType.FILE_VALUE_PROHIBITED), None
    )
    if idx_missing is None or idx_prohibited is None:
        return problems
    missing_problem = problems[idx_missing]
    prohibited_problem = problems[idx_prohibited]
    # The result of the closed constraint violation, contains the input value,
    # while the message of the other shape is better, we want to include the actual input value.
    missing_problem.input_value = prohibited_problem.input_value
    return [problem for i, problem in enumerate(problems) if i not in {idx_missing, idx_prohibited}] + [missing_problem]


def _group_problems_by_resource(
    problems: list[InputProblem],
) -> tuple[dict[str, list[InputProblem]], list[InputProblem]]:
    grouped_res = defaultdict(list)
    problem_no_res_id = []
    for prob in problems:
        if not prob.res_id:
            problem_no_res_id.append(prob)
        else:
            grouped_res[prob.res_id].append(prob)
    return grouped_res, problem_no_res_id


def get_user_message(sorted_problems: SortedProblems, severity: ValidationSeverity) -> UserPrintMessages:
    """
    Creates the string to communicate the user message.

    Args:
        sorted_problems: validation problems
        severity: Severity level of validation information

    Returns:
        Problem message
    """
    violation_message, warning_message, info_message, unexpected_violations = None, None, None, None
    too_many_to_print = _are_there_too_many_to_print(sorted_problems, severity)
    if sorted_problems.unique_violations:
        if too_many_to_print:
            violation_body = None
            violation_df = _get_message_df(sorted_problems.unique_violations)
        else:
            violation_body = _get_problem_print_message(sorted_problems.unique_violations)
            violation_df = None
        violation_header = (
            f"During the validation of the data {len(sorted_problems.unique_violations)} errors were found. "
            f"Until they are resolved an xmlupload is not possible."
        )
        violation_message = MessageComponents(violation_header, violation_body, violation_df)
    if sorted_problems.user_warnings:
        if too_many_to_print:
            warning_body = None
            warning_df = _get_message_df(sorted_problems.user_warnings)
        else:
            warning_body = _get_problem_print_message(sorted_problems.user_warnings)
            warning_df = None
        warning_header = (
            f"During the validation of the data {len(sorted_problems.user_warnings)} "
            f"problems were found. Warnings are allowed on test servers. "
            f"Please note that an xmlupload on a prod sever will fail."
        )
        warning_message = MessageComponents(warning_header, warning_body, warning_df)
    if sorted_problems.user_info:
        if too_many_to_print:
            info_body = None
            info_df = _get_message_df(sorted_problems.user_info)
        else:
            info_body = _get_problem_print_message(sorted_problems.user_info)
            info_df = None
        info_header = (
            f"During the validation of the data {len(sorted_problems.user_info)} "
            f"potential problems were found. They will not impede an xmlupload."
        )
        info_message = MessageComponents(info_header, info_body, info_df)
    if sorted_problems.unexpected_shacl_validation_components:
        unexpected_header = "The following unknown violation types were found!"
        unexpected_body = LIST_SEPARATOR + LIST_SEPARATOR.join(sorted_problems.unexpected_shacl_validation_components)
        unexpected_violations = MessageComponents(unexpected_header, unexpected_body, None)
    return UserPrintMessages(violation_message, warning_message, info_message, unexpected_violations)


def _are_there_too_many_to_print(sorted_problems: SortedProblems, severity: ValidationSeverity) -> bool:
    number_of_problems = len(sorted_problems.unique_violations)
    if severity.value <= ValidationSeverity.WARNING.value:
        number_of_problems += len(sorted_problems.user_warnings)
    if severity.value == ValidationSeverity.INFO.value:
        number_of_problems += len(sorted_problems.user_info)
    return bool(number_of_problems > 60)


def _get_problem_print_message(problems: list[InputProblem]) -> str:
    grouped, without_res_id = _group_problems_by_resource(problems)
    messages = [_get_message_for_one_resource(without_res_id)] if without_res_id else []
    messages_with_ids = [
        _get_message_for_one_resource(v) for v in sorted(grouped.values(), key=lambda x: str(x[0].res_id))
    ]
    messages.extend(messages_with_ids)
    return GRAND_SEPARATOR.join(messages)


def _get_message_for_one_resource(problems: list[InputProblem]) -> str:
    if problems[0].res_id:
        start_msg = f"Resource ID: {problems[0].res_id} | Resource Type: {problems[0].res_type}"
    else:
        start_msg = ""
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
        msg.append(f"Your input: '{_shorten_input(problem.input_value, problem.problem_type)}'")
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


def _get_message_df(problems: list[InputProblem]) -> pd.DataFrame:
    problem_dicts = [_get_message_dict(x) for x in problems]
    df = pd.DataFrame.from_records(problem_dicts)
    df = df.sort_values(by=["Resource Type", "Resource ID", "Property"])
    return df


def _get_message_dict(problem: InputProblem) -> dict[str, str]:
    msg_dict = {
        "Resource ID": problem.res_id,
        "Resource Type": problem.res_type,
        "Property": problem.prop_name,
        "Your Input": _shorten_input(problem.input_value, problem.problem_type),
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


def _shorten_input(user_input: str | None, problem_type: ProblemType) -> str | None:
    if problem_type in [
        ProblemType.FILE_DUPLICATE,
        ProblemType.FILE_VALUE_MISSING,
        ProblemType.FILE_VALUE_PROHIBITED,
        ProblemType.LINK_TARGET_TYPE_MISMATCH,
        ProblemType.INEXISTENT_LINKED_RESOURCE,
    ]:
        return user_input
    if not user_input:
        return None
    if user_input.startswith(("http://rdfh.ch/", " / http://rdfh.ch/lists/")):
        return user_input
    if len(user_input) < 51:
        return user_input
    return f"{user_input[:50]}[...]"
