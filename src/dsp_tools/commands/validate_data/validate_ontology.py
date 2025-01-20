import importlib.resources

from rdflib import Graph

from dsp_tools.commands.validate_data.api_clients import ShaclValidator
from dsp_tools.commands.validate_data.models.input_problems import OntologyResourceProblem
from dsp_tools.commands.validate_data.models.input_problems import OntologyValidationProblem

LIST_SEPARATOR = "\n    - "


def validate_ontology(onto_graph: Graph, shacl_validator: ShaclValidator) -> OntologyValidationProblem | None:
    """
    The API accepts erroneous cardinalities in the ontology.
    To distinguish a mistake in the data from the erroneous ontology, the ontology will be validated beforehand.
    This way, we do not have to take an erroneous ontology into account when validating the data.
    Args:
        onto_graph: the graph of the project ontologies
        shacl_validator: connection to the API for the validation
    Returns:
        A validation report if errors were found
    """
    shacl_file = importlib.resources.files("dsp_tools").joinpath("resources/validate_data/validate-ontology.ttl")
    onto_shacl = Graph()
    onto_shacl = onto_shacl.parse(str(shacl_file))
    validation_result = shacl_validator.validate_ontology(onto_graph, onto_shacl)
    if validation_result.conforms:
        return None
    return OntologyValidationProblem(_reformat_ontology_validation_result(validation_result.validation_graph))


def _reformat_ontology_validation_result(validation_result: Graph) -> list[OntologyResourceProblem]:
    pass
