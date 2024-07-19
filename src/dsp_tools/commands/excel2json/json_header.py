from __future__ import annotations

from pathlib import Path
from typing import Any
from typing import cast

import pandas as pd
import regex

from dsp_tools.commands.excel2json.models.input_error import AtLeastOneValueRequiredProblem
from dsp_tools.commands.excel2json.models.input_error import EmptySheetsProblem
from dsp_tools.commands.excel2json.models.input_error import ExcelFileProblem
from dsp_tools.commands.excel2json.models.input_error import ExcelSheetProblem
from dsp_tools.commands.excel2json.models.input_error import MissingValuesProblem
from dsp_tools.commands.excel2json.models.input_error import MoreThanOneRowProblem
from dsp_tools.commands.excel2json.models.input_error import PositionInExcel
from dsp_tools.commands.excel2json.models.input_error import Problem
from dsp_tools.commands.excel2json.models.input_error import RequiredColumnMissingProblem
from dsp_tools.commands.excel2json.models.json_header import Descriptions
from dsp_tools.commands.excel2json.models.json_header import EmptyJsonHeader
from dsp_tools.commands.excel2json.models.json_header import FilledJsonHeader
from dsp_tools.commands.excel2json.models.json_header import JsonHeader
from dsp_tools.commands.excel2json.models.json_header import Prefixes
from dsp_tools.commands.excel2json.models.json_header import Project
from dsp_tools.commands.excel2json.models.json_header import User
from dsp_tools.commands.excel2json.models.json_header import Users
from dsp_tools.commands.excel2json.utils import check_contains_required_columns
from dsp_tools.commands.excel2json.utils import check_required_values_get_position_in_excel
from dsp_tools.commands.excel2json.utils import read_and_clean_all_sheets
from dsp_tools.models.exceptions import InputError


def get_json_header(excel_filepath: Path) -> JsonHeader:
    """
    Returns the header of the JSON file.
    If an Excel file with the information is provided it is filled out.
    Otherwise it will return a header with the fields left blank.

    Args:
        excel_filepath: path to the excel file

    Returns:
        JsonHeader object

    Raises:
        InputError: If the file does not conform to the specifics
    """
    if not excel_filepath.is_file():
        return EmptyJsonHeader()
    sheets_df_dict = read_and_clean_all_sheets(excel_filepath)
    sheets_df_dict = {x.lower(): df for x, df in sheets_df_dict.items()}
    if compliance_problem := _do_formal_compliance(sheets_df_dict):
        raise InputError(compliance_problem.execute_error_protocol())
    result = _process_file(sheets_df_dict)
    if isinstance(result, ExcelFileProblem):
        raise InputError(result.execute_error_protocol())
    return result


def _do_formal_compliance(df_dict: dict[str, pd.DataFrame]) -> ExcelFileProblem | None:
    expected_sheets = ["prefixes", "project", "description", "keywords"]

    def _check_df(sheet: str) -> str | None:
        if (df := df_dict.get(sheet)) is None:
            return sheet
        if len(df) == 0:
            return sheet
        return None

    if empty := [x for x in expected_sheets if _check_df(x)]:
        return ExcelFileProblem("json_header.xlsx", [EmptySheetsProblem(empty)])
    return None


def _process_file(df_dict: dict[str, pd.DataFrame]) -> ExcelFileProblem | FilledJsonHeader:
    problems: list[Problem] = []
    prefix_result = _do_prefixes(df_dict["prefixes"])
    if isinstance(prefix_result, ExcelSheetProblem):
        problems.append(prefix_result)
    project_result = _do_project(df_dict)
    if not isinstance(project_result, Project):
        problems.extend(project_result)
    if problems:
        return ExcelFileProblem("json_header.xlsx", problems)
    project = cast(Project, project_result)
    prefixes = cast(Prefixes, prefix_result)
    return FilledJsonHeader(project, prefixes)


def _do_prefixes(df: pd.DataFrame) -> ExcelSheetProblem | Prefixes:
    if missing_cols := check_contains_required_columns(df, {"prefixes", "uri"}):
        return ExcelSheetProblem("prefixes", [missing_cols])
    if missing_vals := check_required_values_get_position_in_excel(df, ["prefixes", "uri"]):
        return ExcelSheetProblem("prefixes", [missing_vals])
    pref = dict(zip(df["prefixes"], df["uri"]))
    pref = {k.replace(":", ""): v for k, v in pref.items()}
    return Prefixes(pref)


def _do_project(df_dict: dict[str, pd.DataFrame]) -> list[ExcelSheetProblem] | Project:
    problems: list[Problem] = []
    if project_problem := _check_project_sheet(df_dict["project"]):
        problems.append(project_problem)
    description_result = _do_description(df_dict["description"])
    if isinstance(description_result, ExcelSheetProblem):
        problems.append(description_result)
    keywords_result = _do_keywords(df_dict["keywords"])
    if isinstance(keywords_result, ExcelSheetProblem):
        problems.append(keywords_result)


def _check_project_sheet(df: pd.DataFrame) -> None | ExcelSheetProblem:
    problems: list[Problem] = []
    cols = {"shortcode", "shortname", "longname"}
    if missing_cols := check_contains_required_columns(df, cols):
        problems.append(missing_cols)
    if len(df) > 1:
        problems.append(MoreThanOneRowProblem(len(df)))
    if problems:
        return ExcelSheetProblem("project", problems)
    if missing_values := check_required_values_get_position_in_excel(df, list(cols)):
        return ExcelSheetProblem("project", [missing_values])
    return None


def _do_description(df: pd.DataFrame) -> ExcelSheetProblem | Descriptions:
    if len(df) > 1:
        return ExcelSheetProblem("description", [MoreThanOneRowProblem(len(df))])
    desc_columns = ["description_en", "description_de", "description_fr", "description_it", "description_rm"]
    if not (desc_col_dict := _get_description_cols(list(df.columns))):
        return ExcelSheetProblem("description", [RequiredColumnMissingProblem(desc_columns)])
    desc_dict = {lang: str(value) for lang, column in desc_col_dict.items() if not pd.isna(value := df.loc[0, column])}
    if not desc_dict:
        return ExcelSheetProblem("description", [AtLeastOneValueRequiredProblem(desc_columns, 1)])
    return Descriptions(desc_dict)


def _get_description_cols(cols: list[str]) -> dict[str, str]:
    re_pat = r"^(\w*)(en|it|de|fr|rm)$"
    return {found.group(2): x for x in cols if (found := regex.search(re_pat, x))}


def _do_keywords(df: pd.DataFrame) -> ExcelSheetProblem | list[str]:
    if "keywords" not in df.columns:
        return ExcelSheetProblem("keywords", [RequiredColumnMissingProblem(["keywords"])])
    keywords = list({x for x in df["keywords"] if not pd.isna(x)})
    if len(keywords) == 0:
        return ExcelSheetProblem("keywords", [MissingValuesProblem([PositionInExcel(column="keywords")])])
    return sorted(keywords)


def _do_users(df: pd.DataFrame) -> ExcelSheetProblem | Users:
    pass


def _do_one_user(row: pd.Series[Any]) -> User | PositionInExcel:
    pass
