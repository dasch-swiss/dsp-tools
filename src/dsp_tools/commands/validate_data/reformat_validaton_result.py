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
from dsp_tools.commands.validate_data.models.validation import DetailBaseInfo
from dsp_tools.commands.validate_data.models.validation import ExtractedResultDetail
from dsp_tools.commands.validate_data.models.validation import ExtractedResultWithDetail
from dsp_tools.commands.validate_data.models.validation import QueryInfo
from dsp_tools.commands.validate_data.models.validation import ResultLinkTargetViolation
from dsp_tools.commands.validate_data.models.validation import ResultMaxCardinalityViolation
from dsp_tools.commands.validate_data.models.validation import ResultMinCardinalityViolation
from dsp_tools.commands.validate_data.models.validation import ResultNonExistentCardinalityViolation
from dsp_tools.commands.validate_data.models.validation import ResultPatternViolation
from dsp_tools.commands.validate_data.models.validation import ResultValueTypeViolation
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
    reformatted_results: list[InputProblem] = _reformat_extracted_results(validation_results)

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
    no_details = [x for x in base_info if not x.detail]
    with_details = [x for x in base_info if x.detail]
    return no_details, with_details


def _extract_base_info_of_resource_results(
    results_and_onto: Graph, data_onto_graph: Graph
) -> list[ValidationResultBaseInfo]:
    focus_nodes = list(results_and_onto.subject_objects(SH.focusNode))
    resource_classes = list(data_onto_graph.subjects(KNORA_API.canBeInstantiated, Literal(True)))
    all_res_focus_nodes = []
    for nd in focus_nodes:
        focus_iri = nd[1]
        res_type = next(data_onto_graph.objects(focus_iri, RDF.type))
        if res_type in resource_classes:
            info = QueryInfo(
                validation_bn=nd[0],
                focus_iri=focus_iri,
                focus_rdf_type=res_type,
            )
            all_res_focus_nodes.append(_extract_one_base_info(info, results_and_onto))
    return all_res_focus_nodes


def _extract_one_base_info(info: QueryInfo, results_and_onto: Graph) -> ValidationResultBaseInfo:
    path = next(results_and_onto.objects(info.validation_bn, SH.resultPath))
    main_component_type = next(results_and_onto.objects(info.validation_bn, SH.sourceConstraintComponent))
    detail = None
    if detail_bn_list := list(results_and_onto.objects(info.validation_bn, SH.detail)):
        detail_bn = detail_bn_list[0]
        detail_component = next(results_and_onto.objects(detail_bn, SH.sourceConstraintComponent))
        detail = DetailBaseInfo(
            detail_bn=detail_bn,
            source_constraint_component=detail_component,
        )
    return ValidationResultBaseInfo(
        result_bn=info.validation_bn,
        source_constraint_component=main_component_type,
        resource_iri=info.focus_iri,
        res_class_type=info.focus_rdf_type,
        result_path=path,
        detail=detail,
    )


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
    msg = str(next(results_and_onto.objects(base_info.result_bn, SH.resultMessage)))
    component = next(results_and_onto.objects(base_info.result_bn, SH.sourceConstraintComponent))
    match component:
        case SH.PatternConstraintComponent:
            return _query_pattern_constraint_component_violation(base_info, results_and_onto)
        case SH.MinCountConstraintComponent:
            return ResultMinCardinalityViolation(
                res_iri=base_info.resource_iri,
                res_class=base_info.res_class_type,
                property=base_info.result_path,
                results_message=msg,
            )
        case SH.MaxCountConstraintComponent:
            return ResultMaxCardinalityViolation(
                res_iri=base_info.resource_iri,
                res_class=base_info.res_class_type,
                property=base_info.result_path,
                results_message=msg,
            )
        case DASH.ClosedByTypesConstraintComponent:
            return ResultNonExistentCardinalityViolation(
                res_iri=base_info.resource_iri,
                res_class=base_info.res_class_type,
                property=base_info.result_path,
            )
        case _:
            return UnexpectedComponent(str(component))


