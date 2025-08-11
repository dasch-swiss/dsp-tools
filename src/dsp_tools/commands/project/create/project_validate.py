from __future__ import annotations

import importlib.resources
import json
from pathlib import Path
from typing import Any
from typing import Union

import jsonpath_ng
import jsonpath_ng.ext
import jsonschema
import networkx as nx
import regex

from dsp_tools.error.exceptions import BaseError
from dsp_tools.error.exceptions import InputError


def validate_project(input_file_or_json: Union[dict[str, Any], str]) -> bool:
    """
    Validates a JSON project definition file.

    First, the Excel files referenced in the "lists" section are expanded
    (unless this behaviour is disabled).

    Then, the project is validated against the JSON schema.

    Next, some checks are performed that are too complex for JSON schema.

    At last, a check is performed
    if this project's ontologies contain properties derived from hasLinkTo
    that form a circular reference.
    If so, these properties must have the cardinality 0-1 or 0-n,
    because during the xmlupload process,
    these values are temporarily removed.

    Args:
        input_file_or_json: the project to be validated, can either be a file path or a parsed JSON file

    Raises:
        BaseError: detailed error report if the validation doesn't pass

    Returns:
        True if the project passed validation.
    """

    # parse input
    if isinstance(input_file_or_json, dict) and "project" in input_file_or_json:
        project_definition = input_file_or_json
    elif (
        isinstance(input_file_or_json, str)
        and Path(input_file_or_json).is_file()
        and regex.search(r"\.json$", input_file_or_json)
    ):
        with open(input_file_or_json, encoding="utf-8") as f:
            project_definition = json.load(f)
    else:
        raise BaseError(f"Input '{input_file_or_json}' is neither a file path nor a JSON object.")

    # validate the project definition against the schema
    with (
        importlib.resources.files("dsp_tools")
        .joinpath("resources/schema/project.json")
        .open(encoding="utf-8") as schema_file
    ):
        project_schema = json.load(schema_file)
    try:
        jsonschema.validate(instance=project_definition, schema=project_schema)
    except jsonschema.ValidationError as err:
        # Check for the specific case of private permissions with overrule
        if (
            "should not be valid under {'required': ['default_permissions_overrule']}" in err.message
            and project_definition.get("project", {}).get("default_permissions") == "private"
        ):
            raise BaseError(
                "When default_permissions is 'private', default_permissions_overrule cannot be specified. "
                "Private permissions cannot be overruled."
            ) from None

        raise BaseError(
            f"The JSON project file cannot be created due to the following validation error: {err.message}.\n"
            f"The error occurred at {err.json_path}:\n{err.instance}"
        ) from None

    # make some checks that are too complex for JSON schema
    _check_for_invalid_default_permissions_overrule(project_definition)
    _check_for_undefined_super_property(project_definition)
    _check_for_undefined_super_resource(project_definition)
    _check_for_undefined_cardinalities(project_definition)
    _check_for_duplicate_res_and_props(project_definition)
    if lists_section := project_definition["project"].get("lists"):
        _check_for_duplicate_listnodes(lists_section)
    _check_for_deprecated_syntax(project_definition)

    # cardinalities check for circular references
    return _check_cardinalities_of_circular_references(project_definition)


def _build_resource_lookup(project_definition: dict[str, Any]) -> dict[str, dict[str, dict[str, Any]]]:
    """
    Build a lookup dictionary for resources by ontology and name.

    Args:
        project_definition: parsed JSON project definition

    Returns:
        Dictionary mapping ontology names to resource names to resource definitions
    """
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


