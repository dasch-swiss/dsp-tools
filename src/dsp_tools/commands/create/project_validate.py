from __future__ import annotations

import importlib.resources
import json
from collections import Counter
from collections import defaultdict
from copy import deepcopy
from pathlib import Path
from typing import Any

import jsonschema
import rustworkx as rx
from loguru import logger

from dsp_tools.commands.create.communicate_problems import print_all_problem_collections
from dsp_tools.commands.create.communicate_problems import print_msg_str_for_potential_problematic_circles
from dsp_tools.commands.create.exceptions import ProjectJsonSchemaValidationError
from dsp_tools.commands.create.models.create_problems import CardinalitiesThatMayCreateAProblematicCircle
from dsp_tools.commands.create.models.create_problems import CollectedProblems
from dsp_tools.commands.create.models.create_problems import CreateProblem
from dsp_tools.commands.create.models.create_problems import InputProblem
from dsp_tools.commands.create.models.create_problems import InputProblemType
from dsp_tools.commands.create.models.parsed_ontology import Cardinality
from dsp_tools.commands.create.models.parsed_ontology import GuiElement
from dsp_tools.commands.create.models.parsed_ontology import ParsedClass
from dsp_tools.commands.create.models.parsed_ontology import ParsedClassCardinalities
from dsp_tools.commands.create.models.parsed_ontology import ParsedOntology
from dsp_tools.commands.create.models.parsed_ontology import ParsedProperty
from dsp_tools.commands.create.models.parsed_ontology import ParsedPropertyCardinality
from dsp_tools.commands.create.models.parsed_project import DefaultPermissions
from dsp_tools.commands.create.models.parsed_project import GlobalLimitedViewPermission
from dsp_tools.commands.create.models.parsed_project import LimitedViewPermissionsSelection
from dsp_tools.commands.create.models.parsed_project import ParsedList
from dsp_tools.commands.create.models.parsed_project import ParsedListNode
from dsp_tools.commands.create.models.parsed_project import ParsedPermissions
from dsp_tools.commands.create.models.parsed_project import ParsedProject
from dsp_tools.commands.create.models.parsed_project import ParsedProjectMetadata
from dsp_tools.commands.create.parsing.parse_project import parse_lists
from dsp_tools.commands.create.parsing.parse_project import parse_metadata
from dsp_tools.commands.create.parsing.parse_project import parse_project
from dsp_tools.error.exceptions import UnreachableCodeError
from dsp_tools.setup.ansi_colors import BACKGROUND_BOLD_GREEN
from dsp_tools.setup.ansi_colors import RESET_TO_DEFAULT
from dsp_tools.utils.data_formats.iri_util import from_dsp_iri_to_prefixed_iri
from dsp_tools.utils.data_formats.iri_util import is_dsp_project_iri
from dsp_tools.utils.json_parsing import parse_json_file
from dsp_tools.utils.rdf_constants import KNORA_API_PREFIX
from dsp_tools.utils.rdf_constants import KNORA_PROPERTIES_FOR_DIRECT_USE


def validate_project_only(project_file: Path, server: str) -> bool:
    result, potential_circles = parse_and_validate_project(project_file, server)
    if potential_circles:
        print_msg_str_for_potential_problematic_circles(potential_circles)
    if not isinstance(result, ParsedProject):
        print_all_problem_collections(result)
        return False
    print(
        BACKGROUND_BOLD_GREEN + "JSON project file is syntactically correct and passed validation." + RESET_TO_DEFAULT
    )
    return True


def parse_and_validate_project(
    project_file: Path, server: str
) -> tuple[list[CollectedProblems] | ParsedProject, list[CardinalitiesThatMayCreateAProblematicCircle]]:
    json_project = parse_json_file(project_file)
    return _validate_parsed_json_project(json_project, server)


def parse_and_validate_lists(
    project_file: Path,
) -> tuple[CollectedProblems | None, ParsedProjectMetadata, list[ParsedList]]:
    json_project = parse_json_file(project_file)
    _validate_with_json_schema(json_project)
    parsed_metadata = parse_metadata(json_project["project"])
    parsed_lists = parse_lists(json_project["project"])
    duplicates = _check_for_duplicates_in_list_section(parsed_lists)
    return duplicates, parsed_metadata, parsed_lists


