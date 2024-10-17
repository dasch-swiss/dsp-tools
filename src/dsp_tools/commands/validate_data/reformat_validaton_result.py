import regex
from rdflib import RDF
from rdflib import SH
from rdflib import Graph
from rdflib import Literal
from rdflib import Namespace
from rdflib.term import Node

from dsp_tools.commands.validate_data.models.input_problems import AllProblems
from dsp_tools.commands.validate_data.models.input_problems import ContentRegexViolation
from dsp_tools.commands.validate_data.models.input_problems import InputProblem
from dsp_tools.commands.validate_data.models.input_problems import LinkedResourceDoesNotExist
from dsp_tools.commands.validate_data.models.input_problems import LinkTargetTypeMismatch
from dsp_tools.commands.validate_data.models.input_problems import MaxCardinalityViolation
from dsp_tools.commands.validate_data.models.input_problems import MinCardinalityViolation
from dsp_tools.commands.validate_data.models.input_problems import NonExistentCardinalityViolation
from dsp_tools.commands.validate_data.models.input_problems import UnexpectedResults
from dsp_tools.commands.validate_data.models.input_problems import ValueTypeViolation
from dsp_tools.commands.validate_data.models.validation import ResultDetail
from dsp_tools.commands.validate_data.models.validation import ResultMaxCardinalityViolation
from dsp_tools.commands.validate_data.models.validation import ResultMinCardinalityViolation
from dsp_tools.commands.validate_data.models.validation import ResultNonExistentCardinalityViolation
from dsp_tools.commands.validate_data.models.validation import ResultPatternViolation
from dsp_tools.commands.validate_data.models.validation import ResultValueTypeViolation
from dsp_tools.commands.validate_data.models.validation import ResultWithDetail
from dsp_tools.commands.validate_data.models.validation import ResultWithoutDetail
from dsp_tools.commands.validate_data.models.validation import UnexpectedComponent
from dsp_tools.commands.validate_data.models.validation import ValidationReport
from dsp_tools.commands.validate_data.models.validation import ValidationResult
from dsp_tools.commands.validate_data.models.validation import ValidationResultBaseInfo

DASH = Namespace("http://datashapes.org/dash#")
KNORA_API = Namespace("http://api.knora.org/ontology/knora-api/v2#")
API_SHAPES = Namespace("http://api.knora.org/ontology/knora-api/shapes/v2#")


def reformat_validation_graph(report: ValidationReport) -> AllProblems:
    """
    Reformats the validation result from an RDF graph into class instances
    that are used to communicate the problems with the user.

    Args:
        report: with all the information necessary to construct a user message

    Returns:
        All Problems
    """
    unexpected_components: list[UnexpectedComponent] = []

    results_and_onto = report.validation_graph + report.onto_graph
    data_and_onto = report.onto_graph + report.data_graph

    validation_results, unexpected_extracted = _query_all_results(results_and_onto, data_and_onto)
    reformatted_results: list[InputProblem] = _reformat_validation_results(validation_results)

    unexpected_found = UnexpectedResults(unexpected_components) if unexpected_components else None
    return AllProblems(reformatted_results, unexpected_found)


def _query_all_results(
    results_and_onto: Graph, data_onto_graph: Graph
) -> tuple[list[ValidationResult], list[UnexpectedComponent]]:
    no_details, with_details = _separate_result_types(results_and_onto, data_onto_graph)
    extracted_results: list[ValidationResult] = []
    unexpected_components: list[UnexpectedComponent] = []

    no_detail_extracted, no_detail_unexpected = _query_all_without_detail(no_details, results_and_onto)
    extracted_results.extend(no_detail_extracted)
    unexpected_components.extend(no_detail_unexpected)

    detail_reformatted, detail_unexpected = _query_all_with_detail(with_details, results_and_onto, data_onto_graph)
    extracted_results.extend(detail_reformatted)
    unexpected_components.extend(detail_unexpected)
    return extracted_results, unexpected_components


def _separate_result_types(
    results_and_onto: Graph, data_onto_graph: Graph
) -> tuple[list[ValidationResultBaseInfo], list[ValidationResultBaseInfo]]:
    base_info = _extract_base_info_of_resource_results(results_and_onto, data_onto_graph)
    no_details = [x for x in base_info if not x.detail_node]
    with_details = [x for x in base_info if x.detail_node]
    return no_details, with_details


