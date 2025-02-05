from dsp_tools.commands.validate_data.models.input_problems import InputProblem


def get_user_message(problems: list[InputProblem]):
    pass


def _get_message_details_dict(problem: InputProblem) -> dict[str, str]:
    msg_dict = {
        "Resource ID": problem.res_id,
        "Resource Type": problem.res_type,
        "Property": problem.prop_name,
        "Problem": problem.message,
        "Your Input": problem.actual_input,
        "Input Type": problem.actual_input_type,
        "Expected": problem.expected,
    }
    return {k: v for k, v in msg_dict.items() if v}


def _get_message_detail_str(problem: InputProblem) -> str:
    pass
