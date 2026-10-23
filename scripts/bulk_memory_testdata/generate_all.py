"""
Generates the bulk-import memory test data from the validate-data test data.

Run from the repository root, with a local stack that has the projects 9999 and 0011:
    python -m scripts.bulk_memory_testdata.generate_all
"""

import dataclasses
import json
from dataclasses import dataclass
from pathlib import Path

from lxml import etree

from dsp_tools.cli.args import ServerCredentials
from scripts.bulk_memory_testdata.add_values import fill_resources
from scripts.bulk_memory_testdata.add_values import get_class_properties
from scripts.bulk_memory_testdata.combine import SourceFile
from scripts.bulk_memory_testdata.combine import combine_xml_files
from scripts.bulk_memory_testdata.mix import mix_resources
from scripts.bulk_memory_testdata.multiply import multiply_resources
from scripts.bulk_memory_testdata.problem_types import get_problem_types
from scripts.bulk_memory_testdata.transformer_errors import TRANSFORMER_REJECTED_BASE_IDS
from scripts.bulk_memory_testdata.xml_ids import remove_resources

OUTPUT_DIR = Path("testdata/bulk-memory")
SIZES = (10_000, 20_000, 50_000, 100_000)
LOCAL_CREDS = ServerCredentials(server="http://0.0.0.0:3333", user="root@example.com", password="test")
_CORE = Path("testdata/validate-data/core_validation")
_INHERITANCE = Path("testdata/validate-data/inheritance")


@dataclass(frozen=True)
class ValueFilling:
    """
    Gives resources between 2 and 50 generated values.
    Each failing resource gets values, as far as its class allows.
    Correct resources get values only in the given classes.
    """

    project_json: Path
    correct_classes: frozenset[str]
    seed: int = 20261023


@dataclass(frozen=True)
class ProjectSources:
    shortcode: str
    default_ontology: str
    failing: list[Path]
    correct: list[Path]
    excluded_failing_ids: frozenset[str] = frozenset()
    folder: str = ""
    value_filling: ValueFilling | None = None

    @property
    def output_dir(self) -> Path:
        return OUTPUT_DIR / (self.folder or self.shortcode)


_CORE_9999 = ProjectSources(
    shortcode="9999",
    default_ontology="onto",
    failing=[
        _CORE / f"{x}.xml"
        for x in (
            "cardinality_violation",
            "content_violation",
            "value_type_violation",
            "unique_value_violation",
            "file_value_violation",
            "dsp_inbuilt_violation",
        )
    ],
    correct=[
        _CORE / f"{x}.xml"
        for x in (
            "cardinality_correct",
            "content_correct",
            "file_value_correct",
            "minimal_correct",
            "dsp_inbuilt_correct",
        )
    ],
    excluded_failing_ids=TRANSFORMER_REJECTED_BASE_IDS,
)

PROJECTS = [
    _CORE_9999,
    dataclasses.replace(
        _CORE_9999,
        folder="9999-many-values",
        value_filling=ValueFilling(
            project_json=_CORE / "core-validation-project-9999.json",
            correct_classes=frozenset({":ClassWithEverything"}),
        ),
    ),
    ProjectSources(
        shortcode="0011",
        default_ontology="onto",
        failing=[_INHERITANCE / "inheritance_violation-0011.xml"],
        correct=[_INHERITANCE / "inheritance_correct-0011.xml"],
    ),
]


def generate_project(project: ProjectSources) -> None:
    out_dir = project.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    failing = _combine(project, project.failing)
    remove_resources(failing, project.excluded_failing_ids)
    correct = _combine(project, project.correct)
    if filling := project.value_filling:
        _write_json(_fill_values(project.default_ontology, filling, failing, correct), out_dir / "values_added.json")
    _write(failing, out_dir / "failing_combined.xml")
    _write(correct, out_dir / "correct_combined.xml")
    problem_types = get_problem_types(out_dir / "failing_combined.xml", LOCAL_CREDS)
    _write_json(problem_types, out_dir / "failing_combined_problem_types.json")
    for size in SIZES:
        _write(multiply_resources(failing, size), out_dir / f"failing_{size}.xml")
        _write(multiply_resources(correct, size), out_dir / f"correct_{size}.xml")
        mixed, stats = mix_resources(correct, failing, problem_types, size)
        _write(mixed, out_dir / f"mixed20_{size}.xml")
        _write_json(vars(stats), out_dir / f"mixed20_{size}_stats.json")


def _fill_values(
    default_ontology: str, filling: ValueFilling, failing: etree._Element, correct: etree._Element
) -> dict[str, int]:
    project_json = json.loads(filling.project_json.read_text(encoding="utf-8"))
    classes = get_class_properties(project_json, default_ontology)
    return {
        "failing": fill_resources(failing, classes, set(classes), filling.seed),
        "correct": fill_resources(correct, classes, set(filling.correct_classes), filling.seed),
    }


def _combine(project: ProjectSources, paths: list[Path]) -> etree._Element:
    sources = [SourceFile(path, path.stem.removesuffix(f"-{project.shortcode}")) for path in paths]
    return combine_xml_files(sources, project.shortcode, project.default_ontology)


def _write(root: etree._Element, path: Path) -> None:
    etree.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True, pretty_print=True)
    print(f"Wrote {path}")


def _write_json(content: object, path: Path) -> None:
    path.write_text(json.dumps(content, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    for proj in PROJECTS:
        generate_project(proj)
