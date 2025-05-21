from loguru import logger
from rdflib import Graph

from dsp_tools.commands.validate_data.models.api_responses import OneList


def construct_property_shapes(onto: Graph, project_lists: list[OneList]) -> Graph:
    """
    Returns the sh:PropertyShape for the properties in the ontology.

    Args:
        onto: ontology graph
        project_lists: all lists from a project

    Returns:
        Graph with the property shapes
    """
    logger.info("Constructing property shapes for ontology.")
    g = Graph()
    g += _construct_link_value_shape(onto)
    g += _construct_link_value_node_shape(onto)
    g += _construct_property_type_text_value(onto)
    g += _construct_list_shapes(onto, project_lists)
    g += _construct_seqnum_is_part_of_prop_shape(onto)
    g += _construct_value_type_shapes_to_class_shapes(onto)
    g += _construct_link_value_type_shapes_to_class_shapes(onto)
    return g + _add_property_shapes_to_class_shapes(onto)


def _add_property_shapes_to_class_shapes(onto: Graph) -> Graph:
    logger.info("Add property shape to resources")
    query_s = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#> 
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX api-shapes: <http://api.knora.org/ontology/knora-api/shapes/v2#>
    PREFIX knora-api:  <http://api.knora.org/ontology/knora-api/v2#>

    CONSTRUCT {

      ?class a sh:NodeShape ;
             sh:property ?propShapesIRI .
    
    } WHERE {

      ?class a owl:Class ;
          knora-api:isResourceClass true ;
          knora-api:canBeInstantiated true ;
          rdfs:subClassOf ?restriction .
      ?restriction a owl:Restriction ;          
          owl:onProperty ?propRestriction .
          
      ?propRestriction knora-api:isEditable true .
      FILTER NOT EXISTS { ?propRestriction knora-api:isLinkValueProperty true }

      BIND(IRI(CONCAT(str(?propRestriction), "_PropShape")) AS ?propShapesIRI)
    }
    """
    if results_graph := onto.query(query_s).graph:
        return results_graph
    return Graph()


def _construct_value_type_shapes_to_class_shapes(onto: Graph) -> Graph:
    logger.info("Add value type shape to resources")
    query_s = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#> 
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX api-shapes: <http://api.knora.org/ontology/knora-api/shapes/v2#>
    PREFIX knora-api:  <http://api.knora.org/ontology/knora-api/v2#>

    CONSTRUCT {

      ?shapesIRI a sh:PropertyShape ;
                sh:path ?propRestriction ;
                sh:class ?objectType ;
                sh:message ?objectTypeMessage .

    } WHERE {

      ?class a owl:Class ;
          knora-api:isResourceClass true ;
          knora-api:canBeInstantiated true ;
          rdfs:subClassOf ?restriction .
      ?restriction a owl:Restriction ;          
          owl:onProperty ?propRestriction .

      ?propRestriction knora-api:isEditable true ;
                       knora-api:objectType ?objectType .

      FILTER NOT EXISTS { ?propRestriction knora-api:isLinkProperty true }
      FILTER NOT EXISTS { ?propRestriction knora-api:isLinkValueProperty true }
      
      BIND(IRI(CONCAT(str(?propRestriction), "_PropShape")) AS ?shapesIRI)
      BIND(CONCAT("This property requires a ", STRAFTER(STR(?objectType), "#")) AS ?objectTypeMessage)
    }
    """
    if results_graph := onto.query(query_s).graph:
        return results_graph
    return Graph()


def _construct_link_value_type_shapes_to_class_shapes(onto: Graph) -> Graph:
    logger.info("Add value type shape to resources")
    query_s = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#> 
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX api-shapes: <http://api.knora.org/ontology/knora-api/shapes/v2#>
    PREFIX knora-api:  <http://api.knora.org/ontology/knora-api/v2#>

    CONSTRUCT {

      ?shapesIRI a sh:PropertyShape ;
                 sh:path ?propRestriction ;
                 sh:class knora-api:LinkValue ;
                 sh:message "This property requires a LinkValue" .

    } WHERE {

      ?class a owl:Class ;
          knora-api:isResourceClass true ;
          knora-api:canBeInstantiated true ;
          rdfs:subClassOf ?restriction .
      ?restriction a owl:Restriction ;          
          owl:onProperty ?propRestriction .

      ?propRestriction knora-api:isEditable true ;
                       knora-api:isLinkProperty true .

      BIND(IRI(CONCAT(str(?propRestriction), "_PropShape")) AS ?shapesIRI)
    }
    """
    if results_graph := onto.query(query_s).graph:
        return results_graph
    return Graph()


def _construct_link_value_shape(onto: Graph) -> Graph:
    logger.info("Constructing LinkValue PropertyShape")
    query_s = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#> 
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX api-shapes: <http://api.knora.org/ontology/knora-api/shapes/v2#>
    PREFIX knora-api:  <http://api.knora.org/ontology/knora-api/v2#>
    PREFIX salsah-gui: <http://api.knora.org/ontology/salsah-gui/v2#>

    CONSTRUCT {

        ?shapesIRI a sh:PropertyShape ;
                   sh:path ?prop ;
                   sh:node ?nodeShapeIRI .

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
    logger.info("Constructing LinkValue NodeShape")
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
                                sh:message   ?msg ;
                            ] ;
            sh:severity    sh:Violation .

    } WHERE {

        ?prop a owl:ObjectProperty ;
                knora-api:isLinkProperty true ;
                knora-api:objectType ?rangeClass .

        BIND(IRI(CONCAT(str(?prop), "_NodeShape")) AS ?nodeShapeIRI)
        BIND(CONCAT("Range is ", str(?rangeClass), " or a subclass") AS ?msg)
    }
    """
    if results_graph := onto.query(query_s).graph:
        return results_graph
    return Graph()


