from rdflib import Graph

from dsp_tools.commands.xml_validate.sparql.resource_shacl import construct_resource_class_node_shape


def construct_shapes_graph(onto: Graph) -> Graph:
    """
    Constructs a shapes graph from a project ontology

    Args:
        onto: ontology as graph

    Returns:
        shapes graph
    """
    return construct_resource_class_node_shape(onto)
