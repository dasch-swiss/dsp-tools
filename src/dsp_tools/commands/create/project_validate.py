from __future__ import annotations

import importlib.resources
import json
from collections import Counter
from copy import deepcopy
from pathlib import Path
from typing import Any

import jsonpath_ng
import jsonpath_ng.ext
import jsonschema
import networkx as nx
import regex
from loguru import logger

from dsp_tools.commands.create.communicate_problems import print_all_problem_collections
from dsp_tools.commands.create.exceptions import ProjectJsonSchemaValidationError
from dsp_tools.commands.create.models.create_problems import CollectedProblems
from dsp_tools.commands.create.models.create_problems import CreateProblem
from dsp_tools.commands.create.models.create_problems import InputProblem
from dsp_tools.commands.create.models.create_problems import InputProblemType
from dsp_tools.commands.create.models.parsed_ontology import ParsedClass
from dsp_tools.commands.create.models.parsed_ontology import ParsedClassCardinalities
from dsp_tools.commands.create.models.parsed_ontology import ParsedOntology
from dsp_tools.commands.create.models.parsed_ontology import ParsedProperty
from dsp_tools.commands.create.models.parsed_project import ParsedList
from dsp_tools.commands.create.models.parsed_project import ParsedListNode
from dsp_tools.commands.create.models.parsed_project import ParsedProject
from dsp_tools.commands.create.parsing.parse_project import parse_project
from dsp_tools.setup.ansi_colors import BACKGROUND_BOLD_GREEN
from dsp_tools.setup.ansi_colors import RESET_TO_DEFAULT
from dsp_tools.utils.data_formats.iri_util import from_dsp_iri_to_prefixed_iri
from dsp_tools.utils.data_formats.iri_util import is_dsp_project_iri
from dsp_tools.utils.json_parsing import parse_json_file
from dsp_tools.utils.rdf_constants import KNORA_PROPERTIES_FOR_DIRECT_USE


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
    validation_problems.extend(_complex_parsed_project_validation(parsing_result.ontologies, parsing_result.lists))
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
    if card_probs := _check_cardinalities_of_circular_references(project_definition):
        problems.append(card_probs)
    return problems


def _complex_parsed_project_validation(
    ontologies: list[ParsedOntology], parsed_lists: list[ParsedList]
) -> list[CollectedProblems]:
    cls_iris = []
    prop_iris = []
    cls_flattened = []
    props_flattened = []
    cards_flattened = []
    for o in ontologies:
        cls_iris.extend([x.name for x in o.classes])
        cls_flattened.extend(o.classes)
        prop_iris.extend([x.name for x in o.properties])
        props_flattened.extend(o.properties)
        cards_flattened.extend(o.cardinalities)

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
    if undefined_cards := _check_for_undefined_properties_in_cardinalities(cards_flattened, prop_iris):
        problems.append(undefined_cards)
    if duplicates_in_lists := _check_for_duplicates_in_list_section(parsed_lists):
        problems.append(duplicates_in_lists)
    return problems


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
    all_nodes = _flatten_all_list(parsed_lists)
    if duplicate_nodes := _get_duplicates_in_list(all_nodes):
        problems.extend(
            [InputProblem(f"Node name '{x}'", InputProblemType.DUPLICATE_LIST_NODE_NAME) for x in duplicate_nodes]
        )
    if problems:
        return CollectedProblems("The list section has the following problems:", problems)
    return None


def _flatten_all_list(parsed_lists: list[ParsedList]) -> list[str]:
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


def _check_cardinalities_of_circular_references(project_definition: dict[Any, Any]) -> CollectedProblems | None:
    link_properties = _collect_link_properties(project_definition)
    errors = _identify_problematic_cardinalities(project_definition, link_properties)
    if errors:
        msg = (
            "ERROR: Your ontology contains properties derived from 'hasLinkTo' that allow circular references "
            "between resources. This is not a problem in itself, but if you try to upload data that actually "
            "contains circular references, these 'hasLinkTo' properties will be temporarily removed from the "
            "affected resources. Therefore, it is necessary that all involved 'hasLinkTo' properties have a "
            "cardinality of 0-1 or 0-n. \n"
            "Please make sure that the following properties have a cardinality of 0-1 or 0-n:"
        )
        return CollectedProblems(msg, errors)
    return None


