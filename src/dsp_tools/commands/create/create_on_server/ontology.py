import time
from http import HTTPStatus

from loguru import logger
from tqdm import tqdm

from dsp_tools.clients.ontology_clients import OntologyCreateClient
from dsp_tools.commands.create.models.create_problems import CollectedProblems
from dsp_tools.commands.create.models.create_problems import CreateProblem
from dsp_tools.commands.create.models.create_problems import UploadProblem
from dsp_tools.commands.create.models.create_problems import UploadProblemType
from dsp_tools.commands.create.models.parsed_ontology import ParsedOntology
from dsp_tools.commands.create.serialisation.ontology import serialise_ontology_graph_for_request
from dsp_tools.utils.request_utils import ResponseCodeAndText


def create_all_ontologies(
    ontologies: list[ParsedOntology],
    project_iri: str,
    client: OntologyCreateClient,
) -> CollectedProblems | None:
    logger.debug("Creating ontologies")
    progress_bar = tqdm(ontologies, "     Creating ontologies", dynamic_ncols=True)
    problems: list[CreateProblem] = []
    for o in progress_bar:
        if problem := _create_one_ontology(o, project_iri, client):
            problems.append(problem)
    if problems:
        return CollectedProblems("    While creating ontologies the following problems occurred:", problems)
    return None


def _create_one_ontology(
    onto: ParsedOntology,
    project_iri: str,
    client: OntologyCreateClient,
) -> UploadProblem | None:
    serialised = serialise_ontology_graph_for_request(onto, project_iri)
    result = client.post_new_ontology(serialised)
    if isinstance(result, ResponseCodeAndText):
        if _should_retry_request(result):
            result = client.post_new_ontology(serialised)
        if isinstance(result, ResponseCodeAndText):
            return UploadProblem(result.text, UploadProblemType.ONTOLOGY_COULD_NOT_BE_CREATED)
    return None


def _should_retry_request(response: ResponseCodeAndText) -> bool:
    if HTTPStatus.INTERNAL_SERVER_ERROR <= response.status_code <= HTTPStatus.NETWORK_AUTHENTICATION_REQUIRED:
        time.sleep(5)
        return True
    return False
