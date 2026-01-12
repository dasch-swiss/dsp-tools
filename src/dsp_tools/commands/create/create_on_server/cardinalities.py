from http import HTTPStatus

import regex
from loguru import logger
from rdflib import Literal
from rdflib import URIRef
from tqdm import tqdm

from dsp_tools.clients.ontology_clients import OntologyCreateClient
from dsp_tools.commands.create.models.create_problems import CollectedProblems
from dsp_tools.commands.create.models.create_problems import CreateProblem
from dsp_tools.commands.create.models.create_problems import UploadProblem
from dsp_tools.commands.create.models.create_problems import UploadProblemType
from dsp_tools.commands.create.models.parsed_ontology import ParsedClassCardinalities
from dsp_tools.commands.create.models.parsed_ontology import ParsedOntology
from dsp_tools.commands.create.models.parsed_ontology import ParsedPropertyCardinality
from dsp_tools.commands.create.models.server_project_info import CreatedIriCollection
from dsp_tools.commands.create.models.server_project_info import ProjectIriLookup
from dsp_tools.commands.create.serialisation.ontology import serialise_cardinality_graph_for_request
from dsp_tools.error.exceptions import UnreachableCodeError
from dsp_tools.utils.data_formats.iri_util import from_dsp_iri_to_prefixed_iri
from dsp_tools.utils.request_utils import ResponseCodeAndText
from dsp_tools.utils.request_utils import log_and_warn_unexpected_non_ok_response


def add_all_cardinalities(
    ontologies: list[ParsedOntology],
    project_iri_lookup: ProjectIriLookup,
    created_iris: CreatedIriCollection,
    onto_client: OntologyCreateClient,
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
        if c.class_iri not in created_iris.created_classes:
            logger.warning(f"CARDINALITY: Class '{c.class_iri}' not in successes, no cardinalities added.")
            continue
        last_modification_date, creation_problems = _add_cardinalities_for_one_class(
            resource_card=c,
            onto_iri=onto_iri,
            last_modification_date=last_modification_date,
            onto_client=onto_client,
            successful_props=created_iris.created_properties,
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
            problems.append(UploadProblem(one_card.propname, UploadProblemType.CARDINALITY_PROPERTY_NOT_FOUND))
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
    card_serialised = serialise_cardinality_graph_for_request(card, res_iri, onto_iri, last_modification_date)
    result = onto_client.post_resource_cardinalities(card_serialised)
    match result:
        case Literal():
            return result, None
        case ResponseCodeAndText():
            return last_modification_date, _create_user_problem_message(str(res_iri), card.propname, result)
        case None:
            return last_modification_date, None
        case _:
            raise UnreachableCodeError()


def _create_user_problem_message(res_iri: str, propname: str, response: ResponseCodeAndText) -> UploadProblem | None:
    if response.status_code == HTTPStatus.BAD_REQUEST:
        prefixed_cls = from_dsp_iri_to_prefixed_iri(res_iri)
        prefixed_prop = from_dsp_iri_to_prefixed_iri(propname)
        wrong_subject_constraint = (
            r"Class .+ has a cardinality for property .+ but is not a subclass of that property's .+v2#subjectType"
        )
        if regex.search(wrong_subject_constraint, response.text):
            problem_type = UploadProblemType.CARDINALITY_WITH_WRONG_SUBJECT_CONSTRAINT
        else:
            problem_type = UploadProblemType.CARDINALITY_COULD_NOT_BE_ADDED
        return UploadProblem(f"{prefixed_cls} / {prefixed_prop}", problem_type)
    else:
        log_and_warn_unexpected_non_ok_response(response.status_code, response.text)
        return None
