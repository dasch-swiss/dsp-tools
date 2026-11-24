import json
from pathlib import Path

import pytest
import regex

from dsp_tools.commands.ingest_xmlupload.bulk_import.payload_files import data_imports_folder
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
    assert regex.fullmatch(r"0001_\d{4}-\d{2}-\d{2}_\d{6}\.jsonld", files.payload.name)
    assert files.id2iri.name == f"{files.payload.stem}_id2iri.json"
    assert files.error.name == f"{files.payload.stem}_error.txt"


def test_write_minted_mapping(tmp_path: Path) -> None:
    target = tmp_path / "map.json"
    write_minted_mapping({"a": "http://rdfh.ch/0001/x"}, target)
    assert json.loads(target.read_text(encoding="utf-8")) == {"a": "http://rdfh.ch/0001/x"}


def test_data_imports_folder(tmp_path: Path) -> None:
    folder = data_imports_folder("localhost")
    assert folder == tmp_path / ".dsp-tools" / "data-imports" / "localhost"
    assert folder.is_dir()
