from loguru import logger
from rdflib import Graph

from dsp_tools.commands.validate_data.models.api_responses import EnabledLicenseIris


def construct_legal_info_shapes(license_iris: EnabledLicenseIris, is_production_server: bool) -> Graph:
    """

    Args:
        license_iris: iris of the enabled licenses of a project
        is_production_server: if the server is a production server (rdu-test or prod).
            Dummy information is not allowed there, resulting in different shapes.

    Returns:
        Legal info graph
    """
    legal_graph = Graph()
    if not is_production_server:
        # This license is "allowed" if we are not on a production server.
        license_iris.enabled_licenses.append("http://rdfh.ch/licenses/dummy")
        # Even though we do not prohibit it we want to warn the user.
        # This warning is not necessary when we are on a production server
        # because omitting it from the permitted values is enough.
        legal_graph += _add_warn_for_dummy_license_shape()
    legal_graph += _construct_allowed_licenses_shape(license_iris)
    return legal_graph


def _construct_allowed_licenses_shape(license_iris: EnabledLicenseIris) -> Graph:
    """Create a constraint detailing the allowed licences."""
    formatted_iris = [f"<{x}>" for x in license_iris.enabled_licenses]
    license_str = " ".join(formatted_iris)
    if len(formatted_iris) == 0:
        msg_str = '"You are only allowed to reference enabled licenses. No licenses are enabled for this project."'
    else:
        msg_str = (
            '"Please only use enabled licenses in your data. Consult the project information for enabled licenses."'
        )
    logger.info("Constructing allowed licesnses shapes.")
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


def _add_warn_for_dummy_license_shape() -> Graph:
    g = Graph()
    shape = '''
    @prefix sh:         <http://www.w3.org/ns/shacl#> .
    @prefix knora-api:  <http://api.knora.org/ontology/knora-api/v2#> .
    @prefix api-shapes: <http://api.knora.org/ontology/knora-api/shapes/v2#> .
    
    api-shapes:DummyLicense_Shape
        a              sh:NodeShape ;
        sh:targetClass knora-api:FileValue ;
        sh:sparql      [
                       a          sh:SPARQLConstraint ;
                       sh:select  """
                                    PREFIX knora-api:  <http://api.knora.org/ontology/knora-api/v2#>
                                    
                                    SELECT $this ?path WHERE {
                                      BIND( knora-api:hasLicense AS ?path )
                                      $this ?path <http://rdfh.ch/licenses/dummy> .
                                      
                                    }
                                  """
                     ] ;
        sh:severity sh:Warning ;
        sh:message  "A dummy license is used, please note that an upload on a production server will fail." .
    '''
    g.parse(data=shape, format="turtle")
    return g
