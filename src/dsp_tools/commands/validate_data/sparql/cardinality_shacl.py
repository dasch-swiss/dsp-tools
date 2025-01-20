from rdflib import Graph


def construct_cardinality_node_shapes(onto: Graph) -> Graph:
    """
    Returns the sh:NodeShapes for the resource classes in the ontology.

    Args:
        onto: ontology graph

    Returns:
        Graph with the resource class node shapes
    """
    g = Graph()
    g += _construct_resource_nodeshape(onto)
    g += _construct_all_cardinalities(onto)
    g += _construct_coexist_for_sub_props_of_seqnum(onto)
    return g


def _construct_resource_nodeshape(onto_graph: Graph) -> Graph:
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
                sh:property [
                              a sh:PropertyShape ;
                              sh:path rdfs:label ;
                              sh:minCount 1 ;
                              sh:maxCount 1 ;
                              sh:severity sh:Violation ;
                              sh:message "A label is required" ;
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
          sh:message "1" ;
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
      FILTER (?class NOT IN (
            knora-api:Region, knora-api:AudioSegment, knora-api:VideoSegment)
      )
      FILTER (?propRestriction NOT IN (
             knora-api:hasArchiveFileValue, knora-api:hasAudioFileValue, knora-api:hasDocumentFileValue, 
             knora-api:hasMovingImageFileValue, knora-api:hasStillImageFileValue, knora-api:hasTextFileValue
             )
      )
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
          sh:message "0-1" ;
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
      FILTER (?class NOT IN (
            knora-api:Region, knora-api:AudioSegment, knora-api:VideoSegment)
      )
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
    PREFIX api-shapes: <http://api.knora.org/ontology/knora-api/shapes/v2#>
    PREFIX knora-api:  <http://api.knora.org/ontology/knora-api/v2#>
    PREFIX dash: <http://datashapes.org/dash#>

    CONSTRUCT {
      ?class sh:property [
          a sh:PropertyShape ;
          sh:path ?propRestriction ;
          sh:minCount 1 ;
          sh:severity sh:Violation ;
          sh:message "1-n" ;
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
      FILTER (?class NOT IN (
            knora-api:Region, knora-api:AudioSegment, knora-api:VideoSegment)
      )
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
    PREFIX api-shapes: <http://api.knora.org/ontology/knora-api/shapes/v2#>
    PREFIX knora-api:  <http://api.knora.org/ontology/knora-api/v2#>
    PREFIX dash: <http://datashapes.org/dash#>

    CONSTRUCT {
      ?class sh:property [
          a sh:PropertyShape ;
          sh:path ?propRestriction ;
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
      FILTER (?class NOT IN (
            knora-api:Region, knora-api:AudioSegment, knora-api:VideoSegment)
      )
    }
    """
    if results_graph := onto_graph.query(query_s).graph:
        return results_graph
    return Graph()


def _construct_coexist_for_sub_props_of_seqnum(onto_graph: Graph) -> Graph:
    query_s = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX knora-api:  <http://api.knora.org/ontology/knora-api/v2#>
    PREFIX dash: <http://datashapes.org/dash#>
    
    CONSTRUCT {
        
      _:constructedShape
      a                 sh:PropertyShape ;
      sh:message        "The properties seqnum and isPartOf must be used together. This resource used only one of the properties." ;
      sh:path           ?seqnumProp ;
      dash:coExistsWith ?isPartOfProp ;
      sh:severity       sh:Violation .
    
    } WHERE {
      
        ?targetClass a owl:Class ;
                    rdfs:subClassOf ?restrictionIsPartOf .
        ?restrictionIsPartOf a owl:Restriction ;
                             owl:onProperty ?isPartOfProp .
        ?isPartOfProp rdfs:subPropertyOf* knora-api:isPartOf .
     
        ?targetClass a owl:Class ;
                      rdfs:subClassOf ?restrictionSeqnum .
        ?restrictionSeqnum a owl:Restriction ;
                               owl:onProperty ?seqnumProp .
        ?seqnumProp rdfs:subPropertyOf* knora-api:seqnum .
    }
    """  # noqa:E501 (line too long)
    if results_graph := onto_graph.query(query_s).graph:
        return results_graph
    return Graph()
