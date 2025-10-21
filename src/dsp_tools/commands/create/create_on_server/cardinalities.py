from rdflib import OWL
from rdflib import RDF
from rdflib import RDFS
from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.clients.ontology_client import OntologyClient
from dsp_tools.commands.create.constants import SALSAH_GUI_NAMESPACE
from dsp_tools.commands.create.create_on_server.mappers import PARSED_CARDINALITY_TO_RDF
from dsp_tools.commands.create.create_on_server.ontology import make_ontology_base_graph
from dsp_tools.commands.create.models.input_problems import CollectedProblems
from dsp_tools.commands.create.models.input_problems import ProblemType
from dsp_tools.commands.create.models.input_problems import UploadProblem
from dsp_tools.commands.create.models.parsed_ontology import ParsedClassCardinalities
from dsp_tools.commands.create.models.parsed_ontology import ParsedPropertyCardinality


def add_all_cardinalities(
    cardinalities: list[ParsedClassCardinalities],
    onto_iri: URIRef,
    last_modification_date: Literal,
    onto_client: OntologyClient,
) -> CollectedProblems | None:
    problems = []
    for c in cardinalities:
        last_modification_date, creation_problems = _add_cardinalities_for_one_class(
            c, onto_iri, last_modification_date, onto_client
        )
        problems.extend(creation_problems)
    if not problems:
        return None
    return CollectedProblems("The following problems occurred when adding cardinalities", problems)


def _add_cardinalities_for_one_class(
    resource_card: ParsedClassCardinalities,
    onto_iri: URIRef,
    last_modification_date: Literal,
    onto_client: OntologyClient,
) -> tuple[Literal, list[UploadProblem]]:
    res_iri = URIRef(resource_card.class_iri)
    problems = []
    for one_card in resource_card.cards:
        last_modification_date, problem = _add_one_cardinality(
            one_card, res_iri, onto_iri, last_modification_date, onto_client
        )
        if problem:
            problems.append(problem)
    return last_modification_date, problems


def _add_one_cardinality(
    card: ParsedPropertyCardinality,
    res_iri: URIRef,
    onto_iri: URIRef,
    last_modification_date: Literal,
    onto_client: OntologyClient,
) -> tuple[Literal, UploadProblem | None]:
    card_g = _make_cardinality_graph_for_request(card, res_iri, onto_iri, last_modification_date)
    new_mod_date = onto_client.post_resource_cardinalities(card_g)
    if not new_mod_date:
        return last_modification_date, UploadProblem(
            f"{res_iri!s} / {card.propname}", ProblemType.CARDINALITY_COULD_NOT_BE_ADDED
        )
    return new_mod_date, None


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
    if card.gui_order is not None:
        g.add((bn_card, SALSAH_GUI_NAMESPACE.guiOrder, Literal(card.gui_order)))
    return g
