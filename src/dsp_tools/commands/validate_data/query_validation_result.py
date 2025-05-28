from typing import cast

from loguru import logger
from rdflib import RDF
from rdflib import RDFS
from rdflib import SH
from rdflib import Graph
from rdflib import URIRef

from dsp_tools.commands.validate_data.constants import FILE_VALUE_PROPERTIES
from dsp_tools.commands.validate_data.constants import FILEVALUE_DETAIL_INFO
from dsp_tools.commands.validate_data.mappers import RESULT_TO_PROBLEM_MAPPER
from dsp_tools.commands.validate_data.models.input_problems import AllProblems
from dsp_tools.commands.validate_data.models.input_problems import InputProblem
from dsp_tools.commands.validate_data.models.input_problems import ProblemType
from dsp_tools.commands.validate_data.models.input_problems import Severity
from dsp_tools.commands.validate_data.models.validation import DetailBaseInfo
from dsp_tools.commands.validate_data.models.validation import QueryInfo
from dsp_tools.commands.validate_data.models.validation import ReformattedIRI
from dsp_tools.commands.validate_data.models.validation import UnexpectedComponent
from dsp_tools.commands.validate_data.models.validation import ValidationReportGraphs
from dsp_tools.commands.validate_data.models.validation import ValidationResult
from dsp_tools.commands.validate_data.models.validation import ValidationResultBaseInfo
from dsp_tools.commands.validate_data.models.validation import ViolationType
from dsp_tools.commands.validate_data.utils import reformat_any_iri
from dsp_tools.commands.validate_data.utils import reformat_data_iri
from dsp_tools.commands.validate_data.utils import reformat_onto_iri
from dsp_tools.error.exceptions import BaseError
from dsp_tools.utils.rdflib_constants import DASH
from dsp_tools.utils.rdflib_constants import KNORA_API
from dsp_tools.utils.rdflib_constants import SubjectObjectTypeAlias

LEGAL_INFO_PROPS = {KNORA_API.hasLicense, KNORA_API.hasCopyrightHolder, KNORA_API.hasAuthorship}


