"""
Validates generated files with validate-data and compares the result with the expected violations.

Run from the repository root, with a local stack that has the projects 9999 and 0011:
    python -m scripts.bulk_memory_testdata.verify testdata/bulk-memory/9999/failing_10000.xml ...
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path

from lxml import etree

from scripts.bulk_memory_testdata.generate_all import LOCAL_CREDS
from scripts.bulk_memory_testdata.problem_types import get_problem_types
from scripts.bulk_memory_testdata.xml_ids import get_resources

_COPY_SUFFIX = re.compile(r"__[ce]\d{6}$")


def expected_problem_types(xml_file: Path, base_problem_types: dict[str, list[str]]) -> Counter[str]:
    expected: Counter[str] = Counter()
    for res in get_resources(etree.parse(xml_file).getroot()):
        expected.update(base_problem_types.get(_COPY_SUFFIX.sub("", res.attrib["id"]), []))
    return expected


def verify(xml_file: Path) -> bool:
    base = json.loads((xml_file.parent / "failing_combined_problem_types.json").read_text(encoding="utf-8"))
    expected = expected_problem_types(xml_file, base)
    found = Counter(t for types in get_problem_types(xml_file, LOCAL_CREDS).values() for t in types)
    print(f"{xml_file}: expected {expected.total()}, found {found.total()}")
    if expected != found:
        print(f"  difference: expected - found {expected - found}, found - expected {found - expected}")
    return expected == found


if __name__ == "__main__":
    results = [verify(Path(x)) for x in sys.argv[1:]]
    sys.exit(0 if all(results) else 1)
