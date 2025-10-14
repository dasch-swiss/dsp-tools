from rdflib import OWL
from rdflib import RDF
from rdflib import RDFS
from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.clients.ontology_client import OntologyClient
from dsp_tools.commands.project.create.models.ontology import Cardinality
from dsp_tools.commands.project.create.ontology.ontology import make_ontology_base_graph


def add_all_cardinalities(
    cardinalities: list[Cardinality], onto_iri: URIRef, last_modification_date: Literal, onto_client: OntologyClient
) -> bool:
    success = True
    for c in cardinalities:
        result = _add_one_cardinality(c, onto_iri, last_modification_date, onto_client)
        if result is not None:
            last_modification_date = result
        else:
            success = False
    return success


def _add_one_cardinality(
    resource_card: Cardinality, onto_iri: URIRef, last_modification_date: Literal, onto_client: OntologyClient
) -> Literal | None:
    card_g = _make_cardinality_graph_for_request(resource_card, onto_iri, last_modification_date)
    return onto_client.post_resource_cardinalities(card_g)


def _make_cardinality_graph_for_request(
    resource_card: Cardinality, onto_iri: URIRef, last_modification_date: Literal
) -> Graph:
    g = make_ontology_base_graph(onto_iri, last_modification_date)
    g += _make_one_cardinality_graph(resource_card)
    return g


def _make_one_cardinality_graph(card: Cardinality) -> Graph:
    g = Graph()
    bn_card = BNode()
    g.add((card.res_iri, RDFS.subClassOf, bn_card))
    g.add((bn_card, RDF.type, OWL.Restriction))
    g.add((bn_card, card.cardinality.owl_property, card.cardinality.cardinality_value))
    g.add((bn_card, OWL.onProperty, card.on_property))
    return g