def _check_for_invalid_default_permissions_overrule(project_definition: dict[str, Any]) -> bool:
    """
    Check if classes in default_permissions_overrule.limited_view are subclasses of StillImageRepresentation.

    Args:
        project_definition: parsed JSON project definition

    Raises:
        BaseError: detailed error message if a class in limited_view doesn't have the correct superclass

    Returns:
        True if all classes in limited_view are subclasses of StillImageRepresentation
    """
    if not (default_permissions_overrule := project_definition.get("project", {}).get("default_permissions_overrule")):
        return True
    if not (limited_view := default_permissions_overrule.get("limited_view")):
        return True

    # If limited_view is "all", no validation needed - it applies to all image classes
    if limited_view == "all":
        return True

    errors: dict[str, str] = {}
    resource_lookup = _build_resource_lookup(project_definition)

    # Check each class in limited_view (when it's a list)
    for class_ref in limited_view:
        parsed_ref = _parse_class_reference(class_ref)
        if not parsed_ref:
            errors[f"Class reference '{class_ref}'"] = "Invalid format, expected 'ontology:ClassName'"
            continue

        ontology_name, class_name = parsed_ref

        # Check if the ontology exists
        if ontology_name not in resource_lookup:
            errors[f"Class reference '{class_ref}'"] = f"Ontology '{ontology_name}' not found"
            continue

        # Check if the resource exists in the ontology
        if class_name not in resource_lookup[ontology_name]:
            errors[f"Class reference '{class_ref}'"] = (
                f"Resource '{class_name}' not found in ontology '{ontology_name}'"
            )
            continue

        # Check if the resource is a subclass of StillImageRepresentation
        if not _is_subclass_of_still_image_representation(ontology_name, class_name, resource_lookup):
            errors[f"Class reference '{class_ref}'"] = (
                f"Resource '{class_name}' must be a subclass of 'StillImageRepresentation' "
                f"(directly or through inheritance)"
            )

    if errors:
        err_msg = (
            "All classes in project.default_permissions_overrule.limited_view "
            "must be subclasses of 'StillImageRepresentation', because the 'limited view' "
            "permission is only implemented for images (i.e. blurring, watermarking). \n"
            "In order to check, the classes must be provided in the form \n"
            '    "limited_view": ["ontoname:Classname", ...]\n\n'
            "The following classes do not meet this requirement:\n"
        )
        err_msg += "\n".join(f" - {loc}: {error}" for loc, error in errors.items())
        raise BaseError(err_msg)

    return True


def _check_for_undefined_super_property(project_definition: dict[str, Any]) -> bool:
    """
    Check the superproperties that claim to point to a property defined in the same JSON project.
    Check if the property they point to actually exists.
    (DSP base properties and properties from other ontologies are not considered.)

    Args:
        project_definition: parsed JSON project definition

    Raises:
        BaseError: detailed error message if a superproperty is not existent

    Returns:
        True if the superproperties are valid
    """
    errors: dict[str, list[str]] = {}
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
                errors[f"Ontology '{ontoname}', property '{prop['name']}'"] = invalid_references

    if errors:
        err_msg = "Your data model contains properties that are derived from an invalid super-property:\n" + "\n".join(
            f" - {loc}: {invalids}" for loc, invalids in errors.items()
        )
        raise BaseError(err_msg)
    return True


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


def _check_for_undefined_super_resource(project_definition: dict[str, Any]) -> bool:
    """
    Check the superresources that claim to point to a resource defined in the same JSON project.
    Check if the resource they point to actually exists.
    (DSP base resources and resources from other ontologies are not considered.)

    Args:
        project_definition: parsed JSON project definition

    Raises:
        BaseError: detailed error message if a superresource is not existent

    Returns:
        True if the superresource are valid
    """
    errors: dict[str, list[str]] = {}
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
                errors[f"Ontology '{ontoname}', resource '{res['name']}'"] = invalid_references

    if errors:
        err_msg = "Your data model contains resources that are derived from an invalid super-resource:\n" + "\n".join(
            f" - {loc}: {invalids}" for loc, invalids in errors.items()
        )
        raise BaseError(err_msg)
    return True


