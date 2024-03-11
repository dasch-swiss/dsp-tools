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

from dsp_tools.commands.excel2json.lists import expand_lists_from_excel
from dsp_tools.models.exceptions import BaseError


def _check_for_duplicate_names(project_definition: dict[str, Any]) -> bool:
    """
    Check that the resource names and property names are unique.

    Args:
        project_definition: parsed JSON project definition

    Raises:
        BaseError: detailed error message if there is a duplicate resource name / property name

    Returns:
        True if the resource/property names are unique
    """
    propnames_duplicates, resnames_duplicates = _find_duplicates(project_definition)

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


def _find_duplicates(project_definition: dict[str, Any]) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
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
            #  - isSequenceOf  # DSP base property
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
            #  - isSequenceOf  # DSP base property
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


def validate_project(
    input_file_or_json: Union[dict[str, Any], str],
    expand_lists: bool = True,
) -> bool:
    """
    Validates a JSON project definition file.

    First, the Excel file references in the "lists" section are expanded
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
        expand_lists: if True, the Excel file references in the "lists" section will be expanded

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

    # expand all lists referenced in the "lists" section of the project definition,
    # and add them to the project definition
    if expand_lists:
        if new_lists := expand_lists_from_excel(project_definition["project"].get("lists", [])):
            project_definition["project"]["lists"] = new_lists

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
        raise BaseError(
            f"The JSON project file cannot be created due to the following validation error: {err.message}.\n"
            f"The error occurred at {err.json_path}:\n{err.instance}"
        ) from None

    # make some checks that are too complex for JSON schema
    _check_for_undefined_super_property(project_definition)
    _check_for_undefined_super_resource(project_definition)
    _check_for_undefined_cardinalities(project_definition)
    _check_for_duplicate_names(project_definition)

    # cardinalities check for circular references
    return _check_cardinalities_of_circular_references(project_definition)


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
    hasLinkTo_props = {"hasLinkTo", "isPartOf", "isRegionOf", "isAnnotationOf"}
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


def _make_cardinality_dependency_graph(dependencies: dict[str, dict[str, list[str]]]) -> nx.MultiDiGraph:
    graph = nx.MultiDiGraph()
    for start, cards in dependencies.items():
        for edge, targets in cards.items():
            for target in targets:
                graph.add_edge(start, target, edge)
    return graph


def _find_circles_with_min_one_cardinality(
    graph: nx.MultiDiGraph, cardinalities: dict[str, dict[str, str]], dependencies: dict[str, dict[str, list[str]]]
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
