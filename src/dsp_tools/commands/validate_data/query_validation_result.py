from typing import cast

from loguru import logger
from rdflib import RDF
from rdflib import RDFS
from rdflib import SH
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.commands.validate_data.constants import DASH
from dsp_tools.commands.validate_data.constants import FILE_VALUE_PROP_SHAPES
from dsp_tools.commands.validate_data.constants import FILE_VALUE_PROPERTIES
from dsp_tools.commands.validate_data.constants import KNORA_API
from dsp_tools.commands.validate_data.constants import VALUE_CLASS_SHAPES
from dsp_tools.commands.validate_data.constants import SubjectObjectTypeAlias
from dsp_tools.commands.validate_data.mappers import RESULT_TO_PROBLEM_MAPPER
from dsp_tools.commands.validate_data.models.input_problems import AllProblems
from dsp_tools.commands.validate_data.models.input_problems import InputProblem
from dsp_tools.commands.validate_data.models.input_problems import ProblemType
from dsp_tools.commands.validate_data.models.input_problems import UnexpectedResults
from dsp_tools.commands.validate_data.models.validation import DetailBaseInfo
from dsp_tools.commands.validate_data.models.validation import QueryInfo
from dsp_tools.commands.validate_data.models.validation import ReformattedIRI
from dsp_tools.commands.validate_data.models.validation import UnexpectedComponent
from dsp_tools.commands.validate_data.models.validation import ValidationReportGraphs
from dsp_tools.commands.validate_data.models.validation import ValidationResult
from dsp_tools.commands.validate_data.models.validation import ValidationResultBaseInfo
from dsp_tools.commands.validate_data.models.validation import ViolationType
from dsp_tools.commands.validate_data.utils import reformat_data_iri
from dsp_tools.commands.validate_data.utils import reformat_onto_iri
from dsp_tools.models.exceptions import BaseError


def reformat_validation_graph(report: ValidationReportGraphs) -> AllProblems:
    """
    Reformats the validation result from an RDF graph into class instances
    that are used to communicate the problems with the user.

    Args:
        report: with all the information necessary to construct a user message

    Returns:
        All Problems
    """
    logger.info("Reformatting validation results.")
    results_and_onto = report.validation_graph + report.onto_graph
    data_and_onto = report.onto_graph + report.data_graph
    validation_results, unexpected_extracted = _query_all_results(results_and_onto, data_and_onto)
    reformatted_results = _reformat_extracted_results(validation_results)

    unexpected_found = UnexpectedResults(unexpected_extracted) if unexpected_extracted else None
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
            all_res_focus_nodes.extend(_extract_one_base_info(info, results_and_onto))
    return all_res_focus_nodes


def _extract_one_base_info(info: QueryInfo, results_and_onto: Graph) -> list[ValidationResultBaseInfo]:
    results = []
    path = next(results_and_onto.objects(info.validation_bn, SH.resultPath))
    main_component_type = next(results_and_onto.objects(info.validation_bn, SH.sourceConstraintComponent))
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
                    resource_iri=info.focus_iri,
                    res_class_type=info.focus_rdf_type,
                    result_path=path,
                    detail=detail,
                )
            )
    else:
        results.append(
            ValidationResultBaseInfo(
                result_bn=info.validation_bn,
                source_constraint_component=main_component_type,
                resource_iri=info.focus_iri,
                res_class_type=info.focus_rdf_type,
                result_path=path,
                detail=None,
            )
        )
    return results


def _query_all_without_detail(
    all_base_info: list[ValidationResultBaseInfo], results_and_onto: Graph
) -> tuple[list[ValidationResult], list[UnexpectedComponent]]:
    extracted_results: list[ValidationResult] = []
    unexpected_components: list[UnexpectedComponent] = []

    for base_info in all_base_info:
        res = _query_one_without_detail(base_info, results_and_onto)
        if res is None:
            pass
        elif isinstance(res, UnexpectedComponent):
            unexpected_components.append(res)
        else:
            extracted_results.append(res)
    return extracted_results, unexpected_components


