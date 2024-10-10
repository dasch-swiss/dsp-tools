import regex
from rdflib import RDF
from rdflib import RDFS
from rdflib import SH
from rdflib import Graph
from rdflib import Namespace
from rdflib.term import Node

from dsp_tools.commands.validate_data.models.input_problems import AllProblems
from dsp_tools.commands.validate_data.models.input_problems import ContentRegexViolation
from dsp_tools.commands.validate_data.models.input_problems import InputProblem
from dsp_tools.commands.validate_data.models.input_problems import MaxCardinalityViolation
from dsp_tools.commands.validate_data.models.input_problems import MinCardinalityViolation
from dsp_tools.commands.validate_data.models.input_problems import NonExistentCardinalityViolation
from dsp_tools.commands.validate_data.models.input_problems import UnexpectedResults
from dsp_tools.commands.validate_data.models.input_problems import ValueTypeViolation
from dsp_tools.commands.validate_data.models.validation import CardinalityValidationResult
from dsp_tools.commands.validate_data.models.validation import ContentValidationResult
from dsp_tools.commands.validate_data.models.validation import ResourceValidationReportIdentifiers
from dsp_tools.commands.validate_data.models.validation import UnexpectedComponent
from dsp_tools.commands.validate_data.models.validation import ValidationReport

DASH = Namespace("http://datashapes.org/dash#")
KNORA_API = Namespace("http://api.knora.org/ontology/knora-api/v2#")


def reformat_validation_graph(report: ValidationReport) -> AllProblems:
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

    reformatted_cardinality, unexpected_cardinality = _get_cardinality_input_errors(
        report.validation_graph, report.data_graph
    )
    reformatted_results.extend(reformatted_cardinality)
    unexpected_components.extend(unexpected_cardinality)

    reformatted_content, unexpected_content = _get_content_input_errors(report.validation_graph, report.data_graph)
    reformatted_results.extend(reformatted_content)
    unexpected_components.extend(unexpected_content)

    unexpected_found = UnexpectedResults(unexpected_components) if unexpected_components else None
    return AllProblems(reformatted_results, unexpected_found)


def _extract_identifiers_of_resource_results(
    results_graph: Graph, data_onto_graph: Graph
) -> list[ResourceValidationReportIdentifiers]:
    focus_nodes = list(results_graph.subject_objects(SH.focusNode))
    resource_classes = list(data_onto_graph.transitive_subjects(RDFS.subClassOf, KNORA_API.Resource))
    all_res_focus_nodes = []
    for nd in focus_nodes:
        validation_bn = nd[0]
        focus_iri = nd[1]
        res_type = next(data_onto_graph.objects(focus_iri, RDF.type))
        if res_type in resource_classes:
            all_res_focus_nodes.append(
                ResourceValidationReportIdentifiers(
                    validation_bn=validation_bn, focus_node_iri=focus_iri, res_class_type=res_type
                )
            )
    return all_res_focus_nodes


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
    all_violations = set(results_graph.subjects(RDF.type, SH.ValidationResult))
    content_violations = set(results_graph.subjects(SH.sourceConstraintComponent, SH.NodeConstraintComponent))
    card_violations = all_violations - content_violations
    return [_query_for_one_cardinality_validation_result(x, results_graph, data_graph) for x in card_violations]


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
        case DASH.ClosedByTypesConstraintComponent:
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
    detail_component = next(results_graph.objects(detail_bn, SH.sourceConstraintComponent))
    val = None
    if node_value := list(results_graph.objects(detail_bn, SH.value)):
        val = str(node_value[0])
    msg = str(next(results_graph.objects(detail_bn, SH.resultMessage)))
    return ContentValidationResult(
        source_constraint_component=component,
        res_iri=focus_nd,
        res_class=res_type,
        property=path,
        results_message=msg,
        detail_bn_component=detail_component,
        value_type=value_type,
        value=val,
    )


def _reformat_one_content_validation_result(val_result: ContentValidationResult) -> InputProblem | UnexpectedComponent:
    subject_id = _reformat_data_iri(str(val_result.res_iri))
    prop_name = _reformat_onto_iri(str(val_result.property))
    res_type = _reformat_onto_iri(str(val_result.res_class))
    match val_result.detail_bn_component:
        case SH.PatternConstraintComponent:
            val: str | None = val_result.value
            if val and not regex.search(r"\S+", val):
                val = None
            return ContentRegexViolation(
                res_id=subject_id,
                res_type=res_type,
                prop_name=prop_name,
                expected_format=val_result.results_message,
                actual_content=val,
            )
        case SH.ClassConstraintComponent | SH.MinCountConstraintComponent:
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
