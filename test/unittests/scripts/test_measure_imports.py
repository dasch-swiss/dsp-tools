import csv
import json
from pathlib import Path

from scripts.bulk_memory_testdata.measure_imports import CSV_COLUMNS
from scripts.bulk_memory_testdata.measure_imports import append_row
from scripts.bulk_memory_testdata.measure_imports import count_resources
from scripts.bulk_memory_testdata.measure_imports import count_shacl_results
from scripts.bulk_memory_testdata.measure_imports import get_payloads
from scripts.bulk_memory_testdata.measure_imports import get_shortcode
from scripts.bulk_memory_testdata.measure_imports import parse_docker_memory
from scripts.bulk_memory_testdata.measure_imports import parse_metrics

LOG = """\
2026-10-23T13:00:01+02 INFO  abc: Starting data import annotations=[bulkImportTask=abc] spans=[]
2026-10-23T13:00:01+02 INFO  BULK_IMPORT_METRIC jsonld_bytes=1200 annotations=[bulkImportTask=abc] spans=[]
2026-10-23T13:00:02+02 INFO  BULK_IMPORT_METRIC jsonld_bytes=999 annotations=[bulkImportTask=other] spans=[]
2026-10-23T13:00:03+02 INFO  BULK_IMPORT_METRIC heap_peak_bytes=52428800 annotations=[bulkImportTask=abc] spans=[]
"""


def test_parse_metrics_of_one_task() -> None:
    assert parse_metrics(LOG, "abc") == {"jsonld_bytes": 1200, "heap_peak_bytes": 52428800}


def test_parse_metrics_strips_ansi_colours() -> None:
    line = "\x1b[36mINFO \x1b[0m \x1b[36mBULK_IMPORT_METRIC quads=7\x1b[0m annotations=[bulkImportTask=abc]"
    assert parse_metrics(line, "abc") == {"quads": 7}


def test_count_shacl_results() -> None:
    report = "<http://www.w3.org/ns/shacl#result> [ a <http://www.w3.org/ns/shacl#ValidationResult>; ] ;" * 3
    assert count_shacl_results(report) == 3
    assert count_shacl_results("") == 0


def test_parse_docker_memory() -> None:
    assert parse_docker_memory("2.641GiB / 23.19GiB") == int(2.641 * 1024**3)
    assert parse_docker_memory("512MiB / 23.19GiB") == 512 * 1024**2
    assert parse_docker_memory("900KiB / 1GiB") == 900 * 1024


def test_count_resources(tmp_path: Path) -> None:
    payload = tmp_path / "p.jsonld"
    nodes = [
        {"@id": "http://rdfh.ch/9999/a"},
        {"@id": "http://rdfh.ch/9999/a/values/x"},
        {"@id": "http://rdfh.ch/9999/b"},
    ]
    payload.write_text(json.dumps(nodes), encoding="utf-8")
    assert count_resources(payload) == 2


def test_append_row_writes_header_once(tmp_path: Path) -> None:
    out = tmp_path / "m.csv"
    append_row(out, {"payload": "a", "status": "completed"})
    append_row(out, {"payload": "b", "status": "failed"})
    with out.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert [x["payload"] for x in rows] == ["a", "b"]
    assert list(rows[0].keys()) == CSV_COLUMNS
    assert rows[0]["quads"] == ""


def test_get_payloads_sorted_by_size_and_limited(tmp_path: Path) -> None:
    for name in [
        "9999/correct_20000",
        "9999/correct_10000",
        "0011/failing_10000",
        "9999/correct_100000",
        "9999/correct_combined",
    ]:
        path = tmp_path / f"{name}.jsonld"
        path.parent.mkdir(exist_ok=True)
        path.write_text("[]", encoding="utf-8")
    names = [f"{x.parent.name}/{x.stem}" for x in get_payloads(tmp_path, max_size=50_000)]
    assert names == ["9999/correct_combined", "0011/failing_10000", "9999/correct_10000", "9999/correct_20000"]


def test_get_shortcode() -> None:
    assert get_shortcode(Path("testdata/bulk-memory/9999/failing_10000.jsonld")) == "9999"
    assert get_shortcode(Path("testdata/bulk-memory/9999-many-values/failing_10000.jsonld")) == "9999"