def _validate_parsed_json_project(
    json_project: dict[str, Any], server: str
) -> tuple[list[CollectedProblems] | ParsedProject, list[CardinalitiesThatMayCreateAProblematicCircle]]:
    _validate_with_json_schema(json_project)
    parsing_result = parse_project(json_project, server)

    match parsing_result:
        case ParsedProject():
            validation_problems, potential_circles = _complex_parsed_project_validation(
                parsing_result.ontologies,
                parsing_result.lists,
                parsing_result.permissions,
            )
            if validation_problems:
                return validation_problems, potential_circles
            return parsing_result, potential_circles
        case list():
            return parsing_result, []
        case _:
            raise UnreachableCodeError()


def _validate_with_json_schema(project_definition: dict[str, Any]) -> None:
    with (
        importlib.resources.files("dsp_tools")
        .joinpath("resources/schema/project.json")
        .open(encoding="utf-8") as schema_file
    ):
        project_schema = json.load(schema_file)
    try:
        jsonschema.validate(instance=project_definition, schema=project_schema)
    except jsonschema.ValidationError as err:
        logger.error(err)
        # Check for the specific case of missing 'default_permissions'
        if "'default_permissions' is a required property" in err.message:
            raise ProjectJsonSchemaValidationError("You forgot to specify the 'default_permissions'") from None
        # Check for the specific case of private permissions with overrule
        if (
            "should not be valid under {'required': ['default_permissions_overrule']}" in err.message
            and project_definition.get("project", {}).get("default_permissions") == "private"
        ):
            raise ProjectJsonSchemaValidationError(
                "When default_permissions is 'private', default_permissions_overrule cannot be specified. "
                "Private permissions cannot be overruled."
            ) from None

        raise ProjectJsonSchemaValidationError(
            f"The JSON project file cannot be created due to the following validation error: {err.message}.\n"
            f"The error occurred at {err.json_path}:\n{err.instance}"
        ) from None


def _complex_parsed_project_validation(
    ontologies: list[ParsedOntology], parsed_lists: list[ParsedList], parsed_permissions: ParsedPermissions
) -> tuple[list[CollectedProblems], list[CardinalitiesThatMayCreateAProblematicCircle]]:
    cls_iris = []
    prop_iris = []
    cls_flattened = []
    props_flattened = []
    cardinalities_flattened = []
    for o in ontologies:
        cls_iris.extend([x.name for x in o.classes])
        cls_flattened.extend(o.classes)
        prop_iris.extend([x.name for x in o.properties])
        props_flattened.extend(o.properties)
        cardinalities_flattened.extend(o.cardinalities)

    problems = []
    # DUPLICATES
    if dup_cls := _check_for_duplicate_iris(cls_iris, InputProblemType.DUPLICATE_CLASS_NAME, "classes"):
        problems.append(dup_cls)
    if dup_props := _check_for_duplicate_iris(prop_iris, InputProblemType.DUPLICATE_PROPERTY_NAME, "properties"):
        problems.append(dup_props)
    if duplicates_in_lists := _check_for_duplicates_in_list_section(parsed_lists):
        problems.append(duplicates_in_lists)
    # UNDEFINED REFERENCES
    if undefined_super_prop := _check_for_undefined_supers(
        props_flattened, set(prop_iris), InputProblemType.UNDEFINED_SUPER_PROPERTY, "Property"
    ):
        problems.append(undefined_super_prop)
    if undefined_super_cls := _check_for_undefined_supers(
        cls_flattened, set(cls_iris), InputProblemType.UNDEFINED_SUPER_CLASS, "Class"
    ):
        problems.append(undefined_super_cls)
    if undefined_cards := _check_for_undefined_properties_in_cardinalities(cardinalities_flattened, prop_iris):
        problems.append(undefined_cards)
    # CIRCULAR INHERITANCE
    if circular_cls := _check_circular_inheritance_in_classes(cls_flattened):
        problems.append(circular_cls)
    if circular_prop := _check_circular_inheritance_in_properties(props_flattened):
        problems.append(circular_prop)
    # CARDINALITY PROBLEMS
    if card_probs := _check_circular_references_in_mandatory_property_cardinalities(
        cardinalities_flattened, props_flattened
    ):
        problems.append(card_probs)
    # PERMISSIONS
    still_image_classes = _get_still_image_classes(cls_flattened)
    if perm_problem := _check_for_invalid_default_permissions_overrule(
        parsed_permissions, prop_iris, cls_iris, still_image_classes
    ):
        problems.append(perm_problem)
    potential_circles = _check_for_mandatory_cardinalities_with_knora_resources(
        props_flattened, cardinalities_flattened
    )
    return problems, potential_circles


