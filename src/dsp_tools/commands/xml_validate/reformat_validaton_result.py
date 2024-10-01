from typing import Callable

from rdflib import SH
from rdflib import Graph
from rdflib import URIRef
from rdflib.term import Node

from dsp_tools.commands.xml_validate.models.input_problems import AllProblems
from dsp_tools.commands.xml_validate.models.input_problems import GeneralInfo
from dsp_tools.commands.xml_validate.models.input_problems import InputProblem
from dsp_tools.commands.xml_validate.models.input_problems import MaxCardinalityViolation
from dsp_tools.commands.xml_validate.models.input_problems import MinCardinalityViolation
from dsp_tools.commands.xml_validate.models.input_problems import NonExistentCardinalityViolation
from dsp_tools.commands.xml_validate.models.input_problems import UnexpectedResults


def reformat_validation_graph(g: Graph) -> AllProblems:
    """
    Reformats the validation result from an RDF graph into class instances
    that are used to communicate the problems with the user.

    Args:
        g: Contains the possible two validation errors

    Returns:
        List of individual problems
    """
    problems: list[InputProblem] = _reformat_cardinality_violations(g)
    unexpected = _check_for_unexpected_constraint_components(g)
    return AllProblems(problems, unexpected)


def _check_for_unexpected_constraint_components(g: Graph) -> None | UnexpectedResults:
    known_components = {
        SH.MaxCountConstraintComponent,
        SH.MinCountConstraintComponent,
        SH.ClosedConstraintComponent,
    }
    components_in_graph = set(g.objects(predicate=SH.sourceConstraintComponent))
    if diff := components_in_graph - known_components:
        diff_names = [str(x) for x in diff]
        msg = (
            f"Unknown constraint component: {', '.join(diff_names)}. "
            f"Please contact the dsp-tools developer team with this information."
        )
        return UnexpectedResults(msg, g)
    return None


def _reformat_cardinality_violations(g: Graph) -> list[InputProblem]:
    problems: list[InputProblem] = _get_general_violation(g, SH.MaxCountConstraintComponent, MaxCardinalityViolation)
    problems.extend(_get_general_violation(g, SH.MinCountConstraintComponent, MinCardinalityViolation))
    non_existing = g.subjects(SH.sourceConstraintComponent, SH.ClosedConstraintComponent)
    for bn in non_existing:
        general_info = _get_general_info(g, bn)
        problems.append(NonExistentCardinalityViolation(general_info.subject_id, general_info.prop_name))
    return problems


def _get_general_violation(
    g: Graph, constraint_component: URIRef, func: Callable[[str, str, str], InputProblem]
) -> list[InputProblem]:
    problems: list[InputProblem] = []
    constraints = g.subjects(SH.sourceConstraintComponent, constraint_component)
    for bn in constraints:
        general_info = _get_general_info(g, bn)
        problems.append(func(general_info.subject_id, general_info.prop_name, general_info.results_message))
    return problems


def _get_general_info(g: Graph, validation_node: Node) -> GeneralInfo:
    subject = next(g.objects(validation_node, SH.focusNode))
    res_id = _reformat_data_iri(str(subject))
    property_name = next(g.objects(validation_node, SH.resultPath))
    prop_str = _reformat_prop_iri(str(property_name))
    msg = str(next(g.objects(validation_node, SH.resultMessage)))
    return GeneralInfo(res_id, prop_str, msg)


def _reformat_prop_iri(prop: str) -> str:
    onto = prop.split("/")[-2]
    return f'{onto}:{prop.split("#")[-1]}'


def _reformat_data_iri(iri: str) -> str:
    return iri.lstrip("http://data/")
