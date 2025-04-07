import importlib.resources
from pathlib import Path

from loguru import logger
from rdflib import RDF
from rdflib import SH
from rdflib import Graph

from dsp_tools.commands.validate_data.api_clients import ShaclValidator
from dsp_tools.commands.validate_data.models.input_problems import OntologyResourceProblem
from dsp_tools.commands.validate_data.models.input_problems import OntologyValidationProblem
from dsp_tools.commands.validate_data.utils import reformat_onto_iri
from dsp_tools.utils.rdflib_constants import SubjectObjectTypeAlias

LIST_SEPARATOR = "\n    - "


def validate_ontology(
    onto_graph: Graph, shacl_validator: ShaclValidator, save_path: Path | None
) -> OntologyValidationProblem | None:
    """
    The API accepts erroneous cardinalities in the ontology.
    To distinguish a mistake in the data from the erroneous ontology, the ontology will be validated beforehand.
    This way, we do not have to take an erroneous ontology into account when validating the data.

    Args:
        onto_graph: the graph of the project ontologies
        shacl_validator: connection to the API for the validation
        save_path: the path where the turtle file should be saved if so desired

    Returns:
        A validation report if errors were found
    """
    logger.info("Validating the ontology.")
    shacl_file = importlib.resources.files("dsp_tools").joinpath("resources/validate_data/validate-ontology.ttl")
    onto_shacl = Graph()
    onto_shacl = onto_shacl.parse(str(shacl_file))
    validation_result = shacl_validator.validate_ontology(onto_graph, onto_shacl)
    if validation_result.conforms:
        return None
    if save_path:
        validation_result.validation_graph.serialize(f"{save_path}_ONTO_VIOLATIONS.ttl")
    return OntologyValidationProblem(_reformat_ontology_validation_result(validation_result.validation_graph))


def _reformat_ontology_validation_result(validation_result: Graph) -> list[OntologyResourceProblem]:
    bns = validation_result.subjects(RDF.type, SH.ValidationResult)
    return [_get_one_problem(validation_result, bn) for bn in bns]


def _get_one_problem(val_g: Graph, result_bn: SubjectObjectTypeAlias) -> OntologyResourceProblem:
    iri = next(val_g.objects(result_bn, SH.focusNode))
    iri_str = reformat_onto_iri(iri)
    msg = str(next(val_g.objects(result_bn, SH.resultMessage)))
    splt = [x.strip() for x in msg.split("\n")]
    return OntologyResourceProblem(iri_str, " ".join(splt))
