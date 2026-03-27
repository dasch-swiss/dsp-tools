from collections.abc import Callable
from pathlib import Path

import pandas as pd

from dsp_tools.commands.excel2json.exceptions import InvalidFileFormatError
from dsp_tools.commands.excel2json.utils import check_contains_required_columns
from dsp_tools.commands.excel2json.utils import read_and_clean_all_sheets
from dsp_tools.commands.mapping.models import ParsedClassMapping
from dsp_tools.commands.mapping.models import ParsedMapping
from dsp_tools.commands.mapping.models import ParsedMappings
from dsp_tools.commands.mapping.models import ParsedPropertyMapping

REQUIRED_SHEETS = {"prefix", "classes", "properties"}
PREFIX_COLUMNS = {"prefix", "link"}
CLASSES_COLUMNS = {"class", "mapping"}
PROPERTIES_COLUMNS = {"property", "mapping"}


def parse_mapping_excel(excel_path: Path) -> tuple[ParsedMappings, dict[str, str]]:
    sheets = read_and_clean_all_sheets(excel_path)
    _validate_sheets(sheets, excel_path)
    _validate_columns(sheets, excel_path)
    prefix_map = _parse_prefix_sheet(sheets["prefix"])
    classes: list[ParsedClassMapping] = _parse_mapping_sheet(sheets["classes"], "class", ParsedClassMapping)
    properties: list[ParsedPropertyMapping] = _parse_mapping_sheet(
        sheets["properties"], "property", ParsedPropertyMapping
    )
    return ParsedMappings(classes=classes, properties=properties), prefix_map


def _validate_sheets(sheets: dict[str, pd.DataFrame], excel_path: Path) -> None:
    missing = REQUIRED_SHEETS - set(sheets.keys())
    if missing:
        raise InvalidFileFormatError(
            f"The Excel file '{excel_path}' is missing required sheets: {', '.join(sorted(missing))}"
        )


def _validate_columns(sheets: dict[str, pd.DataFrame], excel_path: Path) -> None:
    problems: list[str] = []
    for sheet_name, required_cols in [
        ("prefix", PREFIX_COLUMNS),
        ("classes", CLASSES_COLUMNS),
        ("properties", PROPERTIES_COLUMNS),
    ]:
        problem = check_contains_required_columns(sheets[sheet_name], required_cols)
        if problem:
            problems.append(f"Sheet '{sheet_name}': {problem.execute_error_protocol()}")
    if problems:
        raise InvalidFileFormatError(f"The Excel file '{excel_path}' has column problems:\n" + "\n".join(problems))


def _parse_prefix_sheet(df: pd.DataFrame) -> dict[str, str]:
    df = df.dropna(how="any")
    return dict(zip(df["prefix"].tolist(), df["link"].tolist()))


def _parse_mapping_sheet(df: pd.DataFrame, col_name: str, output_type: Callable[ParsedMapping]) -> list[ParsedMapping]:
    df = df.dropna(how="any")
    parsed = []
    for _, row in df.iterrows():
        name_ = row[col_name]
        raw_mappings = [m.strip() for m in str(row["mapping"]).split(";") if m.strip()]
        parsed.append(output_type(name_, raw_mappings))
    return parsed
