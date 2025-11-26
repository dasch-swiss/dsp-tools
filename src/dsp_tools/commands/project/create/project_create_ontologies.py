from typing import Any
from typing import Optional

from loguru import logger

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.connection import Connection
from dsp_tools.clients.ontology_create_client_live import OntologyCreateClientLive
from dsp_tools.commands.create.communicate_problems import print_problem_collection
from dsp_tools.commands.create.create_on_server.cardinalities import add_all_cardinalities
from dsp_tools.commands.create.create_on_server.classes import create_all_classes
from dsp_tools.commands.create.create_on_server.properties import create_all_properties
from dsp_tools.commands.create.models.parsed_ontology import ParsedOntology
from dsp_tools.commands.create.models.server_project_info import CreatedIriCollection
from dsp_tools.commands.create.models.server_project_info import ListNameToIriLookup
from dsp_tools.commands.create.models.server_project_info import ProjectIriLookup
from dsp_tools.commands.project.legacy_models.context import Context
from dsp_tools.commands.project.legacy_models.ontology import Ontology
from dsp_tools.commands.project.legacy_models.project import Project
from dsp_tools.error.exceptions import BaseError
from dsp_tools.error.exceptions import InputError
from dsp_tools.utils.ansi_colors import BOLD
from dsp_tools.utils.ansi_colors import RESET_TO_DEFAULT


def create_ontologies(  # noqa:PLR0912 Too many branches
    con: Connection,
    context: Context,
    list_name_2_iri: ListNameToIriLookup,
    ontology_definitions: list[dict[str, Any]],
    project_remote: Project,
    verbose: bool,
    parsed_ontologies: list[ParsedOntology],
    project_iri_lookup: ProjectIriLookup,
    auth: AuthenticationClient,
) -> bool:
    """
    Iterates over the ontologies in a JSON project file and creates the ontologies that don't exist on the DSP server
    yet. For every ontology, it first creates the resource classes, then the properties, and then adds the cardinalities
    to the resource classes.

    Args:
        con: Connection to the DSP server
        context: prefixes and the ontology IRIs they stand for
        list_name_2_iri: IRIs of list nodes that were already created and are available on the DSP server
        ontology_definitions: the "ontologies" section of the parsed JSON project file
        project_remote: representation of the project on the DSP server
        verbose: verbose switch
        parsed_ontologies: parsed ontologies
        project_iri_lookup: lookup for IRIs
        auth: Authentication Client

    Raises:
        InputError: if an error occurs during the creation of an ontology.
        All other errors are printed, the process continues, but the success status will be false.

    Returns:
        True if everything went smoothly, False otherwise
    """
    success_collection = CreatedIriCollection()
    onto_client = OntologyCreateClientLive(auth.server, auth)

    overall_success = True
    logger.info("Processing Ontology Section")
    try:
        project_ontologies = Ontology.getProjectOntologies(con=con, project_id=str(project_remote.iri))
    except BaseError:
        err_msg = "Unable to retrieve remote ontologies. Cannot check if your ontology already exists."
        print(f"    WARNING: {err_msg}")
        logger.exception(err_msg)
        project_ontologies = []

    for existing_onto in project_ontologies:
        project_iri_lookup.add_onto(existing_onto.name, existing_onto.iri)

    for ontology_definition in ontology_definitions:
        ontology_remote = _create_ontology(
            onto_name=ontology_definition["name"],
            onto_label=ontology_definition["label"],
            onto_comment=ontology_definition.get("comment"),
            project_ontologies=project_ontologies,
            con=con,
            project_remote=project_remote,
            context=context,
            verbose=verbose,
        )
        if not ontology_remote:
            overall_success = False
            continue
        else:
            project_iri_lookup.add_onto(ontology_remote.name, ontology_remote.iri)

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

    return overall_success


def _create_ontology(
    onto_name: str,
    onto_label: str,
    onto_comment: Optional[str],
    project_ontologies: list[Ontology],
    con: Connection,
    project_remote: Project,
    context: Context,
    verbose: bool,
) -> Optional[Ontology]:
    """
    Create an ontology on the DSP server,
    and add the prefixes defined in the JSON file to its context.
    If the ontology already exists on the DSP server, it is skipped.

    Args:
        onto_name: name of the ontology
        onto_label: label of the ontology
        onto_comment: comment of the ontology
        project_ontologies: ontologies existing on the DSP server
        con: Connection to the DSP server
        project_remote: representation of the project on the DSP server
        context: prefixes and the ontology IRIs they stand for
        verbose: verbose switch

    Raises:
        InputError: if the ontology cannot be created on the DSP server

    Returns:
        representation of the created ontology on the DSP server, or None if it already existed
    """
    # skip if it already exists on the DSP server
    if onto_name in [onto.name for onto in project_ontologies]:
        err_msg = f"Ontology '{onto_name}' already exists on the DSP server. Skipping..."
        print(f"WARNING: {err_msg}")
        logger.warning(err_msg)
        return None

    print(BOLD + f"Processing ontology '{onto_name}':" + RESET_TO_DEFAULT)
    logger.info(f"Processing ontology '{onto_name}'")
    ontology_local = Ontology(
        con=con,
        project=project_remote,
        label=onto_label,
        name=onto_name,
        comment=onto_comment,
    )
    try:
        ontology_remote = ontology_local.create()
    except BaseError:
        # if ontology cannot be created, let the error escalate
        logger.exception(f"ERROR while trying to create ontology '{onto_name}'.")
        raise InputError(f"ERROR while trying to create ontology '{onto_name}'.") from None

    if verbose:
        print(f"    Created ontology '{onto_name}'.")
    logger.info(f"Created ontology '{onto_name}'.")

    context.add_context(
        ontology_remote.name,
        ontology_remote.iri + ("" if ontology_remote.iri.endswith("#") else "#"),
    )

    # add the prefixes defined in the JSON file
    for onto_prefix, onto_info in context:
        if onto_info and str(onto_prefix) not in ontology_remote.context:
            onto_iri = onto_info.iri + ("#" if onto_info.hashtag else "")
            ontology_remote.context.add_context(prefix=str(onto_prefix), iri=onto_iri)

    return ontology_remote
