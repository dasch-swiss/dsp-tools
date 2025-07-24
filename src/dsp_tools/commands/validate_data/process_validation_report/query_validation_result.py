from typing import cast

from loguru import logger
from rdflib import RDF
from rdflib import RDFS
from rdflib import SH
from rdflib import XSD
from rdflib import Graph
from rdflib import Literal

from dsp_tools.commands.validate_data.constants import FILE_VALUE_PROPERTIES
from dsp_tools.commands.validate_data.constants import LEGAL_INFO_PROPS
from dsp_tools.commands.validate_data.models.input_problems import AllProblems
from dsp_tools.commands.validate_data.models.validation import DetailBaseInfo
from dsp_tools.commands.validate_data.models.validation import QueryInfo
from dsp_tools.commands.validate_data.models.validation import UnexpectedComponent
from dsp_tools.commands.validate_data.models.validation import ValidationReportGraphs
from dsp_tools.commands.validate_data.models.validation import ValidationResult
from dsp_tools.commands.validate_data.models.validation import ValidationResultBaseInfo
from dsp_tools.commands.validate_data.models.validation import ViolationType
from dsp_tools.commands.validate_data.process_validation_report.reformat_validation_results import (
    reformat_extracted_results,
)
from dsp_tools.utils.rdflib_constants import API_SHAPES
from dsp_tools.utils.rdflib_constants import DASH
from dsp_tools.utils.rdflib_constants import KNORA_API
from dsp_tools.utils.rdflib_constants import SubjectObjectTypeAlias


def reformat_validation_graph(report: ValidationReportGraphs) -> AllProblems:
    """
    Reformats the validation result from an RDF graph into class instances
    that are used to communicate the problems with the user.

    Args:
        report: with all the information necessary to construct a user message

    Returns:
        All Problems
    """
    logger.debug("Reformatting validation results.")
    results_and_onto = report.validation_graph + report.onto_graph
    data_and_onto = report.onto_graph + report.data_graph
    validation_results, unexpected_extracted = _query_all_results(results_and_onto, data_and_onto)
    reformatted_results = reformat_extracted_results(validation_results)
    return AllProblems(reformatted_results, unexpected_extracted)


def _query_all_results(
    results_and_onto: Graph, data_onto_graph: Graph
) -> tuple[list[ValidationResult], list[UnexpectedComponent]]:
    no_details, with_details = _separate_result_types(results_and_onto, data_onto_graph)
    extracted_results: list[ValidationResult] = []
    unexpected_components: list[UnexpectedComponent] = []

    no_detail_extracted, no_detail_unexpected = _query_all_without_detail(no_details, results_and_onto, data_onto_graph)
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
    all_res_focus_nodes = []
    main_bns = _get_all_main_result_bns(results_and_onto)
    value_types = _get_all_value_classes(data_onto_graph)
    for nd in main_bns:
        focus_iri = next(results_and_onto.objects(nd, SH.focusNode))
        res_type = next(data_onto_graph.objects(focus_iri, RDF.type))
        info = QueryInfo(
            validation_bn=nd,
            focus_iri=focus_iri,
            focus_rdf_type=res_type,
        )
        all_res_focus_nodes.extend(_extract_one_base_info(info, results_and_onto, data_onto_graph, value_types))
    return all_res_focus_nodes


def _get_all_value_classes(data_onto_graph: Graph) -> set[SubjectObjectTypeAlias]:
    all_types = set(data_onto_graph.objects(predicate=RDF.type))
    all_value_types = set()
    for type_ in all_types:
        super_classes = set(data_onto_graph.transitive_objects(type_, RDFS.subClassOf))
        if KNORA_API.Value in super_classes:
            all_value_types.add(type_)
    return all_value_types


