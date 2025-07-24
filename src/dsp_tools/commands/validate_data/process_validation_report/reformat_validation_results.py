from typing import cast

from rdflib import SH
from rdflib import URIRef

from dsp_tools.commands.validate_data.constants import FILE_VALUE_PROPERTIES
from dsp_tools.commands.validate_data.constants import FILEVALUE_DETAIL_INFO
from dsp_tools.commands.validate_data.constants import LEGAL_INFO_PROPS
from dsp_tools.commands.validate_data.mappers import RESULT_TO_PROBLEM_MAPPER
from dsp_tools.commands.validate_data.models.input_problems import InputProblem
from dsp_tools.commands.validate_data.models.input_problems import ProblemType
from dsp_tools.commands.validate_data.models.input_problems import Severity
from dsp_tools.commands.validate_data.models.validation import ReformattedIRI
from dsp_tools.commands.validate_data.models.validation import ValidationResult
from dsp_tools.commands.validate_data.models.validation import ViolationType
from dsp_tools.commands.validate_data.utils import reformat_any_iri
from dsp_tools.commands.validate_data.utils import reformat_data_iri
from dsp_tools.commands.validate_data.utils import reformat_onto_iri
from dsp_tools.error.exceptions import BaseError
from dsp_tools.utils.rdflib_constants import KNORA_API
from dsp_tools.utils.rdflib_constants import SubjectObjectTypeAlias

SEVERITY_MAPPER: dict[SubjectObjectTypeAlias, Severity] = {
    SH.Violation: Severity.VIOLATION,
    SH.Warning: Severity.WARNING,
    SH.Info: Severity.INFO,
}


def reformat_extracted_results(results: list[ValidationResult]) -> list[InputProblem]:
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
        case ViolationType.FILE_VALUE_PROHIBITED | ViolationType.FILE_VALUE_MISSING as violation:
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
        problem_type = ProblemType.FILE_VALUE_MISSING
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
    # If it is a stand-off link, we want to preserve the message
    if result.property == KNORA_API.hasStandoffLinkTo:
        msg = str(result.message)
    else:
        msg = None

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
        message=msg,
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
