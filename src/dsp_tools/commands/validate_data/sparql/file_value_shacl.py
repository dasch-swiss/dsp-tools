from loguru import logger
from rdflib import Graph


def construct_file_value_cardinality(onto: Graph) -> Graph:
    """
    Returns cardinalities for classes with a file value.

    Args:
        onto: project ontologies

    Returns:
        Graph with file cardinalities
    """
    logger.info("Constructing File Value shapes for ontology.")
    val_prop_mapper = {
        "ArchiveRepresentation": "hasArchiveFileValue",
        "AudioRepresentation": "hasAudioFileValue",
        "DocumentRepresentation": "hasDocumentFileValue",
        "MovingImageRepresentation": "hasMovingImageFileValue",
        "StillImageRepresentation": "hasStillImageFileValue",
        "TextRepresentation": "hasTextFileValue",
    }

    def as_class_type_and_shacl_shape(cls_name: str) -> tuple[str, str]:
        return f"knora-api:{cls_name}", f"api-shapes:{val_prop_mapper[cls_name]}_PropShape"

    g = Graph()
    for t in val_prop_mapper.keys():
        representation_type, shacl_shape = as_class_type_and_shacl_shape(t)
        g += _construct_one_representation_shape(onto, representation_type, shacl_shape)
    return g


def _construct_one_representation_shape(onto: Graph, representation_type: str, shacl_shape: str) -> Graph:
    query_s = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#> 
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX api-shapes: <http://api.knora.org/ontology/knora-api/shapes/v2#>
    PREFIX knora-api:  <http://api.knora.org/ontology/knora-api/v2#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
    PREFIX dash: <http://datashapes.org/dash#>

    CONSTRUCT {
        ?class sh:property %(shacl_shape)s .
    } WHERE {
        ?class a owl:Class ;
               rdfs:subClassOf %(representation_type)s .
    }
    """ % {"representation_type": representation_type, "shacl_shape": shacl_shape}  # noqa: UP031 (printf-string-formatting)
    if results_graph := onto.query(query_s).graph:
        return results_graph
    return Graph()


def construct_allowed_licenses_shape() -> Graph:
    """Create a constraint detailing the allowed licences."""
    ttl_str = """
    @prefix sh:         <http://www.w3.org/ns/shacl#> .
    @prefix knora-api:  <http://api.knora.org/ontology/knora-api/v2#> .
    @prefix api-shapes: <http://api.knora.org/ontology/knora-api/shapes/v2#> .
    
    api-shapes:FileValue_ClassShape
      a sh:NodeShape ;
      sh:targetClass knora-api:FileValue ;
      sh:property [
          a sh:PropertyShape ;
          sh:path knora-api:hasLicense ;
          sh:in (
                  <http://rdfh.ch/licenses/cc-by-4.0> <http://rdfh.ch/licenses/cc-by-sa-4.0>
                  <http://rdfh.ch/licenses/cc-by-nc-4.0> <http://rdfh.ch/licenses/cc-by-nc-sa-4.0>
                  <http://rdfh.ch/licenses/cc-by-nd-4.0> <http://rdfh.ch/licenses/cc-by-nc-nd-4.0>
                  <http://rdfh.ch/licenses/ai-generated> <http://rdfh.ch/licenses/unknown>
                  <http://rdfh.ch/licenses/public-domain>
                ) ;
          sh:message "You are required to use one of the pre-defined licenses, please consult the documentation for details." ;
          sh:severity sh:Violation
                  ] .
    """  # noqa: E501 Line too long (135 > 120)
    g = Graph()
    g.parse(data=ttl_str, format="turtle")
    return g
