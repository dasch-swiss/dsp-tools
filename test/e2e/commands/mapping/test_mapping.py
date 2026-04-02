import urllib.parse
from pathlib import Path

import pytest
import requests

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.mapping.config_file import parse_mapping_config
from dsp_tools.commands.mapping.mapping_add import mapping_add
from dsp_tools.utils.data_formats.iri_util import make_dsp_ontology_prefix
# TODO: fix tests, add more info


SHORTCODE = "4125"
ONTO_NAME = "e2e-testonto"
CLASS_LOCAL_NAME = "ImageResource"
PROP_LOCAL_NAME = "hasText"

_TESTDATA = Path("testdata/mapping")
CORRECT_XLSX = _TESTDATA / "correct.xlsx"
MALFORMED_XLSX = _TESTDATA / "malformed_mapping_values.xlsx"
NONEXISTENT_CLASS_XLSX = _TESTDATA / "nonexistent_class.xlsx"
NONEXISTENT_ONTO_CONFIG_TEMPLATE = _TESTDATA / "nonexistent_ontology_config.yaml"


@pytest.fixture(scope="module")
def ontology_iri(creds: ServerCredentials) -> str:
    return make_dsp_ontology_prefix(creds.server, SHORTCODE, ONTO_NAME).rstrip("#")


@pytest.fixture(scope="module")
def config_path(tmp_path_factory: pytest.TempPathFactory, creds: ServerCredentials) -> Path:
    path = tmp_path_factory.mktemp("mapping_cfg") / f"mapping-{SHORTCODE}-{ONTO_NAME}.yaml"
    path.write_text(
        f"shortcode: '{SHORTCODE}'\n"
        f"ontology: {ONTO_NAME}\n"
        f"server: {creds.server}\n"
        f"user: {creds.user}\n"
        f"password: {creds.password}\n"
        f"excel-file: {CORRECT_XLSX}\n",
        encoding="utf-8",
    )
    return path


@pytest.fixture(scope="module")
def nonexistent_onto_config_path(tmp_path_factory: pytest.TempPathFactory, creds: ServerCredentials) -> Path:
    template = NONEXISTENT_ONTO_CONFIG_TEMPLATE.read_text(encoding="utf-8")
    content = (
        template.replace("server: PLACEHOLDER", f"server: {creds.server}")
        .replace("user: PLACEHOLDER", f"user: {creds.user}")
        .replace("password: PLACEHOLDER", f"password: {creds.password}")
        .replace("excel-file: PLACEHOLDER", f"excel-file: {CORRECT_XLSX}")
    )
    path = tmp_path_factory.mktemp("mapping_cfg") / "mapping-9999-nonexistent-onto.yaml"
    path.write_text(content, encoding="utf-8")
    return path


@pytest.mark.xfail(reason="v3 mapping endpoints may not yet be in the testcontainer image", strict=False)
def test_mapping_add_success(config_path: Path, ontology_iri: str, creds: ServerCredentials) -> None:
    info = parse_mapping_config(config_path)
    result = mapping_add(info)
    assert result is True

    encoded_iri = urllib.parse.quote(ontology_iri, safe="")
    response = requests.get(
        f"{creds.server}/v2/ontologies/allentities/{encoded_iri}",
        timeout=10,
    )
    assert response.status_code == 200
    body = response.json()
    class_iri = f"{ontology_iri}#{CLASS_LOCAL_NAME}"
    classes = body.get("@graph", [])
    target = next((c for c in classes if c.get("@id") == class_iri), None)
    assert target is not None
    sub_class_of = target.get("rdfs:subClassOf", [])
    external_iris = [
        entry["@id"] for entry in (sub_class_of if isinstance(sub_class_of, list) else [sub_class_of]) if "@id" in entry
    ]
    assert "http://schema.org/Thing" in external_iris


def test_mapping_add_malformed_values(config_path: Path, creds: ServerCredentials) -> None:
    path = config_path.parent / "mapping-malformed.yaml"
    path.write_text(
        f"shortcode: '{SHORTCODE}'\n"
        f"ontology: {ONTO_NAME}\n"
        f"server: {creds.server}\n"
        f"user: {creds.user}\n"
        f"password: {creds.password}\n"
        f"excel-file: {MALFORMED_XLSX}\n",
        encoding="utf-8",
    )
    info = parse_mapping_config(path)
    result = mapping_add(info)
    assert result is False


@pytest.mark.xfail(reason="v3 mapping endpoints may not yet be in the testcontainer image", strict=False)
def test_mapping_add_nonexistent_class(config_path: Path, creds: ServerCredentials) -> None:
    path = config_path.parent / "mapping-nonexistent-class.yaml"
    path.write_text(
        f"shortcode: '{SHORTCODE}'\n"
        f"ontology: {ONTO_NAME}\n"
        f"server: {creds.server}\n"
        f"user: {creds.user}\n"
        f"password: {creds.password}\n"
        f"excel-file: {NONEXISTENT_CLASS_XLSX}\n",
        encoding="utf-8",
    )
    info = parse_mapping_config(path)
    result = mapping_add(info)
    assert result is False


@pytest.mark.xfail(reason="v3 mapping endpoints may not yet be in the testcontainer image", strict=False)
def test_mapping_add_nonexistent_ontology(nonexistent_onto_config_path: Path) -> None:
    info = parse_mapping_config(nonexistent_onto_config_path)
    result = mapping_add(info)
    assert result is False
