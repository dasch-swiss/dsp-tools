"""
Sends each bulk-import payload to the local API and writes the measured values to a CSV file.

The API must log BULK_IMPORT_METRIC lines (dsp-api branch investigate/bulk-import-validation-memory).
Before each import, the data graph is reset to the exported baseline (the lists of the project),
so that the project IRI and the list IRIs stay the same.

Run from the repository root, with a local stack that has the projects 9999 and 0011:
    python -m scripts.bulk_memory_testdata.measure_imports [max size, default 50000]
"""

import csv
import json
import re
import subprocess
import sys
import threading
import time
from datetime import UTC
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests

from scripts.bulk_memory_testdata.generate_all import OUTPUT_DIR

API = "http://0.0.0.0:3333"
FUSEKI = "http://0.0.0.0:3030/dsp-repo"
FUSEKI_AUTH = ("admin", "test")
API_CONTAINER = "start-stack-api-1"
BASELINE_DIR = OUTPUT_DIR / "baseline"
CSV_FILE = OUTPUT_DIR / "measurements.csv"
DATA_GRAPHS = {
    "9999": "http://www.knora.org/data/9999/core-validation",
    "0011": "http://www.knora.org/data/0011/test-inheritance",
}
TIMEOUT_SECONDS = 60 * 60
CSV_COLUMNS = [
    "payload",
    "shortcode",
    "resources",
    "file_bytes",
    "jsonld_bytes",
    "transform_ms",
    "nquads_bytes",
    "quads",
    "model_triples",
    "heap_max_bytes",
    "heap_baseline_bytes",
    "heap_after_load_bytes",
    "heap_peak_bytes",
    "load_ms",
    "shacl_ms",
    "validation_ms",
    "container_peak_bytes",
    "status",
    "shacl_results",
    "total_s",
    "error",
]

_ANSI = re.compile(r"\x1b\[[0-9;]*m")
_METRIC = re.compile(r"BULK_IMPORT_METRIC (\w+)=(-?\d+)")
_SIZE = re.compile(r"_(\d+)$")
_DOCKER_UNITS = {"B": 1, "KiB": 1024, "MiB": 1024**2, "GiB": 1024**3, "TiB": 1024**4}


def parse_metrics(log: str, task_id: str) -> dict[str, int]:
    metrics: dict[str, int] = {}
    for line in _ANSI.sub("", log).splitlines():
        if f"bulkImportTask={task_id}" in line and (match := _METRIC.search(line)):
            metrics[match.group(1)] = int(match.group(2))
    return metrics


def count_shacl_results(report: str) -> int:
    return report.count("http://www.w3.org/ns/shacl#ValidationResult>")


def parse_docker_memory(usage: str) -> int:
    """Parses the used part of `docker stats` MemUsage, for example `2.641GiB / 23.19GiB`."""
    match = re.match(r"([\d.]+)([KMGT]?i?B)", usage.strip())
    if not match:
        raise ValueError(f"Unknown docker memory value: {usage}")
    return int(float(match.group(1)) * _DOCKER_UNITS[match.group(2)])


def count_resources(payload: Path) -> int:
    nodes = json.loads(payload.read_text(encoding="utf-8"))
    return sum(1 for x in nodes if "/values/" not in x["@id"])


def append_row(csv_file: Path, row: dict[str, Any]) -> None:
    is_new = not csv_file.exists()
    with csv_file.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        if is_new:
            writer.writeheader()
        writer.writerow({key: row.get(key, "") for key in CSV_COLUMNS})


def get_payloads(directory: Path, max_size: int) -> list[Path]:
    """The combined files count as size 0. Sorted by size, so that a problem shows early."""
    sized = [(_size_of(x), x) for x in directory.glob("*/*.jsonld")]
    return [path for size, path in sorted(sized, key=lambda x: (x[0], str(x[1]))) if size <= max_size]


def _size_of(payload: Path) -> int:
    stem = payload.stem.removesuffix("_no_transformer_errors")
    return int(match.group(1)) if (match := _SIZE.search(stem)) else 0


