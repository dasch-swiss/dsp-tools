from dsp_tools.commands.validate_data.models.input_problems import InputProblem


def get_user_message(problems: list[InputProblem]):
    pass


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
