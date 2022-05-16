import os
from typing import Any, Union, List, Set
import jsonschema
import json
from typing import List
import networkx as nx
from ..utils.expand_all_lists import expand_lists_from_excel


def validate_ontology(input_file_or_json: Union[str, dict[Any, Any], 'os.PathLike[Any]']) -> bool:
    """
    Validates an ontology against the knora schema

    Args:
        input_file_or_json: the ontology to be validated, can either be a file or a json string (dict)

    Returns:
        True if ontology passed validation, False otherwise
    """

    data_model: dict[Any, Any] = {}
    if isinstance(input_file_or_json, dict):
        data_model = input_file_or_json
    elif os.path.isfile(input_file_or_json):
        with open(input_file_or_json) as f:
            onto_json_str = f.read()
        data_model = json.loads(onto_json_str)
    else:
        print('Input is not valid.')
        exit(1)

    # expand all lists referenced in the list section of the data model
    new_lists = expand_lists_from_excel(data_model)

    # add the newly created lists from Excel to the ontology
    data_model['project']['lists'] = new_lists

    # validate the data model against the schema
    current_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(current_dir, '../schemas/ontology.json')) as s:
        schema = json.load(s)
    try:
        jsonschema.validate(instance=data_model, schema=schema)
    except jsonschema.exceptions.ValidationError as err:
        print(f'Data model did not pass validation. The error message is: {err.message}\n'
              f'The error occurred at {err.json_path}')
        return False

    # cardinalities check for circular references
    if check_cardinalities_of_circular_references(data_model):
        print('Data model is syntactically correct and passed validation.')
        return True
    else:
        return False


def check_cardinalities_of_circular_references(data_model: dict[Any, Any]) -> bool:
    """
    Check if there are properties derived from hasLinkTo that form a circular reference. If so, these
    properties must have the cardinality 0-1 or 0-n, because during the xmlupload process, these values
    are temporarily removed.
    """
    # 1. prepare
    properties = get_properties(data_model=data_model)
    resources = get_resources(data_model=data_model)
    shortname = get_shortname(data_model=data_model)
    links = get_HasLinkTo_dict(properties=properties, shortname=shortname)

    # get resources and their links
    resources_and_links = get_resources_and_links(resources, links)
    # get circles
    circles = get_circles(resources_and_links, shortname)

    # check circles
    ok_cardinalities = ['0-1', '0-n']
    errors = get_circle_errors(circles, resources_and_links, ok_cardinalities)
    if len(errors) == 0:
        return True
    else:
        print('ERROR: Your ontology contains properties derived from "hasLinkTo" that allow circular references '
              'between resources. This is not a problem in itself, but if you try to upload data that actually '
              'contains circular references, these "hasLinkTo" cardinalities will be temporarily removed from the '
              'affected resources. Therefore, it is necessary that the involved "hasLinkTo" cardinalities have a '
              'cardinality of 0-1 or 0-n. \n'
              'Please make sure that the following cardinalities have a cardinality of 0-1 or 0-n:')
        for error in errors:
            print(error)
        return False


def get_circle_errors(circles, resources_and_links, ok_cardinalities) -> List:
    """
    checks circles and returns errors

    Args:
        circles: list of circles that were detected
        resources_and_links: resources with their respective hasLinkToProperties
        ok_cardinalities: cardinalities that are valuable for hasLinkTo-Properties in circles

    Returns:
        errors: List of errors

    """
    errors: List = list()
    for circle in circles:
        for element in circle:
            for key_name in resources_and_links:
                resource = resources_and_links[key_name]
                for hasLinkTo_props in resource:
                    # hasLinkTo: Resource could always cause a circle
                    if hasLinkTo_props[1] == element or hasLinkTo_props[1] == 'Resource':
                        cardinality = hasLinkTo_props[2]
                        if cardinality not in ok_cardinalities:
                            error_message = "Resource " + key_name + " with hasLinkTo-Property " + str(hasLinkTo_props)
                            if not errors.__contains__(error_message):
                                errors.append(error_message)
    return errors