def _query_all_with_detail(
    all_base_info: list[ValidationResultBaseInfo], results_and_onto: Graph, data_onto_graph: Graph
) -> tuple[list[ValidationResult], list[UnexpectedComponent]]:
    extracted_results: list[ValidationResult] = []
    unexpected_components: list[UnexpectedComponent] = []

    for base_info in all_base_info:
        res = _query_one_with_detail(base_info, results_and_onto, data_onto_graph)
        if isinstance(res, UnexpectedComponent):
            unexpected_components.append(res)
        else:
            extracted_results.append(res)
    return extracted_results, unexpected_components


def _query_one_with_detail(
    base_info: ValidationResultBaseInfo, results_and_onto: Graph, data_graph: Graph
) -> ValidationResult | UnexpectedComponent:
    match base_info.detail.source_constraint_component:
        case SH.MinCountConstraintComponent:
            return _query_for_value_type_violation(base_info, results_and_onto, data_graph)
        case SH.PatternConstraintComponent:
            return _query_pattern_constraint_component_violation(base_info, results_and_onto)
        case SH.ClassConstraintComponent:
            return _query_class_constraint_component_violation(base_info, results_and_onto, data_graph)
        case _:
            return UnexpectedComponent(str(base_info.detail.source_constraint_component))


def _query_class_constraint_component_violation(
    base_info: ValidationResultBaseInfo, results_and_onto: Graph, data_graph: Graph
) -> ValidationResult | UnexpectedComponent:
    detail_component = list(results_and_onto.objects(base_info.detail.detail_bn, SH.sourceConstraintComponent))
    if detail_component:
        return _query_for_value_type_violation(base_info, results_and_onto, data_graph)
    return _query_for_link_value_target_violation(base_info, results_and_onto, data_graph)


def _query_for_value_type_violation(
    base_info: ValidationResultBaseInfo, results_and_onto: Graph, data_graph: Graph
) -> ResultValueTypeViolation:
    msg = next(results_and_onto.objects(base_info.detail.detail_bn, SH.resultMessage))
    val = next(results_and_onto.objects(base_info.result_bn, SH.value))
    val_type = next(data_graph.objects(val, RDF.type))
    return ResultValueTypeViolation(
        res_iri=base_info.resource_iri,
        res_class=base_info.res_class_type,
        property=base_info.result_path,
        results_message=str(msg),
        actual_value_type=val_type,
    )


def _query_pattern_constraint_component_violation(
    base_info: ValidationResultBaseInfo, results_and_onto: Graph
) -> ResultPatternViolation:
    val = next(results_and_onto.objects(base_info.result_bn, SH.value))
    msg = str(next(results_and_onto.objects(base_info.result_bn, SH.resultMessage)))
    return ResultPatternViolation(
        res_iri=base_info.resource_iri,
        res_class=base_info.res_class_type,
        property=base_info.result_path,
        results_message=msg,
        actual_value=str(val),
    )


def _query_for_link_value_target_violation(
    base_info: ValidationResultBaseInfo, results_and_onto: Graph, data_graph: Graph
) -> ResultLinkTargetViolation:
    target_iri = next(results_and_onto.objects(base_info.detail.detail_bn, SH.value))
    target_rdf_type: Node | None = None
    if target_type := list(data_graph.objects(target_iri, RDF.type)):
        target_rdf_type = target_type[0]
    msg = next(results_and_onto.objects(base_info.detail.detail_bn, SH.resultMessage))
    return ResultLinkTargetViolation(
        res_iri=base_info.resource_iri,
        res_class=base_info.res_class_type,
        property=base_info.result_path,
        results_message=str(msg),
        target_id=target_iri,
        target_resource_type=target_rdf_type,
    )


def _reformat_extracted_results(results: list[ValidationResult]) -> list[InputProblem]:
    pass


def _reformat_one_validation_result(validation_result: ValidationResult) -> InputProblem:
    pass


def _reformat_one_without_detail(violation: ExtractedResultDetail) -> InputProblem | UnexpectedComponent:
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


def _reformat_one_with_detail(val_result: ExtractedResultWithDetail) -> InputProblem | UnexpectedComponent:
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


def _reformat_detail_class_constraint_component(val_result: ExtractedResultWithDetail) -> InputProblem:
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
