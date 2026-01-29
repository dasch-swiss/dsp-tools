import time

from loguru import logger
from tqdm import tqdm

from dsp_tools.clients.ontology_clients import OntologyCreateClient
from dsp_tools.commands.create.models.create_problems import CollectedProblems
from dsp_tools.commands.create.models.create_problems import CreateProblem
from dsp_tools.commands.create.models.create_problems import UploadProblem
from dsp_tools.commands.create.models.create_problems import UploadProblemType
from dsp_tools.commands.create.models.parsed_ontology import ParsedOntology
from dsp_tools.commands.create.models.server_project_info import ProjectIriLookup
from dsp_tools.commands.create.serialisation.ontology import serialise_ontology_graph_for_request
from dsp_tools.utils.request_utils import ResponseCodeAndText
from dsp_tools.utils.request_utils import is_server_error


def create_all_ontologies(
    ontologies: list[ParsedOntology],
    project_iri_lookup: ProjectIriLookup,
    client: OntologyCreateClient,
) -> tuple[ProjectIriLookup, CollectedProblems | None]:
    logger.debug("Creating ontologies")
    progress_bar = tqdm(ontologies, "     Creating ontologies", dynamic_ncols=True)
    problems: list[CreateProblem] = []
    for o in progress_bar:
        result = _create_one_ontology(o, project_iri_lookup.project_iri, client)
        if isinstance(result, UploadProblem):
            problems.append(result)
        else:
            project_iri_lookup.add_onto(o.name, result)
    if problems:
        return project_iri_lookup, CollectedProblems(
            "    While creating ontologies the following problems occurred:", problems
        )
    return project_iri_lookup, None


def _create_one_ontology(
    onto: ParsedOntology,
    project_iri: str,
    client: OntologyCreateClient,
) -> UploadProblem | str:
    serialised = serialise_ontology_graph_for_request(onto, project_iri)
    result = client.post_new_ontology(serialised)
    if isinstance(result, ResponseCodeAndText):
        if is_server_error(result):
            time.sleep(5)
            result = client.post_new_ontology(serialised)
        if isinstance(result, ResponseCodeAndText):
            return UploadProblem(result.text, UploadProblemType.ONTOLOGY_COULD_NOT_BE_CREATED)
    return result
