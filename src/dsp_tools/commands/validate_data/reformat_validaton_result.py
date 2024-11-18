from typing import cast

import regex
from rdflib import RDF
from rdflib import SH
from rdflib import Graph
from rdflib import Literal
from rdflib import Namespace
from rdflib.term import Node

from dsp_tools.commands.validate_data.models.input_problems import AllProblems
from dsp_tools.commands.validate_data.models.input_problems import ContentRegexProblem
from dsp_tools.commands.validate_data.models.input_problems import DuplicateValueProblem
from dsp_tools.commands.validate_data.models.input_problems import FileValueProblem
from dsp_tools.commands.validate_data.models.input_problems import GenericProblem
from dsp_tools.commands.validate_data.models.input_problems import InputProblem
from dsp_tools.commands.validate_data.models.input_problems import LinkedResourceDoesNotExistProblem
from dsp_tools.commands.validate_data.models.input_problems import LinkTargetTypeMismatchProblem
from dsp_tools.commands.validate_data.models.input_problems import MaxCardinalityProblem
from dsp_tools.commands.validate_data.models.input_problems import MinCardinalityProblem
from dsp_tools.commands.validate_data.models.input_problems import NonExistentCardinalityProblem
from dsp_tools.commands.validate_data.models.input_problems import UnexpectedResults
from dsp_tools.commands.validate_data.models.input_problems import ValueTypeProblem
from dsp_tools.commands.validate_data.models.validation import DetailBaseInfo
from dsp_tools.commands.validate_data.models.validation import QueryInfo
from dsp_tools.commands.validate_data.models.validation import ReformattedIRI
from dsp_tools.commands.validate_data.models.validation import ResultGenericViolation
from dsp_tools.commands.validate_data.models.validation import ResultLinkTargetViolation
from dsp_tools.commands.validate_data.models.validation import ResultMaxCardinalityViolation
from dsp_tools.commands.validate_data.models.validation import ResultMinCardinalityViolation
from dsp_tools.commands.validate_data.models.validation import ResultNonExistentCardinalityViolation
from dsp_tools.commands.validate_data.models.validation import ResultPatternViolation
from dsp_tools.commands.validate_data.models.validation import ResultUniqueValueViolation
from dsp_tools.commands.validate_data.models.validation import ResultValueTypeViolation
from dsp_tools.commands.validate_data.models.validation import UnexpectedComponent
from dsp_tools.commands.validate_data.models.validation import ValidationReportGraphs
from dsp_tools.commands.validate_data.models.validation import ValidationResult
from dsp_tools.commands.validate_data.models.validation import ValidationResultBaseInfo
from dsp_tools.commands.validate_data.utils import reformat_data_iri
from dsp_tools.commands.validate_data.utils import reformat_onto_iri
from dsp_tools.models.exceptions import BaseError

DASH = Namespace("http://datashapes.org/dash#")
KNORA_API = Namespace("http://api.knora.org/ontology/knora-api/v2#")
API_SHAPES = Namespace("http://api.knora.org/ontology/knora-api/shapes/v2#")


def reformat_validation_graph(report: ValidationReportGraphs) -> AllProblems:
    """
    Reformats the validation result from an RDF graph into class instances
    that are used to communicate the problems with the user.

    Args:
        report: with all the information necessary to construct a user message

    Returns:
        All Problems
    """

    results_and_onto = report.validation_graph + report.onto_graph
    data_and_onto = report.onto_graph + report.data_graph

    validation_results, unexpected_extracted = _query_all_results(results_and_onto, data_and_onto)
    reformatted_results: list[InputProblem] = _reformat_extracted_results(validation_results)

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
            return _query_pattern_constraint_component_violation(base_info.result_bn, base_info, results_and_onto)
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
        case SH.SPARQLConstraintComponent:
            return _query_for_unique_value_violation(base_info, results_and_onto)
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
    detail_info = cast(DetailBaseInfo, base_info.detail)
    match detail_info.source_constraint_component:
        case SH.MinCountConstraintComponent:
            return _query_for_value_type_violation(base_info, results_and_onto, data_graph)
        case SH.PatternConstraintComponent:
            return _query_pattern_constraint_component_violation(detail_info.detail_bn, base_info, results_and_onto)
        case SH.ClassConstraintComponent:
            return _query_class_constraint_component_violation(base_info, results_and_onto, data_graph)
        case SH.InConstraintComponent:
            return _query_generic_violation(base_info, results_and_onto)
        case _:
            return UnexpectedComponent(str(detail_info.source_constraint_component))


