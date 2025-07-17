import shutil
from importlib.resources import as_file
from importlib.resources import files
from pathlib import Path

from loguru import logger
from rdflib import RDF
from rdflib import SH
from rdflib import Graph

from dsp_tools.cli.args import ValidateDataConfig
from dsp_tools.commands.validate_data.constants import ONTOLOGIES_DATA_TTL
from dsp_tools.commands.validate_data.constants import ONTOLOGIES_REPORT_TTL
from dsp_tools.commands.validate_data.constants import ONTOLOGIES_SHACL_TTL
from dsp_tools.commands.validate_data.models.input_problems import OntologyResourceProblem
from dsp_tools.commands.validate_data.models.input_problems import OntologyValidationProblem
from dsp_tools.commands.validate_data.models.validation import ValidationFilePaths
from dsp_tools.commands.validate_data.shacl_cli_validator import ShaclCliValidator
from dsp_tools.commands.validate_data.utils import clean_up_temp_directory
from dsp_tools.commands.validate_data.utils import get_temp_directory
from dsp_tools.commands.validate_data.utils import reformat_onto_iri
from dsp_tools.error.exceptions import ShaclValidationError
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
    tmp_dir = get_temp_directory()
    tmp_path = Path(tmp_dir.name)
    save_graph_dir = config.save_graph_dir
    try:
        result = _get_ontology_validation_result(onto_graph, shacl_validator, tmp_path)
        return result
    except Exception as e:  # noqa: BLE001
        logger.exception(e)
        save_graph_dir = tmp_path.parent / "validation-graphs"
        msg = (
            f"An error occurred during the ontology validation. "
            f"Please contact the dsp-tools development team "
            f"with your log files and the files in the directory: {save_graph_dir}"
        )
        raise ShaclValidationError(msg) from None
    finally:
        clean_up_temp_directory(tmp_dir, save_graph_dir)


def _get_ontology_validation_result(
    onto_graph: Graph, shacl_validator: ShaclCliValidator, tmp_path: Path
) -> OntologyValidationProblem | None:
    with as_file(files("dsp_tools").joinpath("resources/validate_data/validate-ontology.ttl")) as shacl_file_path:
        shacl_file = Path(shacl_file_path)
        shutil.copy(shacl_file, tmp_path / ONTOLOGIES_SHACL_TTL)
    onto_graph.serialize(tmp_path / ONTOLOGIES_DATA_TTL)
    paths = ValidationFilePaths(
        directory=tmp_path,
        data_file=ONTOLOGIES_DATA_TTL,
        shacl_file=ONTOLOGIES_SHACL_TTL,
        report_file=ONTOLOGIES_REPORT_TTL,
    )
    validation_result = shacl_validator.validate(paths)
    if validation_result.conforms:
        return None
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


def get_msg_str_ontology_validation_violation(onto_violations: OntologyValidationProblem) -> str:
    probs = sorted(onto_violations.problems, key=lambda x: x.res_iri)

    def get_resource_msg(res: OntologyResourceProblem) -> str:
        return f"Resource Class: {res.res_iri} | Problem: {res.msg}"

    problems = [get_resource_msg(x) for x in probs]
    return (
        "The ontology structure contains errors that prevent the validation of the data.\n"
        "Please correct the following errors and re-upload the corrected ontology.\n"
        f"Once those two steps are done, the command `validate-data` will find any problems in the data.\n"
        f"{LIST_SEPARATOR}{LIST_SEPARATOR.join(problems)}"
    )
