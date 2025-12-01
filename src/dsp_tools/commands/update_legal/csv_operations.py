from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import regex

from dsp_tools.commands.update_legal.models import Authorships
from dsp_tools.commands.update_legal.models import LegalMetadata
from dsp_tools.commands.update_legal.models import Problem
from dsp_tools.error.exceptions import InputError


@dataclass(frozen=True)
class ProblemAggregator:
    """Aggregates multiple problems and provides DataFrame export for CSV generation."""

    problems: list[Problem]

    def to_dataframe(self) -> pd.DataFrame:
        """Convert problems to DataFrame for CSV export."""
        problem_dicts = []
        max_authorships = max((len(p.authorships) for p in self.problems), default=0)

        for problem in self.problems:
            row_dict = {
                "file": problem.file_or_iiif_uri,
                "resource_id": problem.res_id,
                "license": problem.license,
                "copyright": problem.copyright,
            }

            # Add authorship columns (authorship_1, authorship_2, etc.)
            for i in range(1, max_authorships + 1):
                auth_idx = i - 1
                authorship_value = problem.authorships[auth_idx] if auth_idx < len(problem.authorships) else ""
                row_dict[f"authorship_{i}"] = authorship_value

            problem_dicts.append(row_dict)

        df = pd.DataFrame.from_records(problem_dicts)
        df = df.sort_values(by=["resource_id"])

        # Ensure column order matches documentation
        base_cols = ["file", "resource_id", "license", "copyright"]
        auth_cols = [f"authorship_{i}" for i in range(1, max_authorships + 1)]
        df = df[base_cols + auth_cols]

        return df

    def save_to_csv(self, input_file: Path) -> Path:
        """
        Save problems to CSV file.

        Args:
            input_file: The input XML file path, used to determine the output path

        Returns:
            Path to the created CSV file
        """
        output_path = input_file.parent / f"{input_file.stem}_legal_errors.csv"
        i = 1
        while output_path.exists():
            stem_without_suffix = regex.sub(r"_\d+$", "", output_path.stem)
            output_path = output_path.with_name(f"{stem_without_suffix}_{i}{output_path.suffix}")
            i += 1
        df = self.to_dataframe()
        df.to_csv(output_path, index=False, mode="x")
        return output_path


def read_corrections_csv(csv_path: Path) -> dict[str, LegalMetadata]:
    """Read corrected legal metadata from a CSV file, and return a mapping from resource ID to LegalMetadata."""
    df = pd.read_csv(csv_path)

    # Validate required columns
    required_cols = {"file", "resource_id", "license", "copyright"}
    if not required_cols.issubset(df.columns):
        missing = required_cols - set(df.columns)
        msg = f"CSV file is missing required columns: {missing}"
        raise InputError(msg)

    corrections = {}
    for _, row in df.iterrows():
        res_id = str(row["resource_id"])

        license_val = str(row["license"]) if pd.notna(row["license"]) else None
        copyright_val = str(row["copyright"]) if pd.notna(row["copyright"]) else None

        # Skip rows that still have FIXME markers (not yet corrected)
        if is_fixme_value(license_val):
            license_val = None
        if is_fixme_value(copyright_val):
            copyright_val = None

        # Collect all authorship columns (authorship_1, authorship_2, etc.)
        authorships = _collect_authorships_from_row(row, df.columns)

        corrections[res_id] = LegalMetadata(
            license=license_val,
            copyright=copyright_val,
            authorships=authorships,
        )

    return corrections


def _collect_authorships_from_row(row: pd.Series, df_columns: pd.Index) -> Authorships:
    """
    Collect all authorship values from a CSV row.

    Returns:
        List of authorship values (excluding FIXME markers)
    """
    authorships = []
    i = 1
    while f"authorship_{i}" in df_columns:
        auth_val = row[f"authorship_{i}"]
        if pd.notna(auth_val):
            auth_str = str(auth_val)
            if not is_fixme_value(auth_str):
                authorships.append(auth_str)
        i += 1
    return Authorships.from_iterable(authorships)


def is_fixme_value(value: str | None) -> bool:
    """Check if a value is a FIXME marker"""
    return value is not None and value.startswith("FIXME:")


def write_problems_to_csv(input_file: Path, problems: list[Problem]) -> None:
    aggregator = ProblemAggregator(problems)
    csv_path = aggregator.save_to_csv(input_file)
    print(f"\n⚠️  Legal metadata contains errors. Please fix them in the CSV file:\n    {csv_path}")
    print(f"\nAfter fixing the errors, rerun the command with:\n    --fixed_errors={csv_path}")
