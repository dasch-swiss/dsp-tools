from rdflib import Namespace

ONTO = Namespace("http://0.0.0.0:3333/ontology/9999/onto/v2#")
IN_BUILT_ONTO = Namespace("http://0.0.0.0:3333/ontology/9999/in-built/v2#")

PREFIXES = """
    @prefix owl: <http://www.w3.org/2002/07/owl#> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix salsah-gui: <http://api.knora.org/ontology/salsah-gui/v2#> .
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
    @prefix sh: <http://www.w3.org/ns/shacl#> .
    @prefix dash: <http://datashapes.org/dash#> .
    @prefix api-shapes: <http://api.knora.org/ontology/knora-api/shapes/v2#> .
    @prefix knora-api: <http://api.knora.org/ontology/knora-api/v2#> .
    @prefix rdf:        <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

    @prefix onto: <http://0.0.0.0:3333/ontology/9999/onto/v2#> .
    @prefix in-built: <http://0.0.0.0:3333/ontology/9999/in-built/v2#> .
    """
