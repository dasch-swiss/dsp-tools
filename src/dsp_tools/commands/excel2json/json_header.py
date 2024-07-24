from __future__ import annotations

from pathlib import Path

import pandas as pd
import regex

from dsp_tools.commands.excel2json.models.input_error import AtLeastOneValueRequiredProblem
from dsp_tools.commands.excel2json.models.input_error import EmptySheetsProblem
from dsp_tools.commands.excel2json.models.input_error import ExcelFileProblem
from dsp_tools.commands.excel2json.models.input_error import ExcelSheetProblem
from dsp_tools.commands.excel2json.models.input_error import InvalidExcelContentProblem
from dsp_tools.commands.excel2json.models.input_error import MissingValuesProblem
from dsp_tools.commands.excel2json.models.input_error import MoreThanOneRowProblem
from dsp_tools.commands.excel2json.models.input_error import PositionInExcel
from dsp_tools.commands.excel2json.models.input_error import Problem
from dsp_tools.commands.excel2json.models.input_error import RequiredColumnMissingProblem
from dsp_tools.commands.excel2json.models.json_header import Descriptions
from dsp_tools.commands.excel2json.models.json_header import EmptyJsonHeader
from dsp_tools.commands.excel2json.models.json_header import FilledJsonHeader
from dsp_tools.commands.excel2json.models.json_header import JsonHeader
from dsp_tools.commands.excel2json.models.json_header import Keywords
from dsp_tools.commands.excel2json.models.json_header import Prefixes
from dsp_tools.commands.excel2json.models.json_header import Project
from dsp_tools.commands.excel2json.models.json_header import User
from dsp_tools.commands.excel2json.models.json_header import UserRole
from dsp_tools.commands.excel2json.models.json_header import Users
from dsp_tools.commands.excel2json.utils import check_contains_required_columns
from dsp_tools.commands.excel2json.utils import find_missing_required_values
from dsp_tools.commands.excel2json.utils import read_and_clean_all_sheets
from dsp_tools.models.exceptions import InputError
from dsp_tools.utils.uri_util import is_uri


def get_json_header(excel_filepath: Path) -> JsonHeader:
    """
    Returns the header of the JSON file.
    If the Excel file exists, the header will be filled in.
    Otherwise, it will return a header with the fields left blank.

    Args:
        excel_filepath: path to the excel file

    Returns:
        JsonHeader object

    Raises:
        InputError: If the file does not conform to the specifications
    """
    if not excel_filepath.is_file():
        print("No json_header.xlsx file found in the directory, empty header was added.")
        return EmptyJsonHeader()
    sheets_df_dict = read_and_clean_all_sheets(excel_filepath)
    sheets_df_dict = {k.lower(): df for k, df in sheets_df_dict.items()}
    if compliance_problem := _do_all_checks(sheets_df_dict):
        raise InputError(compliance_problem.execute_error_protocol())
    print("json_header.xlsx file used to construct the json header.")
    return _process_file(sheets_df_dict)


def _do_all_checks(df_dict: dict[str, pd.DataFrame]) -> ExcelFileProblem | None:
    if file_problems := _check_if_sheets_are_filled_and_exist(df_dict):
        return file_problems
    sheet_problems: list[Problem] = []
    if prefix_problem := _check_prefixes(df_dict["prefixes"]):
        sheet_problems.append(prefix_problem)
    if project_problems := _check_project_sheet(df_dict["project"]):
        sheet_problems.append(project_problems)
    if description_problem := _check_descriptions(df_dict["description"]):
        sheet_problems.append(description_problem)
    if keywords_problem := _check_keywords(df_dict["keywords"]):
        sheet_problems.append(keywords_problem)
    if (user_df := df_dict.get("users")) is not None:
        if user_problems := _check_all_users(user_df):
            sheet_problems.append(user_problems)
    if sheet_problems:
        return ExcelFileProblem("json_header.xlsx", sheet_problems)
    return None


