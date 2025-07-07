import shutil
from importlib.resources import as_file
from importlib.resources import files
from pathlib import Path

from rdflib import RDF
from rdflib import SH
from rdflib import Graph

from dsp_tools.cli.args import ValidateDataConfig
from dsp_tools.commands.validate_data.constants import ONTOLOGIES_REPORT_TTL
from dsp_tools.commands.validate_data.constants import ONTOLOGIES_SHACL_TTL
from dsp_tools.commands.validate_data.constants import ONTOLOGIES_TTL
from dsp_tools.commands.validate_data.constants import TURTLE_FILE_PATH
from dsp_tools.commands.validate_data.models.input_problems import OntologyResourceProblem
from dsp_tools.commands.validate_data.models.input_problems import OntologyValidationProblem
from dsp_tools.commands.validate_data.models.validation import ValidationFilePaths
from dsp_tools.commands.validate_data.shacl_cli_validator import ShaclCliValidator
from dsp_tools.commands.validate_data.utils import reformat_onto_iri
from dsp_tools.utils.rdflib_constants import SubjectObjectTypeAlias

LIST_SEPARATOR = "\n    - "


def validate_ontology(
    onto_graph: Graph, shacl_validator: ShaclCliValidator, config: ValidateDataConfig
) -> OntologyValidationProblem | None:
    """
    The API accepts erroneous cardinalities in the ontology.
    To distinguish a mistake in the data from the erroneous ontology, the ontology will be validated beforehand.
    This way, we do not have to take an erroneous ontology into account when validating the data.

    Args:
        onto_graph: the graph of the project ontologies
        shacl_validator: SHACL CLI validator
        config: The configuration where to save the information to

    Returns:
        A validation report if errors were found
    """
    with as_file(files("dsp_tools").joinpath("resources/validate_data/validate-ontology.ttl")) as shacl_file_path:
        shacl_file = Path(shacl_file_path)
        shutil.copy(shacl_file, TURTLE_FILE_PATH / ONTOLOGIES_SHACL_TTL)
    onto_graph.serialize(TURTLE_FILE_PATH / ONTOLOGIES_TTL)
    paths = ValidationFilePaths(
        directory=TURTLE_FILE_PATH,
        data_file=ONTOLOGIES_TTL,
        shacl_file=ONTOLOGIES_SHACL_TTL,
        report_file=ONTOLOGIES_REPORT_TTL,
    )
    validation_result = shacl_validator.validate(paths)
    if validation_result.conforms:
        return None
    if config.save_graph_dir:
        validation_result.validation_graph.serialize(f"{config.save_graph_dir}_ONTO_VIOLATIONS.ttl")
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
