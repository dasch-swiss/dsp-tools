from rdflib import OWL
from rdflib import RDF
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.utils.rdflib_constants import KNORA_API


def get_ontology_graph(onto_iri: URIRef, last_modification_date: Literal) -> Graph:
    g = Graph()
    g.add((onto_iri, RDF.type, OWL.Ontology))
    g.add((onto_iri, KNORA_API.lastModificationDate, last_modification_date))
    return g
