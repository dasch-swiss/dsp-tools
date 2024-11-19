from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLBitstream
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLProperty
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLValue
from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import XMLResource
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.resource_value_models import AbstractFileValue
from dsp_tools.commands.xmlupload.models.resource_value_models import CollectedProblems
from dsp_tools.commands.xmlupload.models.resource_value_models import IntermediaryBoolean
from dsp_tools.commands.xmlupload.models.resource_value_models import IntermediaryResource
from dsp_tools.commands.xmlupload.models.resource_value_models import IntermediaryValue
from dsp_tools.commands.xmlupload.models.resource_value_models import ResolvingInformationProblem
from dsp_tools.commands.xmlupload.models.resource_value_models import ResourceTransformationProblems
from dsp_tools.commands.xmlupload.models.resource_value_models import TransformationSteps
from dsp_tools.commands.xmlupload.value_transformers import transform_boolean

transformation_lookup = {"bool": TransformationSteps(IntermediaryBoolean, transform_boolean)}


def transform_resource(
    xml_resource: XMLResource, permission_lookup: dict[str, Permissions]
) -> IntermediaryResource | ResourceTransformationProblems:
    problems = []
    values = _transform_properties(xml_resource.properties, permission_lookup)
    if isinstance(values, CollectedProblems):
        problems.extend(values.problems)
    resource_permissions = _get_permissions(xml_resource.permissions, permission_lookup)
    file_val = None
    if xml_resource.bitstream:
        file_result = _transform_file_value(xml_resource.bitstream, permission_lookup)
        if isinstance(file_result, ResolvingInformationProblem):
            problems.append(file_result.problem)
    if problems:
        return ResourceTransformationProblems(xml_resource.res_id, problems)
    return IntermediaryResource(
        res_id=xml_resource.res_id,
        res_type=xml_resource.restype,
        values=values,
        permissions=resource_permissions,
        file_value=file_val,
    )


def _transform_properties(
    props: list[XMLProperty], permission_lookup: dict[str, Permissions]
) -> list[IntermediaryValue] | CollectedProblems:
    all_values = []
    problems = []
    for prop in props:
        match prop.valtype:
            case "bool":
                result = _transform_property(prop, permission_lookup, transformation_lookup["bool"])
            case _:
                ...  # continue in the same manner
        if isinstance(result, CollectedProblems):
            problems.extend(result.problems)
    if problems:
        return CollectedProblems(problems)
    return all_values


def _transform_property(
    prop: XMLProperty, permission_lookup: dict[str, Permissions], transformations: TransformationSteps
) -> list[IntermediaryValue] | CollectedProblems:
    good_properties = []
    problems = []
    for val in prop.values:
        result = _transform_value(prop.name, val, permission_lookup, transformations)
        if isinstance(result, CollectedProblems):
            problems.extend(result.problems)
        else:
            good_properties.append(result)
    if problems:
        return CollectedProblems(problems)
    return good_properties


def _transform_value(
    prop_name: str, value: XMLValue, permission_lookup: dict[str, Permissions], transformations: TransformationSteps
) -> IntermediaryValue | CollectedProblems:
    problems = []
    permissions = _get_permissions(value.permissions, permission_lookup)
    if isinstance(permissions, ResolvingInformationProblem):
        problems.append(permissions.problem)
    transformed_value = transformations.transformer(value.value)
    if isinstance(transformed_value, ResolvingInformationProblem):
        problems.append(transformed_value.problem)
    if problems:
        return CollectedProblems(problems)
    return transformations.intermediary_value(prop_name, transformed_value, value.comment, permissions)


def _transform_file_value(
    value: XMLBitstream, permission_lookup: dict[str, Permissions]
) -> AbstractFileValue | ResolvingInformationProblem: ...


def _get_permissions(
    permissions_str: str | None, lookup: dict[str, Permissions]
) -> Permissions | None | ResolvingInformationProblem:
    if not permissions_str:
        return None
    if not (found := lookup.get(permissions_str)):
        return ResolvingInformationProblem(permissions_str)
    return found