def _extract_one_base_info(
    info: QueryInfo, results_and_onto: Graph, data_onto_graph: Graph, value_types: set[SubjectObjectTypeAlias]
) -> list[ValidationResultBaseInfo]:
    results = []
    path = next(results_and_onto.objects(info.validation_bn, SH.resultPath))
    main_component_type = next(results_and_onto.objects(info.validation_bn, SH.sourceConstraintComponent))
    severity = next(results_and_onto.objects(info.validation_bn, SH.resultSeverity))
    if detail_bn_list := list(results_and_onto.objects(info.validation_bn, SH.detail)):
        for single_detail in detail_bn_list:
            detail_component = next(results_and_onto.objects(single_detail, SH.sourceConstraintComponent))
            detail = DetailBaseInfo(
                detail_bn=single_detail,
                source_constraint_component=detail_component,
            )
            results.append(
                ValidationResultBaseInfo(
                    result_bn=info.validation_bn,
                    source_constraint_component=main_component_type,
                    focus_node_iri=info.focus_iri,
                    focus_node_type=info.focus_rdf_type,
                    result_path=path,
                    severity=severity,
                    detail=detail,
                )
            )
    else:
        resource_iri, resource_type, user_facing_prop = _get_resource_iri_and_type(
            info, path, data_onto_graph, value_types
        )
        results.append(
            ValidationResultBaseInfo(
                result_bn=info.validation_bn,
                source_constraint_component=main_component_type,
                focus_node_iri=resource_iri,
                focus_node_type=resource_type,
                result_path=user_facing_prop,
                severity=severity,
                detail=None,
            )
        )
    return results


def _get_all_main_result_bns(results_and_onto: Graph) -> set[SubjectObjectTypeAlias]:
    all_bns = set(results_and_onto.subjects(RDF.type, SH.ValidationResult))
    # All the blank nodes that are referenced in a sh:detail will be queried together with the main validation result
    # if we queried them separately we would get duplicate errors
    detail_bns = set(results_and_onto.objects(predicate=SH.detail))
    return all_bns - detail_bns


def _get_resource_iri_and_type(
    info: QueryInfo, path: SubjectObjectTypeAlias, data_onto_graph: Graph, value_types: set[SubjectObjectTypeAlias]
) -> tuple[SubjectObjectTypeAlias, SubjectObjectTypeAlias, SubjectObjectTypeAlias]:
    resource_iri, resource_type, user_facing_prop = info.focus_iri, info.focus_rdf_type, path
    if info.focus_rdf_type in value_types:
        resource_iri, predicate = next(data_onto_graph.subject_predicates(object=info.focus_iri))
        resource_type = next(data_onto_graph.objects(resource_iri, RDF.type))
        if user_facing_prop not in LEGAL_INFO_PROPS:
            user_facing_prop = predicate
    return resource_iri, resource_type, user_facing_prop


def _query_all_without_detail(
    all_base_info: list[ValidationResultBaseInfo], results_and_onto: Graph, data: Graph
) -> tuple[list[ValidationResult], list[UnexpectedComponent]]:
    extracted_results: list[ValidationResult] = []
    unexpected_components: list[UnexpectedComponent] = []

    for base_info in all_base_info:
        res = _query_one_without_detail(base_info, results_and_onto, data)
        if res is None:
            pass
        elif isinstance(res, UnexpectedComponent):
            unexpected_components.append(res)
        else:
            extracted_results.append(res)
    return extracted_results, unexpected_components


