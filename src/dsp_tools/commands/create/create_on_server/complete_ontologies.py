from loguru import logger

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.ontology_clients import OntologyCreateClient
from dsp_tools.clients.ontology_create_client_live import OntologyCreateClientLive
from dsp_tools.commands.create.communicate_problems import print_problem_collection
from dsp_tools.commands.create.create_on_server.cardinalities import add_all_cardinalities
from dsp_tools.commands.create.create_on_server.classes import create_all_classes
from dsp_tools.commands.create.create_on_server.onto_utils import get_project_iri_lookup
from dsp_tools.commands.create.create_on_server.ontology import create_all_ontologies
from dsp_tools.commands.create.create_on_server.properties import create_all_properties
from dsp_tools.commands.create.models.create_problems import CollectedProblems
from dsp_tools.commands.create.models.parsed_ontology import ParsedOntology
from dsp_tools.commands.create.models.server_project_info import CreatedIriCollection
from dsp_tools.commands.create.models.server_project_info import ListNameToIriLookup
from dsp_tools.commands.create.models.server_project_info import ProjectIriLookup
from dsp_tools.setup.ansi_colors import BOLD
from dsp_tools.setup.ansi_colors import BOLD_RED
from dsp_tools.setup.ansi_colors import RESET_TO_DEFAULT


def create_ontologies(
    parsed_ontologies: list[ParsedOntology],
    list_name_2_iri: ListNameToIriLookup,
    project_iri: str,
    shortcode: str,
    auth: AuthenticationClient,
) -> tuple[bool, CreatedIriCollection]:
    success_collection = CreatedIriCollection()
    onto_client = OntologyCreateClientLive(auth.server, auth)
    overall_success = True

    logger.info("Processing Ontology Section")
    print(BOLD + "Processing Ontology Section:" + RESET_TO_DEFAULT)
    project_iri_lookup, ontology_problems = _create_ontologies_on_server(
        ontologies=parsed_ontologies,
        project_iri=project_iri,
        shortcode=shortcode,
        client=onto_client,
    )
    if ontology_problems:
        overall_success = False
        print_problem_collection(ontology_problems)
    if not project_iri_lookup.onto_iris:
        msg = "No ontologies could be created on the server."
        logger.error(msg)
        print(BOLD_RED + "    " + msg + RESET_TO_DEFAULT)
        return False, success_collection

    all_classes = []
    for onto in parsed_ontologies:
        all_classes.extend(onto.classes)
    if all_classes:
        print(BOLD + "Processing Classes:" + RESET_TO_DEFAULT)
        success_collection, cls_problems = create_all_classes(
            classes=all_classes,
            project_iri_lookup=project_iri_lookup,
            created_iris=success_collection,
            client=onto_client,
        )
        if cls_problems:
            overall_success = False
            print_problem_collection(cls_problems)
    else:
        logger.info("No classes found in the ontology.")

    all_props = []
    for onto in parsed_ontologies:
        all_props.extend(onto.properties)
    if all_props:
        print(BOLD + "Processing Properties:" + RESET_TO_DEFAULT)
        success_collection, property_problems = create_all_properties(
            properties=all_props,
            project_iri_lookup=project_iri_lookup,
            created_iris=success_collection,
            list_lookup=list_name_2_iri,
            client=onto_client,
        )
        if property_problems:
            overall_success = False
            print_problem_collection(property_problems)
    else:
        logger.info("No properties found in the ontology.")

    print(BOLD + "Processing Cardinalities:" + RESET_TO_DEFAULT)
    problems = add_all_cardinalities(
        ontologies=parsed_ontologies,
        project_iri_lookup=project_iri_lookup,
        created_iris=success_collection,
        onto_client=onto_client,
    )
    if problems:
        overall_success = False
        print_problem_collection(problems)

    return overall_success, success_collection


def _create_ontologies_on_server(
    ontologies: list[ParsedOntology], project_iri: str, shortcode: str, client: OntologyCreateClient
) -> tuple[ProjectIriLookup, CollectedProblems | None]:
    project_iri_lookup = get_project_iri_lookup(client.server, shortcode, project_iri)
    new_ontologies = []
    for parsed_onto in ontologies:
        if not project_iri_lookup.does_onto_exist(parsed_onto.name):
            new_ontologies.append(parsed_onto)
    if not new_ontologies:
        if len(ontologies) > 0:
            msg = (
                "No new ontologies were found in the project. "
                "All ontologies already exist on the server. Continuing adding information to the ontologies."
            )
            logger.info(msg)
            print(BOLD + "    " + msg + RESET_TO_DEFAULT)
        return project_iri_lookup, None
    return create_all_ontologies(new_ontologies, project_iri_lookup, client)
