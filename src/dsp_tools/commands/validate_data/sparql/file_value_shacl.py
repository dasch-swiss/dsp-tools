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
    val_prop_mapper = {"MovingImageRepresentation": "hasMovingImageFileValue"}

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
