from __future__ import annotations

from loguru import logger

from dsp_tools.commands.create.models.create_problems import CardinalitiesThatMayCreateAProblematicCircle
from dsp_tools.commands.create.models.create_problems import CollectedProblems
from dsp_tools.commands.create.models.create_problems import CreateProblem
from dsp_tools.setup.ansi_colors import BACKGROUND_BOLD_YELLOW
from dsp_tools.setup.ansi_colors import BOLD_RED
from dsp_tools.setup.ansi_colors import RESET_TO_DEFAULT

LIST_SEPARATOR = "\n    - "


def print_all_problem_collections(problems: list[CollectedProblems]) -> None:
    for prob in problems:
        print_problem_collection(prob)


def print_problem_collection(problem_collection: CollectedProblems) -> None:
    individual_problems = _create_individual_problem_strings(problem_collection.problems)
    logger.error(problem_collection.header + individual_problems)
    print(BOLD_RED, problem_collection.header, RESET_TO_DEFAULT)
    print(individual_problems)


def _create_individual_problem_strings(problems: list[CreateProblem]) -> str:
    str_list = [f"{p.problematic_object}: {p.problem!s}" for p in problems]
    return "   - " + "\n    - ".join(str_list)


def print_msg_str_for_potential_problematic_circles(
    circle_info: list[CardinalitiesThatMayCreateAProblematicCircle],
) -> None:
    header = "Potentially problematic cardinalities found that may cause an upload to fail."
    detail_start = (
        "Your ontology contains cardinalities with a minimum of 1 that point to a generic knora-api Resource.\n"
        "Because we upload resources sequentially, we must break up any circles in your data. "
        "Because of the generic nature of the object constraint we cannot infer from the ontology "
        "if your data contains a circle which would cause a minimum cardinality violation when broken up. "
        "Therefore, we cannot guarantee that your upload will succeed even if the validation passes.\n"
        "The following classes contain potentially problematic links:\n"
    )
    detail_strings = []
    for problem in circle_info:
        detail = (
            f"Class: {problem.subject} | "
            f"Property: {problem.prop} | "
            f"Object Class: {problem.object_cls} | "
            f"Cardinality: {problem.card}"
        )
        detail_strings.append(detail)
    details = detail_start + LIST_SEPARATOR + LIST_SEPARATOR.join(detail_strings)
    logger.warning(header, details)
    print(BACKGROUND_BOLD_YELLOW + header + RESET_TO_DEFAULT)
    print(details + "\n")