def _query_class_constraint_component_violation(
    base_info: ValidationResultBaseInfo, results_and_onto: Graph, data_graph: Graph
) -> ValidationResult | UnexpectedComponent:
    detail_info = cast(DetailBaseInfo, base_info.detail)
    detail_source_shape = next(results_and_onto.objects(detail_info.detail_bn, SH.sourceShape))
    all_class_shapes = {
        API_SHAPES.BooleanValue_ClassShape,
        API_SHAPES.ColorValue_ClassShape,
        API_SHAPES.DateValue_ClassShape,
        API_SHAPES.DecimalValue_ClassShape,
        API_SHAPES.GeonameValue_ClassShape,
        API_SHAPES.IntValue_ClassShape,
        API_SHAPES.LinkValue_ClassShape,
        API_SHAPES.ListValue_ClassShape,
        API_SHAPES.TimeValue_ClassShape,
        API_SHAPES.UriValue_ClassShape,
    }
    if detail_source_shape in all_class_shapes:
        return _query_for_value_type_violation(base_info, results_and_onto, data_graph)
    return _query_for_link_value_target_violation(base_info, results_and_onto, data_graph)


def _query_for_value_type_violation(
    base_info: ValidationResultBaseInfo, results_and_onto: Graph, data_graph: Graph
) -> ResultValueTypeViolation:
    detail_info = cast(DetailBaseInfo, base_info.detail)
    msg = next(results_and_onto.objects(detail_info.detail_bn, SH.resultMessage))
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
    bn_with_info: Node, base_info: ValidationResultBaseInfo, results_and_onto: Graph
) -> ResultPatternViolation:
    val = next(results_and_onto.objects(bn_with_info, SH.value))
    msg = str(next(results_and_onto.objects(bn_with_info, SH.resultMessage)))
    return ResultPatternViolation(
        res_iri=base_info.resource_iri,
        res_class=base_info.res_class_type,
        property=base_info.result_path,
        results_message=msg,
        actual_value=str(val),
    )


def _query_generic_violation(base_info: ValidationResultBaseInfo, results_and_onto: Graph) -> ResultGenericViolation:
    detail_info = cast(DetailBaseInfo, base_info.detail)
    val = next(results_and_onto.objects(detail_info.detail_bn, SH.value))
    msg = str(next(results_and_onto.objects(detail_info.detail_bn, SH.resultMessage)))
    return ResultGenericViolation(
        res_iri=base_info.resource_iri,
        res_class=base_info.res_class_type,
        property=base_info.result_path,
        results_message=msg,
        actual_value=str(val),
    )


def _query_for_link_value_target_violation(
    base_info: ValidationResultBaseInfo, results_and_onto: Graph, data_graph: Graph
) -> ResultLinkTargetViolation:
    detail_info = cast(DetailBaseInfo, base_info.detail)
    target_iri = next(results_and_onto.objects(detail_info.detail_bn, SH.value))
    target_rdf_type: Node | None = None
    if target_type := list(data_graph.objects(target_iri, RDF.type)):
        target_rdf_type = target_type[0]
    expected_type = next(results_and_onto.objects(detail_info.detail_bn, SH.resultMessage))
    return ResultLinkTargetViolation(
        res_iri=base_info.resource_iri,
        res_class=base_info.res_class_type,
        property=base_info.result_path,
        expected_type=expected_type,
        target_iri=target_iri,
        target_resource_type=target_rdf_type,
    )


def _query_for_unique_value_violation(
    base_info: ValidationResultBaseInfo,
    results_and_onto: Graph,
) -> ResultUniqueValueViolation:
    val = next(results_and_onto.objects(base_info.result_bn, SH.value))
    return ResultUniqueValueViolation(
        res_iri=base_info.resource_iri,
        res_class=base_info.res_class_type,
        property=base_info.result_path,
        actual_value=val,
    )


def _reformat_extracted_results(results: list[ValidationResult]) -> list[InputProblem]:
    all_reformatted: list[InputProblem] = [_reformat_one_validation_result(x) for x in results]
    return all_reformatted


