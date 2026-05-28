from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

import requests
import yaml

from dsp_tools.commands.xmlupload.fuseki_export import _GRAPH_URIS
from dsp_tools.commands.xmlupload.fuseki_export import _fetch_graph
from dsp_tools.commands.xmlupload.fuseki_export import export_graphs_to_folder


class TestFetchGraph:
    def test_returns_turtle_content_on_success(self) -> None:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "@prefix ex: <http://example.org/> ."
        with patch("dsp_tools.commands.xmlupload.fuseki_export.requests.get", return_value=mock_response):
            result = _fetch_graph("http://www.knora.org/ontology/9999/onto")
        assert result == "@prefix ex: <http://example.org/> ."

    def test_returns_none_on_404(self) -> None:
        mock_response = MagicMock()
        mock_response.status_code = 404
        with patch("dsp_tools.commands.xmlupload.fuseki_export.requests.get", return_value=mock_response):
            result = _fetch_graph("http://www.knora.org/ontology/9999/missing")
        assert result is None

    def test_returns_none_on_request_exception(self) -> None:
        with patch(
            "dsp_tools.commands.xmlupload.fuseki_export.requests.get",
            side_effect=requests.RequestException("timeout"),
        ):
            result = _fetch_graph("http://www.knora.org/ontology/9999/onto")
        assert result is None


class TestExportGraphsToFolder:
    def test_creates_output_dir(self, tmp_path: Path) -> None:
        output_dir = tmp_path / "my_data"
        with patch("dsp_tools.commands.xmlupload.fuseki_export._fetch_graph", return_value=None):
            export_graphs_to_folder(output_dir)
        assert output_dir.exists()

    def test_saves_found_graph_as_ttl(self, tmp_path: Path) -> None:
        ttl = "@prefix ex: <http://example.org/> ."
        responses = {iri: (ttl if iri == _GRAPH_URIS[0] else None) for iri in _GRAPH_URIS}
        with patch("dsp_tools.commands.xmlupload.fuseki_export._fetch_graph", side_effect=lambda iri: responses[iri]):
            export_graphs_to_folder(tmp_path)
        last_segment = _GRAPH_URIS[0].rsplit("/", 1)[-1]
        assert (tmp_path / f"{last_segment}.ttl").read_text(encoding="utf-8") == ttl

    def test_skips_missing_graphs(self, tmp_path: Path) -> None:
        with patch("dsp_tools.commands.xmlupload.fuseki_export._fetch_graph", return_value=None):
            export_graphs_to_folder(tmp_path)
        assert list(tmp_path.glob("*.ttl")) == []

    def test_writes_manifest_for_fetched_graphs(self, tmp_path: Path) -> None:
        ttl = "@prefix ex: <http://example.org/> ."
        with patch("dsp_tools.commands.xmlupload.fuseki_export._fetch_graph", return_value=ttl):
            export_graphs_to_folder(tmp_path)
        manifest = yaml.safe_load((tmp_path / "graphs.yaml").read_text(encoding="utf-8"))
        assert len(manifest["graphs"]) == len(_GRAPH_URIS)
        for entry in manifest["graphs"]:
            assert "iri" in entry
            assert "file" in entry
            assert entry["file"].endswith(".ttl")

    def test_no_manifest_when_no_graphs_found(self, tmp_path: Path) -> None:
        with patch("dsp_tools.commands.xmlupload.fuseki_export._fetch_graph", return_value=None):
            export_graphs_to_folder(tmp_path)
        assert not (tmp_path / "graphs.yaml").exists()

    def test_manifest_iri_matches_filename(self, tmp_path: Path) -> None:
        ttl = "@prefix ex: <http://example.org/> ."
        iri = _GRAPH_URIS[2]  # http://www.knora.org/ontology/9999/onto
        responses = {i: (ttl if i == iri else None) for i in _GRAPH_URIS}
        with patch("dsp_tools.commands.xmlupload.fuseki_export._fetch_graph", side_effect=lambda i: responses[i]):
            export_graphs_to_folder(tmp_path)
        manifest = yaml.safe_load((tmp_path / "graphs.yaml").read_text(encoding="utf-8"))
        assert manifest["graphs"][0]["iri"] == iri
        assert manifest["graphs"][0]["file"] == f"{iri.rsplit('/', 1)[-1]}.ttl"

    def test_ttl_content_is_written_correctly(self, tmp_path: Path) -> None:
        ttl = "@prefix ex: <http://example.org/> .\nex:subject ex:predicate ex:object ."
        responses = {iri: (ttl if iri == _GRAPH_URIS[1] else None) for iri in _GRAPH_URIS}
        with patch("dsp_tools.commands.xmlupload.fuseki_export._fetch_graph", side_effect=lambda iri: responses[iri]):
            export_graphs_to_folder(tmp_path)
        last_segment = _GRAPH_URIS[1].rsplit("/", 1)[-1]
        written = (tmp_path / f"{last_segment}.ttl").read_text(encoding="utf-8")
        assert written == ttl
