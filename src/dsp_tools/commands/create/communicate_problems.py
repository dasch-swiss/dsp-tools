from loguru import logger

from dsp_tools.commands.create.models.input_problems import CollectedProblems
from dsp_tools.commands.create.models.input_problems import CreateProblem
from dsp_tools.utils.ansi_colors import BOLD_RED
from dsp_tools.utils.ansi_colors import RED
from dsp_tools.utils.ansi_colors import RESET_TO_DEFAULT


def print_problem_collection(problem_collection: CollectedProblems) -> None:
    individual_problems = _create_individual_problem_strings(problem_collection.problems)
    logger.error(problem_collection.header, individual_problems)
    print(BOLD_RED, problem_collection.header, RESET_TO_DEFAULT)
    print(RED, individual_problems, RESET_TO_DEFAULT)


def _create_individual_problem_strings(problems: list[CreateProblem]) -> str:
    str_list = [f"{p.problematic_object}: {p.problem!s}" for p in problems]
    return "   - " + "\n    - ".join(str_list)
