import logging
from pathlib import Path
from unittest.mock import Mock

import pytest
from loguru import logger
from rdflib import Graph

from dsp_tools.cli.args import ValidateDataConfig
from dsp_tools.cli.args import ValidationSeverity
from dsp_tools.commands.validate_data.exceptions import ShaclValidationCliError
from dsp_tools.commands.validate_data.exceptions import ShaclValidationError
from dsp_tools.commands.validate_data.shacl_cli_validator import ShaclCliValidator
from dsp_tools.commands.validate_data.validation.validate_ontology import _reformat_ontology_validation_result
from dsp_tools.commands.validate_data.validation.validate_ontology import validate_ontology


def _make_config() -> ValidateDataConfig:
    return ValidateDataConfig(
        xml_file=Path("data.xml"),
        save_graph_dir=None,
        severity=ValidationSeverity.ERROR,
        ignore_duplicate_files_warning=False,
        is_on_prod_server=False,
        skip_ontology_validation=False,
        do_not_request_resource_metadata_from_db=False,
    )


def _raise_already_logged_docker_failure(*_args: object, **_kwargs: object) -> None:
    # simulates ShaclCliValidator.validate() itself: logs once at the origin, then raises
    logger.exception("Docker command failed with 1: stdout='stdout', stderr='stderr'")
    raise ShaclValidationCliError(1, "stdout", "stderr")


def test_already_logged_docker_failure_is_not_logged_again(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    shacl_validator = Mock(spec=ShaclCliValidator)
    shacl_validator.validate.side_effect = _raise_already_logged_docker_failure
    with caplog.at_level(logging.ERROR):
        with pytest.raises(ShaclValidationCliError):
            validate_ontology(Graph(), shacl_validator, _make_config())
    assert len(caplog.records) == 1
    assert "Docker command failed" in caplog.text


def test_already_logged_docker_failure_still_preserves_validation_graphs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    shacl_validator = Mock(spec=ShaclCliValidator)
    shacl_validator.validate.side_effect = ShaclValidationCliError(1, "stdout", "stderr")
    with pytest.raises(ShaclValidationCliError):
        validate_ontology(Graph(), shacl_validator, _make_config())
    assert (tmp_path / ".dsp-tools" / "validate-data" / "validation-graphs").is_dir()


def test_fresh_failure_is_logged_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    shacl_validator = Mock(spec=ShaclCliValidator)
    shacl_validator.validate.side_effect = ShaclValidationError("SHACL file not found: shacl.ttl")
    with caplog.at_level(logging.ERROR):
        with pytest.raises(ShaclValidationError, match="ontology validation"):
            validate_ontology(Graph(), shacl_validator, _make_config())
    assert len(caplog.records) == 1
    assert "SHACL file not found" in caplog.text


def test_reformat_ontology_validation_result() -> None:
    val_result = """
    @prefix api-shapes: <http://api.knora.org/ontology/knora-api/shapes/v2#> .
    @prefix knora-api: <http://api.knora.org/ontology/knora-api/v2#> .
    @prefix sh: <http://www.w3.org/ns/shacl#> .
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
    
    [ a sh:ValidationResult ;
            sh:focusNode <http://0.0.0.0:3333/ontology/9991/error/v2#ImageWithKnoraProp_MissingSeqnum> ;
            sh:resultMessage "Message from the turtle file" ;
            sh:resultPath knora-api:isPartOf ;
            sh:resultSeverity sh:Violation ;
            sh:sourceConstraint _:n5badee8ae46f40828e18b000160a9e58b9 ;
            sh:sourceConstraintComponent sh:SPARQLConstraintComponent ;
            sh:sourceShape api-shapes:FindCardinalityMismatchSeqnum_OntologyShape ;
            sh:value <http://0.0.0.0:3333/ontology/9991/error/v2#ImageWithKnoraProp_MissingSeqnum> ] .
    """
    g = Graph()
    g.parse(data=val_result, format="ttl")
    reformatted = _reformat_ontology_validation_result(g)
    assert len(reformatted) == 1
    result = reformatted.pop(0)
    assert result.res_iri == "error:ImageWithKnoraProp_MissingSeqnum"
    assert result.msg == "Message from the turtle file"
