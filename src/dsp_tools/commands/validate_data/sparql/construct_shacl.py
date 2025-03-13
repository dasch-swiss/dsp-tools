from loguru import logger
from rdflib import Graph

from dsp_tools.commands.validate_data.models.api_responses import AllProjectLists
from dsp_tools.commands.validate_data.models.validation import SHACLGraphs
from dsp_tools.commands.validate_data.sparql.cardinality_shacl import construct_cardinality_node_shapes
from dsp_tools.commands.validate_data.sparql.legal_info_shacl import construct_allowed_licenses_shape
from dsp_tools.commands.validate_data.sparql.value_shacl import construct_property_shapes


def construct_shapes_graphs(onto: Graph, knora_api: Graph, project_lists: AllProjectLists) -> SHACLGraphs:
    """
    Constructs a shapes graph from a project ontology

    Args:
        onto: ontology as graph
        knora_api: the knora-api ontology
        project_lists: the lists of a project

    Returns:
        shapes graph
    """
    logger.info("Constructing SHACL shapes from ontology.")
    knora_subset = _get_all_relevant_knora_subset(knora_api)
    graph_to_query = knora_subset + onto
    cardinality = construct_cardinality_node_shapes(graph_to_query)
    content = construct_property_shapes(graph_to_query, project_lists)
    content += construct_allowed_licenses_shape()
    return SHACLGraphs(cardinality=cardinality, content=content)


def _get_all_relevant_knora_subset(knora_api: Graph) -> Graph:
    logger.info("Getting relevant knora-api subset")
    props = ["isLinkProperty", "isEditable", "isLinkValueProperty"]
    g = Graph()
    for p in props:
        g += _get_one_relevant_knora_subset(knora_api, p)
    return g


def _get_one_relevant_knora_subset(knora_api: Graph, knora_prop: str) -> Graph:
    query_s = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#> 
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX knora-api:  <http://api.knora.org/ontology/knora-api/v2#>

    CONSTRUCT {
    
      ?focusProp a owl:ObjectProperty ;
                 knora-api:objectType ?type ;
                 knora-api:%(knora_prop)s ?object .
      
    } WHERE {
      
      ?focusProp a owl:ObjectProperty ;
                 knora-api:objectType ?type ;
                 knora-api:%(knora_prop)s ?object .
      
    }
    """ % {"knora_prop": knora_prop}  # noqa: UP031 (printf-string-formatting)
    if results_graph := knora_api.query(query_s).graph:
        return results_graph
    return Graph()
