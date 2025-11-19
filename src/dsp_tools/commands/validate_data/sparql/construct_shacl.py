from loguru import logger
from rdflib import Graph

from dsp_tools.commands.validate_data.models.api_responses import ProjectDataFromApi
from dsp_tools.commands.validate_data.models.validation import SHACLGraphs
from dsp_tools.commands.validate_data.sparql.cardinality_shacl import construct_cardinality_node_shapes
from dsp_tools.commands.validate_data.sparql.legal_info_shacl import construct_allowed_licenses_shape
from dsp_tools.commands.validate_data.sparql.value_shacl import construct_property_shapes


def construct_shapes_graphs(
    onto: Graph,
    knora_api: Graph,
    project_info_from_api: ProjectDataFromApi,
    permission_ids: list[str],
) -> SHACLGraphs:
    """
    Constructs a shapes graph from a project ontology

    Args:
        onto: ontology as graph
        knora_api: the knora-api ontology
        project_info_from_api: information from a project from the api, for example lists
        permission_ids: ids of permissions that were defined in the XML

    Returns:
        shapes graph
    """
    logger.debug("Constructing SHACL shapes from ontology.")
    knora_subset = _get_all_relevant_knora_subset(knora_api)
    graph_to_query = knora_subset + onto
    cardinality = construct_cardinality_node_shapes(graph_to_query)
    content = construct_property_shapes(graph_to_query, project_info_from_api.all_lists)
    content += construct_allowed_licenses_shape(project_info_from_api.enabled_licenses)
    content += _get_defined_permissions_shape(permission_ids)
    return SHACLGraphs(cardinality=cardinality, content=content)


def _get_all_relevant_knora_subset(knora_api: Graph) -> Graph:
    logger.debug("Getting relevant knora-api subset")
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


def _get_defined_permissions_shape(permission_ids: list[str]) -> Graph:
    g = Graph()
    permissions = " ".join([f'"{x}"' for x in permission_ids])
    msg = f"You must reference one of the pre-defined permissions: {', '.join(permission_ids)}"
    shape = f"""
     @prefix sh:         <http://www.w3.org/ns/shacl#> .
     @prefix owl:        <http://www.w3.org/2002/07/owl#> .
     @prefix knora-api:  <http://api.knora.org/ontology/knora-api/v2#> .
     @prefix api-shapes: <http://api.knora.org/ontology/knora-api/shapes/v2#> .
     
     api-shapes:hasPermissions_Shape
       a              sh:NodeShape ;
       sh:targetClass knora-api:Value , knora-api:Resource ;
       sh:path        knora-api:hasPermissions ;
       sh:in          ( {permissions} ) ;
       sh:message     "{msg}" ;
       sh:severity    sh:Violation .
     """
    g.parse(data=shape, format="turtle")
    return g
