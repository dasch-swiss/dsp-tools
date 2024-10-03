from rdflib import Graph


def construct_property_shapes(onto: Graph) -> Graph:
    """
    Returns the sh:PropertyShape for the properties in the ontology.

    Args:
        onto: ontology graph

    Returns:
        Graph with the property shapes
    """
    return _construct_property_type_shape(onto)


def _construct_property_type_shape(onto: Graph) -> Graph:
    property_type_mapper = {}
    g = Graph()
    for object_type, shacl_shape in property_type_mapper.items():
        g += _construct_one_property_type_shape(onto, object_type, shacl_shape)
    return g


def _construct_one_property_type_shape(onto: Graph, object_type: str, shacl_shape: str) -> Graph:
    query_s = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#> 
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX api-shapes: <http://api.knora.org/ontology/knora-api/shapes/v2#>
    PREFIX knora-api:  <http://api.knora.org/ontology/knora-api/v2#>
    PREFIX salsah-gui: <http://api.knora.org/ontology/salsah-gui/v2#>
    
    CONSTRUCT {
        
        ?shapesIRI a sh:PropertyShape ;
                   sh:path ?prop ;
                   sh:node api-shapes:BooleanValue_ClassShape .
    
    } WHERE {
      
        ?prop a owl:ObjectProperty ;
                knora-api:objectType knora-api:BooleanValue .
      
        BIND(IRI(CONCAT(str(?prop), "_PropShape")) AS ?shapesIRI)
    }
    """
    if results_graph := onto.query(query_s).graph:
        return results_graph
    return Graph()