def _query_one_without_detail(  # noqa:PLR0911 (Too many return statements)
    base_info: ValidationResultBaseInfo, results_and_onto: Graph, data: Graph
) -> ValidationResult | UnexpectedComponent | None:
    msg = next(results_and_onto.objects(base_info.result_bn, SH.resultMessage))
    component = next(results_and_onto.objects(base_info.result_bn, SH.sourceConstraintComponent))
    match component:
        case SH.PatternConstraintComponent:
            return _query_pattern_constraint_component_violation(base_info.result_bn, base_info, results_and_onto)
        case SH.MinCountConstraintComponent:
            return _query_for_min_cardinality_violation(base_info, msg)
        case SH.MaxCountConstraintComponent:
            return ValidationResult(
                violation_type=ViolationType.MAX_CARD,
                res_iri=base_info.focus_node_iri,
                res_class=base_info.focus_node_type,
                severity=base_info.severity,
                property=base_info.result_path,
                expected=msg,
            )
        case SH.LessThanOrEqualsConstraintComponent:
            return _query_for_less_than_or_equal_violation(base_info, results_and_onto, data, msg)
        case DASH.ClosedByTypesConstraintComponent:
            return _query_for_non_existent_cardinality_violation(base_info, results_and_onto, data)
        case SH.SPARQLConstraintComponent:
            return _query_for_unique_value_violation(base_info, results_and_onto)
        case DASH.CoExistsWithConstraintComponent:
            return _query_for_coexists_with_violation(base_info, results_and_onto, data, msg)
        case SH.ClassConstraintComponent:
            return _query_class_constraint_without_detail(base_info, results_and_onto, data, msg)
        case (
            SH.InConstraintComponent
            | SH.LessThanConstraintComponent
            | SH.MinExclusiveConstraintComponent
            | SH.MinInclusiveConstraintComponent
            | DASH.SingleLineConstraintComponent
        ):
            return _query_general_violation_info(
                base_info.result_bn, base_info, results_and_onto, ViolationType.GENERIC
            )
        case SH.OrConstraintComponent:
            return _query_general_violation_info_with_value_as_string(
                base_info.result_bn, base_info, results_and_onto, data
            )
        case _:
            return UnexpectedComponent(str(component))


def _query_class_constraint_without_detail(
    base_info: ValidationResultBaseInfo, results_and_onto: Graph, data: Graph, message: SubjectObjectTypeAlias
) -> ValidationResult | None:
    val: None | SubjectObjectTypeAlias = next(results_and_onto.objects(base_info.result_bn, SH.value))
    # In this case we have some kind of FileValue violation
    violation_type = ViolationType.GENERIC
    value_type: None | SubjectObjectTypeAlias = None
    msg: None | SubjectObjectTypeAlias = message
    expected = None
    val_type_list = list(data.objects(val, RDF.type))
    # Here we have a normal value type violation
    if val_type_list:
        val_type = val_type_list.pop(0)
        value_super_class = list(results_and_onto.transitive_objects(val_type, RDFS.subClassOf))
        if KNORA_API.FileValue not in value_super_class:
            value_type = val_type
            val = None
            violation_type = ViolationType.VALUE_TYPE
            msg = None
            expected = message
    elif base_info.result_path == KNORA_API.hasStandoffLinkTo:
        violation_type = ViolationType.LINK_TARGET
    return ValidationResult(
        violation_type=violation_type,
        res_iri=base_info.focus_node_iri,
        res_class=base_info.focus_node_type,
        severity=base_info.severity,
        property=base_info.result_path,
        message=msg,
        expected=expected,
        input_value=val,
        input_type=value_type,
    )


def _query_for_less_than_or_equal_violation(
    base_info: ValidationResultBaseInfo, results_and_onto: Graph, data: Graph, message: SubjectObjectTypeAlias
) -> ValidationResult | None:
    value_iri = next(results_and_onto.objects(base_info.result_bn, SH.focusNode))
    start = next(data.objects(value_iri, API_SHAPES.dateHasStart))
    end = next(data.objects(value_iri, API_SHAPES.dateHasEnd))
    start_lit = cast(Literal, start)
    end_lit = cast(Literal, end)
    start_is_string = start_lit.datatype == XSD.string
    end_is_string = end_lit.datatype == XSD.string
    # If any one of the date ranges cannot be parsed as an xsd date, we get this violation also.
    # But the main problem is, that the date format is wrong, in which case the datatype is xsd:string.
    # This produces its own message
    if any([start_is_string, end_is_string]):
        return None
    return ValidationResult(
        violation_type=ViolationType.GENERIC,
        res_iri=base_info.focus_node_iri,
        res_class=base_info.focus_node_type,
        severity=base_info.severity,
        property=base_info.result_path,
        input_value=_get_value_as_string(base_info.result_bn, results_and_onto, data),
        message=message,
    )