def _extract_base_info_of_resource_results(
    results_and_onto: Graph, data_onto_graph: Graph
) -> list[ValidationResultBaseInfo]:
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
            path = next(results_and_onto.objects(validation_bn, SH.resultPath))
            all_res_focus_nodes.append(
                ValidationResultBaseInfo(
                    validation_bn=validation_bn,
                    focus_node_iri=focus_iri,
                    res_class_type=res_type,
                    result_path=path,
                    detail_node=detail_bn,
                )
            )
    return all_res_focus_nodes


def _query_all_without_detail(
    all_base_info: list[ValidationResultBaseInfo], results_and_onto: Graph
) -> tuple[list[ValidationResult], list[UnexpectedComponent]]:
    extracted_results: list[ValidationResult] = []
    unexpected_components: list[UnexpectedComponent] = []

    for base_info in all_base_info:
        res = _query_one_without_detail(base_info, results_and_onto)
        if isinstance(res, UnexpectedComponent):
            unexpected_components.append(res)
        else:
            extracted_results.append(res)
    return extracted_results, unexpected_components


def _query_one_without_detail(
    base_info: ValidationResultBaseInfo, results_and_onto: Graph
) -> ValidationResult | UnexpectedComponent:
    msg = str(next(results_and_onto.objects(base_info.validation_bn, SH.resultMessage)))
    component = next(results_and_onto.objects(base_info.validation_bn, SH.sourceConstraintComponent))
    match component:
        case SH.PatternConstraintComponent:
            val = next(results_and_onto.objects(base_info.validation_bn, SH.value))
            return ResultPatternViolation(
                res_iri=base_info.focus_node_iri,
                res_class=base_info.res_class_type,
                property=base_info.result_path,
                results_message=msg,
                actual_value=str(val),
            )
        case SH.MinCountConstraintComponent:
            return ResultMinCardinalityViolation(
                res_iri=base_info.focus_node_iri,
                res_class=base_info.res_class_type,
                property=base_info.result_path,
                results_message=msg,
            )
        case SH.MaxCountConstraintComponent:
            return ResultMaxCardinalityViolation(
                res_iri=base_info.focus_node_iri,
                res_class=base_info.res_class_type,
                property=base_info.result_path,
                results_message=msg,
            )
        case DASH.ClosedByTypesConstraintComponent:
            return ResultNonExistentCardinalityViolation(
                res_iri=base_info.focus_node_iri,
                res_class=base_info.res_class_type,
                property=base_info.result_path,
            )
        case _:
            return UnexpectedComponent(str(component))


def _query_all_with_detail(
    all_base_info: list[ValidationResultBaseInfo], results_and_onto: Graph, data_graph: Graph
) -> tuple[list[ValidationResult], list[UnexpectedComponent]]:
    extracted_results: list[ValidationResult] = []
    unexpected_components: list[UnexpectedComponent] = []

    for base_info in all_base_info:
        res = _query_one_with_detail(base_info, results_and_onto)
        if isinstance(res, UnexpectedComponent):
            unexpected_components.append(res)
        else:
            extracted_results.append(res)
    return extracted_results, unexpected_components


def _query_one_with_detail(
    base_info: ValidationResultBaseInfo, results_and_onto: Graph, data_graph: Graph
) -> ValidationResult | UnexpectedComponent:
    component = next(results_and_onto.objects(base_info.validation_bn, SH.sourceConstraintComponent))
    match component:
        case SH.MinCountConstraintComponent:
            return ResultValueTypeViolation

        case SH.PatternConstraintComponent:
            return ResultPatternViolation

        case SH.ClassConstraintComponent:
            return _query_one_class_constraint_component(base_info, results_and_onto, data_graph)

        case _:
            return UnexpectedComponent(str(component))
    """
    TODO:
    constraint component type
    - MinCount
    - Pattern
    - Class
        - source shape
            - None -> Link
            - Other -> ValueType
    - OTHER

    """

    path = next(results_and_onto.objects(base_info.validation_bn, SH.resultPath))
    value_iri = next(results_and_onto.objects(base_info.validation_bn, SH.value))
    value_type = next(data_graph.objects(value_iri, RDF.type))
    detail_component = next(results_and_onto.objects(base_info.detail_node, SH.sourceConstraintComponent))
    detail_path: None | Node = None
    if path_found := list(results_and_onto.objects(base_info.detail_node, SH.resultPath)):
        detail_path = path_found[0]
    val = None
    if node_value := list(results_and_onto.objects(base_info.detail_node, SH.value)):
        val = str(node_value[0])
    msg = str(next(results_and_onto.objects(base_info.detail_node, SH.resultMessage)))
    detail = ResultDetail(
        component=detail_component,
        results_message=msg,
        result_path=detail_path,
        value_type=value_type,
        value=val,
    )


