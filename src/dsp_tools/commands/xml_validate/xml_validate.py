from pathlib import Path

from dsp_tools.commands.xml_validate.deserialise_project import deserialise_project
from dsp_tools.commands.xml_validate.models.data_deserialised import DataDeserialised
from dsp_tools.commands.xml_validate.models.data_deserialised import LinkValueData
from dsp_tools.commands.xml_validate.models.data_deserialised import ListValueData
from dsp_tools.commands.xml_validate.models.data_deserialised import ResourceData
from dsp_tools.commands.xml_validate.models.input_problems import AllProblems
from dsp_tools.commands.xml_validate.models.input_problems import DuplicateContent
from dsp_tools.commands.xml_validate.models.input_problems import InputProblem
from dsp_tools.commands.xml_validate.models.input_problems import LinkTargetMismatch
from dsp_tools.commands.xml_validate.models.input_problems import ListNodeNotFound
from dsp_tools.commands.xml_validate.models.input_problems import MaxCardinalityViolation
from dsp_tools.commands.xml_validate.models.input_problems import PropTypeMismatch
from dsp_tools.commands.xml_validate.models.project_deserialised import CardinalityOne
from dsp_tools.commands.xml_validate.models.project_deserialised import CardinalityZeroToN
from dsp_tools.commands.xml_validate.models.project_deserialised import ProjectDeserialised
from dsp_tools.commands.xml_validate.models.project_deserialised import ResourceClass
from dsp_tools.commands.xml_validate.prepare_input import parse_file
from dsp_tools.models.exceptions import InputError


def xml_validate(xml_filepath: Path) -> bool:
    """Validates an XML file without uploading data."""
    # This function assumes that all classes and properties used exist in the ontology.
    data = parse_file(xml_filepath)
    onto = deserialise_project()
    if problems := _find_all_problems(data, onto):
        msg = AllProblems(problems).get_msg()
        raise InputError(msg)
    return True


def _find_all_problems(data: DataDeserialised, onto: ProjectDeserialised) -> list[InputProblem]:
    problems: list[InputProblem] = _check_for_duplicate_values(data)
    problems.extend(_check_cardinalities(data, onto))
    problems.extend(_check_prop_type_match(data, onto))
    problems.extend(_check_link_target_class_match(data, onto))
    problems.extend(_check_list_values(data, onto))
    return problems


def _check_for_duplicate_values(data: DataDeserialised) -> list[InputProblem]:
    problems = []
    for r in data.resources:
        if duplicates := r.get_duplicate_content():
            for dup in duplicates:
                problems.append(DuplicateContent(res_id=r.res_id, prop_name=dup[0], content=dup[1]))
    return problems


def _check_cardinalities(data: DataDeserialised, onto: ProjectDeserialised) -> list[InputProblem]:
    problems = []
    for res in data.resources:
        problems.extend(_check_cardinality_one_resource(res, onto.resources[res.res_class]))
    return problems


def _check_cardinality_one_resource(res: ResourceData, resource_class: ResourceClass) -> list[InputProblem]:
    card_problems: list[InputProblem] = []
    cards_used = res.get_cardinalities()
    # The situation if a property does not exist in the look-up is not dealt with
    for card in cards_used:
        expected_card = resource_class.restrictions[card.prop_name]
        match expected_card:
            case CardinalityOne():
                if not card.num_used == 1:
                    card_problems.append(MaxCardinalityViolation(res_id=res.res_id, prop_name=card.prop_name))
            case CardinalityZeroToN():
                pass
            case _:
                raise NotImplementedError
    # Min cardinality violations are not checked here
    return card_problems


def _check_prop_type_match(data: DataDeserialised, onto: ProjectDeserialised) -> list[InputProblem]:
    problems: list[InputProblem] = []
    # The situation if a property does not exist in the look-up is not dealt with
    for res in data.resources:
        for val in res.values:
            expected_type = onto.properties[val.prop_name].type()
            if not val.type() == expected_type:
                problems.append(
                    PropTypeMismatch(
                        res_id=res.res_id,
                        prop_name=val.prop_name,
                        prop_type_used=val.type(),
                        prop_type_expected=expected_type,
                    )
                )
    return problems


def _check_link_target_class_match(data: DataDeserialised, onto: ProjectDeserialised) -> list[InputProblem]:
    type_lookup = {x.res_id: x.res_class for x in data.resources}
    link_prop_lookup = onto.get_link_prop_lookup()
    problems: list[InputProblem] = []
    # The situation if a resource does not exist in the look-up is not dealt with
    for res in data.resources:
        for val in res.values:
            if isinstance(val, LinkValueData):
                expected_type = link_prop_lookup[val.prop_name]
                actual_type = type_lookup[val.prop_value]
                if actual_type not in expected_type:
                    problems.append(
                        LinkTargetMismatch(
                            res_id=res.res_id,
                            prop_name=val.prop_name,
                            target_id=val.prop_value,
                            target_class_used=actual_type,
                            target_class_expected=expected_type,
                        )
                    )
    return problems


def _check_list_values(data: DataDeserialised, onto: ProjectDeserialised) -> list[InputProblem]:
    list_look_up = onto.get_list_prop_lookup()
    problems: list[InputProblem] = []
    # The situation if a property does not exist in the look-up is not dealt with
    for res in data.resources:
        for val in res.values:
            if isinstance(val, ListValueData):
                list_onto = list_look_up[val.prop_name]
                if val.prop_value not in list_onto.nodes:
                    problems.append(
                        ListNodeNotFound(
                            res_id=res.res_id,
                            prop_name=val.prop_name,
                            list_name=val.list_name,
                            node_name=val.prop_value,
                        )
                    )
    return problems
