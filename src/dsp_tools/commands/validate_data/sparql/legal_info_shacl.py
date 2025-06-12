from loguru import logger
from rdflib import Graph

from dsp_tools.commands.validate_data.models.api_responses import EnabledLicenseIris


def construct_allowed_licenses_shape(license_iris: EnabledLicenseIris) -> Graph:
    """Create a constraint detailing the allowed licences."""
    formatted_iris = [f"<{x}>" for x in license_iris.enabled_licenses]
    license_str = " ".join(formatted_iris)
    if len(formatted_iris) == 0:
        msg_str = '"You are only allowed to reference enabled licenses. No licenses are enabled for this project."'
    else:
        msg_str = (
            '"Please only use enabled licenses in your data. Consult the project information for enabled licenses."'
        )
    logger.debug("Constructing allowed licenses shapes.")
    ttl_str = """
    @prefix sh:         <http://www.w3.org/ns/shacl#> .
    @prefix knora-api:  <http://api.knora.org/ontology/knora-api/v2#> .
    @prefix api-shapes: <http://api.knora.org/ontology/knora-api/shapes/v2#> .
    
    api-shapes:FileValue_ClassShape
      a sh:NodeShape ;
      sh:targetClass knora-api:FileValue ;
      sh:property [
          a           sh:PropertyShape ;
          sh:path     knora-api:hasLicense ;
          sh:in       ( %(license_str)s ) ;
          sh:message  %(msg)s ;
          sh:severity  sh:Violation
                  ] .
    """ % {"license_str": license_str, "msg": msg_str}  # noqa: UP031 Use format specifiers instead of percent format
    g = Graph()
    g.parse(data=ttl_str, format="turtle")
    return g
