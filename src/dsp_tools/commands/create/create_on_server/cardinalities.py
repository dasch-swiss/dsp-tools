from typing import Any

from loguru import logger
from rdflib import Literal
from rdflib import URIRef
from tqdm import tqdm

from dsp_tools.clients.ontology_clients import OntologyCreateClient
from dsp_tools.clients.ontology_create_client_live import OntologyCreateClientLive
from dsp_tools.commands.create.models.input_problems import CollectedProblems
from dsp_tools.commands.create.models.input_problems import CreateProblem
from dsp_tools.commands.create.models.input_problems import ProblemType
from dsp_tools.commands.create.models.input_problems import UploadProblem
from dsp_tools.commands.create.models.parsed_ontology import ParsedClassCardinalities
from dsp_tools.commands.create.models.parsed_ontology import ParsedOntology
from dsp_tools.commands.create.models.parsed_ontology import ParsedPropertyCardinality
from dsp_tools.commands.create.models.server_project_info import CreatedIriCollection
from dsp_tools.commands.create.models.server_project_info import ProjectIriLookup
from dsp_tools.commands.create.serialisation.ontology import _make_one_cardinality_graph
from dsp_tools.commands.create.serialisation.ontology import make_ontology_base_graph
from dsp_tools.utils.data_formats.iri_util import from_dsp_iri_to_prefixed_iri
from dsp_tools.utils.rdflib_utils import serialise_json


def add_all_cardinalities(
    ontologies: list[ParsedOntology],
    project_iri_lookup: ProjectIriLookup,
    created_iris: CreatedIriCollection,
    onto_client: OntologyCreateClientLive,
) -> CollectedProblems | None:
    all_problems = []
    for onto in ontologies:
        onto_iri = project_iri_lookup.onto_iris.get(onto.name)
        # we do not inform about onto failures here, as it will have been done upstream
        if onto_iri:
            last_mod_date = onto_client.get_last_modification_date(project_iri_lookup.project_iri, onto_iri)
            problems = _add_all_cardinalities_for_one_onto(
                cardinalities=onto.cardinalities,
                onto_iri=URIRef(onto_iri),
                onto_name=onto.name,
                last_modification_date=last_mod_date,
                onto_client=onto_client,
                created_iris=created_iris,
            )
            all_problems.extend(problems)
    if all_problems:
        return CollectedProblems("    While adding cardinalities the following problems occurred:", all_problems)
    return None


def _add_all_cardinalities_for_one_onto(
    cardinalities: list[ParsedClassCardinalities],
    onto_iri: URIRef,
    onto_name: str,
    last_modification_date: Literal,
    onto_client: OntologyCreateClient,
    created_iris: CreatedIriCollection,
) -> list[CreateProblem]:
    problems: list[CreateProblem] = []
    progress_bar = tqdm(
        cardinalities, desc=f"    Adding cardinalities to the ontology '{onto_name}'", dynamic_ncols=True
    )
    for c in progress_bar:
        # we do not inform about classes failures here, as it will have been done upstream
        if c.class_iri not in created_iris.classes:
            logger.warning(f"CARDINALITY: Class '{c.class_iri}' not in successes, no cardinalities added.")
            continue
        last_modification_date, creation_problems = _add_cardinalities_for_one_class(
            resource_card=c,
            onto_iri=onto_iri,
            last_modification_date=last_modification_date,
            onto_client=onto_client,
            successful_props=created_iris.properties,
        )
        problems.extend(creation_problems)
    return problems


def _add_cardinalities_for_one_class(
    resource_card: ParsedClassCardinalities,
    onto_iri: URIRef,
    last_modification_date: Literal,
    onto_client: OntologyCreateClient,
    successful_props: set[str],
) -> tuple[Literal, list[UploadProblem]]:
    res_iri = URIRef(resource_card.class_iri)
    problems = []
    for one_card in resource_card.cards:
        if one_card.propname not in successful_props:
            logger.warning(f"CARDINALITY: Property '{one_card.propname}' not in successes, no cardinality added.")
            continue
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
    onto_client: OntologyCreateClient,
) -> tuple[Literal, UploadProblem | None]:
    card_serialised = _serialise_card(card, res_iri, onto_iri, last_modification_date)
    new_mod_date = onto_client.post_resource_cardinalities(card_serialised)
    if not new_mod_date:
        prefixed_cls = from_dsp_iri_to_prefixed_iri(str(res_iri))
        prefixed_prop = from_dsp_iri_to_prefixed_iri(card.propname)
        return last_modification_date, UploadProblem(
            f"{prefixed_cls} / {prefixed_prop}",
            ProblemType.CARDINALITY_COULD_NOT_BE_ADDED,
        )
    return new_mod_date, None


def _serialise_card(
    card: ParsedPropertyCardinality, res_iri: URIRef, onto_iri: URIRef, last_modification_date: Literal
) -> dict[str, Any]:
    onto_g = make_ontology_base_graph(onto_iri, last_modification_date)
    onto_serialised = next(iter(serialise_json(onto_g)))
    card_g = _make_one_cardinality_graph(card, res_iri)
    card_serialised = serialise_json(card_g)
    onto_serialised["@graph"] = card_serialised
    return onto_serialised
