import pygraphviz as pgv
import json
from pprint import pprint
from typing import List, Set, Dict, Tuple, Optional


class Graph:

    def __init__(self, filename: str):
        # read the data model definition
        with open(filename) as f:
            self.datamodel = json.load(f)
            #pprint(self.datamodel)

        self.resources = self.datamodel["project"]["ontologies"][0]["resources"]
        self.properties = self.datamodel["project"]["ontologies"][0]["properties"]
        self.propertiesMap = dict(
            map(lambda x: (x["name"], x["object"]), self.datamodel["project"]["ontologies"][0]["properties"]))


if __name__ == '__main__':

    graph = Graph("BiZ-onto.json")

    reslist = []
    for res in graph.resources:
        oneres = {"resname": res["name"], "props": []}
        for prop in res["cardinalities"]:
            tmp = prop["propname"].split(":")
            if tmp[0] == '':
                proptype = graph.propertiesMap[tmp[1]]
            else:
                pass  # ToDo: treat here properties from external ontolopgies
            oneres["props"].append({"propname": prop["propname"], "proptype": proptype})
        reslist.append(oneres)

    # Creates the graph using pygraphviz
    G = pgv.AGraph(strict=False, directed=True, ranksep='2', page="8.3,11.7", size="8.0,11.0", margin=0.3,
                   center='true', landscape='true')
    for resProps in reslist:
        G.add_node(resProps["resname"], style='filled', fillcolor='#03dffc')

        # creates the edges

        for propType in resProps["props"]:

            # Cleansing the string from the ':' character at the beginning
            if propType["proptype"].startswith(':'):  # In this case nodes are being connected. (Nodes start with ':')
                temp = propType["proptype"][1:]
                G.add_edge(resProps["resname"], temp, label=propType["propname"])


            else:  # Here Nodes are connected with literals
                temp = propType["proptype"]

                G.add_node(temp, shape='box', style='filled', fillcolor='#95f0b0')
                G.add_edge(resProps["resname"], temp, label=propType["propname"])

    G.draw('OntologyGraph.pdf', prog='dot')  # Differente layouts: prog=neato|dot|twopi|circo|fdp|nop
