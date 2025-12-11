from __future__ import annotations

import importlib.resources
import json
from collections import Counter
from collections import defaultdict
from pathlib import Path
from typing import Any

import jsonschema
import regex
import rustworkx as rx
from loguru import logger

from dsp_tools.commands.create.communicate_problems import print_all_problem_collections
from dsp_tools.commands.create.exceptions import ProjectJsonSchemaValidationError
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
from dsp_tools.commands.create.models.parsed_project import ParsedProject
from dsp_tools.commands.create.parsing.parse_project import parse_project
from dsp_tools.setup.ansi_colors import BACKGROUND_BOLD_GREEN
from dsp_tools.setup.ansi_colors import RESET_TO_DEFAULT
from dsp_tools.utils.data_formats.iri_util import from_dsp_iri_to_prefixed_iri
from dsp_tools.utils.data_formats.iri_util import is_dsp_project_iri
from dsp_tools.utils.json_parsing import parse_json_file


def validate_project_only(project_file: Path, server: str) -> bool:
    result = parse_and_validate_project(project_file, server)
    if not isinstance(result, ParsedProject):
        print_all_problem_collections(result)
        return False
    print(
        BACKGROUND_BOLD_GREEN + "JSON project file is syntactically correct and passed validation." + RESET_TO_DEFAULT
    )
    return True


def parse_and_validate_project(project_file: Path, server: str) -> list[CollectedProblems] | ParsedProject:
    json_project = parse_json_file(project_file)
    return _validate_parsed_json_project(json_project, server)


def _validate_parsed_json_project(json_project: dict[str, Any], server: str) -> list[CollectedProblems] | ParsedProject:
    _validate_with_json_schema(json_project)
    parsing_result = parse_project(json_project, server)
    if not isinstance(parsing_result, ParsedProject):
        return parsing_result
    validation_problems = _complex_json_project_validation(json_project)
    validation_problems.extend(_complex_parsed_project_validation(parsing_result.ontologies))
    if validation_problems:
        return validation_problems
    return parsing_result


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


def _complex_json_project_validation(project_definition: dict[str, Any]) -> list[CollectedProblems]:
    problems: list[CollectedProblems] = []
    # make some checks that are too complex for JSON schema
    if perm_res := _check_for_invalid_default_permissions_overrule(project_definition):
        problems.append(perm_res)
    if card_problem := _check_for_undefined_cardinalities(project_definition):
        problems.append(card_problem)
    if lists_section := project_definition["project"].get("lists"):
        if list_prob := _check_for_duplicate_listnodes(lists_section):
            problems.append(list_prob)
    return problems


def _complex_parsed_project_validation(ontologies: list[ParsedOntology]) -> list[CollectedProblems]:
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
    if dup_cls := _check_for_duplicate_iris(cls_iris, InputProblemType.DUPLICATE_CLASS_NAME, "classes"):
        problems.append(dup_cls)
    if dup_props := _check_for_duplicate_iris(prop_iris, InputProblemType.DUPLICATE_PROPERTY_NAME, "properties"):
        problems.append(dup_props)
    if undefined_super_prop := _check_for_undefined_supers(
        props_flattened, set(prop_iris), InputProblemType.UNDEFINED_SUPER_PROPERTY, "Property"
    ):
        problems.append(undefined_super_prop)
    if undefined_super_cls := _check_for_undefined_supers(
        cls_flattened, set(cls_iris), InputProblemType.UNDEFINED_SUPER_CLASS, "Class"
    ):
        problems.append(undefined_super_cls)
    if card_probs := _check_circular_references_in_mandatory_property_cardinalities(
        cardinalities_flattened, props_flattened
    ):
        problems.append(card_probs)
    return problems


def _check_for_duplicate_iris(
    input_list: list[str], input_problem_type: InputProblemType, location: str
) -> CollectedProblems | None:
    if duplicates := [item for item, count in Counter(input_list).items() if count > 1]:
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