SEVERITY_MAPPER: dict[SubjectObjectTypeAlias, Severity] = {
    SH.Violation: Severity.VIOLATION,
    SH.Warning: Severity.WARNING,
    SH.Info: Severity.INFO,
}


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
    reformatted_results = _reformat_extracted_results(validation_results)
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
        case DASH.ClosedByTypesConstraintComponent:
            return _query_for_non_existent_cardinality_violation(base_info, results_and_onto)
        case SH.SPARQLConstraintComponent:
            return _query_for_unique_value_violation(base_info, results_and_onto)
        case DASH.CoExistsWithConstraintComponent:
            return ValidationResult(
                violation_type=ViolationType.SEQNUM_IS_PART_OF,
                res_iri=base_info.focus_node_iri,
                res_class=base_info.focus_node_type,
                severity=base_info.severity,
                message=msg,
            )
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
        case DASH.UniqueValueForClassConstraintComponent:
            return _query_general_violation_info(
                base_info.result_bn, base_info, results_and_onto, ViolationType.FILE_DUPLICATE
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


def _query_for_non_existent_cardinality_violation(
    base_info: ValidationResultBaseInfo, results_and_onto: Graph
) -> ValidationResult | None:
    # If a class is for example, an AudioRepresentation, but a jpg file is used,
    # the created value is of type StillImageFileValue.
    # This creates a min cardinality and a closed constraint violation.
    # The closed constraint we ignore, because the problem is communicated through the min cardinality violation.
    if base_info.result_path in FILE_VALUE_PROPERTIES:
        sub_classes = list(results_and_onto.transitive_objects(base_info.focus_node_type, RDFS.subClassOf))
        if KNORA_API.Representation in sub_classes:
            return None
        violation_type = ViolationType.FILEVALUE_PROHIBITED
    else:
        violation_type = ViolationType.NON_EXISTING_CARD

    return ValidationResult(
        violation_type=violation_type,
        res_iri=base_info.focus_node_iri,
        res_class=base_info.focus_node_type,
        severity=base_info.severity,
        property=base_info.result_path,
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
) -> ValidationResult:
    val = None
    if found_val := list(results_and_onto.objects(result_bn, SH.value)):
        val = found_val.pop()
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


def _query_for_link_value_target_violation(
    base_info: ValidationResultBaseInfo, results_and_onto: Graph, data_graph: Graph
) -> ValidationResult:
    detail_info = cast(DetailBaseInfo, base_info.detail)
    target_iri = next(results_and_onto.objects(detail_info.detail_bn, SH.value))
    target_rdf_type: SubjectObjectTypeAlias | None = None
    if target_type := list(data_graph.objects(target_iri, RDF.type)):
        target_rdf_type = target_type[0]
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


def _reformat_extracted_results(results: list[ValidationResult]) -> list[InputProblem]:
    return [_reformat_one_validation_result(x) for x in results]


def _reformat_one_validation_result(validation_result: ValidationResult) -> InputProblem:
    match validation_result.violation_type:
        case ViolationType.MIN_CARD:
            return _reformat_min_card(validation_result)
        case (
            ViolationType.MAX_CARD
            | ViolationType.NON_EXISTING_CARD
            | ViolationType.PATTERN
            | ViolationType.UNIQUE_VALUE
            | ViolationType.VALUE_TYPE as violation
        ):
            problem = RESULT_TO_PROBLEM_MAPPER[violation]
            return _reformat_generic(result=validation_result, problem_type=problem)
        case ViolationType.GENERIC:
            prop_str = None
            if validation_result.property in LEGAL_INFO_PROPS or validation_result.property in FILE_VALUE_PROPERTIES:
                prop_str = "bitstream / iiif-uri"
            return _reformat_generic(validation_result, ProblemType.GENERIC, prop_string=prop_str)
        case ViolationType.FILEVALUE_PROHIBITED | ViolationType.FILE_VALUE | ViolationType.FILE_DUPLICATE as violation:
            problem = RESULT_TO_PROBLEM_MAPPER[violation]
            return _reformat_generic(result=validation_result, problem_type=problem, prop_string="bitstream / iiif-uri")
        case ViolationType.SEQNUM_IS_PART_OF:
            return _reformat_generic(
                result=validation_result, problem_type=ProblemType.GENERIC, prop_string="seqnum or isPartOf"
            )
        case ViolationType.LINK_TARGET:
            return _reformat_link_target_violation_result(validation_result)
        case _:
            raise BaseError(f"An unknown violation result was found: {validation_result.__class__.__name__}")


def _reformat_min_card(result: ValidationResult) -> InputProblem:
    iris = _reformat_main_iris(result)
    if file_prop_info := FILEVALUE_DETAIL_INFO.get(cast(URIRef, result.property)):
        prop_str, file_extensions = file_prop_info
        detail_msg = None
        problem_type = ProblemType.FILE_VALUE
        expected: str | None = f"This resource requires a file with one of the following extensions: {file_extensions}"
    else:
        prop_str = iris.prop_name
        detail_msg = _convert_rdflib_input_to_string(result.message)
        problem_type = ProblemType.MIN_CARD
        expected = _convert_rdflib_input_to_string(result.expected)

    return InputProblem(
        problem_type=problem_type,
        res_id=iris.res_id,
        res_type=iris.res_type,
        prop_name=prop_str,
        severity=SEVERITY_MAPPER[result.severity],
        message=detail_msg,
        input_value=_convert_rdflib_input_to_string(result.input_value),
        input_type=_convert_rdflib_input_to_string(result.input_type),
        expected=expected,
    )


def _reformat_generic(
    result: ValidationResult, problem_type: ProblemType, prop_string: str | None = None
) -> InputProblem:
    iris = _reformat_main_iris(result)
    user_prop = iris.prop_name if not prop_string else prop_string
    return InputProblem(
        problem_type=problem_type,
        res_id=iris.res_id,
        res_type=iris.res_type,
        prop_name=user_prop,
        severity=SEVERITY_MAPPER[result.severity],
        message=_convert_rdflib_input_to_string(result.message),
        input_value=_convert_rdflib_input_to_string(result.input_value),
        input_type=_convert_rdflib_input_to_string(result.input_type),
        expected=_convert_rdflib_input_to_string(result.expected),
    )


def _reformat_link_target_violation_result(result: ValidationResult) -> InputProblem:
    iris = _reformat_main_iris(result)
    input_type = None
    expected = None
    problem_type = ProblemType.INEXISTENT_LINKED_RESOURCE

    if result.input_type:
        problem_type = ProblemType.LINK_TARGET_TYPE_MISMATCH
        input_type = reformat_onto_iri(str(result.input_type))
        expected = reformat_onto_iri(str(result.expected))

    return InputProblem(
        problem_type=problem_type,
        res_id=iris.res_id,
        res_type=iris.res_type,
        prop_name=iris.prop_name,
        severity=SEVERITY_MAPPER[result.severity],
        input_value=reformat_data_iri(str(result.input_value)),
        input_type=input_type,
        expected=expected,
    )


def _reformat_main_iris(result: ValidationResult) -> ReformattedIRI:
    subject_id = reformat_data_iri(result.res_iri)
    prop_name = reformat_onto_iri(result.property) if result.property else ""
    res_type = reformat_onto_iri(result.res_class)
    return ReformattedIRI(res_id=subject_id, res_type=res_type, prop_name=prop_name)


def _convert_rdflib_input_to_string(input_val: SubjectObjectTypeAlias | None) -> str | None:
    if not input_val:
        return None
    if isinstance(input_val, URIRef):
        return reformat_any_iri(input_val)
    return str(input_val)
