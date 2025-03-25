from typing import Any
from typing import Optional

import regex
from loguru import logger

from dsp_tools.clients.connection import Connection
from dsp_tools.commands.project.legacy_models.context import Context
from dsp_tools.commands.project.legacy_models.helpers import Cardinality
from dsp_tools.commands.project.legacy_models.ontology import Ontology
from dsp_tools.commands.project.legacy_models.project import Project
from dsp_tools.commands.project.legacy_models.propertyclass import PropertyClass
from dsp_tools.commands.project.legacy_models.resourceclass import ResourceClass
from dsp_tools.error.exceptions import BaseError
from dsp_tools.error.exceptions import InputError
from dsp_tools.legacy_models.datetimestamp import DateTimeStamp
from dsp_tools.legacy_models.langstring import LangString


def create_ontologies(
    con: Connection,
    context: Context,
    knora_api_prefix: str,
    names_and_iris_of_list_nodes: dict[str, Any],
    ontology_definitions: list[dict[str, Any]],
    project_remote: Project,
    verbose: bool,
) -> bool:
    """
    Iterates over the ontologies in a JSON project file and creates the ontologies that don't exist on the DSP server
    yet. For every ontology, it first creates the resource classes, then the properties, and then adds the cardinalities
    to the resource classes.

    Args:
        con: Connection to the DSP server
        context: prefixes and the ontology IRIs they stand for
        knora_api_prefix: the prefix that stands for the knora-api ontology
        names_and_iris_of_list_nodes: IRIs of list nodes that were already created and are available on the DSP server
        ontology_definitions: the "ontologies" section of the parsed JSON project file
        project_remote: representation of the project on the DSP server
        verbose: verbose switch

    Raises:
        InputError: if an error occurs during the creation of an ontology.
        All other errors are printed, the process continues, but the success status will be false.

    Returns:
        True if everything went smoothly, False otherwise
    """

    overall_success = True

    print("Create ontologies...")
    logger.info("Create ontologies...")
    try:
        project_ontologies = Ontology.getProjectOntologies(con=con, project_id=str(project_remote.iri))
    except BaseError:
        err_msg = "Unable to retrieve remote ontologies. Cannot check if your ontology already exists."
        print("WARNING: {err_msg}")
        logger.exception(err_msg)
        project_ontologies = []

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

        # add the empty resource classes to the remote ontology
        last_modification_date, remote_res_classes, success = _add_resource_classes_to_remote_ontology(
            onto_name=ontology_definition["name"],
            resclass_definitions=ontology_definition.get("resources", []),
            ontology_remote=ontology_remote,
            con=con,
            last_modification_date=ontology_remote.lastModificationDate,
            verbose=verbose,
        )
        if not success:
            overall_success = False

        # add the property classes to the remote ontology
        last_modification_date, success = _add_property_classes_to_remote_ontology(
            onto_name=ontology_definition["name"],
            property_definitions=ontology_definition.get("properties", []),
            ontology_remote=ontology_remote,
            names_and_iris_of_list_nodes=names_and_iris_of_list_nodes,
            con=con,
            last_modification_date=last_modification_date,
            knora_api_prefix=knora_api_prefix,
            verbose=verbose,
        )
        if not success:
            overall_success = False

        # Add cardinalities to class
        success = _add_cardinalities_to_resource_classes(
            resclass_definitions=ontology_definition.get("resources", []),
            ontology_remote=ontology_remote,
            remote_res_classes=remote_res_classes,
            last_modification_date=last_modification_date,
            knora_api_prefix=knora_api_prefix,
            verbose=verbose,
        )
        if not success:
            overall_success = False

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
        print(f"    WARNING: {err_msg}")
        logger.warning(err_msg)
        return None

    print(f"Create ontology '{onto_name}'...")
    logger.info(f"Create ontology '{onto_name}'...")
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


