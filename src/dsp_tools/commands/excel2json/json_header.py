from pathlib import Path

import pandas as pd

from dsp_tools.commands.excel2json.models.input_error import EmptySheetsProblem
from dsp_tools.commands.excel2json.models.input_error import ExcelFileProblem
from dsp_tools.commands.excel2json.models.input_error import ExcelSheetProblem
from dsp_tools.commands.excel2json.models.input_error import Problem
from dsp_tools.commands.excel2json.models.input_error import UserProblem
from dsp_tools.commands.excel2json.models.json_header import Descriptions
from dsp_tools.commands.excel2json.models.json_header import EmptyJsonHeader
from dsp_tools.commands.excel2json.models.json_header import FilledJsonHeader
from dsp_tools.commands.excel2json.models.json_header import JsonHeader
from dsp_tools.commands.excel2json.models.json_header import Prefixes
from dsp_tools.commands.excel2json.models.json_header import Project
from dsp_tools.commands.excel2json.models.json_header import User
from dsp_tools.commands.excel2json.models.json_header import Users
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
    return FilledJsonHeader(project_result, prefix_result)


def _do_prefixes(df: pd.DataFrame) -> ExcelSheetProblem | Prefixes: ...


def _do_project(df_dict: dict[str, pd.DataFrame]) -> list[ExcelSheetProblem] | Project: ...


def _do_description(df: pd.DataFrame) -> ExcelSheetProblem | Descriptions: ...


def _do_users(df: pd.DataFrame) -> ExcelSheetProblem | Users: ...


def _do_one_user(row: pd.Series) -> User | UserProblem: ...