def _build_resource_lookup(project_definition: dict[str, Any]) -> dict[str, dict[str, dict[str, Any]]]:
    resource_lookup: dict[str, dict[str, dict[str, Any]]] = {}
    for onto in project_definition["project"]["ontologies"]:
        resource_lookup[onto["name"]] = {}
        for resource in onto["resources"]:
            resource_lookup[onto["name"]][resource["name"]] = resource
    return resource_lookup


def _parse_class_reference(class_ref: str) -> tuple[str, str] | None:
    """
    Parse a class reference in the format 'ontology:ClassName'.

    Args:
        class_ref: Class reference string

    Returns:
        Tuple of (ontology_name, class_name) or None if invalid format
    """
    if ":" not in class_ref:
        return None

    parts = class_ref.split(":")
    if len(parts) != 2:
        return None

    return parts[0], parts[1]


def _is_subclass_of_still_image_representation(
    ontology_name: str, class_name: str, resource_lookup: dict[str, dict[str, dict[str, Any]]]
) -> bool:
    """
    Check if a class is a subclass of StillImageRepresentation by traversing the inheritance chain.

    Args:
        ontology_name: Name of the ontology containing the class
        class_name: Name of the class to check
        resource_lookup: Dictionary mapping ontology names to resource definitions

    Returns:
        True if the class is a subclass of StillImageRepresentation
    """
    current_onto = ontology_name
    current_class = class_name
    visited = set()

    # Follow the inheritance chain up to 10 levels (prevent infinite loops)
    for _ in range(10):
        class_id = f"{current_onto}:{current_class}"
        if class_id in visited:
            break  # Circular reference detected
        visited.add(class_id)

        if current_onto not in resource_lookup or current_class not in resource_lookup[current_onto]:
            break  # Resource not found

        resource = resource_lookup[current_onto][current_class]
        super_class = resource.get("super")

        # Handle both string and list formats for super
        super_classes = []
        if isinstance(super_class, list):
            super_classes = super_class
        elif super_class:
            super_classes = [super_class]

        # Check if any superclass is StillImageRepresentation
        if "StillImageRepresentation" in super_classes:
            return True

        # Find the next class in the inheritance chain
        next_class = None
        for super_cls in super_classes:
            if super_cls.startswith(":"):
                # Same ontology reference
                next_class = (current_onto, super_cls[1:])
                break
            elif ":" in super_cls and super_cls != "StillImageRepresentation":
                # Different ontology reference
                super_parts = super_cls.split(":", 1)
                if len(super_parts) == 2:
                    next_class = (super_parts[0], super_parts[1])
                    break

        if next_class:
            current_onto, current_class = next_class
        else:
            break  # No more inheritance to follow

    return False


