from rdflib import Graph

from dsp_tools.commands.validate_data.models.api_responses import AllProjectLists
from dsp_tools.commands.validate_data.models.validation import SHACLGraphs
from dsp_tools.commands.validate_data.sparql.cardinality_shacl import construct_cardinality_node_shapes
from dsp_tools.commands.validate_data.sparql.file_value_shacl import construct_file_value_cardinality
from dsp_tools.commands.validate_data.sparql.value_shacl import construct_property_shapes


def construct_shapes_graphs(onto: Graph, project_lists: AllProjectLists) -> SHACLGraphs:
    """
    Constructs a shapes graph from a project ontology

    Args:
        onto: ontology as graph
        project_lists: the lists of a project

    Returns:
        shapes graph
    """
    cardinality = construct_cardinality_node_shapes(onto)
    content = construct_property_shapes(onto, project_lists)
    file_values = construct_file_value_cardinality(onto)
    cardinality += file_values
    return SHACLGraphs(cardinality=cardinality, content=content)
