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
                    print(tmp)
                    # TODO: handle this case
            else:
                print(tmp)
                # TODO: handle this case
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
            # TODO: not always correct (green boxes!)
            else:  # Here Nodes are connected with literals
                temp = propType["proptype"]

                G.add_node(temp, shape='box', style='filled', fillcolor='#95f0b0')
                G.add_edge(resProps["resname"], temp, label=propType["propname"])

    # G.layout()
    # G.draw("graph.dot")
    # TODO: pass out file as argument
    # TODO: find good way of handling different layouts
    # TODO: fix rotation of output
    G.draw('OntologyGraph1.pdf', prog='neato')  # Differente layouts: prog=neato|dot|twopi|circo|fdp|nop
    G.draw('OntologyGraph2.pdf', prog='dot')  # Differente layouts: prog=neato|dot|twopi|circo|fdp|nop
    G.draw('OntologyGraph3.pdf', prog='twopi')  # Differente layouts: prog=neato|dot|twopi|circo|fdp|nop
    G.draw('OntologyGraph4.pdf', prog='circo')  # Differente layouts: prog=neato|dot|twopi|circo|fdp|nop
    G.draw('OntologyGraph5.pdf', prog='fdp')  # Differente layouts: prog=neato|dot|twopi|circo|fdp|nop
    # G.draw('OntologyGraph6.pdf', prog='nop')  # Differente layouts: prog=neato|dot|twopi|circo|fdp|nop