def _collect_link_properties(project_definition: dict[Any, Any]) -> dict[str, list[str]]:
    """
    Maps the properties derived from hasLinkTo to the resource classes they point to.
    Args:
        project_definition: parsed JSON file
    Returns:
        A (possibly empty) dictionary in the form {"rosetta:hasImage2D": ["rosetta:Image2D"], ...}
    """
    ontos = project_definition["project"]["ontologies"]
    hasLinkTo_props = {"hasLinkTo", "isPartOf", "isRegionOf"}
    link_properties: dict[str, list[str]] = {}
    for index, onto in enumerate(ontos):
        hasLinkTo_matches = []
        # look for child-properties down to 5 inheritance levels that are derived from hasLinkTo-properties
        for _ in range(5):
            for hasLinkTo_prop in hasLinkTo_props:
                hasLinkTo_matches.extend(
                    jsonpath_ng.ext.parse(
                        f"$.project.ontologies[{index}].properties[?super[*] == {hasLinkTo_prop}]"
                    ).find(project_definition)
                )
            # make the children from this iteration to the parents of the next iteration
            hasLinkTo_props = {x.value["name"] for x in hasLinkTo_matches}
        prop_obj_pair: dict[str, list[str]] = {}
        for match in hasLinkTo_matches:
            prop = onto["name"] + ":" + match.value["name"]
            target = match.value["object"]
            if target != "Resource":
                # make the target a fully qualified name (with the ontology's name prefixed)
                target = regex.sub(r"^:([^:]+)$", f"{onto['name']}:\\1", target)
            prop_obj_pair[prop] = [target]
        link_properties.update(prop_obj_pair)

    # in case the object of a property is "Resource", the link can point to any resource class
    all_res_names: list[str] = []
    for onto in ontos:
        matches = jsonpath_ng.ext.parse("$.resources[*].name").find(onto)
        tmp = [f"{onto['name']}:{match.value}" for match in matches]
        all_res_names.extend(tmp)
    for prop, targ in link_properties.items():
        if "Resource" in targ:
            link_properties[prop] = all_res_names

    return link_properties


def _identify_problematic_cardinalities(
    project_definition: dict[Any, Any],
    link_properties: dict[str, list[str]],
) -> list[CreateProblem]:
    """
    Make an error list with all cardinalities that are part of a circle but have a cardinality of "1" or "1-n".
    Args:
        project_definition: parsed JSON file
        link_properties: mapping of hasLinkTo-properties to classes they point to,
            e.g. {"rosetta:hasImage2D": ["rosetta:Image2D"], ...}
    Returns:
        a (possibly empty) list of (resource, problematic_cardinality) tuples
    """
    cardinalities, dependencies = _extract_cardinalities_from_project(project_definition, link_properties)
    graph = _make_cardinality_dependency_graph(dependencies)
    errors = _find_circles_with_min_one_cardinality(graph, cardinalities, dependencies)
    return [
        InputProblem(f"Class: {res} / Property: {prop}", InputProblemType.MIN_CARDINALITY_ONE_WITH_CIRCLE)
        for (res, prop) in errors
    ]


def _extract_cardinalities_from_project(
    project_definition: dict[Any, Any],
    link_properties: dict[str, list[str]],
) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, list[str]]]]:
    # dependencies = {"rosetta:Text": {"rosetta:hasImage2D": ["rosetta:Image2D"], ...}}
    dependencies: dict[str, dict[str, list[str]]] = {}
    # cardinalities = {"rosetta:Text": {"rosetta:hasImage2D": "0-1", ...}}
    cardinalities: dict[str, dict[str, str]] = {}

    for onto in project_definition["project"]["ontologies"]:
        for resource in onto["resources"]:
            resname: str = onto["name"] + ":" + resource["name"]
            for card in resource.get("cardinalities", []):
                # make the cardinality a fully qualified name (with the ontology's name prefixed)
                cardname = regex.sub(r"^(:?)([^:]+)$", f"{onto['name']}:\\2", card["propname"])
                if cardname in link_properties:
                    # Look out: if `targets` is created with `targets = link_properties[cardname]`, the ex-
                    # pression `dependencies[resname][cardname] = targets` causes `dependencies[resname][cardname]`
                    # to point to `link_properties[cardname]`. Due to that, the expression
                    # `dependencies[resname][cardname].extend(targets)` will modify "link_properties"!
                    # For this reason, `targets` must be created with `targets = list(link_properties[cardname])`
                    targets = list(link_properties[cardname])
                    if resname not in dependencies:
                        dependencies[resname] = {cardname: targets}
                        cardinalities[resname] = {cardname: card["cardinality"]}
                    elif cardname not in dependencies[resname]:
                        dependencies[resname][cardname] = targets
                        cardinalities[resname][cardname] = card["cardinality"]
                    else:
                        dependencies[resname][cardname].extend(targets)
    return cardinalities, dependencies


def _make_cardinality_dependency_graph(dependencies: dict[str, dict[str, list[str]]]) -> nx.MultiDiGraph[Any]:
    graph: nx.MultiDiGraph[Any] = nx.MultiDiGraph()
    for start, cards in dependencies.items():
        for edge, targets in cards.items():
            for target in targets:
                graph.add_edge(start, target, edge)
    return graph


def _find_circles_with_min_one_cardinality(
    graph: nx.MultiDiGraph[Any], cardinalities: dict[str, dict[str, str]], dependencies: dict[str, dict[str, list[str]]]
) -> set[tuple[str, str]]:
    errors: set[tuple[str, str]] = set()
    circles = list(nx.algorithms.cycles.simple_cycles(graph))
    for circle in circles:
        for index, resource in enumerate(circle):
            target = circle[(index + 1) % len(circle)]
            prop = ""
            for _property, targets in dependencies[resource].items():
                if target in targets:
                    prop = _property
            if cardinalities[resource].get(prop) not in ["0-1", "0-n"]:
                errors.add((resource, prop))
    return errors