def _query_one_without_detail(  # noqa:PLR0911 (Too many return statements)
    base_info: ValidationResultBaseInfo, results_and_onto: Graph
) -> ValidationResult | UnexpectedComponent | None:
    msg = next(results_and_onto.objects(base_info.result_bn, SH.resultMessage))
    component = next(results_and_onto.objects(base_info.result_bn, SH.sourceConstraintComponent))
    match component:
        case SH.PatternConstraintComponent:
            return _query_pattern_constraint_component_violation(base_info.result_bn, base_info, results_and_onto)
        case SH.MinCountConstraintComponent:
            return _query_for_min_cardinality_violation(base_info, msg, results_and_onto)
        case SH.MaxCountConstraintComponent:
            return ValidationResult(
                violation_type=ViolationType.MAX_CARD,
                res_iri=base_info.resource_iri,
                res_class=base_info.res_class_type,
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
                res_iri=base_info.resource_iri,
                res_class=base_info.res_class_type,
                message=msg,
            )
        case SH.ClassConstraintComponent:
            val = next(results_and_onto.objects(base_info.result_bn, SH.value))
            return ValidationResult(
                violation_type=ViolationType.GENERIC,
                res_iri=base_info.resource_iri,
                res_class=base_info.res_class_type,
                property=base_info.result_path,
                message=msg,
                input_value=val,
            )
        case _:
            return UnexpectedComponent(str(component))


def _query_for_non_existent_cardinality_violation(
    base_info: ValidationResultBaseInfo, results_and_onto: Graph
) -> ValidationResult | None:
    # If a class is for example, an AudioRepresentation, but a jpg file is used,
    # the created value is of type StillImageFileValue.
    # This creates a min cardinality and a closed constraint violation.
    # The closed constraint we ignore, because the problem is communicated through the min cardinality violation.
    if base_info.result_path in FILE_VALUE_PROPERTIES:
        sub_classes = list(results_and_onto.transitive_objects(base_info.res_class_type, RDFS.subClassOf))
        if KNORA_API.Representation in sub_classes:
            return None
        violation_type = ViolationType.FILEVALUE_PROHIBITED
    else:
        violation_type = ViolationType.NON_EXISTING_CARD

    return ValidationResult(
        violation_type=violation_type,
        res_iri=base_info.resource_iri,
        res_class=base_info.res_class_type,
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
            return _query_for_value_type_violation(base_info, results_and_onto, data_graph)
        case SH.PatternConstraintComponent:
            return _query_pattern_constraint_component_violation(detail_info.detail_bn, base_info, results_and_onto)
        case SH.ClassConstraintComponent:
            return _query_class_constraint_component_violation(base_info, results_and_onto, data_graph)
        case (
            SH.InConstraintComponent
            | SH.LessThanConstraintComponent
            | SH.MinExclusiveConstraintComponent
            | SH.MinInclusiveConstraintComponent
        ):
            return _query_generic_violation(base_info, results_and_onto)
        case _:
            return UnexpectedComponent(str(detail_info.source_constraint_component))


def _query_class_constraint_component_violation(
    base_info: ValidationResultBaseInfo, results_and_onto: Graph, data_graph: Graph
) -> ValidationResult | UnexpectedComponent:
    detail_info = cast(DetailBaseInfo, base_info.detail)
    detail_source_shape = next(results_and_onto.objects(detail_info.detail_bn, SH.sourceShape))
    if detail_source_shape in VALUE_CLASS_SHAPES:
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
        res_iri=base_info.resource_iri,
        res_class=base_info.res_class_type,
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
        res_iri=base_info.resource_iri,
        res_class=base_info.res_class_type,
        property=base_info.result_path,
        expected=msg,
        input_value=val,
    )


def _query_generic_violation(base_info: ValidationResultBaseInfo, results_and_onto: Graph) -> ValidationResult:
    detail_info = cast(DetailBaseInfo, base_info.detail)
    val = next(results_and_onto.objects(detail_info.detail_bn, SH.value))
    msg = next(results_and_onto.objects(detail_info.detail_bn, SH.resultMessage))
    return ValidationResult(
        violation_type=ViolationType.GENERIC,
        res_iri=base_info.resource_iri,
        res_class=base_info.res_class_type,
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
        res_iri=base_info.resource_iri,
        res_class=base_info.res_class_type,
        property=base_info.result_path,
        expected=expected_type,
        input_value=target_iri,
        input_type=target_rdf_type,
    )


def _query_for_min_cardinality_violation(
    base_info: ValidationResultBaseInfo,
    msg: SubjectObjectTypeAlias,
    results_and_onto: Graph,
) -> ValidationResult:
    source_shape = next(results_and_onto.objects(base_info.result_bn, SH.sourceShape))
    if source_shape in FILE_VALUE_PROP_SHAPES:
        violation_type = ViolationType.FILE_VALUE
    else:
        violation_type = ViolationType.MIN_CARD
    return ValidationResult(
        violation_type=violation_type,
        res_iri=base_info.resource_iri,
        res_class=base_info.res_class_type,
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
        res_iri=base_info.resource_iri,
        res_class=base_info.res_class_type,
        property=base_info.result_path,
        input_value=val,
    )


