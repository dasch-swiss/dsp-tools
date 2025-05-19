from loguru import logger
from rdflib import Graph


def construct_allowed_licenses_shape() -> Graph:
    """Create a constraint detailing the allowed licences."""
    logger.info("Constructing allowed licesnses shapes.")
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
          sh:message "You are required to use one of the pre-defined licenses, please consult the documentation for details." ;
          sh:severity sh:Violation
                  ] .
    """  # noqa: E501 Line too long (135 > 120)
    g = Graph()
    g.parse(data=ttl_str, format="turtle")
    return g
