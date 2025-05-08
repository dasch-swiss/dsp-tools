# mypy: disable-error-code="no-untyped-def"

from pathlib import Path

import pytest

from dsp_tools.commands.xmlupload.xmlupload import xmlupload

PROJECT_SHORTCODE = "9999"
ONTO_NAME = "onto"
SECOND_ONTO = "second-onto"


@pytest.fixture(scope="module")
def onto_iri(creds) -> str:
    return f"{creds.server}/ontology/{PROJECT_SHORTCODE}/{ONTO_NAME}/v2"


@pytest.fixture(scope="module")
def second_onto_iri(creds) -> str:
    return f"{creds.server}/ontology/{PROJECT_SHORTCODE}/{SECOND_ONTO}/v2"


@pytest.fixture(scope="module")
def _xmlupload(_create_project: None, creds) -> None:
    assert xmlupload(Path("testdata/validate-data/generic/minimal_correct.xml"), creds, ".")
