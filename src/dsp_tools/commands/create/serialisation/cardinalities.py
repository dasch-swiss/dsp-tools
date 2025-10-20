from rdflib import OWL
from rdflib import RDF
from rdflib import RDFS
from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.clients.ontology_client import OntologyClient
from dsp_tools.commands.create.models.parsed_ontology import ParsedClassCardinalities
from dsp_tools.commands.create.models.parsed_ontology import ParsedPropertyCardinality
from dsp_tools.commands.create.serialisation.mappers import PARSED_CARDINALITY_TO_RDF
from dsp_tools.commands.create.serialisation.ontology import make_ontology_base_graph


def add_all_cardinalities(
    cardinalities: list[ParsedClassCardinalities],
    onto_iri: URIRef,
    last_modification_date: Literal,
    onto_client: OntologyClient,
) -> bool:
    success = True
    for c in cardinalities:
        result = _add_cardinalities_for_one_class(c, onto_iri, last_modification_date, onto_client)
        if result is not None:
            last_modification_date = result
        else:
            success = False
    return success


def _add_cardinalities_for_one_class(
    resource_card: ParsedClassCardinalities,
    onto_iri: URIRef,
    last_modification_date: Literal,
    onto_client: OntologyClient,
) -> Literal | None:
    res_iri = URIRef(resource_card.class_iri)
    for one_card in resource_card.cards:
        new_mod_date = _add_one_cardinality(one_card, res_iri, onto_iri, last_modification_date, onto_client)
        if new_mod_date:
            last_modification_date = new_mod_date


def _add_one_cardinality(
    card: ParsedPropertyCardinality,
    res_iri: URIRef,
    onto_iri: URIRef,
    last_modification_date: Literal,
    onto_client: OntologyClient,
) -> Literal | None:
    card_g = _make_cardinality_graph_for_request(card, res_iri, onto_iri, last_modification_date)
    return onto_client.post_resource_cardinalities(card_g)


def _make_cardinality_graph_for_request(
    card: ParsedPropertyCardinality, res_iri: URIRef, onto_iri: URIRef, last_modification_date: Literal
) -> Graph:
    g = make_ontology_base_graph(onto_iri, last_modification_date)
    g += _make_one_cardinality_graph(card, res_iri)
    return g


def _make_one_cardinality_graph(card: ParsedPropertyCardinality, res_iri: URIRef) -> Graph:
    card_info = PARSED_CARDINALITY_TO_RDF[card.cardinality]
    g = Graph()
    bn_card = BNode()
    g.add((res_iri, RDFS.subClassOf, bn_card))
    g.add((bn_card, RDF.type, OWL.Restriction))
    g.add((bn_card, card_info.owl_property, card_info.cardinality_value))
    g.add((bn_card, OWL.onProperty, URIRef(card.propname)))
    return g
