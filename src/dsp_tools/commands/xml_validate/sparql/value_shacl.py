from rdflib import Graph


def construct_property_shapes(onto: Graph) -> Graph:
    """
    Returns the sh:PropertyShape for the properties in the ontology.

    Args:
        onto: ontology graph

    Returns:
        Graph with the property shapes
    """
    g = Graph()
    g += _construct_property_type_shape_based_on_object_type(onto)
    g += _construct_property_type_shape_based_on_gui_element(onto)
    return g + _add_property_shapes_to_class_shapes(onto)


def _add_property_shapes_to_class_shapes(onto: Graph) -> Graph:
    query_s = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#> 
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX salsah-gui: <http://api.knora.org/ontology/salsah-gui/v2#> 
    PREFIX api-shapes: <http://api.knora.org/ontology/knora-api/shapes/v2#>
    PREFIX knora-api:  <http://api.knora.org/ontology/knora-api/v2#>

    CONSTRUCT {

      ?classShapeIRI sh:property ?propShapesIRI .

    } WHERE {

      ?class a owl:Class ;
          knora-api:isResourceClass true ;
          knora-api:canBeInstantiated true ;
          rdfs:subClassOf ?restriction .
      ?restriction a owl:Restriction ;
          owl:onProperty ?propRestriction ;
          salsah-gui:guiOrder ?order .
      FILTER NOT EXISTS { ?propRestriction knora-api:isLinkValueProperty true }

      BIND(IRI(CONCAT(str(?class), "_Shape")) AS ?classShapeIRI)
      BIND(IRI(CONCAT(str(?propRestriction), "_PropShape")) AS ?propShapesIRI)
    }
    """
    if results_graph := onto.query(query_s).graph:
        return results_graph
    return Graph()


def _construct_property_type_shape_based_on_object_type(onto: Graph) -> Graph:
    property_type_mapper = {
        "knora-api:BooleanValue": "api-shapes:BooleanValue_ClassShape",
        "knora-api:ColorValue": "api-shapes:ColorValue_ClassShape",
        "knora-api:DateValue": "api-shapes:DateValue_ClassShape",
        "knora-api:DecimalValue": "api-shapes:DecimalValue_ClassShape",
        "knora-api:GeonameValue": "api-shapes:GeonameValue_ClassShape",
        "knora-api:IntValue": "api-shapes:IntValue_ClassShape",
        "knora-api:ListValue": "api-shapes:ListValue_ClassShape",
        "knora-api:TimeValue": "api-shapes:TimeValue_ClassShape",
        "knora-api:UriValue": "api-shapes:UriValue_ClassShape",
    }
    g = Graph()
    for object_type, shacl_shape in property_type_mapper.items():
        g += _construct_one_property_type_shape_based_on_object_type(onto, object_type, shacl_shape)
    return g


def _construct_one_property_type_shape_based_on_object_type(onto: Graph, object_type: str, shacl_shape: str) -> Graph:
    query_s = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#> 
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX api-shapes: <http://api.knora.org/ontology/knora-api/shapes/v2#>
    PREFIX knora-api:  <http://api.knora.org/ontology/knora-api/v2#>
    PREFIX salsah-gui: <http://api.knora.org/ontology/salsah-gui/v2#>
    
    CONSTRUCT {
        
        ?shapesIRI a sh:PropertyShape ;
                   sh:path ?prop ;
                   sh:node %(shacl_shape)s .
    
    } WHERE {
      
        ?prop a owl:ObjectProperty ;
                knora-api:objectType %(object_type)s .
      
        BIND(IRI(CONCAT(str(?prop), "_PropShape")) AS ?shapesIRI)
    }
    """ % {"object_type": object_type, "shacl_shape": shacl_shape}  # noqa: UP031 (printf-string-formatting)
    if results_graph := onto.query(query_s).graph:
        return results_graph
    return Graph()


def _construct_property_type_shape_based_on_gui_element(onto: Graph) -> Graph:
    property_type_mapper = {
        "salsah-gui:SimpleText": "api-shapes:SimpleTextValue_ClassShape",
        "salsah-gui:Textarea": "api-shapes:SimpleTextValue_ClassShape",
        "salsah-gui:Richtext": "api-shapes:FormattedTextValue_ClassShape",
        "salsah-gui:Searchbox": "api-shapes:LinkValue_ClassShape",
    }
    g = Graph()
    for object_type, shacl_shape in property_type_mapper.items():
        g += _construct_one_property_type_shape_gui_element(onto, object_type, shacl_shape)
    return g


def _construct_one_property_type_shape_gui_element(onto: Graph, gui_element: str, shacl_shape: str) -> Graph:
    query_s = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#> 
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX api-shapes: <http://api.knora.org/ontology/knora-api/shapes/v2#>
    PREFIX knora-api:  <http://api.knora.org/ontology/knora-api/v2#>
    PREFIX salsah-gui: <http://api.knora.org/ontology/salsah-gui/v2#>

    CONSTRUCT {

        ?shapesIRI a sh:PropertyShape ;
                   sh:path ?prop ;
                   sh:node %(shacl_shape)s .

    } WHERE {

        ?prop a owl:ObjectProperty ;
                salsah-gui:guiElement %(gui_element)s .

        BIND(IRI(CONCAT(str(?prop), "_PropShape")) AS ?shapesIRI)
    }
    """ % {"gui_element": gui_element, "shacl_shape": shacl_shape}  # noqa: UP031 (printf-string-formatting)
    if results_graph := onto.query(query_s).graph:
        return results_graph
    return Graph()