def _check_if_sheets_are_filled_and_exist(df_dict: dict[str, pd.DataFrame]) -> ExcelFileProblem | None:
    expected_sheets = ["prefixes", "project", "description", "keywords"]

    def _check_df(sheet: str) -> str | None:
        if (df := df_dict.get(sheet)) is None:
            return sheet
        if len(df) == 0:
            return sheet
        return None

    if empty_or_missing_sheets := [x for x in expected_sheets if _check_df(x)]:
        return ExcelFileProblem("json_header.xlsx", [EmptySheetsProblem(empty_or_missing_sheets)])
    return None


def _check_prefixes(df: pd.DataFrame) -> ExcelSheetProblem | None:
    if missing_cols := check_contains_required_columns(df, {"prefixes", "uri"}):
        return ExcelSheetProblem("prefixes", [missing_cols])
    problems: list[Problem] = []
    if missing_vals := find_missing_required_values(df, ["prefixes", "uri"]):
        problems.append(MissingValuesProblem(missing_vals))
    if not (uri_series := pd.Series([is_uri(x) for x in df["uri"].tolist()])).all():
        problematic_uri = df["uri"][~uri_series]
        problematic_vals: list[Problem] = [
            InvalidExcelContentProblem(
                expected_content="A valid URI",
                actual_content=value,
                excel_position=PositionInExcel(column="uri", row=int(str(i)) + 2),
            )
            for i, value in problematic_uri.items()
        ]
        problems.extend(problematic_vals)
    if problems:
        return ExcelSheetProblem("prefixes", problems)
    return None


def _check_project_sheet(df: pd.DataFrame) -> ExcelSheetProblem | None:
    problems: list[Problem] = []
    cols = {"shortcode", "shortname", "longname"}
    if missing_cols := check_contains_required_columns(df, cols):
        problems.append(missing_cols)
    if len(df) > 1:
        problems.append(MoreThanOneRowProblem(len(df)))
    if problems:
        return ExcelSheetProblem("project", problems)
    if missing_values := find_missing_required_values(df, list(cols)):
        return ExcelSheetProblem("project", [MissingValuesProblem(missing_values)])
    return None


def _check_descriptions(df: pd.DataFrame) -> ExcelSheetProblem | None:
    if len(df) > 1:
        return ExcelSheetProblem("description", [MoreThanOneRowProblem(len(df))])
    desc_columns = ["description_en", "description_de", "description_fr", "description_it", "description_rm"]
    extracted_desc = _extract_descriptions(df)
    if not extracted_desc.descriptions:
        return ExcelSheetProblem("description", [AtLeastOneValueRequiredProblem(desc_columns, 2)])
    return None


def _check_keywords(df: pd.DataFrame) -> ExcelSheetProblem | None:
    if "keywords" not in df.columns:
        return ExcelSheetProblem("keywords", [RequiredColumnMissingProblem(["keywords"])])
    extracted_keywords = _extract_keywords(df)
    if len(extracted_keywords.keywords) == 0:
        return ExcelSheetProblem("keywords", [MissingValuesProblem([PositionInExcel(column="keywords")])])
    return None


def _check_all_users(df: pd.DataFrame) -> ExcelSheetProblem | None:
    if not len(df) > 0:
        return None
    columns = ["username", "email", "givenname", "familyname", "password", "lang", "role"]
    if missing_cols := check_contains_required_columns(df, set(columns)):
        return ExcelSheetProblem("users", [missing_cols])
    if missing_vals := find_missing_required_values(df, columns):
        return ExcelSheetProblem("users", [MissingValuesProblem(missing_vals)])
    problems: list[Problem] = []
    for i, row in df.iterrows():
        if user_problem := _check_one_user(row, int(str(i)) + 2):
            problems.extend(user_problem)
    if problems:
        return ExcelSheetProblem("users", problems)
    return None


def _check_one_user(row: pd.Series[str], row_number: int) -> list[InvalidExcelContentProblem]:
    problems: list[InvalidExcelContentProblem] = []
    if bad_language := _check_lang(row["lang"], row_number):
        problems.append(bad_language)
    if bad_email := _check_email(row["email"], row_number):
        problems.append(bad_email)
    if bad_role := _check_role(row["role"], row_number):
        problems.append(bad_role)
    return problems