def _reformat_one_validation_result(validation_result: ValidationResult) -> InputProblem:  # noqa: PLR0911 Too many return statements
    match validation_result:
        case ResultMaxCardinalityViolation():
            iris = _reformat_main_iris(validation_result)
            return MaxCardinalityProblem(
                res_id=iris.res_id,
                res_type=iris.res_type,
                prop_name=iris.prop_name,
                expected_cardinality=validation_result.results_message,
            )
        case ResultMinCardinalityViolation():
            return _reformat_min_cardinality_validation_result(validation_result)
        case ResultNonExistentCardinalityViolation():
            iris = _reformat_main_iris(validation_result)
            return NonExistentCardinalityProblem(
                res_id=iris.res_id,
                res_type=iris.res_type,
                prop_name=iris.prop_name,
            )
        case ResultGenericViolation():
            iris = _reformat_main_iris(validation_result)
            return GenericProblem(
                res_id=iris.res_id,
                res_type=iris.res_type,
                prop_name=iris.prop_name,
                results_message=validation_result.results_message,
                actual_content=validation_result.actual_value,
            )
        case ResultValueTypeViolation():
            return _reformat_value_type_violation_result(validation_result)
        case ResultPatternViolation():
            return _reformat_pattern_violation_result(validation_result)
        case ResultLinkTargetViolation():
            return _reformat_link_target_violation_result(validation_result)
        case ResultUniqueValueViolation():
            return _reformat_unique_value_violation_result(validation_result)
        case _:
            raise BaseError(f"An unknown violation result was found: {validation_result.__class__.__name__}")


def _reformat_min_cardinality_validation_result(validation_result: ResultMinCardinalityViolation) -> InputProblem:
    iris = _reformat_main_iris(validation_result)
    file_value_properties = ["hasMovingImageFileValue"]
    if iris.prop_name in file_value_properties:
        return FileValueProblem(
            res_id=iris.res_id,
            res_type=iris.res_type,
            prop_name="bitstream / iiif-uri",
            expected=validation_result.results_message,
        )
    return MinCardinalityProblem(
        res_id=iris.res_id,
        res_type=iris.res_type,
        prop_name=iris.prop_name,
        expected_cardinality=validation_result.results_message,
    )


def _reformat_value_type_violation_result(result: ResultValueTypeViolation) -> ValueTypeProblem:
    iris = _reformat_main_iris(result)
    actual_type = reformat_onto_iri(result.actual_value_type)
    return ValueTypeProblem(
        res_id=iris.res_id,
        res_type=iris.res_type,
        prop_name=iris.prop_name,
        actual_type=actual_type,
        expected_type=result.results_message,
    )


def _reformat_pattern_violation_result(result: ResultPatternViolation) -> ContentRegexProblem:
    iris = _reformat_main_iris(result)
    val: str | None = result.actual_value
    if val and not regex.search(r"\S+", val):
        val = None
    return ContentRegexProblem(
        res_id=iris.res_id,
        res_type=iris.res_type,
        prop_name=iris.prop_name,
        expected_format=result.results_message,
        actual_content=val,
    )


def _reformat_link_target_violation_result(result: ResultLinkTargetViolation) -> InputProblem:
    iris = _reformat_main_iris(result)
    target_id = reformat_data_iri(result.target_iri)
    if not result.target_resource_type:
        return LinkedResourceDoesNotExistProblem(
            res_id=iris.res_id,
            res_type=iris.res_type,
            prop_name=iris.prop_name,
            link_target_id=target_id,
        )
    actual_type = reformat_onto_iri(result.target_resource_type)
    expected_type = reformat_onto_iri(result.expected_type)
    return LinkTargetTypeMismatchProblem(
        res_id=iris.res_id,
        res_type=iris.res_type,
        prop_name=iris.prop_name,
        link_target_id=target_id,
        actual_type=actual_type,
        expected_type=expected_type,
    )


def _reformat_unique_value_violation_result(result: ResultUniqueValueViolation) -> DuplicateValueProblem:
    iris = _reformat_main_iris(result)
    if isinstance(result.actual_value, Literal):
        actual_value = str(result.actual_value)
    else:
        actual_value = reformat_data_iri(result.actual_value)
    return DuplicateValueProblem(
        res_id=iris.res_id,
        res_type=iris.res_type,
        prop_name=iris.prop_name,
        actual_content=actual_value,
    )


def _reformat_main_iris(result: ValidationResult) -> ReformattedIRI:
    subject_id = reformat_data_iri(result.res_iri)
    prop_name = reformat_onto_iri(result.property)
    res_type = reformat_onto_iri(result.res_class)
    return ReformattedIRI(res_id=subject_id, res_type=res_type, prop_name=prop_name)
