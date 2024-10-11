import regex
from rdflib import RDF
from rdflib import SH
from rdflib import Graph
from rdflib import Literal
from rdflib import Namespace

from dsp_tools.commands.validate_data.models.input_problems import AllProblems
from dsp_tools.commands.validate_data.models.input_problems import ContentRegexViolation
from dsp_tools.commands.validate_data.models.input_problems import InputProblem
from dsp_tools.commands.validate_data.models.input_problems import MaxCardinalityViolation
from dsp_tools.commands.validate_data.models.input_problems import MinCardinalityViolation
from dsp_tools.commands.validate_data.models.input_problems import NonExistentCardinalityViolation
from dsp_tools.commands.validate_data.models.input_problems import UnexpectedResults
from dsp_tools.commands.validate_data.models.input_problems import ValueTypeViolation
from dsp_tools.commands.validate_data.models.validation import ResourceValidationReportIdentifiers
from dsp_tools.commands.validate_data.models.validation import ResultWithDetail
from dsp_tools.commands.validate_data.models.validation import ResultWithoutDetail
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

    results_and_onto = report.validation_graph + report.onto_graph
    data_and_onto = report.onto_graph + report.data_graph
    no_detail_results, details_results = _separate_result_types(
        results_and_onto=results_and_onto, data_onto_graph=data_and_onto
    )

    no_detail_reformatted, no_detail_unexpected = _reformat_without_detail(no_detail_results)
    reformatted_results.extend(no_detail_reformatted)
    unexpected_components.extend(no_detail_unexpected)

    detail_reformatted, detail_unexpected = _reformat_with_detail(details_results)
    reformatted_results.extend(detail_reformatted)
    unexpected_components.extend(detail_unexpected)

    unexpected_found = UnexpectedResults(unexpected_components) if unexpected_components else None
    return AllProblems(reformatted_results, unexpected_found)


def _separate_result_types(
    results_and_onto: Graph, data_onto_graph: Graph
) -> tuple[list[ResultWithoutDetail], list[ResultWithDetail]]:
    identifiers = _extract_identifiers_of_resource_results(results_and_onto, data_onto_graph)
    no_details = [x for x in identifiers if not x.detail_node]
    no_detail_results = [_query_without_detail(x, results_and_onto) for x in no_details]
    with_details = [x for x in identifiers if x.detail_node]
    details_results = [_query_with_detail(x, results_and_onto, data_onto_graph) for x in with_details]
    return no_detail_results, details_results


def _extract_identifiers_of_resource_results(
    results_and_onto: Graph, data_onto_graph: Graph
) -> list[ResourceValidationReportIdentifiers]:
    focus_nodes = list(results_and_onto.subject_objects(SH.focusNode))
    resource_classes = list(data_onto_graph.subjects(KNORA_API.canBeInstantiated, Literal(True)))
    all_res_focus_nodes = []
    for nd in focus_nodes:
        validation_bn = nd[0]
        focus_iri = nd[1]
        res_type = next(data_onto_graph.objects(focus_iri, RDF.type))
        if res_type in resource_classes:
            detail_bn = None
            if detail_bn_list := list(results_and_onto.objects(validation_bn, SH.detail)):
                detail_bn = detail_bn_list[0]
            all_res_focus_nodes.append(
                ResourceValidationReportIdentifiers(
                    validation_bn=validation_bn,
                    focus_node_iri=focus_iri,
                    res_class_type=res_type,
                    detail_node=detail_bn,
                )
            )
    return all_res_focus_nodes


def _query_without_detail(
    identifiers: ResourceValidationReportIdentifiers, results_and_onto: Graph
) -> ResultWithoutDetail:
    path = next(results_and_onto.objects(identifiers.validation_bn, SH.resultPath))
    component = next(results_and_onto.objects(identifiers.validation_bn, SH.sourceConstraintComponent))
    msg = str(next(results_and_onto.objects(identifiers.validation_bn, SH.resultMessage)))
    res_value: str | None = None
    if val := list(results_and_onto.objects(identifiers.validation_bn, SH.value)):
        res_value = str(val[0])
    return ResultWithoutDetail(
        source_constraint_component=component,
        res_iri=identifiers.focus_node_iri,
        res_class=identifiers.res_class_type,
        property=path,
        results_message=msg,
        value=res_value,
    )


def _query_with_detail(
    identifiers: ResourceValidationReportIdentifiers, results_and_onto: Graph, data_graph: Graph
) -> ResultWithDetail:
    path = next(results_and_onto.objects(identifiers.validation_bn, SH.resultPath))
    value_iri = next(results_and_onto.objects(identifiers.validation_bn, SH.value))
    value_type = next(data_graph.objects(value_iri, RDF.type))
    component = next(results_and_onto.objects(identifiers.validation_bn, SH.sourceConstraintComponent))
    detail_component = next(results_and_onto.objects(identifiers.detail_node, SH.sourceConstraintComponent))
    val = None
    if node_value := list(results_and_onto.objects(identifiers.detail_node, SH.value)):
        val = str(node_value[0])
    msg = str(next(results_and_onto.objects(identifiers.detail_node, SH.resultMessage)))
    return ResultWithDetail(
        source_constraint_component=component,
        res_iri=identifiers.focus_node_iri,
        res_class=identifiers.res_class_type,
        property=path,
        results_message=msg,
        detail_bn_component=detail_component,
        value_type=value_type,
        value=val,
    )


def _reformat_without_detail(
    validation_results: list[ResultWithoutDetail],
) -> tuple[list[InputProblem], list[UnexpectedComponent]]:
    input_problems: list[InputProblem] = []
    unexpected_components: list[UnexpectedComponent] = []

    for violation in validation_results:
        problem = _reformat_one_without_detail(violation)
        if isinstance(problem, UnexpectedComponent):
            unexpected_components.append(problem)
        else:
            input_problems.append(problem)
    return input_problems, unexpected_components


def _reformat_one_without_detail(violation: ResultWithoutDetail) -> InputProblem | UnexpectedComponent:
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
        case SH.PatternConstraintComponent:
            return ContentRegexViolation(
                res_id=subject_id,
                res_type=res_type,
                prop_name=prop_name,
                expected_format=violation.results_message,
                actual_content=violation.value,
            )
        case _:
            return UnexpectedComponent(str(violation.source_constraint_component))


def _reformat_with_detail(
    validation_results: list[ResultWithDetail],
) -> tuple[list[InputProblem], list[UnexpectedComponent]]:
    input_problems: list[InputProblem] = []
    unexpected_components: list[UnexpectedComponent] = []

    for violation in validation_results:
        problem = _reformat_one_with_detail(violation)
        if isinstance(problem, UnexpectedComponent):
            unexpected_components.append(problem)
        else:
            input_problems.append(problem)
    return input_problems, unexpected_components


def _reformat_one_with_detail(val_result: ResultWithDetail) -> InputProblem | UnexpectedComponent:
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
    if "http://www.w3.org/2000/01/rdf-schema#" in prop:
        return f'rdfs:{prop.split("#")[-1]}'
    onto = prop.split("/")[-2]
    return f'{onto}:{prop.split("#")[-1]}'


def _reformat_data_iri(iri: str) -> str:
    return iri.replace("http://data/", "")
