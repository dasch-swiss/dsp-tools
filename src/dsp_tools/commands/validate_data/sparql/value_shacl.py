from rdflib import Graph

from dsp_tools.commands.validate_data.models.api_responses import AllProjectLists
from dsp_tools.commands.validate_data.models.api_responses import OneList


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
    g += _construct_link_value_shape(onto)
    g += _construct_link_value_node_shape(onto)
    g += _construct_property_type_text_value(onto)
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

      ?class sh:property ?propShapesIRI .

    } WHERE {

      ?class a owl:Class ;
          knora-api:isResourceClass true ;
          knora-api:canBeInstantiated true ;
          rdfs:subClassOf ?restriction .
      ?restriction a owl:Restriction ;          
          owl:onProperty ?propRestriction ;
          salsah-gui:guiOrder ?order .
      FILTER NOT EXISTS { ?propRestriction knora-api:isLinkValueProperty true }

      BIND(IRI(CONCAT(str(?propRestriction), "_PropShape")) AS ?propShapesIRI)
    }
    """
    if results_graph := onto.query(query_s).graph:
        return results_graph
    return Graph()


def _construct_property_type_shape_based_on_object_type(onto: Graph) -> Graph:
    def as_object_type_and_shacl_shape(property_type: str) -> tuple[str, str]:
        return "knora-api:" + property_type + "Value", "api-shapes:" + property_type + "Value_ClassShape"

    property_types = {"Boolean", "Color", "Date", "Decimal", "Geoname", "Int", "List", "Time", "Uri"}

    g = Graph()
    for t in property_types:
        object_type, shacl_shape = as_object_type_and_shacl_shape(t)
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


def _construct_link_value_shape(onto: Graph) -> Graph:
    query_s = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#> 
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX api-shapes: <http://api.knora.org/ontology/knora-api/shapes/v2#>
    PREFIX knora-api:  <http://api.knora.org/ontology/knora-api/v2#>
    PREFIX salsah-gui: <http://api.knora.org/ontology/salsah-gui/v2#>

    CONSTRUCT {

        ?shapesIRI a sh:PropertyShape ;
                   sh:path ?prop ;
                   sh:node api-shapes:LinkValue_ClassShape , ?nodeShapeIRI .

    } WHERE {

        ?prop a owl:ObjectProperty ;
                salsah-gui:guiElement salsah-gui:Searchbox .

        BIND(IRI(CONCAT(str(?prop), "_PropShape")) AS ?shapesIRI)
        BIND(IRI(CONCAT(str(?prop), "_NodeShape")) AS ?nodeShapeIRI)
    }
    """
    if results_graph := onto.query(query_s).graph:
        return results_graph
    return Graph()


def _construct_link_value_node_shape(onto: Graph) -> Graph:
    query_s = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#> 
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX api-shapes: <http://api.knora.org/ontology/knora-api/shapes/v2#>
    PREFIX knora-api:  <http://api.knora.org/ontology/knora-api/v2#>
    PREFIX salsah-gui: <http://api.knora.org/ontology/salsah-gui/v2#>

    CONSTRUCT {

        ?nodeShapeIRI a sh:NodeShape ;
            sh:property    [
                                a            sh:PropertyShape ;
                                sh:path      api-shapes:linkValueHasTargetID ;
                                sh:class     ?rangeClass ;
                                sh:message   ?rangeString ;
                            ] ;
            sh:severity    sh:Violation .

    } WHERE {

        ?prop a owl:ObjectProperty ;
                knora-api:isLinkProperty true ;
                knora-api:objectType ?rangeClass .

        BIND(IRI(CONCAT(str(?prop), "_NodeShape")) AS ?nodeShapeIRI)
        BIND(STRAFTER(STR(?rangeClass), "#") AS ?rangeString )
    }
    """
    if results_graph := onto.query(query_s).graph:
        return results_graph
    return Graph()


def _construct_property_type_text_value(onto: Graph) -> Graph:
    property_type_mapper = {
        "salsah-gui:SimpleText": "api-shapes:SimpleTextValue_ClassShape",
        "salsah-gui:Textarea": "api-shapes:SimpleTextValue_ClassShape",
        "salsah-gui:Richtext": "api-shapes:FormattedTextValue_ClassShape",
    }
    g = Graph()
    for object_type, shacl_shape in property_type_mapper.items():
        g += _construct_one_property_type_text_value(onto, object_type, shacl_shape)
    return g


def _construct_one_property_type_text_value(onto: Graph, gui_element: str, shacl_shape: str) -> Graph:
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
                knora-api:objectType knora-api:TextValue ;
                salsah-gui:guiElement %(gui_element)s .

        BIND(IRI(CONCAT(str(?prop), "_PropShape")) AS ?shapesIRI)
    }
    """ % {"gui_element": gui_element, "shacl_shape": shacl_shape}  # noqa: UP031 (printf-string-formatting)
    if results_graph := onto.query(query_s).graph:
        return results_graph
    return Graph()


def construct_list_property_shapes(onto: Graph, project_lists: AllProjectLists) -> Graph:
    pass


def _construct_one_list_property_shape(onto: Graph, one_list: OneList) -> Graph:
    pass


"""
onto-shapes:onlyList_NodeShape
  a           sh:NodeShape ;
  sh:name     "Validates the content of the ListValue with the specific property." ;
  sh:property [
                a         sh:PropertyShape ;
                sh:path   val-onto:hasValue ;
                sh:in     ( "n1" "n1.1" "n1.1.1" ) ;
                sh:message "Unknown list node for list 'onlyList'."
              ] ,
              [
                a               sh:PropertyShape ;
                sh:path         val-onto:hasListName ;
                sh:in           ( "onlyList" ) ;
                sh:message      "The list that should be used with this property is 'onlyList'."
              ] ;
  sh:severity sh:Violation .

"""
