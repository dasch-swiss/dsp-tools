from dsp_tools.commands.validate_data.models.input_problems import InputProblem
from dsp_tools.commands.validate_data.models.input_problems import ProblemDetails


def get_user_message(problems: list[InputProblem]):
    pass


def _get_message_details_dict(details: ProblemDetails) -> dict[str, str]:
    msg_dict = {
        "Problem": details.message,
        "Your Input": details.actual_input,
        "Input Type": details.actual_input_type,
        "Expected": details.expected,
    }
    return {k: v for k, v in msg_dict.items() if v}


def _get_message_detail_str(details: ProblemDetails) -> str:
    pass