def get_resources_and_links(resources, links) -> dict:
    """
    get the resources with their respective hasLinkToProperties

    Args:
        resources: all resources of the data model.
        links: hasLinkTo-properties and the respective resource they are pointing to.
    Returns:
    resources_and_links:
        resource name linked to respective hasLinkToProperty-details
        keys: resource name
        values: list of list [hasLinkTo-Property name, target name, cardinality]
    """
    resources_and_links = dict()
    for resource in resources:
        resource_propnames = get_properties_resource(resource)
        list_: List = list()
        # append a list of lists for every resource name
        for name in resource_propnames:
            if name in links:
                target = links[name]
                cardinality = resource_propnames[name]
                list_.append([name, target, cardinality])
        if len(list_) != 0:
            resources_and_links[resource["name"]] = list_
    return resources_and_links


def get_edges_of_resource(resource):
    """
    get all the resources a resource is pointing to

    Args:
        resource: list of [property name, target name,cardinality]

    Returns:
        list_edges: all resources this resource is pointing to
    """
    list_edges: List = list()
    for entry in resource:
        target_name = entry[1]
        list_edges.append(target_name)
    return list_edges


def get_circles(resources_and_links, shortname) -> List:
    """
    detects circles and returns them

    Args:
        resources_and_links: resource names linked to respective hasLinkToProperty-details
        shortname: shortname of the project

    Returns:
        circles: list of circles
    """
    graph = nx.DiGraph()
    graph = populate_graph(graph=graph, resources_and_links=resources_and_links, shortname=shortname)
    circles = nx.simple_cycles(graph)
    return circles


def populate_graph(graph, resources_and_links, shortname):
    """Populates graph with resources and the resources they are pointing to and returns it

    Args:
        graph: a void graph
        resources_and_links: resources with their respective hasLinkToProperties
        shortname: shortname of project

    Returns:
        graph: a populated graph

    """
    for name_key in resources_and_links:
        entry = resources_and_links[name_key]
        list_of_edges = get_edges_of_resource(entry)
        name_key = shortname + ":" + name_key
        for edge_part in list_of_edges:
            graph.add_edge(u_of_edge=name_key, v_of_edge=edge_part)
    return graph


def get_properties(data_model) -> List:
    """returns all properties of an ontology"""
    ontology = data_model['project']['ontologies']
    ontology_dict = ontology[0]
    return ontology_dict["properties"]


def get_resources(data_model) -> List:
    """returns all resources of an ontology"""
    ontology = data_model['project']['ontologies']
    ontology_dict = ontology[0]
    return ontology_dict["resources"]


def get_properties_resource(resource) -> dict:
    """returns all the properties of a single resource with their respective cardinalities"""
    entries = dict()
    cardinalities = resource["cardinalities"]
    for entry in cardinalities:
        name = entry["propname"]
        name = name[1:]
        cardinality = entry["cardinality"]
        entries[name] = cardinality
    return entries


def get_HasLinkTo_dict(properties, shortname) -> dict:
    """returns a dict, with every hasLinkTo-Property-name and the respective resource name they are pointing to
        Args:
            properties: all properties of the ontology
            shortname: shortname of the ontology
        Returns:
            links: keys = name of hasLinkToProperty, values = the resource the hasLinkTo is pointing to
    """
    links: dict[str, str] = dict()
    for prop in properties:
        super_prop = prop["super"]
        if super_prop.__contains__("hasLinkTo"):
            object_prop = prop["object"]
            # add shortname, if shortname is not already part of object_prop
            if object_prop.find(":") == 0:
                object_prop = shortname + object_prop
            name = prop["name"]
            links[name] = object_prop
    return links


def get_shortname(data_model):
    """returns the shortname of the data model"""
    project = data_model["project"]
    return project["shortname"]
