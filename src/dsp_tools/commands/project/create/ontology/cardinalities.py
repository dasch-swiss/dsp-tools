from rdflib import OWL
from rdflib import RDF
from rdflib import RDFS
from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.commands.project.create.models.ontology import Cardinality
from dsp_tools.commands.project.create.models.ontology import ResourceCardinalities
from dsp_tools.commands.project.create.ontology.ontology import make_ontology_base_graph


def _make_one_cardinalities_graph(
    res_card: ResourceCardinalities, onto_iri: URIRef, last_modification_date: Literal
) -> Graph:
    g = make_ontology_base_graph(onto_iri, last_modification_date)
    g += _make_one_resource_card_graph(res_card)
    return g


def _make_one_resource_card_graph(res_card: ResourceCardinalities) -> Graph:
    g = Graph()
    for c in res_card.cards:
        g += _make_one_cardinality_graph(res_card.res_iri, c)
    return g


def _make_one_cardinality_graph(res_iri: URIRef, card: Cardinality) -> Graph:
    g = Graph()
    bn_card = BNode()
    g.add((bn_card, RDF.type, OWL.Restriction))
    g.add((bn_card, card.cardinality.owl_property, card.cardinality.cardinality_value))
    g.add((bn_card, OWL.onProperty, card.on_property))
    g.add((res_iri, RDFS.subClassOf, bn_card))
    return g
