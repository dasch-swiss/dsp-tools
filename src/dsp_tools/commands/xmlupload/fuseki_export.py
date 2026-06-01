from __future__ import annotations

from pathlib import Path

import requests
import yaml
from loguru import logger

_FUSEKI_URL = "http://0.0.0.0:3030"
_DATASET = "dsp-repo"

_GRAPH_URIS: list[str] = [
    "http://www.knora.org/ontology/9999/second-onto",
    "http://www.knora.org/data/9999/core-validation",
    "http://www.knora.org/ontology/9999/onto",
    "http://www.knora.org/ontology/9999/in-built",
    "http://www.knora.org/data/permissions",
]


def export_graphs_to_folder(output_dir: Path) -> None:
    """Fetch all known Fuseki graphs and write each to a .ttl file inside output_dir.

    Each graph URI is tried individually; missing graphs (404) are silently skipped.
    A graphs.yaml manifest is written listing every successfully fetched graph.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    fetched: list[dict[str, str]] = []
    for iri in _GRAPH_URIS:
        ttl_content = _fetch_graph(iri)
        if ttl_content is None:
            continue
        filename = f"{iri.rstrip('/').rsplit('/', 1)[-1]}.ttl"
        (output_dir / filename).write_text(ttl_content, encoding="utf-8")
        logger.info(f"Saved Fuseki graph {iri} to {output_dir / filename}")
        fetched.append({"iri": iri, "file": filename})
    if fetched:
        _write_graph_manifest(output_dir, fetched)


def _fetch_graph(iri: str) -> str | None:
    url = f"{_FUSEKI_URL}/{_DATASET}/data"
    try:
        response = requests.get(
            url, params={"graph": iri}, headers={"Accept": "text/turtle"}, auth=("admin", "test"), timeout=30
        )
    except requests.RequestException as err:
        logger.warning(f"Could not fetch Fuseki graph {iri}: {err}")
        return None
    if response.status_code == 404:
        logger.debug(f"Fuseki graph not found, skipping: {iri}")
        return None
    response.raise_for_status()
    return response.text


def _write_graph_manifest(output_dir: Path, entries: list[dict[str, str]]) -> None:
    content = yaml.safe_dump({"graphs": entries}, default_flow_style=False, allow_unicode=True)
    (output_dir / "graphs.yaml").write_text(content, encoding="utf-8")