def _check_for_duplicate_iris(
    input_list: list[str], input_problem_type: InputProblemType, location: str
) -> CollectedProblems | None:
    if duplicates := _get_duplicates_in_list(input_list):
        cleaned_iris = sorted(from_dsp_iri_to_prefixed_iri(x) for x in duplicates)
        return CollectedProblems(
            f"It is not permissible to have multiple {location} with the same name in one ontology. "
            "The following names were used more than once:",
            [InputProblem(x, input_problem_type) for x in cleaned_iris],
        )
    return None


def _check_for_undefined_supers(
    parsed_info: list[ParsedProperty] | list[ParsedClass],
    all_iris: set[str],
    input_problem: InputProblemType,
    location: str,
) -> CollectedProblems | None:
    problems: list[CreateProblem] = []
    for ele in parsed_info:
        if undefined_supers := _check_has_undefined_references(ele.supers, all_iris):
            supers = sorted(from_dsp_iri_to_prefixed_iri(x) for x in undefined_supers)
            problems.append(
                InputProblem(
                    f"{location}: {from_dsp_iri_to_prefixed_iri(ele.name)} / Undefined-Super: {', '.join(supers)}",
                    input_problem,
                )
            )
    if problems:
        return CollectedProblems(
            f"The following {location} have undefined supers:", sorted(problems, key=lambda x: x.problematic_object)
        )
    return None


def _check_has_undefined_references(references: list[str], existing_iris: set[str]) -> set[str]:
    proj_iris = {x for x in references if is_dsp_project_iri(x)}
    return proj_iris - existing_iris


def _check_for_undefined_properties_in_cardinalities(
    cardinalities: list[ParsedClassCardinalities], property_iris: list[str]
) -> CollectedProblems | None:
    allowed_props = deepcopy(property_iris) + deepcopy(KNORA_PROPERTIES_FOR_DIRECT_USE)
    problems: list[CreateProblem] = []
    for cls_card in cardinalities:
        prefixed_cls = from_dsp_iri_to_prefixed_iri(cls_card.class_iri)
        for card in cls_card.cards:
            if card.propname not in allowed_props:
                problems.append(
                    InputProblem(
                        f"Class '{prefixed_cls}' / Property '{from_dsp_iri_to_prefixed_iri(card.propname)}'",
                        InputProblemType.UNDEFINED_PROPERTY_IN_CARDINALITY,
                    )
                )
    if problems:
        return CollectedProblems("The following classes have cardinalities for properties that do not exist:", problems)
    return None


def _check_for_duplicates_in_list_section(parsed_lists: list[ParsedList]) -> None | CollectedProblems:
    problems: list[CreateProblem] = []
    list_names = [x.list_info.name for x in parsed_lists]
    if duplicate_list_names := _get_duplicates_in_list(list_names):
        problems.extend(
            [InputProblem(f"List name '{x}'", InputProblemType.DUPLICATE_LIST_NAME) for x in duplicate_list_names]
        )
    all_nodes = _flatten_all_lists(parsed_lists)
    if duplicate_nodes := _get_duplicates_in_list(all_nodes):
        problems.extend(
            [InputProblem(f"Node name '{x}'", InputProblemType.DUPLICATE_LIST_NODE_NAME) for x in duplicate_nodes]
        )
    if problems:
        return CollectedProblems("The list section has the following problems:", problems)
    return None


def _flatten_all_lists(parsed_lists: list[ParsedList]) -> list[str]:
    all_nodes = []
    for li in parsed_lists:
        all_nodes.extend(_get_all_children(li.children, []))
    return all_nodes


