from pathlib import Path

from loguru import logger
from rdflib import Graph

from dsp_tools.commands.validate_data.constants import CARDINALITY_DATA_TTL
from dsp_tools.commands.validate_data.constants import CARDINALITY_REPORT_TTL
from dsp_tools.commands.validate_data.constants import CARDINALITY_SHACL_TTL
from dsp_tools.commands.validate_data.constants import CONTENT_DATA_TTL
from dsp_tools.commands.validate_data.constants import CONTENT_REPORT_TTL
from dsp_tools.commands.validate_data.constants import CONTENT_SHACL_TTL
from dsp_tools.commands.validate_data.models.validation import RDFGraphs
from dsp_tools.commands.validate_data.models.validation import ValidationFilePaths
from dsp_tools.commands.validate_data.models.validation import ValidationReportGraphs
from dsp_tools.commands.validate_data.shacl_cli_validator import ShaclCliValidator
from dsp_tools.commands.validate_data.utils import clean_up_temp_directory
from dsp_tools.commands.validate_data.utils import get_temp_directory
from dsp_tools.error.exceptions import ShaclValidationError


def get_validation_report(
    rdf_graphs: RDFGraphs, shacl_validator: ShaclCliValidator, graph_save_dir: Path | None = None
) -> ValidationReportGraphs:
    tmp_dir = get_temp_directory()
    tmp_path = Path(tmp_dir.name)
    dir_to_save_graphs = graph_save_dir
    try:
        result = _call_shacl_cli(rdf_graphs, shacl_validator, tmp_path)
        return result
    except Exception as e:  # noqa: BLE001
        logger.exception(e)
        dir_to_save_graphs = tmp_path.parent / "validation-graphs"
        msg = (
            f"An error occurred during the data validation. "
            f"Please contact the dsp-tools development team "
            f"with your log files and the files in the directory: {dir_to_save_graphs}"
        )
        raise ShaclValidationError(msg) from None
    finally:
        clean_up_temp_directory(tmp_dir, dir_to_save_graphs)


def _call_shacl_cli(
    rdf_graphs: RDFGraphs, shacl_validator: ShaclCliValidator, tmp_path: Path
) -> ValidationReportGraphs:
    _create_and_write_graphs(rdf_graphs, tmp_path)
    results_graph = Graph()
    conforms = True
    card_files = ValidationFilePaths(
        directory=tmp_path,
        data_file=CARDINALITY_DATA_TTL,
        shacl_file=CARDINALITY_SHACL_TTL,
        report_file=CARDINALITY_REPORT_TTL,
    )
    card_result = shacl_validator.validate(card_files)
    if not card_result.conforms:
        results_graph += card_result.validation_graph
        conforms = False
    content_files = ValidationFilePaths(
        directory=tmp_path,
        data_file=CONTENT_DATA_TTL,
        shacl_file=CONTENT_SHACL_TTL,
        report_file=CONTENT_REPORT_TTL,
    )
    content_result = shacl_validator.validate(content_files)
    if not content_result.conforms:
        results_graph += content_result.validation_graph
        conforms = False
    return ValidationReportGraphs(
        conforms=conforms,
        validation_graph=results_graph,
        shacl_graph=rdf_graphs.cardinality_shapes + rdf_graphs.content_shapes,
        onto_graph=rdf_graphs.ontos + rdf_graphs.knora_api,
        data_graph=rdf_graphs.data,
    )


def _create_and_write_graphs(rdf_graphs: RDFGraphs, tmp_path: Path) -> None:
    logger.debug("Serialise RDF graphs into turtle strings")
    data_str = rdf_graphs.data.serialize(format="ttl")
    ontos_str = rdf_graphs.ontos.serialize(format="ttl")
    card_shape_str = rdf_graphs.cardinality_shapes.serialize(format="ttl")
    content_shape_str = rdf_graphs.content_shapes.serialize(format="ttl")
    knora_api_str = rdf_graphs.knora_api.serialize(format="ttl")
    turtle_paths_and_graphs = [
        (tmp_path / CARDINALITY_DATA_TTL, data_str),
        (tmp_path / CARDINALITY_SHACL_TTL, card_shape_str + ontos_str + knora_api_str),
        (tmp_path / CONTENT_DATA_TTL, data_str + ontos_str + knora_api_str),
        (tmp_path / CONTENT_SHACL_TTL, content_shape_str + ontos_str + knora_api_str),
    ]
    for f_path, content in turtle_paths_and_graphs:
        with open(f_path, "w") as writer:
            writer.write(content)
