from __future__ import annotations

import importlib.resources
import json
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
from dsp_tools.commands.create.models.parsed_project import ParsedProject
from dsp_tools.commands.create.parsing.parse_project import parse_project
from dsp_tools.utils.ansi_colors import BACKGROUND_BOLD_GREEN
from dsp_tools.utils.ansi_colors import RESET_TO_DEFAULT
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
    if json_validation_problems := _complex_project_validation(json_project):
        return json_validation_problems
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


def _complex_project_validation(project_definition: dict[str, Any]) -> list[CollectedProblems]:
    problems: list[CollectedProblems] = []
    # make some checks that are too complex for JSON schema
    if perm_res := _check_for_invalid_default_permissions_overrule(project_definition):
        problems.append(perm_res)
    if prop_problem := _check_for_undefined_super_property(project_definition):
        problems.append(prop_problem)
    if cls_problems := _check_for_undefined_super_class(project_definition):
        problems.append(cls_problems)
    if card_problem := _check_for_undefined_cardinalities(project_definition):
        problems.append(card_problem)
    duplicated = _check_for_duplicate_res_and_props(project_definition)
    problems.extend(duplicated)
    if lists_section := project_definition["project"].get("lists"):
        if list_prob := _check_for_duplicate_listnodes(lists_section):
            problems.append(list_prob)
    if card_probs := _check_cardinalities_of_circular_references(project_definition):
        problems.append(card_probs)
    return problems


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


def _check_for_undefined_super_property(project_definition: dict[str, Any]) -> CollectedProblems | None:
    problems: list[CreateProblem] = []
    for onto in project_definition["project"]["ontologies"]:
        ontoname = onto["name"]
        propnames = [p["name"] for p in onto["properties"]]
        for prop in onto["properties"]:
            supers = prop["super"]
            # form of supers:
            #  - isSegmentOf   # DSP base property
            #  - other:prop    # other onto
            #  - same:prop     # same onto
            #  - :prop         # same onto (short form)

            # filter out DSP base properties
            supers = [s for s in supers if ":" in s]
            # extend short form
            supers = [regex.sub(r"^:", f"{ontoname}:", s) for s in supers]
            # filter out other ontos
            supers = [s for s in supers if regex.search(f"^{ontoname}:", s)]
            # convert to short form
            supers = [regex.sub(f"^{ontoname}", "", s) for s in supers]

            if invalid_references := [s for s in supers if regex.sub(":", "", s) not in propnames]:
                invalid_refs_str = ", ".join(invalid_references)
                problems.append(
                    InputProblem(
                        problematic_object=f"{ontoname}:{prop['name']} (invalid super-properties: {invalid_refs_str})",
                        problem=InputProblemType.UNDEFINED_SUPER_PROPERTY,
                    )
                )
    if problems:
        return CollectedProblems("The following properties have undefined super-properties:", problems)
    return None


def _find_duplicate_res_and_props(
    project_definition: dict[str, Any],
) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    resnames_duplicates: dict[str, set[str]] = {}
    propnames_duplicates: dict[str, set[str]] = {}
    for onto in project_definition["project"]["ontologies"]:
        resnames = [r["name"] for r in onto["resources"]]
        if len(set(resnames)) != len(resnames):
            for elem in resnames:
                if resnames.count(elem) > 1:
                    if resnames_duplicates.get(onto["name"]):
                        resnames_duplicates[onto["name"]].add(elem)
                    else:
                        resnames_duplicates[onto["name"]] = {elem}

        propnames = [p["name"] for p in onto["properties"]]
        if len(set(propnames)) != len(propnames):
            for elem in propnames:
                if propnames.count(elem) > 1:
                    if propnames_duplicates.get(onto["name"]):
                        propnames_duplicates[onto["name"]].add(elem)
                    else:
                        propnames_duplicates[onto["name"]] = {elem}
    return propnames_duplicates, resnames_duplicates


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


def _check_for_undefined_super_class(project_definition: dict[str, Any]) -> CollectedProblems | None:
    problems: list[CreateProblem] = []
    for onto in project_definition["project"]["ontologies"]:
        ontoname = onto["name"]
        resnames = [r["name"] for r in onto["resources"]]
        for res in onto["resources"]:
            supers = res["super"] if isinstance(res["super"], list) else [res["super"]]
            # form of supers:
            #  - Resource      # DSP base resource
            #  - other:res     # other onto
            #  - same:res      # same onto
            #  - :res          # same onto (short form)

            # filter out DSP base resources
            supers = [s for s in supers if ":" in s]
            # extend short form
            supers = [regex.sub(r"^:", f"{ontoname}:", s) for s in supers]
            # filter out other ontos
            supers = [s for s in supers if regex.search(f"^{ontoname}:", s)]
            # convert to short form
            supers = [regex.sub(f"^{ontoname}", "", s) for s in supers]

            if invalid_references := [s for s in supers if regex.sub(":", "", s) not in resnames]:
                invalid_refs_str = ", ".join(invalid_references)
                problems.append(
                    InputProblem(
                        problematic_object=f"{ontoname}:{res['name']} (invalid super-classes: {invalid_refs_str})",
                        problem=InputProblemType.UNDEFINED_SUPER_CLASS,
                    )
                )
    if problems:
        return CollectedProblems("The following classes have undefined super-classes:", problems)
    return None


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


def _check_for_duplicate_res_and_props(project_definition: dict[str, Any]) -> list[CollectedProblems]:
    propnames_duplicates, resnames_duplicates = _find_duplicate_res_and_props(project_definition)
    problems: list[CollectedProblems] = []

    res_problems: list[CreateProblem] = []
    for ontoname, res_duplicates in resnames_duplicates.items():
        res_problems.extend(
            [InputProblem(f"{ontoname}:{dup}", InputProblemType.DUPLICATE_CLASS_NAME) for dup in res_duplicates]
        )
    if res_problems:
        problems.append(
            CollectedProblems("The following class names appear multiple times in one ontology:", res_problems)
        )

    prop_problems: list[CreateProblem] = []
    for ontoname, prop_duplicates in propnames_duplicates.items():
        prop_problems.extend(
            [InputProblem(f"{ontoname}:{dup}", InputProblemType.DUPLICATE_PROPERTY_NAME) for dup in prop_duplicates]
        )
    if prop_problems:
        problems.append(
            CollectedProblems("The following property names appear multiple times in one ontology:", prop_problems)
        )

    return problems


def _check_for_duplicate_listnodes(lists_section: list[dict[str, Any]]) -> None | CollectedProblems:
    if listnode_duplicates := _find_duplicate_listnodes(lists_section):
        return CollectedProblems(
            "The following list node names are used multiple times in your project:",
            [InputProblem(", ".join(listnode_duplicates), InputProblemType.DUPLICATE_LIST_NAME)],
        )
    return None