def _get_all_children(children: list[ParsedListNode], existing_nodes: list[str]) -> list[str]:
    for child in children:
        existing_nodes.append(child.node_info.name)
        existing_nodes.extend(_get_all_children(child.children, []))
    return existing_nodes


def _get_duplicates_in_list(input_list: list[str]) -> list[str]:
    return [item for item, count in Counter(input_list).items() if count > 1]


def _check_for_invalid_default_permissions_overrule(
    parsed_permissions: ParsedPermissions, properties: list[str], classes: list[str], still_image_classes: set[str]
) -> CollectedProblems | None:
    if parsed_permissions.default_permissions == DefaultPermissions.PRIVATE:
        return None

    defined_iris_in_ontology = set(properties + classes)
    problems: list[CreateProblem] = []
    if parsed_permissions.overrule_private is not None:
        overrule_private_iris = set(parsed_permissions.overrule_private)
        _, unknown_private_problems = _get_unknown_iris_and_problem(
            overrule_private_iris, defined_iris_in_ontology, InputProblemType.UNKNOWN_IRI_IN_PERMISSIONS_OVERRULE
        )
        problems.extend(unknown_private_problems)

    match parsed_permissions.overrule_limited_view:
        case LimitedViewPermissionsSelection():
            problems.extend(
                _check_limited_view_selection(
                    parsed_permissions.overrule_limited_view, defined_iris_in_ontology, still_image_classes
                )
            )
        case GlobalLimitedViewPermission.ALL | GlobalLimitedViewPermission.NONE:
            # no checks necessary
            pass
        case _:
            raise UnreachableCodeError()

    if problems:
        err_msg = "The 'project.default_permissions_overrule' section of your project has the following problems:"
        return CollectedProblems(err_msg, problems)
    return None


def _check_limited_view_selection(
    limited_view: LimitedViewPermissionsSelection, defined_iris_in_ontology: set[str], still_image_classes: set[str]
) -> list[CreateProblem]:
    problems: list[CreateProblem] = []
    limited_iris = set(limited_view.limited_selection)
    iris_defined_in_the_ontology, undefined_iri_problems = _get_unknown_iris_and_problem(
        limited_iris, defined_iris_in_ontology, InputProblemType.UNKNOWN_IRI_IN_PERMISSIONS_OVERRULE
    )
    problems.extend(undefined_iri_problems)
    # if we do not subtract the unknown iris,
    # they will be duplicated in this check as they are not recognised as still images
    limited_to_check = limited_iris - iris_defined_in_the_ontology
    _, not_still_image_problems = _get_unknown_iris_and_problem(
        limited_to_check, still_image_classes, InputProblemType.INVALID_LIMITED_VIEW_PERMISSIONS_OVERRULE
    )
    problems.extend(not_still_image_problems)
    return problems


def _get_unknown_iris_and_problem(
    used_iris: set[str], defined_iris_in_ontology: set[str], problem_type: InputProblemType
) -> tuple[set[str], list[InputProblem]]:
    if unknown := used_iris - defined_iris_in_ontology:
        return unknown, [InputProblem(from_dsp_iri_to_prefixed_iri(x), problem_type) for x in unknown]
    return set(), []


def _get_still_image_classes(parsed_classes: list[ParsedClass]) -> set[str]:
    knora_still_image = f"{KNORA_API_PREFIX}StillImageRepresentation"

    children_by_parent: dict[str, list[str]] = defaultdict(list)
    for cls in parsed_classes:
        for super_cls in cls.supers:
            children_by_parent[super_cls].append(cls.name)

    def _collect_all_descendants(parent_iri: str, visited: set[str]) -> None:
        for child_iri in children_by_parent.get(parent_iri, []):
            if child_iri not in visited:  # Prevent infinite recursion on cycles
                visited.add(child_iri)
                _collect_all_descendants(child_iri, visited)

    descendants: set[str] = set()
    _collect_all_descendants(knora_still_image, descendants)
    return descendants


