from rdflib import Graph

from dsp_tools.commands.validate_data.sparql.cardinality_shacl import construct_cardinality_node_shapes
from dsp_tools.commands.validate_data.sparql.value_shacl import construct_property_shapes


def construct_shapes_graph(onto: Graph) -> Graph:
    """
    Constructs a shapes graph from a project ontology

    Args:
        onto: ontology as graph

    Returns:
        shapes graph
    """
    g = construct_cardinality_node_shapes(onto)
    return g + construct_property_shapes(onto)
