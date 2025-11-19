from loguru import logger
from rdflib import Graph


def construct_cardinality_node_shapes(onto: Graph) -> Graph:
    """
    Returns the sh:NodeShapes for the resource classes in the ontology.

    Args:
        onto: ontology graph

    Returns:
        Graph with the resource class node shapes
    """
    logger.debug("Constructing cardinality shapes for the ontology.")
    g = Graph()
    g += _construct_resource_nodeshape(onto)
    g += _construct_all_cardinalities(onto)
    return g


def _construct_resource_nodeshape(onto_graph: Graph) -> Graph:
    logger.debug("Constructing resource NodeShape")
    query_s = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#> 
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX api-shapes: <http://api.knora.org/ontology/knora-api/shapes/v2#>
    PREFIX knora-api:  <http://api.knora.org/ontology/knora-api/v2#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
    PREFIX dash: <http://datashapes.org/dash#>

    CONSTRUCT {
        ?class a sh:NodeShape ;
                dash:closedByTypes true ;
                sh:property api-shapes:hasPermissions_Cardinality ,
                            [
                              a sh:PropertyShape ;
                              sh:path rdfs:label ;
                              sh:minCount 1 ;
                              sh:maxCount 1 ;
                              sh:severity sh:Violation ;
                              sh:message "A label is required" 
                            ] ,
                            [ 
                              a sh:PropertyShape ;
                              sh:path knora-api:hasStandoffLinkTo
                            ] .
    } WHERE {
        ?class a owl:Class ;
               knora-api:isResourceClass true ;
               knora-api:canBeInstantiated true .
    }
    """
    if results_graph := onto_graph.query(query_s).graph:
        return results_graph
    return Graph()


def _construct_all_cardinalities(onto_graph: Graph) -> Graph:
    g = Graph()
    g += _construct_1_cardinality(onto_graph)
    g += _construct_0_1_cardinality(onto_graph)
    g += _construct_1_n_cardinality(onto_graph)
    g += _construct_0_n_cardinality(onto_graph)
    return g


def _construct_1_cardinality(onto_graph: Graph) -> Graph:
    logger.debug("Constructing cardinality: 1")
    query_s = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#> 
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX api-shapes: <http://api.knora.org/ontology/knora-api/shapes/v2#>
    PREFIX knora-api:  <http://api.knora.org/ontology/knora-api/v2#>
    PREFIX dash: <http://datashapes.org/dash#>

    CONSTRUCT {
      ?class sh:property [
          a sh:PropertyShape ;
          sh:path ?propRestriction ;
          sh:minCount 1 ;
          sh:maxCount 1 ;
          sh:severity sh:Violation ;
          sh:message "Cardinality 1" 
      ] .
    } WHERE {
      ?class a owl:Class ;
          knora-api:isResourceClass true ;
          knora-api:canBeInstantiated true ;
          rdfs:subClassOf ?restriction .
      ?restriction a owl:Restriction ;
          owl:onProperty ?propRestriction ;
          owl:cardinality 1 .
          
      ?propRestriction knora-api:isEditable true .
      FILTER NOT EXISTS { ?propRestriction knora-api:isLinkValueProperty true }
    }
    """
    if results_graph := onto_graph.query(query_s).graph:
        return results_graph
    return Graph()


def _construct_0_1_cardinality(onto_graph: Graph) -> Graph:
    logger.debug("Constructing cardinality: 0-1")
    query_s = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#> 
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX api-shapes: <http://api.knora.org/ontology/knora-api/shapes/v2#>
    PREFIX knora-api:  <http://api.knora.org/ontology/knora-api/v2#>
    PREFIX dash: <http://datashapes.org/dash#>

    CONSTRUCT {
      ?class sh:property [
          a sh:PropertyShape ;
          sh:path ?propRestriction ;
          sh:minCount 0 ;
          sh:maxCount 1 ;
          sh:severity sh:Violation ;
          sh:message "Cardinality 0-1" 
      ] .
    } WHERE {
      ?class a owl:Class ;
          knora-api:isResourceClass true ;
          knora-api:canBeInstantiated true ;
          rdfs:subClassOf ?restriction .
      ?restriction a owl:Restriction ;
          owl:onProperty ?propRestriction ;
          owl:maxCardinality 1 .
          
      ?propRestriction knora-api:isEditable true .
      FILTER NOT EXISTS { ?propRestriction knora-api:isLinkValueProperty true }
    }
    """
    if results_graph := onto_graph.query(query_s).graph:
        return results_graph
    return Graph()


def _construct_1_n_cardinality(onto_graph: Graph) -> Graph:
    logger.debug("Constructing cardinality: 1-n")
    query_s = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#> 
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX api-shapes: <http://api.knora.org/ontology/knora-api/shapes/v2#>
    PREFIX knora-api:  <http://api.knora.org/ontology/knora-api/v2#>
    PREFIX dash: <http://datashapes.org/dash#>

    CONSTRUCT {
      ?class sh:property [
          a sh:PropertyShape ;
          sh:path ?propRestriction ;
          sh:minCount 1 ;
          sh:severity sh:Violation ;
          sh:message "Cardinality 1-n" 
      ] .
    } WHERE {
      ?class a owl:Class ;
          knora-api:isResourceClass true ;
          knora-api:canBeInstantiated true ;
          rdfs:subClassOf ?restriction .
      ?restriction a owl:Restriction ;
          owl:onProperty ?propRestriction ;
          owl:minCardinality 1 .
          
      ?propRestriction knora-api:isEditable true .
      FILTER NOT EXISTS { ?propRestriction knora-api:isLinkValueProperty true }
    }
    """
    if results_graph := onto_graph.query(query_s).graph:
        return results_graph
    return Graph()


def _construct_0_n_cardinality(onto_graph: Graph) -> Graph:
    logger.debug("Constructing cardinality: 0-n")
    query_s = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#> 
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX api-shapes: <http://api.knora.org/ontology/knora-api/shapes/v2#>
    PREFIX knora-api:  <http://api.knora.org/ontology/knora-api/v2#>
    PREFIX dash: <http://datashapes.org/dash#>

    CONSTRUCT {
      ?class sh:property [
          a sh:PropertyShape ;
          sh:path ?propRestriction 
      ] .
    } WHERE {
      ?class a owl:Class ;
          knora-api:isResourceClass true ;
          knora-api:canBeInstantiated true ;
          rdfs:subClassOf ?restriction .
      ?restriction a owl:Restriction ;
          owl:onProperty ?propRestriction ;
          owl:minCardinality 0 .
          
      ?propRestriction knora-api:isEditable true .
      FILTER NOT EXISTS { ?propRestriction knora-api:isLinkValueProperty true }
    }
    """
    if results_graph := onto_graph.query(query_s).graph:
        return results_graph
    return Graph()
