import json
from typing import List

import networkx as nx

def get_resources_and_links(resources, links) -> dict:
    """
    Returns
    resources_and_links:
        keys: resource name
        values: list of list [hasLinkTo-Property name, target name, cardinality]
    """
    resources_and_links = dict()
    for resource in resources:
        resource_propnames = get_properties_resource(resource)
        list_: List = list()
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

    Parameters
    ----------
    resource: list of [property name, target name,cardinality]

    Returns
    -------
    all resources this resource is pointing to
    """
    list_edges: List = list()
    for entry in resource:
        target_name = entry[1]
        list_edges.append(target_name)
    return list_edges


def get_circles(resources_and_links, shortname) -> List:
    """

    Parameters
    ----------
    resources_and_links
    shortname

    Returns
    -------
    list of circles
    """
    G = nx.DiGraph()
    for name_key in resources_and_links:
        entry = resources_and_links[name_key]
        list_of_edges = get_edges_of_resource(entry)
        name_key = shortname + ":" + name_key
        for edge_part in list_of_edges:
            G.add_edge(u_of_edge=name_key, v_of_edge=edge_part)
    return nx.simple_cycles(G)

def load_ontology(path_json) -> dict:
    """load ontology as dict"""
    with open(path_json) as f:
        onto_json_str = f.read()
    return json.loads(onto_json_str)


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
    """returns a dict, with all hasLinkTo-Properties and the respective resource name they are pointing to"""
    links: dict[str, str] = dict()
    for prop in properties:
        super_prop = prop["super"]
        if super_prop.__contains__("hasLinkTo"):
            object_prop = prop["object"]
            if object_prop.find(":") == 0:
                object_prop = shortname + object_prop
            name = prop["name"]
            links[name] = object_prop
    return links


def get_shortname(data_model):
    """returns the shortname of the data model"""
    project = data_model["project"]
    return project["shortname"]

def validation(data_model) -> bool:
    """
    validate the data model in relation to its circles
    Parameters
    ----------
    data_model

    Returns
    -------
    False: circle(s) contain(s) at least one resource with a forbidden cardinality(=not '0-1' or '0-n')
    """
    # 1. prepare
    properties = get_properties(data_model=data_model)
    resources = get_resources(data_model=data_model)
    shortname = get_shortname(data_model=data_model)
    links = get_HasLinkTo_dict(properties=properties, shortname=shortname)

    # get resources and their links
    resources_and_links = get_resources_and_links(resources, links)
    # build graph
    circles = get_circles(resources_and_links, shortname)

    # check circles
    ok_cardinalities = ['0-1', '0-n']
    passed = True
    for circle_raw in circles:
        for name in resources_and_links:
            resource_raw = resources_and_links[name]
            circle = circle_raw[0]
            resource = resource_raw[0]
            if resource[1] == circle:
                cardinality = resource[2]
                if not cardinality in ok_cardinalities:
                    passed = False
                    print("ERROR not in ok cardinalities " + str(resource))
    return passed




if __name__ == '__main__':
    path_json = "/Users/gregorbachmann/Desktop/biz_onto4circular.json"
    #path_json = "/Users/gregorbachmann/Desktop/postcards_rita/postcards.json"
    #path_json = "/Users/gregorbachmann/Documents/GitHub/dsp-tools/testdata/test-onto.json"
    data_model = load_ontology(path_json=path_json)
    validation(data_model)

