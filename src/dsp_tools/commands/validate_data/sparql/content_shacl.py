from rdflib import Graph

from dsp_tools.commands.validate_data.sparql.value_shacl import construct_property_shapes


def construct_content_shapes_graph(onto: Graph) -> Graph:
    """
    Constructs a shapes graph from a project ontology

    Args:
        onto: ontology as graph

    Returns:
        shapes graph
    """
    return construct_property_shapes(onto)
