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
from dsp_tools.commands.validate_data.models.validation import UnexpectedComponent
from dsp_tools.commands.validate_data.models.validation import ValidationReport
from dsp_tools.commands.validate_data.models.validation import ValidationResult
from dsp_tools.commands.validate_data.models.validation import ValidationResultTypes


def reformat_validation_graph(report: ValidationReport) -> AllProblems:
    """
    Reformats the validation result from an RDF graph into class instances
    that are used to communicate the problems with the user.

    Args:
        results_graph: Contains the possible validation errors
        data_graph: Graph with the data

    Returns:
        All Problems
    """
    reformatted_results: list[InputProblem] = []
    unexpected_components: list[UnexpectedComponent] = []
    if report.cardinality_validation:
        reformatted, unexpected = _reformat_cardinality_graph(report.cardinality_validation)
        reformatted_results.extend(reformatted)
        unexpected_components.extend(unexpected)
    if report.content_validation:
        reformatted, unexpected = _reformat_content_graph(report.content_validation, report.data_graph)
        reformatted_results.extend(reformatted)
        unexpected_components.extend(unexpected)

    unexpected = UnexpectedResults(unexpected_components) if unexpected_components else None
    return AllProblems(reformatted_results, unexpected)


def _reformat_cardinality_graph(results_graph: Graph) -> tuple[list[InputProblem], list[UnexpectedComponent]]:
    pass


def _reformat_content_graph(
    results_graph: Graph, data_graph: Graph
) -> tuple[list[InputProblem], list[UnexpectedComponent]]:
    pass


def _reformat_result_graph(results_graph: Graph, data_graph: Graph) -> list[ValidationResult]:
    results_types = _separate_different_results(results_graph)
    validation_results = [
        _extract_one_cardinality_violation(x, results_graph, data_graph) for x in results_types.cardinality_components
    ]
    validation_results.extend(
        [
            _extract_one_node_constraint_violation(bn, results_graph, data_graph)
            for bn in results_types.node_constraint_component
        ]
    )
    return validation_results


def _separate_different_results(results_graph: Graph) -> ValidationResultTypes:
    violations = set(results_graph.subjects(RDF.type, SH.ValidationResult))
    nodes_constraints = set(results_graph.subjects(SH.sourceConstraintComponent, SH.NodeConstraintComponent))
    class_constraints = set(results_graph.subjects(SH.sourceConstraintComponent, SH.ClassConstraintComponent))
    other_violations = violations - nodes_constraints - class_constraints
    return ValidationResultTypes(
        node_constraint_component=nodes_constraints,
        detail_bns=class_constraints,
        cardinality_components=other_violations,
    )


def _extract_one_cardinality_violation(bn: Node, results_graph: Graph, data_graph: Graph) -> ValidationResult:
    focus_nd = next(results_graph.objects(bn, SH.focusNode))
    res_type = next(data_graph.objects(focus_nd, RDF.type))
    path = next(results_graph.objects(bn, SH.resultPath))
    component = next(results_graph.objects(bn, SH.sourceConstraintComponent))
    msg = str(next(results_graph.objects(bn, SH.resultMessage)))
    return ValidationResult(
        source_constraint_component=component,
        res_iri=focus_nd,
        res_class=res_type,
        property=path,
        results_message=msg,
    )


def _extract_one_node_constraint_violation(bn: Node, results_graph: Graph, data_graph: Graph) -> ValidationResult:
    focus_nd = next(results_graph.objects(bn, SH.focusNode))
    res_type = next(data_graph.objects(focus_nd, RDF.type))
    path = next(results_graph.objects(bn, SH.resultPath))
    value_iri = next(results_graph.objects(bn, SH.value))
    value_type = next(data_graph.objects(value_iri, RDF.type))
    component = next(results_graph.objects(bn, SH.sourceConstraintComponent))
    detail_bn = next(results_graph.objects(bn, SH.detail))
    msg = str(next(results_graph.objects(detail_bn, SH.resultMessage)))
    return ValidationResult(
        source_constraint_component=component,
        res_iri=focus_nd,
        res_class=res_type,
        property=path,
        results_message=msg,
        value_type=value_type,
    )


def _transform_violations_into_input_problems(
    violations: list[ValidationResult],
) -> tuple[list[InputProblem], list[UnexpectedComponent]]:
    input_problems: list[InputProblem] = []
    unexpected_components: list[UnexpectedComponent] = []
    for violation in violations:
        problem = _reformat_one_violation(violation)
        if isinstance(problem, UnexpectedComponent):
            unexpected_components.append(problem)
        else:
            input_problems.append(problem)
    return input_problems, unexpected_components


def _reformat_one_violation(violation: ValidationResult) -> InputProblem | UnexpectedComponent:
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
        case SH.NodeConstraintComponent:
            actual_type = _reformat_onto_iri(str(violation.value_type)).replace("knora-api:", "")
            return ValueTypeViolation(
                res_id=subject_id,
                res_type=res_type,
                prop_name=prop_name,
                actual_type=actual_type,
                expected_type=violation.results_message,
            )
        case _:
            return UnexpectedComponent(str(violation.source_constraint_component))


def _reformat_onto_iri(prop: str) -> str:
    onto = prop.split("/")[-2]
    return f'{onto}:{prop.split("#")[-1]}'


def _reformat_data_iri(iri: str) -> str:
    return iri.replace("http://data/", "")
