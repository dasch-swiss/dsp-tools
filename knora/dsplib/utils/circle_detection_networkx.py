import networkx as nx
from knora.dsplib.utils.circle_detection_draft import *

def get_resources_and_links(resources, links) -> dict:
    resources_and_links = dict()
    for resource in resources:
        resource_propnames = get_properties_resource(resource)
        list_ : List = list()
        for name in resource_propnames:
            if name in links:
                target = links[name]
                list_.append([name, target, resource_propnames[name]])
        resources_and_links[resource["name"]] = list_
    return resources_and_links


def get_edges_of_resource(resource):
    list_edges: List = list()
    for entry in resource:
        list_edges.append(entry[1])
    return list_edges


def build_graph(resources_and_links, shortname):
    G = nx.DiGraph()
    for name_key in resources_and_links:
        entry = resources_and_links[name_key]
        list_of_edges = get_edges_of_resource(entry)
        name_key = shortname + ":" + name_key
        for edge_part in list_of_edges:
            print("tuples " + name_key + " " + edge_part)
            G.add_edge(u_of_edge=name_key, v_of_edge=edge_part)
    for cycle in nx.simple_cycles(G):
        print("circle from to: ")
        print(cycle)


def validation(data_model):
    """validate the data model in relation to its circles"""
    # 1. prepare
    properties = get_properties(data_model=data_model)
    resources = get_resources(data_model=data_model)
    shortname = get_shortname(data_model=data_model)
    links = get_HasLinkTo_dict(properties=properties, shortname=shortname)

    # get resources and their links
    resources_and_links = get_resources_and_links(resources, links)
    # build graph
    build_graph(resources_and_links, shortname)

if __name__ == '__main__':
    path_json = "/Users/gregorbachmann/Desktop/biz_onto4circular.json"
    #path_json = "/Users/gregorbachmann/Desktop/postcards_rita/postcards.json"
    data_model = load_ontology(path_json=path_json)
    validation(data_model)
