from typing import cast

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
from dsp_tools.commands.validate_data.models.validation import ExtractedResultWithoutDetail
from dsp_tools.commands.validate_data.models.validation import QueryInfo
from dsp_tools.commands.validate_data.models.validation import UnexpectedComponent
from dsp_tools.commands.validate_data.models.validation import ValidationReport
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
) -> tuple[list[ExtractedResultWithoutDetail], list[ExtractedResultWithDetail]]:
    all_base_info = _extract_base_info_of_resource_results(results_and_onto, data_onto_graph)
    no_details = [x for x in all_base_info if not x.detail]
    no_detail_results = [_query_without_detail(x, results_and_onto) for x in no_details]
    with_details = [x for x in all_base_info if x.detail]
    details_results = [_query_with_detail(x, results_and_onto, data_onto_graph) for x in with_details]
    return no_detail_results, details_results


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


def _query_without_detail(base_info: ValidationResultBaseInfo, results_and_onto: Graph) -> ExtractedResultWithoutDetail:
    msg = str(next(results_and_onto.objects(base_info.result_bn, SH.resultMessage)))
    res_value: str | None = None
    if val := list(results_and_onto.objects(base_info.result_bn, SH.value)):
        res_value = str(val[0])
    return ExtractedResultWithoutDetail(
        source_constraint_component=base_info.source_constraint_component,
        res_iri=base_info.resource_iri,
        res_class=base_info.res_class_type,
        property=base_info.result_path,
        results_message=msg,
        value=res_value,
    )


def _query_with_detail(
    base_info: ValidationResultBaseInfo, results_and_onto: Graph, data_graph: Graph
) -> ExtractedResultWithDetail:
    detail_info = cast(DetailBaseInfo, base_info.detail)
    value_iri = next(results_and_onto.objects(base_info.result_bn, SH.value))
    value_type = next(data_graph.objects(value_iri, RDF.type))
    detail_path: None | Node = None
    if path_found := list(results_and_onto.objects(detail_info.detail_bn, SH.resultPath)):
        detail_path = path_found[0]
    val = None
    if node_value := list(results_and_onto.objects(detail_info.detail_bn, SH.value)):
        val = str(node_value[0])
    msg = str(next(results_and_onto.objects(detail_info.detail_bn, SH.resultMessage)))
    detail = ExtractedResultDetail(
        component=detail_info.source_constraint_component,
        results_message=msg,
        result_path=detail_path,
        value_type=value_type,
        value=val,
    )
    return ExtractedResultWithDetail(
        source_constraint_component=base_info.source_constraint_component,
        res_iri=base_info.resource_iri,
        res_class=base_info.res_class_type,
        property=base_info.result_path,
        detail=detail,
    )


def _reformat_without_detail(
    validation_results: list[ExtractedResultWithoutDetail],
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


def _reformat_one_without_detail(violation: ExtractedResultWithoutDetail) -> InputProblem | UnexpectedComponent:
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
    validation_results: list[ExtractedResultWithDetail],
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


def _reformat_one_with_detail(val_result: ExtractedResultWithDetail) -> InputProblem | UnexpectedComponent:
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