def _check_circular_references_in_mandatory_property_cardinalities(
    parsed_cardinalities: list[ParsedClassCardinalities], parsed_properties: list[ParsedProperty]
) -> CollectedProblems | None:
    link_prop_to_object = {x.name: x.object for x in parsed_properties if x.gui_element == GuiElement.SEARCHBOX}
    if not link_prop_to_object:
        return None
    mandatory_links = _extract_mandatory_link_props_per_class(parsed_cardinalities, list(link_prop_to_object.keys()))
    if not mandatory_links:
        return None
    graph = _make_cardinality_dependency_graph(mandatory_links, link_prop_to_object)
    errors = _find_circles_with_mandatory_cardinalities(graph, link_prop_to_object)
    if errors:
        msg = (
            "Your ontology contains properties derived from 'hasLinkTo' that allow circular references "
            "between resources. This is not a problem in itself, but if you try to upload data that actually "
            "contains circular references, these 'hasLinkTo' properties will be temporarily removed from the "
            "affected resources. Therefore, it is necessary that all involved 'hasLinkTo' properties have a "
            "cardinality of 0-1 or 0-n.\n"
            "Please make sure that the following properties have a cardinality of 0-1 or 0-n.\n"
            "Cycles are displayed in: Class -- Property --> Object Class"
        )
        return CollectedProblems(msg, errors)
    return None


def _extract_mandatory_link_props_per_class(
    parsed_cardinalities: list[ParsedClassCardinalities], link_prop_iris: list[str]
) -> dict[str, list[str]]:
    lookup = defaultdict(list)
    for cls_card in parsed_cardinalities:
        for card in cls_card.cards:
            if card.propname in link_prop_iris:
                if card.cardinality in [Cardinality.C_1, Cardinality.C_1_N]:
                    lookup[cls_card.class_iri].append(card.propname)
    return lookup


def _make_cardinality_dependency_graph(
    mandatory_links: dict[str, list[str]],
    link_prop_to_object: dict[str, str],
) -> rx.PyDiGraph[Any, Any]:
    graph: rx.PyDiGraph[Any, Any] = rx.PyDiGraph()
    all_classes = set(mandatory_links.keys())
    all_target_classes = set(link_prop_to_object.values())
    all_classes.update(all_target_classes)

    class_to_node_idx = {}
    for class_iri in all_classes:
        node_idx = graph.add_node(class_iri)
        class_to_node_idx[class_iri] = node_idx

    for source_class, prop_iris in mandatory_links.items():
        source_idx = class_to_node_idx[source_class]
        for prop_iri in prop_iris:
            target_class = link_prop_to_object[prop_iri]
            target_idx = class_to_node_idx[target_class]
            graph.add_edge(source_idx, target_idx, prop_iri)

    return graph


def _find_circles_with_mandatory_cardinalities(
    graph: rx.PyDiGraph[Any, Any], link_prop_to_object: dict[str, str]
) -> list[CreateProblem]:
    error_strings = []
    cycles = list(rx.simple_cycles(graph))

    for cycle in cycles:
        cycle_strings = []
        # Iterate through consecutive pairs of nodes in the cycle
        for i in range(len(cycle)):
            current_node_idx = cycle[i]
            next_node_idx = cycle[(i + 1) % len(cycle)]  # Wrap around to first node
            edge_data_list = graph.get_all_edge_data(current_node_idx, next_node_idx)
            for prop_iri in edge_data_list:
                class_iri = graph[current_node_idx]
                cycle_strings.append(
                    f"{from_dsp_iri_to_prefixed_iri(class_iri)} -- "
                    f"{from_dsp_iri_to_prefixed_iri(prop_iri)} --> "
                    f"{from_dsp_iri_to_prefixed_iri(link_prop_to_object[prop_iri])}"
                )
        error_strings.append("Cycle:\n    " + "\n    ".join(sorted(cycle_strings)))
    problems: list[CreateProblem] = [
        InputProblem(x, InputProblemType.MIN_CARDINALITY_ONE_WITH_CIRCLE) for x in error_strings
    ]
    return problems


