from rdflib import RDF
from rdflib import SH
from rdflib import Graph
from rdflib.term import Node

from dsp_tools.commands.validate_data.models.input_problems import AllProblems
from dsp_tools.commands.validate_data.models.input_problems import InputProblem
from dsp_tools.commands.validate_data.models.input_problems import MaxCardinalityViolation
from dsp_tools.commands.validate_data.models.input_problems import MinCardinalityViolation
from dsp_tools.commands.validate_data.models.input_problems import NonExistentCardinalityViolation
from dsp_tools.commands.validate_data.models.input_problems import UnexpectedResults
from dsp_tools.commands.validate_data.models.input_problems import ValueTypeViolation
from dsp_tools.commands.validate_data.models.validation import CardinalityValidationResult
from dsp_tools.commands.validate_data.models.validation import ContentValidationResult
from dsp_tools.commands.validate_data.models.validation import UnexpectedComponent
from dsp_tools.commands.validate_data.models.validation import ValidationReports


def reformat_validation_graph(report: ValidationReports) -> AllProblems:
    """
    Reformats the validation result from an RDF graph into class instances
    that are used to communicate the problems with the user.

    Args:
        report: with all the information necessary to construct a user message

    Returns:
        All Problems
    """
    reformatted_results: list[InputProblem] = []
    unexpected_components: list[UnexpectedComponent] = []
    if report.cardinality_validation:
        reformatted, unexpected = _get_cardinality_input_errors(report.cardinality_validation, report.data_graph)
        reformatted_results.extend(reformatted)
        unexpected_components.extend(unexpected)
    if report.content_validation:
        reformatted, unexpected = _get_content_input_errors(report.content_validation, report.data_graph)
        reformatted_results.extend(reformatted)
        unexpected_components.extend(unexpected)
    unexpected_found = UnexpectedResults(unexpected_components) if unexpected_components else None
    return AllProblems(reformatted_results, unexpected_found)


def _get_cardinality_input_errors(
    results_graph: Graph, data_graph: Graph
) -> tuple[list[InputProblem], list[UnexpectedComponent]]:
    validation_results = _query_for_cardinality_validation_results(results_graph, data_graph)
    input_problems: list[InputProblem] = []
    unexpected_components: list[UnexpectedComponent] = []
    for violation in validation_results:
        problem = _reformat_one_cardinality_validation_result(violation)
        if isinstance(problem, UnexpectedComponent):
            unexpected_components.append(problem)
        else:
            input_problems.append(problem)
    return input_problems, unexpected_components


def _query_for_cardinality_validation_results(
    results_graph: Graph, data_graph: Graph
) -> list[CardinalityValidationResult]:
    violations = results_graph.subjects(RDF.type, SH.ValidationResult)
    return [_query_for_one_cardinality_validation_result(x, results_graph, data_graph) for x in violations]


def _query_for_one_cardinality_validation_result(
    bn: Node, results_graph: Graph, data_graph: Graph
) -> CardinalityValidationResult:
    focus_nd = next(results_graph.objects(bn, SH.focusNode))
    res_type = next(data_graph.objects(focus_nd, RDF.type))
    path = next(results_graph.objects(bn, SH.resultPath))
    component = next(results_graph.objects(bn, SH.sourceConstraintComponent))
    msg = str(next(results_graph.objects(bn, SH.resultMessage)))
    return CardinalityValidationResult(
        source_constraint_component=component,
        res_iri=focus_nd,
        res_class=res_type,
        property=path,
        results_message=msg,
    )


def _reformat_one_cardinality_validation_result(
    violation: CardinalityValidationResult,
) -> InputProblem | UnexpectedComponent:
    subject_id = _reformat_data_iri(str(violation.res_iri))
    prop_name = _reformat_onto_iri(str(violation.property))
    res_type = _reformat_onto_iri(str(violation.res_class))
    match violation.source_constraint_component:
        case SH.MaxCountConstraintComponent:
            return MaxCardinalityViolation(
                res_id=subject_id,
                res_type=res_type,
                prop_name=prop_name,
                expected_cardinality=violation.results_message,
            )
        case SH.MinCountConstraintComponent:
            return MinCardinalityViolation(
                res_id=subject_id,
                res_type=res_type,
                prop_name=prop_name,
                expected_cardinality=violation.results_message,
            )
        case SH.ClosedConstraintComponent:
            return NonExistentCardinalityViolation(
                res_id=subject_id,
                res_type=res_type,
                prop_name=prop_name,
            )
        case _:
            return UnexpectedComponent(str(violation.source_constraint_component))


def _get_content_input_errors(
    results_graph: Graph, data_graph: Graph
) -> tuple[list[InputProblem], list[UnexpectedComponent]]:
    violations = _query_for_content_validation_results(results_graph, data_graph)

    input_problems: list[InputProblem] = []
    unexpected_components: list[UnexpectedComponent] = []
    for violation in violations:
        problem = _reformat_one_content_validation_result(violation)
        if isinstance(problem, UnexpectedComponent):
            unexpected_components.append(problem)
        else:
            input_problems.append(problem)
    return input_problems, unexpected_components


def _query_for_content_validation_results(results_graph: Graph, data_graph: Graph) -> list[ContentValidationResult]:
    main_results = list(results_graph.subjects(SH.sourceConstraintComponent, SH.NodeConstraintComponent))
    return [_query_for_one_content_validation_result(x, results_graph, data_graph) for x in main_results]


def _query_for_one_content_validation_result(
    bn: Node, results_graph: Graph, data_graph: Graph
) -> ContentValidationResult:
    focus_nd = next(results_graph.objects(bn, SH.focusNode))
    res_type = next(data_graph.objects(focus_nd, RDF.type))
    path = next(results_graph.objects(bn, SH.resultPath))
    value_iri = next(results_graph.objects(bn, SH.value))
    value_type = next(data_graph.objects(value_iri, RDF.type))
    component = next(results_graph.objects(bn, SH.sourceConstraintComponent))
    detail_bn = next(results_graph.objects(bn, SH.detail))
    msg = str(next(results_graph.objects(detail_bn, SH.resultMessage)))
    return ContentValidationResult(
        source_constraint_component=component,
        res_iri=focus_nd,
        res_class=res_type,
        property=path,
        results_message=msg,
        value_type=value_type,
    )


def _reformat_one_content_validation_result(val_result: ContentValidationResult) -> InputProblem | UnexpectedComponent:
    subject_id = _reformat_data_iri(str(val_result.res_iri))
    prop_name = _reformat_onto_iri(str(val_result.property))
    res_type = _reformat_onto_iri(str(val_result.res_class))
    match val_result.source_constraint_component:
        case SH.NodeConstraintComponent:
            actual_type = _reformat_onto_iri(str(val_result.value_type)).replace("knora-api:", "")
            return ValueTypeViolation(
                res_id=subject_id,
                res_type=res_type,
                prop_name=prop_name,
                actual_type=actual_type,
                expected_type=val_result.results_message,
            )
        case _:
            return UnexpectedComponent(str(val_result.source_constraint_component))


def _reformat_onto_iri(prop: str) -> str:
    onto = prop.split("/")[-2]
    return f'{onto}:{prop.split("#")[-1]}'


def _reformat_data_iri(iri: str) -> str:
    return iri.replace("http://data/", "")