def _query_for_non_existent_cardinality_violation(
    base_info: ValidationResultBaseInfo, results_and_onto: Graph, data: Graph
) -> ValidationResult | None:
    input_val = None
    if base_info.result_path in FILE_VALUE_PROPERTIES:
        violation_type = ViolationType.FILE_VALUE_PROHIBITED
        if value_bn_found := list(results_and_onto.objects(base_info.result_bn, SH.value)):
            value_bn = value_bn_found.pop(0)
            if file_path := list(data.objects(value_bn, KNORA_API.fileValueHasFilename)):
                input_val = file_path.pop(0)
            elif iiif_uri := list(data.objects(value_bn, KNORA_API.stillImageFileValueHasExternalUrl)):
                input_val = iiif_uri.pop(0)
    else:
        violation_type = ViolationType.NON_EXISTING_CARD
    return ValidationResult(
        violation_type=violation_type,
        res_iri=base_info.focus_node_iri,
        res_class=base_info.focus_node_type,
        severity=base_info.severity,
        property=base_info.result_path,
        input_value=input_val,
    )


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
    detail_info = cast(DetailBaseInfo, base_info.detail)
    match detail_info.source_constraint_component:
        case SH.MinCountConstraintComponent:
            if base_info.result_path in FILE_VALUE_PROPERTIES:
                return _query_general_violation_info(
                    base_info.result_bn, base_info, results_and_onto, ViolationType.GENERIC
                )
            return _query_for_value_type_violation(base_info, results_and_onto, data_graph)
        case SH.PatternConstraintComponent:
            return _query_pattern_constraint_component_violation(detail_info.detail_bn, base_info, results_and_onto)
        case SH.ClassConstraintComponent:
            return _query_class_constraint_component_violation(base_info, results_and_onto, data_graph)
        case SH.InConstraintComponent | DASH.SingleLineConstraintComponent:
            detail = cast(DetailBaseInfo, base_info.detail)
            return _query_general_violation_info(detail.detail_bn, base_info, results_and_onto, ViolationType.GENERIC)
        case _:
            return UnexpectedComponent(str(detail_info.source_constraint_component))


def _query_class_constraint_component_violation(
    base_info: ValidationResultBaseInfo, results_and_onto: Graph, data_graph: Graph
) -> ValidationResult | UnexpectedComponent:
    detail_info = cast(DetailBaseInfo, base_info.detail)
    detail_path = next(results_and_onto.objects(detail_info.detail_bn, SH.resultPath))
    if detail_path == RDF.type:
        return _query_for_value_type_violation(base_info, results_and_onto, data_graph)
    return _query_for_link_value_target_violation(base_info, results_and_onto, data_graph)


def _query_for_value_type_violation(
    base_info: ValidationResultBaseInfo, results_and_onto: Graph, data_graph: Graph
) -> ValidationResult:
    detail_info = cast(DetailBaseInfo, base_info.detail)
    msg = next(results_and_onto.objects(detail_info.detail_bn, SH.resultMessage))
    val = next(results_and_onto.objects(base_info.result_bn, SH.value))
    val_type = next(data_graph.objects(val, RDF.type))
    return ValidationResult(
        violation_type=ViolationType.VALUE_TYPE,
        res_iri=base_info.focus_node_iri,
        res_class=base_info.focus_node_type,
        severity=base_info.severity,
        property=base_info.result_path,
        expected=msg,
        input_type=val_type,
    )


def _query_pattern_constraint_component_violation(
    bn_with_info: SubjectObjectTypeAlias, base_info: ValidationResultBaseInfo, results_and_onto: Graph
) -> ValidationResult:
    val = next(results_and_onto.objects(bn_with_info, SH.value))
    msg = next(results_and_onto.objects(bn_with_info, SH.resultMessage))
    return ValidationResult(
        violation_type=ViolationType.PATTERN,
        res_iri=base_info.focus_node_iri,
        res_class=base_info.focus_node_type,
        severity=base_info.severity,
        property=base_info.result_path,
        expected=msg,
        input_value=val,
    )