def _construct_property_type_text_value(onto: Graph) -> Graph:
    property_type_mapper = {
        "salsah-gui:SimpleText": "api-shapes:SimpleTextValue_ClassShape",
        "salsah-gui:Textarea": "api-shapes:TextareaTextValue_ClassShape",
        "salsah-gui:Richtext": "api-shapes:FormattedTextValue_ClassShape",
    }
    g = Graph()
    for object_type, shacl_shape in property_type_mapper.items():
        g += _construct_one_property_type_text_value(onto, object_type, shacl_shape)
    return g


def _construct_one_property_type_text_value(onto: Graph, gui_element: str, shacl_shape: str) -> Graph:
    logger.info(f"Constructing shape for {gui_element}")
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


def _construct_list_shapes(onto: Graph, project_lists: list[OneList]) -> Graph:
    lists_graph = Graph()
    for one_list in project_lists:
        lists_graph += _construct_one_list_node_shape(one_list)
    for one_list in project_lists:
        lists_graph += _construct_one_list_property_shape(onto, one_list)
    return lists_graph


def _construct_one_list_node_shape(one_list: OneList) -> Graph:
    formatted_iris = [f"<{x.iri}>" for x in one_list.nodes]
    list_nodes = " ".join(formatted_iris)
    # Turtle requires double quotes for its literals.
    # We do not want a multi-line message, therefore, we strip the newlines.
    msg = f"""
    "A valid node from the list '{one_list.list_name}' must be used with this property (input displayed in format 'listName / NodeName')."
    """.strip()  # noqa: E501
    ttl_str = """
    @prefix sh:         <http://www.w3.org/ns/shacl#> .
    @prefix knora-api:  <http://api.knora.org/ontology/knora-api/v2#> .

    <%(list_iri)s>
      a sh:NodeShape ;
      sh:property [
          a           sh:PropertyShape ;
          sh:path     knora-api:listValueAsListNode ;
          sh:in       ( %(list_nodes)s ) ;
          sh:message  %(msg)s ;
          sh:severity  sh:Violation
                  ] .
    """ % {"list_iri": one_list.list_iri, "list_nodes": list_nodes, "msg": msg}  # noqa: UP031
    g = Graph()
    g.parse(data=ttl_str, format="turtle")
    return g


def _construct_one_list_property_shape(onto: Graph, one_list: OneList) -> Graph:
    logger.info(f"Constructing Collection Shape for ListValue: {one_list.list_iri}")
    query_s = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#> 
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX api-shapes: <http://api.knora.org/ontology/knora-api/shapes/v2#>
    PREFIX knora-api:  <http://api.knora.org/ontology/knora-api/v2#>
    PREFIX salsah-gui: <http://api.knora.org/ontology/salsah-gui/v2#>

    CONSTRUCT {
        ?shapesIRI a sh:PropertyShape ;
                   sh:path ?prop ;
                   sh:node <%(list)s> ;
                   sh:severity sh:Violation .
    } WHERE {
        ?prop a owl:ObjectProperty ;
              knora-api:objectType knora-api:ListValue ;
              salsah-gui:guiAttribute %(guiAttribute)s .

        BIND(IRI(CONCAT(str(?prop), "_PropShape")) AS ?shapesIRI)
    }
    """ % {"guiAttribute": one_list.hlist(), "list": one_list.list_iri}  # noqa: UP031 (printf-string-formatting)
    if results_graph := onto.query(query_s).graph:
        return results_graph
    return Graph()


def _construct_seqnum_is_part_of_prop_shape(onto: Graph) -> Graph:
    logger.info("Constructing Collection Shape seqnum / isPartOf")
    query_s = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#> 
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX dash: <http://datashapes.org/dash#>
    PREFIX api-shapes: <http://api.knora.org/ontology/knora-api/shapes/v2#>
    PREFIX knora-api:  <http://api.knora.org/ontology/knora-api/v2#>
    PREFIX salsah-gui: <http://api.knora.org/ontology/salsah-gui/v2#>

    CONSTRUCT {
        ?resourceClass sh:property api-shapes:seqnum_PropShape .
    } WHERE {
        ?resourceClass rdfs:subClassOf ?restriction .
        ?restriction a owl:Restriction .
        {
            ?restriction owl:onProperty knora-api:seqnum .
        }
        UNION
        {
            ?restriction owl:onProperty knora-api:isPartOf .
        }
    }
    """
    # The API allows the ontology to declare cardinalities for seqnum without isPartOf and vice versa.
    # Therefore, we have a union query.
    if results_graph := onto.query(query_s).graph:
        return results_graph
    return Graph()