def _check_for_undefined_cardinalities(project_definition: dict[str, Any]) -> bool:
    """
    Check if the propnames that are used in the cardinalities of each resource are defined in the "properties"
    section. (DSP base properties and properties from other ontologies are not considered.)

    Args:
        project_definition: parsed JSON project definition

    Raises:
        BaseError: detailed error message if a cardinality is used that is not defined

    Returns:
        True if all cardinalities are defined in the "properties" section
    """
    errors: dict[str, list[str]] = {}
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
                errors[f"Ontology '{ontoname}', resource '{res['name']}'"] = invalid_cardnames

    if errors:
        err_msg = "Your data model contains cardinalities with invalid propnames:\n" + "\n".join(
            f" - {loc}: {invalids}" for loc, invalids in errors.items()
        )
        raise BaseError(err_msg)
    return True


def _check_cardinalities_of_circular_references(project_definition: dict[Any, Any]) -> bool:
    """
    Check a JSON project file if it contains properties derived from hasLinkTo that form a circular reference. If so,
    these properties must have the cardinality 0-1 or 0-n, because during the xmlupload process, these values
    are temporarily removed.

    Args:
        project_definition: dictionary with a DSP project (as defined in a JSON project file)

    Raises:
        BaseError: if there is a circle with at least one element that has a cardinality of "1" or "1-n"

    Returns:
        True if no circle was detected, or if all elements of all circles are of cardinality "0-1" or "0-n".
    """

    link_properties = _collect_link_properties(project_definition)
    errors = _identify_problematic_cardinalities(project_definition, link_properties)

    if len(errors) == 0:
        return True

    error_message = (
        "ERROR: Your ontology contains properties derived from 'hasLinkTo' that allow circular references "
        "between resources. This is not a problem in itself, but if you try to upload data that actually "
        "contains circular references, these 'hasLinkTo' properties will be temporarily removed from the "
        "affected resources. Therefore, it is necessary that all involved 'hasLinkTo' properties have a "
        "cardinality of 0-1 or 0-n. \n"
        "Please make sure that the following properties have a cardinality of 0-1 or 0-n:"
    )
    for error in errors:
        error_message = f"{error_message}\n    - Resource {error[0]}, property {error[1]}"
    raise BaseError(error_message)


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
) -> list[tuple[str, str]]:
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
    return sorted(errors, key=lambda x: x[0])


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


def _check_for_duplicate_res_and_props(project_definition: dict[str, Any]) -> bool:
    """
    Check that the resource names and property names are unique.

    Args:
        project_definition: parsed JSON project definition

    Raises:
        BaseError: detailed error message if there is a duplicate resource name / property name

    Returns:
        True if the resource/property names are unique
    """
    propnames_duplicates, resnames_duplicates = _find_duplicate_res_and_props(project_definition)

    if not resnames_duplicates and not propnames_duplicates:
        return True

    err_msg = "Resource names and property names must be unique inside every ontology.\n"
    for ontoname, res_duplicates in resnames_duplicates.items():
        for res_duplicate in sorted(res_duplicates):
            err_msg += f"Resource '{res_duplicate}' appears multiple times in the ontology '{ontoname}'.\n"
    for ontoname, prop_duplicates in propnames_duplicates.items():
        for prop_duplicate in sorted(prop_duplicates):
            err_msg += f"Property '{prop_duplicate}' appears multiple times in the ontology '{ontoname}'.\n"

    raise BaseError(err_msg)


def _check_for_duplicate_listnodes(lists_section: list[dict[str, Any]]) -> None:
    if listnode_duplicates := _find_duplicate_listnodes(lists_section):
        err_msg = "Listnode names must be unique across all lists. The following names appear multiple times:"
        err_msg += "\n - " + "\n - ".join(listnode_duplicates)
        raise InputError(err_msg)


def _check_for_deprecated_syntax(project_definition: dict[str, Any]) -> bool:  # noqa: ARG001 (unused argument)
    return True
