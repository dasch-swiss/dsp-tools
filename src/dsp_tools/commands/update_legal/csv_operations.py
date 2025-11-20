"""CSV operations for reading corrections and writing error reports."""

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from dsp_tools.commands.update_legal.models import LegalMetadata
from dsp_tools.commands.update_legal.models import Problem
from dsp_tools.commands.update_legal.models import is_fixme_value
from dsp_tools.error.exceptions import InputError


@dataclass(frozen=True)
class ProblemAggregator:
    """
    Aggregates multiple problems and provides DataFrame export for CSV generation.
    """

    problems: list[Problem]

    def execute_error_protocol(self) -> str:
        """Format all problems as human-readable string for console output."""
        msg = "The legal metadata in your XML file contains the following problems:\n\n" + "\n - ".join(
            [x.execute_error_protocol() for x in self.problems]
        )
        return msg

    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert problems to DataFrame for CSV export.

        Follows the pattern from validate-data command.
        """
        # Build list of dicts with user-facing column names
        problem_dicts = []
        for problem in self.problems:
            # Start with base columns
            row_dict = {
                "file": problem.file,
                "resource_id": problem.res_id,
                "license": problem.license,
                "copyright": problem.copyright,
            }

            # Add authorship columns (authorship_1, authorship_2, etc.)
            for i, authorship in enumerate(problem.authorships, start=1):
                row_dict[f"authorship_{i}"] = authorship

            problem_dicts.append(row_dict)

        # Create DataFrame from records (same method as validate-data)
        df = pd.DataFrame.from_records(problem_dicts)

        # Sort by resource ID for consistency
        df = df.sort_values(by=["resource_id"])

        return df

    def save_to_csv(self, input_file: Path) -> Path:
        """
        Save problems to CSV file.

        Follows the pattern from validate-data command.

        Args:
            input_file: The input XML file path

        Returns:
            Path to the created CSV file
        """
        # Construct output path: {input_stem}_legal_errors.csv
        output_path = input_file.parent / f"{input_file.stem}_legal_errors.csv"

        # Convert to DataFrame and save (index=False as per validate-data pattern)
        df = self.to_dataframe()
        df.to_csv(output_path, index=False)

        return output_path


def collect_authorships_from_row(row: pd.Series, df_columns: pd.Index) -> list[str]:
    """
    Collect all authorship values from a CSV row.

    Args:
        row: The pandas Series row
        df_columns: The DataFrame columns

    Returns:
        List of authorship values (excluding FIXME markers)
    """
    authorships = []
    i = 1
    while f"authorship_{i}" in df_columns:
        auth_val = row[f"authorship_{i}"]
        if pd.notna(auth_val):
            auth_str = str(auth_val)
            # Skip FIXME markers
            if not is_fixme_value(auth_str):
                authorships.append(auth_str)
        i += 1
    return authorships


def read_corrections_csv(csv_path: Path) -> dict[str, LegalMetadata]:
    """
    Read corrected legal metadata from a CSV file.

    Args:
        csv_path: Path to the CSV file with corrected values

    Returns:
        Dictionary mapping resource_id to LegalMetadata

    Raises:
        InputError: If CSV file cannot be read or has invalid format
    """
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        msg = f"Could not read CSV file '{csv_path}': {e}"
        raise InputError(msg) from e

    # Validate required columns
    required_cols = {"file", "resource_id", "license", "copyright"}
    if not required_cols.issubset(df.columns):
        missing = required_cols - set(df.columns)
        msg = f"CSV file is missing required columns: {missing}"
        raise InputError(msg)

    corrections = {}
    for _, row in df.iterrows():
        res_id = str(row["resource_id"])

        # Skip rows that still have FIXME markers (not yet corrected)
        license_val = str(row["license"]) if pd.notna(row["license"]) else None
        copyright_val = str(row["copyright"]) if pd.notna(row["copyright"]) else None

        if is_fixme_value(license_val):
            license_val = None
        if is_fixme_value(copyright_val):
            copyright_val = None

        # Collect all authorship columns (authorship_1, authorship_2, etc.)
        authorships = collect_authorships_from_row(row, df.columns)

        corrections[res_id] = LegalMetadata(
            multimedia_filepath=str(row["file"]),
            license=license_val,
            copyright=copyright_val,
            authorships=authorships,
        )

    return corrections
