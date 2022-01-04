import importlib.util
import json
import sys

# from pprint import pprint
# from typing import Dict, List, Optional, Set, Tuple

# import pygraphviz as pgv


def visualize(file: str) -> None:
    # ensure that pygraphviz is installed
    spec = importlib.util.find_spec("pygraphviz")
    if not spec:
        print("ERROR: To visualize ontologies, you need to have 'pygraphviz' installed. Please consult the documentation.")
        sys.exit(1)
    import pygraphviz as pgv
    # get data from file
    with open(file) as f:
        datamodel = json.load(f)
    resources = datamodel["project"]["ontologies"][0]["resources"]
    properties = datamodel["project"]["ontologies"][0]["properties"]
    propertiesMap = dict(map(lambda x: (x["name"], x["object"]), datamodel["project"]["ontologies"][0]["properties"]))

    reslist = []
    for res in resources:
        oneres = {"resname": res["name"], "props": []}
        for prop in res["cardinalities"]:
            tmp = prop["propname"].split(":")
            if tmp[0] == '':
                p = propertiesMap.get(tmp[1])
                if p:
                    oneres["props"].append({"propname": prop["propname"], "proptype": p})
            else:
                pass  # ToDo: treat here properties from external ontolopgies
        reslist.append(oneres)
        
    print(reslist)

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
