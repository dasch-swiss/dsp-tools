from rdflib import Graph


def construct_resource_class_node_shape(onto: Graph) -> Graph:
    """
    Returns the sh:NodeShapes for the resource classes in the ontology.

    Args:
        onto: ontology graph

    Returns:
        Graph with the resource class node shapes
    """
    return _construct_resource_nodeshape(onto)


def _construct_resource_nodeshape(onto_graph: Graph) -> Graph:
    query_s = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#> 
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX api-shapes: <http://api.knora.org/ontology/knora-api/shapes/v2#>
    PREFIX knora-api:  <http://api.knora.org/ontology/knora-api/v2#>

    CONSTRUCT {

        ?shapesIRI a sh:NodeShape ;
                sh:targetClass ?class ;
                sh:property api-shapes:RDFS_label ;
                sh:ignoredProperties ( rdf:type ) ;
                sh:closed true .

    } WHERE {

        ?class a owl:Class ;
               knora-api:isResourceClass true .

        BIND(IRI(CONCAT(str(?class), "_Shape")) AS ?shapesIRI)
    }
    """
    if results_graph := onto_graph.query(query_s).graph:
        return results_graph
    return Graph()


def _construct_1_cardinality(onto_graph: Graph) -> Graph:
    query_s = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#> 
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX salsah-gui: <http://api.knora.org/ontology/salsah-gui/v2#> 
    PREFIX api-shapes: <http://api.knora.org/ontology/knora-api/shapes/v2#>
    PREFIX knora-api:  <http://api.knora.org/ontology/knora-api/v2#>
    
    CONSTRUCT {
    
      ?shapesIRI sh:property [
          a sh:PropertyShape ;
          sh:path ?propRestriction ;
          sh:minCount ?cardinality ;
          sh:maxCount ?cardinality ;
          sh:severity sh:Violation ;
          sh:message "Cardinality: 1" ;
      ] .
    
    } WHERE {
    
      ?class a owl:Class ;
          knora-api:isResourceClass true ;
          rdfs:subClassOf ?restriction .
      ?restriction a owl:Restriction ;
          owl:onProperty ?propRestriction ;
          salsah-gui:guiOrder ?order ;
          owl:cardinality ?cardinality .
    
      BIND(IRI(CONCAT(str(?class), "_Shape")) AS ?shapesIRI)
    }
    """
    if results_graph := onto_graph.query(query_s).graph:
        return results_graph
    return Graph()


def _construct_0_1_cardinality(onto_graph: Graph) -> Graph:
    query_s = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#> 
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX salsah-gui: <http://api.knora.org/ontology/salsah-gui/v2#> 
    PREFIX api-shapes: <http://api.knora.org/ontology/knora-api/shapes/v2#>
    PREFIX knora-api:  <http://api.knora.org/ontology/knora-api/v2#>


    }
    """
    if results_graph := onto_graph.query(query_s).graph:
        return results_graph
    return Graph()


def _construct_1_n_cardinality(onto_graph: Graph) -> Graph:
    query_s = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#> 
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX salsah-gui: <http://api.knora.org/ontology/salsah-gui/v2#> 
    PREFIX api-shapes: <http://api.knora.org/ontology/knora-api/shapes/v2#>
    PREFIX knora-api:  <http://api.knora.org/ontology/knora-api/v2#>


    }
    """
    if results_graph := onto_graph.query(query_s).graph:
        return results_graph
    return Graph()


def _construct_0_n_cardinality(onto_graph: Graph) -> Graph:
    query_s = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#> 
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX salsah-gui: <http://api.knora.org/ontology/salsah-gui/v2#> 
    PREFIX api-shapes: <http://api.knora.org/ontology/knora-api/shapes/v2#>
    PREFIX knora-api:  <http://api.knora.org/ontology/knora-api/v2#>


    }
    """
    if results_graph := onto_graph.query(query_s).graph:
        return results_graph
    return Graph()
