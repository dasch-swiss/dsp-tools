from dsp_tools.commands.validate_data.models.input_problems import InputProblem
from collections import defaultdict

def get_user_message(problems: list[InputProblem]):
    pass




def _group_problems_by_resource(problems: list[InputProblem]) -> dict[str: list[InputProblem]]:
    grouped_res = defaultdict(list)
    for prob in problems:
        grouped_res[prob.res_id].append(prob)
    return grouped_res


def _get_message_with_properties(problems: list[InputProblem]) -> str:
    messages = defaultdict(list)
    for prob in problems:
        messages[prob.prop_name].append(_get_message_detail_str(prob))



def _get_message_details_dict(problem: InputProblem) -> dict[str, str]:
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


def _shorten_input(user_input: str | None) -> str | None:
    if not user_input or len(user_input) < 15:
        return user_input
    return f"{user_input[:15]}[...]"
