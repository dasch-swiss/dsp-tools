import json
from pathlib import Path

import pytest
import regex

from dsp_tools.commands.ingest_xmlupload.bulk_import.payload_files import error_file
from dsp_tools.commands.ingest_xmlupload.bulk_import.payload_files import get_or_create_data_imports_folder
from dsp_tools.commands.ingest_xmlupload.bulk_import.payload_files import make_payload_files
from dsp_tools.commands.ingest_xmlupload.bulk_import.payload_files import write_minted_mapping


@pytest.fixture(autouse=True)
def _home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(Path, "home", lambda: tmp_path)


def test_make_payload_files(tmp_path: Path) -> None:
    files = make_payload_files("localhost", "0001")
    folder = tmp_path / ".dsp-tools" / "data-imports" / "localhost"
    assert folder.is_dir()
    assert files.payload.parent == folder
    match = regex.fullmatch(r"(0001_\d{4}-\d{2}-\d{2}_\d{6})_payload\.jsonld", files.payload.name)
    assert match
    base = match.group(1)
    assert files.id2iri.name == f"{base}_id2iri.json"


def test_write_minted_mapping(tmp_path: Path) -> None:
    target = tmp_path / "map.json"
    write_minted_mapping({"a": "http://rdfh.ch/0001/x"}, target)
    assert json.loads(target.read_text(encoding="utf-8")) == {"a": "http://rdfh.ch/0001/x"}


def test_get_or_create_data_imports_folder(tmp_path: Path) -> None:
    folder = get_or_create_data_imports_folder("localhost")
    assert folder == tmp_path / ".dsp-tools" / "data-imports" / "localhost"
    assert folder.is_dir()


def test_error_file(tmp_path: Path) -> None:
    assert error_file(tmp_path, "0001", "imp-1") == tmp_path / "0001_imp-1_error.txt"