def _check_for_mandatory_cardinalities_with_knora_resources(
    parsed_properties: list[ParsedProperty], parsed_cardinalities: list[ParsedClassCardinalities]
) -> list[CardinalitiesThatMayCreateAProblematicCircle]:
    def is_link_prop_with_knora_object(prop: ParsedProperty) -> bool:
        if prop.gui_element != GuiElement.SEARCHBOX:
            return False
        return prop.object.startswith(KNORA_API_PREFIX)

    relevant_link_props = {x.name: x.object for x in parsed_properties if is_link_prop_with_knora_object(x)}
    if not relevant_link_props:
        return []

    def is_mandatory_link(prop_card: ParsedPropertyCardinality) -> bool:
        if prop_card.propname not in relevant_link_props.keys():
            return False
        return prop_card.cardinality in [Cardinality.C_1, Cardinality.C_1_N]

    potential_problems = []
    for cls in parsed_cardinalities:
        for card in cls.cards:
            if is_mandatory_link(card):
                potential_problems.append(
                    CardinalitiesThatMayCreateAProblematicCircle(
                        subject=from_dsp_iri_to_prefixed_iri(cls.class_iri),
                        prop=from_dsp_iri_to_prefixed_iri(card.propname),
                        object_cls=from_dsp_iri_to_prefixed_iri(relevant_link_props[card.propname]),
                        card=str(card.cardinality),
                    )
                )
    return potential_problems


def _check_circular_inheritance_in_classes(classes: list[ParsedClass]) -> CollectedProblems | None:
    graph = _make_inheritance_graph_for_classes(classes)
    errors = _find_and_format_inheritance_cycles(graph, InputProblemType.CIRCULAR_CLASS_INHERITANCE)

    if errors:
        msg = (
            "Your ontology contains circular inheritance dependencies in resource classes. "
            "This means that class A is a subclass of class B, and class B is "
            "(directly or indirectly) a subclass of class A. "
            "Circular inheritance is not allowed and will prevent the ontology from being created."
        )
        return CollectedProblems(msg, errors)
    return None


def _make_inheritance_graph_for_classes(classes: list[ParsedClass]) -> rx.PyDiGraph[Any, Any]:
    graph: rx.PyDiGraph[Any, Any] = rx.PyDiGraph()
    cls_iris = [x.name for x in classes]
    node_indices = list(graph.add_nodes_from(cls_iris))
    iri_to_node = dict(zip(cls_iris, node_indices))

    for cls in classes:
        for super_cls in cls.supers:
            if super_cls in cls_iris:
                graph.add_edge(iri_to_node[cls.name], iri_to_node[super_cls], None)
    return graph


def _check_circular_inheritance_in_properties(properties: list[ParsedProperty]) -> CollectedProblems | None:
    graph = _make_inheritance_graph_for_properties(properties)
    errors = _find_and_format_inheritance_cycles(graph, InputProblemType.CIRCULAR_PROPERTY_INHERITANCE)

    if errors:
        msg = (
            "Your ontology contains circular inheritance dependencies in properties. "
            "This means that property A is a subproperty of property B, and property B is "
            "(directly or indirectly) a subproperty of property A. "
            "Circular inheritance is not allowed and will prevent the ontology from being created."
        )
        return CollectedProblems(msg, errors)
    return None


def _make_inheritance_graph_for_properties(properties: list[ParsedProperty]) -> rx.PyDiGraph[Any, Any]:
    graph: rx.PyDiGraph[Any, Any] = rx.PyDiGraph()
    prop_iris = [x.name for x in properties]
    node_indices = list(graph.add_nodes_from(prop_iris))
    iri_to_node = dict(zip(prop_iris, node_indices))

    for prop in properties:
        for super_prop in prop.supers:
            if super_prop in prop_iris:
                graph.add_edge(iri_to_node[prop.name], iri_to_node[super_prop], None)
    return graph


def _find_and_format_inheritance_cycles(
    graph: rx.PyDiGraph[Any, Any],
    input_problem_type: InputProblemType,
) -> list[CreateProblem]:
    cycles = list(rx.simple_cycles(graph))

    if not cycles:
        return []

    error_strings = []
    for cycle in cycles:
        cycle_iris = [graph[node_idx] for node_idx in cycle]
        cycle_chain_parts = [from_dsp_iri_to_prefixed_iri(iri) for iri in cycle_iris]
        # for nicer output, add the first element at the end
        cycle_chain_parts.append(cycle_chain_parts[0])
        cycle_chain = " -> ".join(cycle_chain_parts)
        error_strings.append(f"Cycle: {cycle_chain}")

    return [InputProblem(x, input_problem_type) for x in sorted(error_strings)]
