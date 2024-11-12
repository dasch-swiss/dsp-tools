from rdflib import Graph
from rdflib import Namespace

API_SHAPES = Namespace("http://api.knora.org/ontology/knora-api/shapes/v2#")


def construct_file_value_cardinality(onto: Graph) -> Graph:
    """
    Returns cardinalities for classes with a file value.

    Args:
        onto: project ontologies

    Returns:
        Graph with file cardinalities
    """
    g = Graph()
    g += _construct_generic_file_value_cardinality(onto)
    return g


def _construct_generic_file_value_cardinality(onto: Graph) -> Graph:
    query_s = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#> 
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX api-shapes: <http://api.knora.org/ontology/knora-api/shapes/v2#>
    PREFIX knora-api:  <http://api.knora.org/ontology/knora-api/v2#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
    PREFIX dash: <http://datashapes.org/dash#>

    CONSTRUCT {
        ?class sh:property [
                              a sh:PropertyShape ;
                              sh:path api-shapes:hasGenericFileValue ;
                              sh:minCount 1 ;
                              sh:maxCount 1 ;
                              sh:severity sh:Violation ;
                              sh:message "A file is required for this resource" ;
                            ] .
    } WHERE {
        ?class a owl:Class ;
               rdfs:subClassOf ?superClass .
        VALUES ?superClass {
            knora-api:ArchiveRepresentation
            knora-api:AudioRepresentation
            knora-api:DocumentRepresentation
            knora-api:MovingImageRepresentation
            knora-api:StillImageRepresentation
            knora-api:TextRepresentation
        }
    }
    """
    if results_graph := onto.query(query_s).graph:
        return results_graph
    return Graph()

def _construct_moving_image_representation(onto: Graph) -> Graph:
    pass