def _add_resource_classes_to_remote_ontology(
    onto_name: str,
    resclass_definitions: list[dict[str, Any]],
    ontology_remote: Ontology,
    con: Connection,
    last_modification_date: DateTimeStamp,
    verbose: bool,
) -> tuple[DateTimeStamp, dict[str, ResourceClass], bool]:
    """
    Creates the resource classes (without cardinalities) defined in the "resources" section of an ontology. The
    containing project and the containing ontology must already be existing on the DSP server.
    If an error occurs during creation of a resource class, it is printed out, the process continues, but the success
    status will be false.

    Args:
        onto_name: name of the current ontology
        resclass_definitions: the part of the parsed JSON project file that contains the resources of the current onto
        ontology_remote: representation of the current ontology on the DSP server
        con: connection to the DSP server
        last_modification_date: last modification date of the ontology on the DSP server
        verbose: verbose switch

    Returns:
        last modification date of the ontology,
        new resource classes,
        success status
    """

    overall_success = True
    print("    Create resource classes...")
    logger.info("Create resource classes...")
    new_res_classes: dict[str, ResourceClass] = {}
    sorted_resources = _sort_resources(resclass_definitions, onto_name)
    for res_class in sorted_resources:
        super_classes = res_class["super"]
        if isinstance(super_classes, str):
            super_classes = [super_classes]
        res_class_local = ResourceClass(
            con=con,
            context=ontology_remote.context,
            ontology_id=ontology_remote.iri,
            name=res_class["name"],
            superclasses=super_classes,
            label=LangString(res_class.get("labels")),
            comment=LangString(res_class.get("comments")) if res_class.get("comments") else None,
        )
        try:
            last_modification_date, res_class_remote = res_class_local.create(last_modification_date)
            new_res_classes[str(res_class_remote.iri)] = res_class_remote
            ontology_remote.lastModificationDate = last_modification_date
            if verbose:
                print(f"    Created resource class '{res_class['name']}'")
            logger.info(f"Created resource class '{res_class['name']}'")
        except BaseError:
            err_msg = f"Unable to create resource class '{res_class['name']}'."
            print(f"WARNING: {err_msg}")
            logger.exception(err_msg)
            overall_success = False

    return last_modification_date, new_res_classes, overall_success


def _sort_resources(
    unsorted_resources: list[dict[str, Any]],
    onto_name: str,
) -> list[dict[str, Any]]:
    """
    This method sorts the resource classes in an ontology according to their inheritance order (parent classes first).

    Args:
        unsorted_resources: list of resources from a parsed JSON project file
        onto_name: name of the onto

    Returns:
        sorted list of resource classes
    """

    # do not modify the original unsorted_resources, which points to the original JSON project file
    resources_to_sort = unsorted_resources.copy()
    sorted_resources: list[dict[str, Any]] = []
    ok_resource_names: list[str] = []
    while resources_to_sort:
        # inside the for loop, resources_to_sort is modified, so a copy must be made to iterate over
        for res in resources_to_sort.copy():
            parent_classes = res["super"]
            if isinstance(parent_classes, str):
                parent_classes = [parent_classes]
            parent_classes = [regex.sub(r"^:([^:]+)$", f"{onto_name}:\\1", elem) for elem in parent_classes]
            parent_classes_ok = [not p.startswith(onto_name) or p in ok_resource_names for p in parent_classes]
            if all(parent_classes_ok):
                sorted_resources.append(res)
                res_name = f"{onto_name}:{res['name']}"
                ok_resource_names.append(res_name)
                resources_to_sort.remove(res)
    return sorted_resources