class _ContainerMemorySampler:
    """Samples the memory of the API container with `docker stats` until it is stopped."""

    def __init__(self) -> None:
        self.peak = 0
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def __enter__(self) -> "_ContainerMemorySampler":
        self._thread.start()
        return self

    def __exit__(self, *_: object) -> None:
        self._stop.set()
        self._thread.join()

    def _run(self) -> None:
        while not self._stop.is_set():
            usage = subprocess.run(
                ["docker", "stats", "--no-stream", "--format", "{{.MemUsage}}", API_CONTAINER],
                capture_output=True,
                text=True,
                check=False,
            ).stdout
            if usage.strip():
                self.peak = max(self.peak, parse_docker_memory(usage))
            self._stop.wait(2)


def measure(payload: Path, token: str) -> dict[str, Any]:
    shortcode = payload.parent.name
    reset_data_graph(shortcode)
    project = quote(_get_project_iri(shortcode), safe="")
    headers = {"Authorization": f"Bearer {token}"}
    since = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    start = time.monotonic()
    with _ContainerMemorySampler() as sampler:
        with payload.open("rb") as body:
            response = requests.post(
                f"{API}/v3/projects/{project}/data-imports",
                params={"onBehalfOfUser": f"bulk{shortcode}"},
                headers={**headers, "Content-Type": "application/ld+json"},
                data=body,
                timeout=600,
            )
        response.raise_for_status()
        task_id = response.json()["id"]
        status = _wait_for_end(f"{API}/v3/projects/{project}/data-imports/{task_id}", headers)
    total_s = round(time.monotonic() - start, 1)
    requests.delete(f"{API}/v3/projects/{project}/data-imports/{task_id}", headers=headers, timeout=60)
    log = subprocess.run(
        ["docker", "logs", "--since", since, API_CONTAINER], capture_output=True, text=True, check=True
    )
    error = status.get("errorMessage") or ""
    return {
        "payload": f"{shortcode}/{payload.name}",
        "shortcode": shortcode,
        "resources": count_resources(payload),
        "file_bytes": payload.stat().st_size,
        **parse_metrics(log.stdout + log.stderr, task_id),
        "container_peak_bytes": sampler.peak,
        "status": status["status"],
        "shacl_results": count_shacl_results(error),
        "total_s": total_s,
        "error": error[:200].replace("\n", " "),
    }


def _wait_for_end(status_url: str, headers: dict[str, str]) -> dict[str, Any]:
    deadline = time.monotonic() + TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        status: dict[str, Any] = requests.get(status_url, headers=headers, timeout=600).json()
        if status["status"] != "in_progress":
            return status
        time.sleep(3)
    return {"status": "timeout"}


def reset_data_graph(shortcode: str) -> None:
    """Replaces the data graph with the exported baseline. Without a baseline file, the data graph is removed."""
    graph = DATA_GRAPHS[shortcode]
    baseline = next(BASELINE_DIR.glob(f"{shortcode}/data-*.ttl"), None)
    if baseline is None:
        response = requests.delete(f"{FUSEKI}/data", params={"graph": graph}, auth=FUSEKI_AUTH, timeout=600)
        if response.status_code != 404:
            response.raise_for_status()
        return
    requests.put(
        f"{FUSEKI}/data",
        params={"graph": graph},
        data=baseline.read_bytes(),
        headers={"Content-Type": "text/turtle"},
        auth=FUSEKI_AUTH,
        timeout=600,
    ).raise_for_status()


def _get_project_iri(shortcode: str) -> str:
    response = requests.get(f"{API}/admin/projects/shortcode/{shortcode}", timeout=60)
    response.raise_for_status()
    iri: str = response.json()["project"]["id"]
    return iri


def _get_token() -> str:
    response = requests.post(
        f"{API}/v2/authentication", json={"email": "root@example.com", "password": "test"}, timeout=60
    )
    response.raise_for_status()
    token: str = response.json()["token"]
    return token


if __name__ == "__main__":
    max_size = int(sys.argv[1]) if len(sys.argv) > 1 else 50_000
    for file in get_payloads(OUTPUT_DIR, max_size):
        row = measure(file, _get_token())
        append_row(CSV_FILE, row)
        print(f"{row['payload']}: {row['status']}, {row['total_s']} s, heap peak {row.get('heap_peak_bytes', '')}")
