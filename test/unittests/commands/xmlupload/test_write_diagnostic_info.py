from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from dsp_tools.commands.xmlupload.write_diagnostic_info import write_resources_as_jsonld


class TestWriteResourcesAsJsonld:
    def test_filename_uses_xml_stem(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.chdir(tmp_path)
        write_resources_as_jsonld([{"key": "value"}], Path("/some/path/my_data.xml"))
        assert (tmp_path / "my_data.jsonld").exists()

    def test_file_contains_serialised_resources(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.chdir(tmp_path)
        resources: list[dict[str, Any]] = [{"@id": "http://iri/1"}, {"@id": "http://iri/2"}]
        write_resources_as_jsonld(resources, Path("upload.xml"))
        loaded = json.loads((tmp_path / "upload.jsonld").read_text(encoding="utf-8"))
        assert loaded == resources

    def test_empty_list_writes_empty_array(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.chdir(tmp_path)
        write_resources_as_jsonld([], Path("upload.xml"))
        loaded = json.loads((tmp_path / "upload.jsonld").read_text(encoding="utf-8"))
        assert loaded == []

    def test_fallback_filename_when_xml_file_is_none(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.chdir(tmp_path)
        write_resources_as_jsonld([], None)
        assert (tmp_path / "resources.jsonld").exists()