def _reformat_extracted_results(results: list[ValidationResult]) -> list[InputProblem]:
    return [_reformat_one_validation_result(x) for x in results]


def _reformat_one_validation_result(validation_result: ValidationResult) -> InputProblem:
    match validation_result.violation_type:
        case (
            ViolationType.MAX_CARD
            | ViolationType.MIN_CARD
            | ViolationType.GENERIC
            | ViolationType.NON_EXISTING_CARD
            | ViolationType.PATTERN
            | ViolationType.UNIQUE_VALUE
            | ViolationType.VALUE_TYPE as violation
        ):
            problem = RESULT_TO_PROBLEM_MAPPER[violation]
            return _reformat_generic(result=validation_result, problem_type=problem)
        case ViolationType.FILEVALUE_PROHIBITED | ViolationType.FILE_VALUE as violation:
            problem = RESULT_TO_PROBLEM_MAPPER[violation]
            iris = _reformat_main_iris(validation_result)
            return InputProblem(
                problem_type=problem,
                res_id=iris.res_id,
                res_type=iris.res_type,
                prop_name="bitstream / iiif-uri",
                expected=_convert_rdflib_input_data_to_string(validation_result.expected),
            )
        case ViolationType.SEQNUM_IS_PART_OF:
            iris = _reformat_main_iris(validation_result)
            return InputProblem(
                problem_type=ProblemType.GENERIC,
                res_id=iris.res_id,
                res_type=iris.res_type,
                prop_name="seqnum or isPartOf",
                message=_convert_rdflib_input_data_to_string(validation_result.message),
            )
        case ViolationType.LINK_TARGET:
            return _reformat_link_target_violation_result(validation_result)
        case _:
            raise BaseError(f"An unknown violation result was found: {validation_result.__class__.__name__}")


def _reformat_generic(
    result: ValidationResult,
    problem_type: ProblemType,
) -> InputProblem:
    iris = _reformat_main_iris(result)
    return InputProblem(
        problem_type=problem_type,
        res_id=iris.res_id,
        res_type=iris.res_type,
        prop_name=iris.prop_name,
        expected=_convert_rdflib_input_data_to_string(result.expected),
    )


def _reformat_value_type_violation_result(result: ValidationResult) -> InputProblem:
    iris = _reformat_main_iris(result)
    return InputProblem(
        problem_type=ProblemType.VALUE_TYPE_MISMATCH,
        res_id=iris.res_id,
        res_type=iris.res_type,
        prop_name=iris.prop_name,
        input_type=reformat_onto_iri(str(result.input_type)),
        expected=_convert_rdflib_input_data_to_string(result.expected),
    )


def _reformat_pattern_violation_result(result: ValidationResult) -> InputProblem:
    iris = _reformat_main_iris(result)
    return InputProblem(
        problem_type=ProblemType.INPUT_REGEX,
        res_id=iris.res_id,
        res_type=iris.res_type,
        prop_name=iris.prop_name,
        input_value=_convert_rdflib_input_data_to_string(result.input_value),
        expected=_convert_rdflib_input_data_to_string(result.expected),
        message=_convert_rdflib_input_data_to_string(result.message),
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
        input_value=_convert_rdflib_input_data_to_string(result.input_value),
        input_type=input_type,
        expected=expected,
    )


def _reformat_unique_value_violation_result(result: ValidationResult) -> InputProblem:
    iris = _reformat_main_iris(result)
    return InputProblem(
        problem_type=ProblemType.DUPLICATE_VALUE,
        res_id=iris.res_id,
        res_type=iris.res_type,
        prop_name=iris.prop_name,
        input_value=_convert_rdflib_input_data_to_string(result.input_value),
    )


def _reformat_main_iris(result: ValidationResult) -> ReformattedIRI:
    subject_id = reformat_data_iri(result.res_iri)
    prop_name = reformat_onto_iri(result.property) if result.property else ""
    res_type = reformat_onto_iri(result.res_class)
    return ReformattedIRI(res_id=subject_id, res_type=res_type, prop_name=prop_name)


def _convert_rdflib_input_data_to_string(input_val: SubjectObjectTypeAlias | None) -> str | None:
    if not input_val:
        return None
    if isinstance(input_val, URIRef):
        return reformat_data_iri(input_val)
    return str(input_val)
