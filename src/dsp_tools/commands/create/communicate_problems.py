from loguru import logger

from dsp_tools.commands.create.models.input_problems import CollectedProblems
from dsp_tools.commands.create.models.input_problems import CreateProblem
from dsp_tools.utils.ansi_colors import BOLD_RED
from dsp_tools.utils.ansi_colors import RESET_TO_DEFAULT


def print_problem_collection(problem_collection: CollectedProblems) -> None:
    individual_problems = _create_individual_problem_strings(problem_collection.problems)
    print_str = f"{problem_collection.header}\n\n{individual_problems}"
    logger.error(print_str)
    print(BOLD_RED, print_str, RESET_TO_DEFAULT)


def _create_individual_problem_strings(problems: list[CreateProblem]) -> str:
    str_list = [f"{p.problematic_object}: {p.problem!s}" for p in problems]
    return "\n    - ".join(str_list)
