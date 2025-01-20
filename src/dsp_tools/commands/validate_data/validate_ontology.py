from dsp_tools.commands.validate_data.api_clients import ShaclValidator
from dsp_tools.commands.validate_data.models.input_problems import OntologyValidationProblem

LIST_SEPARATOR = "\n    - "


def validate_ontology(shacl_validator: ShaclValidator) -> OntologyValidationProblem | None:
    """
    The API accepts erroneous cardinalities in the ontology.
    To distinguish a mistake in the data from the erroneous ontology, the ontology will be validated beforehand.
    This way, we do not have to take an erroneous ontology into account when validating the data.
    Args:
        shacl_validator: connection to the API for the validation
    Returns:
        A validation report if errors were found
    """
    return None


def _reformat_ontology_validation_result():
    pass
