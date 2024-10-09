from rdflib import Namespace

ONTO = Namespace("http://0.0.0.0:3333/ontology/9999/onto/v2#")
DATA = Namespace("http://data/")
DASH = Namespace("http://datashapes.org/dash#")
KNORA_API = Namespace("http://api.knora.org/ontology/knora-api/v2#")
API_SHAPES = Namespace("http://api.knora.org/ontology/knora-api/shapes/v2#")


PREFIXES = """
    @prefix knora-api: <http://api.knora.org/ontology/knora-api/v2#> .
    @prefix onto: <http://0.0.0.0:3333/ontology/9999/onto/v2#> .
    @prefix owl: <http://www.w3.org/2002/07/owl#> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    @prefix salsah-gui: <http://api.knora.org/ontology/salsah-gui/v2#> .
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
    @prefix sh: <http://www.w3.org/ns/shacl#> .
    @prefix dash: <http://datashapes.org/dash#> .
    @prefix api-shapes: <http://api.knora.org/ontology/knora-api/shapes/v2#> .
    """
