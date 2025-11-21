from typing import Any

from rdflib import OWL
from rdflib import RDF
from rdflib import RDFS
from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.commands.create.constants import SALSAH_GUI
from dsp_tools.commands.create.create_on_server.mappers import PARSED_CARDINALITY_TO_RDF
from dsp_tools.commands.create.models.parsed_ontology import ParsedProperty
from dsp_tools.commands.create.models.parsed_ontology import ParsedPropertyCardinality
from dsp_tools.utils.rdflib_constants import KNORA_API
from dsp_tools.utils.rdflib_utils import serialise_json


def _make_ontology_base_graph(onto_iri: URIRef, last_modification_date: Literal) -> Graph:
    g = Graph()
    g.add((onto_iri, RDF.type, OWL.Ontology))
    g.add((onto_iri, KNORA_API.lastModificationDate, last_modification_date))
    return g


def serialise_cardinality_graph_for_request(
    card: ParsedPropertyCardinality, res_iri: URIRef, onto_iri: URIRef, last_modification_date: Literal
) -> dict[str, Any]:
    onto_g = _make_ontology_base_graph(onto_iri, last_modification_date)
    onto_serialised = next(iter(serialise_json(onto_g)))
    card_g = _make_one_cardinality_graph(card, res_iri)
    card_serialised = serialise_json(card_g)
    onto_serialised["@graph"] = card_serialised
    return onto_serialised


def _make_one_cardinality_graph(card: ParsedPropertyCardinality, res_iri: URIRef) -> Graph:
    card_info = PARSED_CARDINALITY_TO_RDF[card.cardinality]
    g = Graph()
    bn_card = BNode()
    g.add((res_iri, RDF.type, OWL.Class))
    g.add((res_iri, RDFS.subClassOf, bn_card))
    g.add((bn_card, RDF.type, OWL.Restriction))
    g.add((bn_card, card_info.owl_property, card_info.cardinality_value))
    g.add((bn_card, OWL.onProperty, URIRef(card.propname)))
    if card.gui_order is not None:
        g.add((bn_card, SALSAH_GUI.guiOrder, Literal(card.gui_order)))
    return g


def serialise_property_graph_for_request(
    prop: ParsedProperty, list_iri: URIRef | None, onto_iri: URIRef, last_modification_date: Literal
) -> dict[str, Any]:
    onto_g = _make_ontology_base_graph(onto_iri, last_modification_date)
    onto_serialised = next(iter(serialise_json(onto_g)))
    prop_g = _make_one_property_graph(prop, list_iri)
    prop_serialised = serialise_json(prop_g)
    onto_serialised["@graph"] = prop_serialised
    return onto_serialised


def _make_one_property_graph(prop: ParsedProperty, list_iri: Literal | None) -> Graph:
    trips = [
        (RDF.type, OWL.ObjectProperty),
        (KNORA_API.objectType, URIRef(str(prop.object))),
        (SALSAH_GUI.guiElement, URIRef(str(prop.gui_element))),
    ]
    trips.extend([(RDFS.label, Literal(lbl, lang=lang_tag)) for lang_tag, lbl in prop.labels.items()])
    if prop.comments:
        trips.extend([(RDFS.comment, Literal(cmnt, lang=lang_tag)) for lang_tag, cmnt in prop.comments.items()])
    trips.extend([(RDFS.subPropertyOf, URIRef(supr)) for supr in prop.supers])
    if prop.subject:
        trips.append((KNORA_API.subjectType, URIRef(prop.subject)))
    if list_iri is not None:
        trips.append((SALSAH_GUI.guiAttribute, list_iri))
    prop_iri = URIRef(prop.name)
    g = Graph()
    for p, o in trips:
        g.add((prop_iri, p, o))
    return g