def _query_one_class_constraint_component(
    base_info: ValidationResultBaseInfo, results_and_onto: Graph, data_graph: Graph
) -> ValidationResult | UnexpectedComponent:
    detail_component = list(results_and_onto.objects(base_info.detail_node, SH.sourceConstraintComponent))
    if detail_component:
        return ResultValueTypeViolation
    return _query_link_value_target_result()

def _query_link_value_target_result(base_info: ValidationResultBaseInfo, results_and_onto: Graph, data_graph: Graph):
    pass

def _reformat_validation_results(results: list[ValidationResult]) -> list[InputProblem]:
    pass


def _reformat_one_validation_result(validation_result: ValidationResult) -> InputProblem:
    pass


def _reformat_one_without_detail(violation: ResultWithoutDetail) -> InputProblem | UnexpectedComponent:
    # TODO: REMOVE
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


def _reformat_one_with_detail(val_result: ResultWithDetail) -> InputProblem | UnexpectedComponent:
    # TODO: REMOVE
    subject_id = _reformat_data_iri(str(val_result.res_iri))
    prop_name = _reformat_onto_iri(str(val_result.property))
    res_type = _reformat_onto_iri(str(val_result.res_class))
    match val_result.detail.component:
        case SH.PatternConstraintComponent:
            val: str | None = val_result.detail.value
            if val and not regex.search(r"\S+", val):
                val = None
            return ContentRegexViolation(
                res_id=subject_id,
                res_type=res_type,
                prop_name=prop_name,
                expected_format=val_result.detail.results_message,
                actual_content=val,
            )
        case SH.ClassConstraintComponent:
            return _reformat_detail_class_constraint_component(val_result)
        case SH.MinCountConstraintComponent:
            actual_type = _reformat_onto_iri(str(val_result.detail.value_type)).replace("knora-api:", "")
            return ValueTypeViolation(
                res_id=subject_id,
                res_type=res_type,
                prop_name=prop_name,
                actual_type=actual_type,
                expected_type=val_result.detail.results_message,
            )
        case _:
            return UnexpectedComponent(str(val_result.source_constraint_component))


def _reformat_detail_class_constraint_component(val_result: ResultWithDetail) -> InputProblem:
    # TODO: REMOVE
    subject_id = _reformat_data_iri(str(val_result.res_iri))
    prop_name = _reformat_onto_iri(str(val_result.property))
    res_type = _reformat_onto_iri(str(val_result.res_class))
    actual_type = _reformat_onto_iri(str(val_result.detail.value_type)).replace("knora-api:", "")
    match val_result.detail.result_path:
        case API_SHAPES.linkValueHasTargetID:
            value = _reformat_data_iri(str(val_result.detail.value))
            if val_result.detail.results_message == "Resource":
                return LinkedResourceDoesNotExist(
                    res_id=subject_id,
                    res_type=res_type,
                    prop_name=prop_name,
                    link_target_id=value,
                )
            return LinkTargetTypeMismatch(
                res_id=subject_id,
                res_type=res_type,
                prop_name=prop_name,
                link_target_id=value,
                expected_type=val_result.detail.results_message,
            )
        case _:
            return ValueTypeViolation(
                res_id=subject_id,
                res_type=res_type,
                prop_name=prop_name,
                actual_type=actual_type,
                expected_type=val_result.detail.results_message,
            )


def _reformat_onto_iri(prop: str) -> str:
    if "http://www.w3.org/2000/01/rdf-schema#" in prop:
        return f'rdfs:{prop.split("#")[-1]}'
    onto = prop.split("/")[-2]
    return f'{onto}:{prop.split("#")[-1]}'


def _reformat_data_iri(iri: str) -> str:
    return iri.replace("http://data/", "")
