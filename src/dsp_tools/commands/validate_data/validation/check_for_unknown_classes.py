from rdflib import Literal
from rdflib import URIRef

from dsp_tools.commands.validate_data.models.input_problems import UnknownClassesInData
from dsp_tools.commands.validate_data.models.validation import RDFGraphs
from dsp_tools.commands.validate_data.utils import reformat_onto_iri
from dsp_tools.utils.rdflib_constants import KNORA_API_STR


def check_for_unknown_resource_classes(
    rdf_graphs: RDFGraphs, used_resource_iris: set[str]
) -> UnknownClassesInData | None:
    """
    Checks if any classes are referenced in the data that are not in the ontology.

    Args:
        rdf_graphs: Data graphs
        used_resource_iris: resource IRIs in use

    Returns:
        Unknown classes if any
    """
    res_cls = _get_all_onto_classes(rdf_graphs)
    if extra_cls := used_resource_iris - res_cls:
        unknown_classes = {reformat_onto_iri(x) for x in extra_cls}
        defined_classes = {reformat_onto_iri(x) for x in res_cls}
        return UnknownClassesInData(unknown_classes=unknown_classes, defined_classes=defined_classes)
    return None


def _get_all_onto_classes(rdf_graphs: RDFGraphs) -> set[str]:
    ontos = rdf_graphs.ontos + rdf_graphs.knora_api
    is_resource_iri = URIRef(KNORA_API_STR + "isResourceClass")
    resource_classes = set(ontos.subjects(is_resource_iri, Literal(True)))
    is_usable = URIRef(KNORA_API_STR + "canBeInstantiated")
    usable_resource_classes = set(ontos.subjects(is_usable, Literal(True)))
    user_facing = usable_resource_classes.intersection(resource_classes)
    return {str(x) for x in user_facing}


def get_msg_str_unknown_classes_in_data(unknown: UnknownClassesInData) -> str:
    if unknown_onto_msg := _get_unknown_ontos_msg(unknown):
        return unknown_onto_msg
    unknown_classes = sorted(list(unknown.unknown_classes))
    known_classes = sorted(list(unknown.defined_classes))
    return (
        f"Your data uses resource classes that do not exist in the ontologies in the database.\n"
        f"The following classes that are used in the data are unknown: {', '.join(unknown_classes)}\n"
        f"The following classes exist in the uploaded ontologies: {', '.join(known_classes)}"
    )


def _get_unknown_ontos_msg(unknown: UnknownClassesInData) -> str | None:
    def split_prefix(relative_iri: str) -> str | None:
        if ":" not in relative_iri:
            return None
        return relative_iri.split(":")[0]

    used_ontos = set(not_knora for x in unknown.unknown_classes if (not_knora := split_prefix(x)))
    exising_ontos = set(not_knora for x in unknown.defined_classes if (not_knora := split_prefix(x)))
    if unknown_found := used_ontos - exising_ontos:
        return (
            f"Your data uses ontologies that don't exist in the database.\n"
            f"The following ontologies that are used in the data are unknown: {', '.join(unknown_found)}\n"
            f"The following ontologies are uploaded: {', '.join(exising_ontos)}"
        )
    return None
