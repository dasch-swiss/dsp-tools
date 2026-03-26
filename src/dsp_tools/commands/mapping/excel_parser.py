from pathlib import Path

import pandas as pd

from dsp_tools.commands.excel2json.exceptions import InvalidFileFormatError
from dsp_tools.commands.excel2json.utils import check_contains_required_columns
from dsp_tools.commands.excel2json.utils import read_and_clean_all_sheets
from dsp_tools.commands.mapping.models import ClassMapping
from dsp_tools.commands.mapping.models import ParsedMappingExcel
from dsp_tools.commands.mapping.models import PropertyMapping

_REQUIRED_SHEETS = {"prefix", "classes", "properties"}
_PREFIX_COLUMNS = {"prefix", "link"}
_CLASSES_COLUMNS = {"class", "mapping"}
_PROPERTIES_COLUMNS = {"property", "mapping"}


def parse_mapping_excel(excel_path: Path) -> tuple[ParsedMappingExcel, dict[str, str]]:
    sheets = read_and_clean_all_sheets(excel_path)
    _validate_sheets(sheets, excel_path)
    _validate_columns(sheets, excel_path)
    prefix_map = _parse_prefix_sheet(sheets["prefix"])
    classes = _parse_classes_sheet(sheets["classes"])
    properties = _parse_properties_sheet(sheets["properties"])
    return ParsedMappingExcel(classes=classes, properties=properties), prefix_map


def _validate_sheets(sheets: dict[str, pd.DataFrame], excel_path: Path) -> None:
    missing = _REQUIRED_SHEETS - set(sheets.keys())
    if missing:
        raise InvalidFileFormatError(
            f"The Excel file '{excel_path}' is missing required sheets: {', '.join(sorted(missing))}"
        )


def _validate_columns(sheets: dict[str, pd.DataFrame], excel_path: Path) -> None:
    problems: list[str] = []
    for sheet_name, required_cols in [
        ("prefix", _PREFIX_COLUMNS),
        ("classes", _CLASSES_COLUMNS),
        ("properties", _PROPERTIES_COLUMNS),
    ]:
        problem = check_contains_required_columns(sheets[sheet_name], required_cols)
        if problem:
            problems.append(f"Sheet '{sheet_name}': {problem.execute_error_protocol()}")
    if problems:
        raise InvalidFileFormatError(f"The Excel file '{excel_path}' has column problems:\n" + "\n".join(problems))


def _parse_prefix_sheet(df: pd.DataFrame) -> dict[str, str]:
    result: dict[str, str] = {}
    for _, row in df.iterrows():
        if pd.isna(row["prefix"]) or pd.isna(row["link"]):
            continue
        result[str(row["prefix"])] = str(row["link"])
    return result


def _parse_classes_sheet(df: pd.DataFrame) -> list[ClassMapping]:
    result: list[ClassMapping] = []
    for _, row in df.iterrows():
        if pd.isna(row["class"]) or pd.isna(row["mapping"]):
            continue
        raw_mappings = [m.strip() for m in str(row["mapping"]).split(";") if m.strip()]
        result.append(ClassMapping(class_iri=str(row["class"]), mapping_iris=raw_mappings))
    return result


def _parse_properties_sheet(df: pd.DataFrame) -> list[PropertyMapping]:
    result: list[PropertyMapping] = []
    for _, row in df.iterrows():
        if pd.isna(row["property"]) or pd.isna(row["mapping"]):
            continue
        raw_mappings = [m.strip() for m in str(row["mapping"]).split(";") if m.strip()]
        result.append(PropertyMapping(property_iri=str(row["property"]), mapping_iris=raw_mappings))
    return result
