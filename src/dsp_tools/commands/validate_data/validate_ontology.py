from rdflib import Graph

from dsp_tools.commands.validate_data.api_connection import ApiConnection
from dsp_tools.commands.validate_data.models.input_problems import OntologyValidationProblem

LIST_SEPARATOR = "\n    - "


def validate_ontology(ontologies_graph: Graph, api_connection: ApiConnection) -> OntologyValidationProblem | None:
    """
    The API accepts erroneous cardinalities in the ontology.
    To distinguish a mistake in the data from the erroneous ontology, the ontology will be validated beforehand.
    This way, we do not have to take an erroneous ontology into account when validating the data.

    Args:
        ontologies_graph: graph with all the project ontologies
        api_connection: connection to the API for the validation

    Returns:
        A validation report if errors were found
    """
    return None
