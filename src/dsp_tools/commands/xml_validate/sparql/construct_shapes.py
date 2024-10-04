from rdflib import Graph

from dsp_tools.commands.xml_validate.sparql.resource_shacl import construct_resource_class_node_shape
from dsp_tools.commands.xml_validate.sparql.value_shacl import construct_property_shapes


def construct_shapes_graph(onto: Graph) -> Graph:
    """
    Constructs a shapes graph from a project ontology

    Args:
        onto: ontology as graph

    Returns:
        shapes graph
    """
    shapes = construct_resource_class_node_shape(onto)
    shapes += construct_property_shapes(onto)
    return shapes