def _check_for_invalid_default_permissions_overrule(project_definition: dict[str, Any]) -> CollectedProblems | None:
    if not (default_permissions_overrule := project_definition.get("project", {}).get("default_permissions_overrule")):
        return None
    if not (limited_view := default_permissions_overrule.get("limited_view")):
        return None

    # If limited_view is "all", no validation needed - it applies to all image classes
    if limited_view == "all":
        return None

    problems: list[CreateProblem] = []
    resource_lookup = _build_resource_lookup(project_definition)

    # Check each class in limited_view (when it's a list)
    for class_ref in limited_view:
        parsed_ref = _parse_class_reference(class_ref)
        if not parsed_ref:
            problems.append(
                InputProblem(
                    problematic_object=f"{class_ref} (Invalid format, expected 'ontology:ClassName')",
                    problem=InputProblemType.PREFIX_COULD_NOT_BE_RESOLVED,
                )
            )
            continue

        ontology_name, class_name = parsed_ref

        # Check if the ontology exists
        if ontology_name not in resource_lookup:
            problems.append(
                InputProblem(
                    problematic_object=f"{ontology_name}:{class_name} (Ontology '{ontology_name}' not found)",
                    problem=InputProblemType.PREFIX_COULD_NOT_BE_RESOLVED,
                )
            )
            continue

        # Check if the resource exists in the ontology
        if class_name not in resource_lookup[ontology_name]:
            problems.append(
                InputProblem(
                    problematic_object=(
                        f"{ontology_name}:{class_name} "
                        f"(Resource '{class_name}' not found in ontology '{ontology_name}')"
                    ),
                    problem=InputProblemType.UNDEFINED_REFERENCE,
                )
            )
            continue

        # Check if the resource is a subclass of StillImageRepresentation
        if not _is_subclass_of_still_image_representation(ontology_name, class_name, resource_lookup):
            problems.append(
                InputProblem(
                    problematic_object=(
                        f"{ontology_name}:{class_name} "
                        f"(Must be a subclass of 'StillImageRepresentation' directly or through inheritance)"
                    ),
                    problem=InputProblemType.INVALID_PERMISSIONS_OVERRULE,
                )
            )
    if problems:
        err_msg = (
            "All classes in project.default_permissions_overrule.limited_view "
            "must be subclasses of 'StillImageRepresentation', because the 'limited view' "
            "permission is only implemented for images (i.e. blurring, watermarking). \n"
            "In order to check, the classes must be provided in the form \n"
            '    "limited_view": ["ontoname:Classname", ...]\n\n'
            "The following classes do not meet this requirement:\n"
        )
        return CollectedProblems(err_msg, problems)
    return None


def _find_duplicate_listnodes(lists_section: list[dict[str, Any]]) -> set[str]:
    def _process_sublist(sublist: dict[str, Any]) -> None:
        existing_nodenames.append(sublist["name"])
        if nodes := sublist.get("nodes"):
            if isinstance(nodes, dict) and list(nodes.keys()) == ["folder"]:
                return
            for x in nodes:
                _process_sublist(x)

    existing_nodenames: list[str] = []
    for lst in lists_section:
        _process_sublist(lst)

    return {x for x in existing_nodenames if existing_nodenames.count(x) > 1}


def _check_for_undefined_cardinalities(project_definition: dict[str, Any]) -> CollectedProblems | None:
    problems: list[CreateProblem] = []
    for onto in project_definition["project"]["ontologies"]:
        ontoname = onto["name"]
        propnames = [prop["name"] for prop in onto["properties"]]
        for res in onto["resources"]:
            cardnames = [card["propname"] for card in res.get("cardinalities", [])]
            # form of the cardnames:
            #  - isSegmentOf   # DSP base property
            #  - other:prop    # other onto
            #  - same:prop     # same onto
            #  - :prop         # same onto (short form)

            # filter out DSP base properties
            cardnames = [card for card in cardnames if ":" in card]
            # extend short form
            cardnames = [regex.sub(r"^:", f"{ontoname}:", card) for card in cardnames]
            # filter out other ontos
            cardnames = [card for card in cardnames if regex.search(f"^{ontoname}:", card)]
            # convert to short form
            cardnames = [regex.sub(f"^{ontoname}:", ":", card) for card in cardnames]

            if invalid_cardnames := [card for card in cardnames if regex.sub(":", "", card) not in propnames]:
                invalid_cards_str = ", ".join(invalid_cardnames)
                problems.append(
                    InputProblem(
                        problematic_object=f"{ontoname}:{res['name']} (invalid cardinalities: {invalid_cards_str})",
                        problem=InputProblemType.UNDEFINED_PROPERTY_IN_CARDINALITY,
                    )
                )
    if problems:
        return CollectedProblems("The following classes have cardinalities for properties that do not exist:", problems)
    return None


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


def _check_for_duplicate_listnodes(lists_section: list[dict[str, Any]]) -> None | CollectedProblems:
    if listnode_duplicates := _find_duplicate_listnodes(lists_section):
        return CollectedProblems(
            "The following list node names are used multiple times in your project:",
            [InputProblem(", ".join(listnode_duplicates), InputProblemType.DUPLICATE_LIST_NAME)],
        )
    return None