def _check_lang(value: str, row_num: int) -> InvalidExcelContentProblem | None:
    lang_options = ["en", "de", "fr", "it", "rm"]
    if value.lower() in lang_options:
        return None
    return InvalidExcelContentProblem(
        expected_content="One of: en, de, fr, it, rm",
        actual_content=value,
        excel_position=PositionInExcel(column="lang", row=row_num),
    )


def _check_email(email: str, row_num: int) -> InvalidExcelContentProblem | None:
    if not regex.search(r".+@.+\..+", email):
        return InvalidExcelContentProblem(
            expected_content="A valid email adress",
            actual_content=email,
            excel_position=PositionInExcel(column="email", row=row_num),
        )
    return None


def _check_role(value: str, row_num: int) -> InvalidExcelContentProblem | None:
    possible_roles = ["projectadmin", "systemadmin", "projectmember"]
    if value.lower() not in possible_roles:
        return InvalidExcelContentProblem(
            expected_content="One of: projectadmin, systemadmin, projectmember",
            actual_content=value,
            excel_position=PositionInExcel(column="role", row=row_num),
        )
    return None


def _process_file(df_dict: dict[str, pd.DataFrame]) -> FilledJsonHeader:
    prefixes = _extract_prefixes(df_dict["prefixes"])
    project = _extract_project(df_dict)
    return FilledJsonHeader(project, prefixes)


def _extract_prefixes(df: pd.DataFrame) -> Prefixes:
    pref: dict[str, str] = dict(zip(df["prefixes"], df["uri"]))
    pref = {k.rstrip(":"): v for k, v in pref.items()}
    return Prefixes(pref)


def _extract_project(df_dict: dict[str, pd.DataFrame]) -> Project:
    project_df = df_dict["project"]
    extracted_description = _extract_descriptions(df_dict["description"])
    extracted_keywords = _extract_keywords(df_dict["keywords"])
    all_users = None
    if (user_df := df_dict.get("users")) is not None:
        if len(user_df) > 0:
            all_users = _extract_users(user_df)
    shortcode = str(project_df.loc[0, "shortcode"]).zfill(4)
    return Project(
        shortcode=shortcode,
        shortname=str(project_df.loc[0, "shortname"]),
        longname=str(project_df.loc[0, "longname"]),
        descriptions=extracted_description,
        keywords=extracted_keywords,
        users=all_users,
    )


def _extract_descriptions(df: pd.DataFrame) -> Descriptions:
    desc_col_dict = _get_description_cols(list(df.columns))
    return Descriptions(
        {lang: str(value) for lang, column in desc_col_dict.items() if not pd.isna(value := df.loc[0, column])}
    )


def _get_description_cols(cols: list[str]) -> dict[str, str]:
    re_pat = r"^(\w*)(en|it|de|fr|rm)$"
    return {found.group(2): x for x in cols if (found := regex.search(re_pat, x))}


def _extract_keywords(df: pd.DataFrame) -> Keywords:
    keywords = list({x for x in df["keywords"] if not pd.isna(x)})
    return Keywords(keywords)


def _extract_users(df: pd.DataFrame) -> Users:
    users = []
    for _, row in df.iterrows():
        str_row: pd.Series[str] = row
        users.append(_extract_one_user(str_row))
    return Users(users)


def _extract_one_user(row: pd.Series[str]) -> User:
    user_role = _get_role(row["role"])
    return User(
        username=row["username"],
        email=row["email"],
        givenName=row["givenname"],
        familyName=row["familyname"],
        password=row["password"],
        lang=row["lang"],
        role=user_role,
    )


def _get_role(value: str) -> UserRole:
    match value.lower():
        case "projectadmin":
            return UserRole(project_admin=True)
        case "systemadmin":
            return UserRole(sys_admin=True)
        case _:
            return UserRole()