def _query_general_violation_info(
    result_bn: SubjectObjectTypeAlias,
    base_info: ValidationResultBaseInfo,
    results_and_onto: Graph,
    violation_type: ViolationType,
    value: SubjectObjectTypeAlias | None = None,
) -> ValidationResult:
    if not value:
        val = next(results_and_onto.objects(result_bn, SH.value), None)
    else:
        val = value
    msg = next(results_and_onto.objects(result_bn, SH.resultMessage))
    return ValidationResult(
        violation_type=violation_type,
        res_iri=base_info.focus_node_iri,
        res_class=base_info.focus_node_type,
        severity=base_info.severity,
        property=base_info.result_path,
        message=msg,
        input_value=val,
    )


def _query_general_violation_info_with_value_as_string(
    result_bn: SubjectObjectTypeAlias,
    base_info: ValidationResultBaseInfo,
    results_and_onto: Graph,
    data: Graph,
) -> ValidationResult:
    value_iri = next(results_and_onto.objects(result_bn, SH.focusNode))
    value = next(data.objects(value_iri, KNORA_API.valueAsString))
    return _query_general_violation_info(result_bn, base_info, results_and_onto, ViolationType.GENERIC, value)


def _query_for_link_value_target_violation(
    base_info: ValidationResultBaseInfo, results_and_onto: Graph, data_graph: Graph
) -> ValidationResult:
    detail_info = cast(DetailBaseInfo, base_info.detail)
    target_iri = next(results_and_onto.objects(detail_info.detail_bn, SH.value))
    target_rdf_type = next(data_graph.objects(target_iri, RDF.type), None)
    expected_type = next(results_and_onto.objects(detail_info.detail_bn, SH.resultMessage))
    return ValidationResult(
        violation_type=ViolationType.LINK_TARGET,
        res_iri=base_info.focus_node_iri,
        res_class=base_info.focus_node_type,
        severity=base_info.severity,
        property=base_info.result_path,
        expected=expected_type,
        input_value=target_iri,
        input_type=target_rdf_type,
    )


def _query_for_min_cardinality_violation(
    base_info: ValidationResultBaseInfo, msg: SubjectObjectTypeAlias
) -> ValidationResult:
    if base_info.result_path in LEGAL_INFO_PROPS:
        violation_type = ViolationType.GENERIC
    else:
        violation_type = ViolationType.MIN_CARD
    return ValidationResult(
        violation_type=violation_type,
        res_iri=base_info.focus_node_iri,
        res_class=base_info.focus_node_type,
        severity=base_info.severity,
        property=base_info.result_path,
        expected=msg,
    )


def _query_for_unique_value_violation(
    base_info: ValidationResultBaseInfo,
    results_and_onto: Graph,
) -> ValidationResult:
    val = next(results_and_onto.objects(base_info.result_bn, SH.value))
    return ValidationResult(
        violation_type=ViolationType.UNIQUE_VALUE,
        res_iri=base_info.focus_node_iri,
        res_class=base_info.focus_node_type,
        severity=base_info.severity,
        property=base_info.result_path,
        input_value=val,
    )


def _query_for_coexists_with_violation(
    base_info: ValidationResultBaseInfo, results_and_onto: Graph, data: Graph, message: SubjectObjectTypeAlias
) -> ValidationResult:
    source_shapes = next(results_and_onto.objects(base_info.result_bn, SH.sourceShape))
    if source_shapes == API_SHAPES.seqnum_PropShape:
        violation_type = ViolationType.SEQNUM_IS_PART_OF
        value = None
        prop = None
    else:
        violation_type = ViolationType.GENERIC
        value = _get_value_as_string(base_info.result_bn, results_and_onto, data)
        prop = base_info.result_path
    return ValidationResult(
        violation_type=violation_type,
        res_iri=base_info.focus_node_iri,
        res_class=base_info.focus_node_type,
        property=prop,
        severity=base_info.severity,
        message=message,
        input_value=value,
    )


def _get_value_as_string(result_bn: SubjectObjectTypeAlias, results: Graph, data: Graph) -> SubjectObjectTypeAlias:
    value_iri = next(results.objects(result_bn, SH.focusNode))
    return next(data.objects(value_iri, KNORA_API.valueAsString))