def _add_property_classes_to_remote_ontology(
    onto_name: str,
    property_definitions: list[dict[str, Any]],
    ontology_remote: Ontology,
    names_and_iris_of_list_nodes: dict[str, Any],
    con: Connection,
    last_modification_date: DateTimeStamp,
    knora_api_prefix: str,
    verbose: bool,
) -> tuple[DateTimeStamp, bool]:
    """
    Creates the property classes defined in the "properties" section of an ontology. The
    containing project and the containing ontology must already be existing on the DSP server.
    If an error occurs during creation of a property class, it is printed out, the process continues, but the success
    status will be false.

    Args:
        onto_name: name of the current ontology
        property_definitions: the part of the parsed JSON project file that contains the properties of the current onto
        ontology_remote: representation of the current ontology on the DSP server
        names_and_iris_of_list_nodes: IRIs of list nodes that were already created and are available on the DSP server
        con: connection to the DSP server
        last_modification_date: last modification date of the ontology on the DSP server
        knora_api_prefix: the prefix that stands for the knora-api ontology
        verbose: verbose switch

    Returns:
        a tuple consisting of the last modification date of the ontology, and the success status
    """
    overall_success = True
    print("    Create property classes...")
    logger.info("Create property classes...")
    sorted_prop_classes = _sort_prop_classes(property_definitions, onto_name)
    for prop_class in sorted_prop_classes:
        # get the super-property/ies, valid forms are:
        #   - "prefix:super-property" : fully qualified name of property in another ontology. The prefix has to be
        #     defined in the prefixes part.
        #   - ":super-property" : super-property defined in current ontology
        #   - "super-property" : super-property defined in the knora-api ontology
        #   - if omitted, "knora-api:hasValue" is assumed
        if prop_class.get("super"):
            super_props = []
            for super_class in prop_class["super"]:
                if ":" in super_class:
                    prefix, _class = super_class.split(":")
                    super_props.append(super_class if prefix else f"{ontology_remote.name}:{_class}")
                else:
                    super_props.append(knora_api_prefix + super_class)
        else:
            super_props = ["knora-api:hasValue"]

        # get the "object", valid forms are:
        #   - "prefix:object_name" : fully qualified object. The prefix has to be defined in the prefixes part.
        #   - ":object_name" : The object is defined in the current ontology.
        #   - "object_name" : The object is defined in "knora-api"
        if ":" in prop_class["object"]:
            prefix, _object = prop_class["object"].split(":")
            prop_object = f"{prefix}:{_object}" if prefix else f"{ontology_remote.name}:{_object}"
        else:
            prop_object = knora_api_prefix + prop_class["object"]

        # get the gui_attributes
        gui_attributes = prop_class.get("gui_attributes")
        if gui_attributes and gui_attributes.get("hlist"):
            list_iri = names_and_iris_of_list_nodes[gui_attributes["hlist"]]["id"]
            gui_attributes["hlist"] = f"<{list_iri}>"

        # create the property class
        prop_class_local = PropertyClass(
            con=con,
            context=ontology_remote.context,
            label=LangString(prop_class.get("labels")),
            name=prop_class["name"],
            ontology_id=ontology_remote.iri,
            superproperties=super_props,
            rdf_object=prop_object,
            rdf_subject=prop_class.get("subject"),
            gui_element="salsah-gui:" + prop_class["gui_element"],
            gui_attributes=gui_attributes,
            comment=LangString(prop_class["comments"]) if prop_class.get("comments") else None,
        )
        try:
            last_modification_date, _ = prop_class_local.create(last_modification_date)
            ontology_remote.lastModificationDate = last_modification_date
            if verbose:
                print(f"    Created property class '{prop_class['name']}'")
            logger.info(f"Created property class '{prop_class['name']}'")
        except BaseError:
            err_msg = f"Unable to create property class '{prop_class['name']}'."
            print(f"WARNING: {err_msg}")
            logger.exception(f"Unable to create property class '{prop_class['name']}'.")
            overall_success = False

    return last_modification_date, overall_success


def _sort_prop_classes(
    unsorted_prop_classes: list[dict[str, Any]],
    onto_name: str,
) -> list[dict[str, Any]]:
    """
    In case of inheritance, parent properties must be uploaded before their children. This method sorts the
    properties.

    Args:
        unsorted_prop_classes: list of properties from a parsed JSON project file
        onto_name: name of the onto

    Returns:
        sorted list of properties
    """

    # do not modify the original unsorted_prop_classes, which points to the original JSON project file
    prop_classes_to_sort = unsorted_prop_classes.copy()
    sorted_prop_classes: list[dict[str, Any]] = []
    ok_propclass_names: list[str] = []
    while prop_classes_to_sort:
        # inside the for loop, resources_to_sort is modified, so a copy must be made to iterate over
        for prop in prop_classes_to_sort.copy():
            prop_name = f"{onto_name}:{prop['name']}"
            parent_classes = prop.get("super", "hasValue")
            if isinstance(parent_classes, str):
                parent_classes = [parent_classes]
            parent_classes = [regex.sub(r"^:([^:]+)$", f"{onto_name}:\\1", elem) for elem in parent_classes]
            parent_classes_ok = [not p.startswith(onto_name) or p in ok_propclass_names for p in parent_classes]
            if all(parent_classes_ok):
                sorted_prop_classes.append(prop)
                ok_propclass_names.append(prop_name)
                prop_classes_to_sort.remove(prop)
    return sorted_prop_classes


def _add_cardinalities_to_resource_classes(
    resclass_definitions: list[dict[str, Any]],
    ontology_remote: Ontology,
    remote_res_classes: dict[str, ResourceClass],
    last_modification_date: DateTimeStamp,
    knora_api_prefix: str,
    verbose: bool,
) -> bool:
    """
    Iterates over the resource classes of an ontology of a JSON project definition, and adds the cardinalities to each
    resource class. The resource classes and the properties must already be existing on the DSP server.
    If an error occurs during creation of a cardinality, it is printed out, the process continues, but the success
    status will be false.

    Args:
        resclass_definitions: the part of the parsed JSON project file that contains the resources of the current onto
        ontology_remote: representation of the current ontology on the DSP server
        remote_res_classes: representations of the resource classes on the DSP server
        last_modification_date: last modification date of the ontology on the DSP server
        knora_api_prefix: the prefix that stands for the knora-api ontology
        verbose: verbose switch

    Returns:
        success status
    """
    overall_success = True
    print("    Add cardinalities to resource classes...")
    logger.info("Add cardinalities to resource classes...")
    switcher = {
        "1": Cardinality.C_1,
        "0-1": Cardinality.C_0_1,
        "0-n": Cardinality.C_0_n,
        "1-n": Cardinality.C_1_n,
    }
    for res_class in resclass_definitions:
        res_class_remote = remote_res_classes.get(f"{ontology_remote.iri}#{res_class['name']}")
        if not res_class_remote:
            msg = (
                f"Unable to add cardinalities to resource class '{res_class['name']}': "
                f"This class doesn't exist on the DSP server."
            )
            print(f"WARNINIG: {msg}")
            logger.exception(msg)
            overall_success = False
            continue
        for card_info in res_class.get("cardinalities", []):
            if ":" in card_info["propname"]:
                prefix, prop = card_info["propname"].split(":")
                qualified_propname = card_info["propname"] if prefix else f"{ontology_remote.name}:{prop}"
            else:
                qualified_propname = knora_api_prefix + card_info["propname"]

            try:
                last_modification_date = res_class_remote.addProperty(
                    property_id=qualified_propname,
                    cardinality=switcher[card_info["cardinality"]],
                    gui_order=card_info.get("gui_order"),
                    last_modification_date=last_modification_date,
                )
                if verbose:
                    print(f"    Added cardinality '{card_info['propname']}' to resource class '{res_class['name']}'")
                logger.info(f"Added cardinality '{card_info['propname']}' to resource class '{res_class['name']}'")
            except BaseError:
                err_msg = f"Unable to add cardinality '{qualified_propname}' to resource class {res_class['name']}."
                print(f"WARNING: {err_msg}")
                logger.exception(err_msg)
                overall_success = False

            ontology_remote.lastModificationDate = last_modification_date

    return overall_success
