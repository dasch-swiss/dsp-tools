from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any
from typing import Optional

import pandas as pd
import regex
from loguru import logger

from dsp_tools.commands.excel2json.lists import validate_lists_section_with_schema
from dsp_tools.commands.excel2json.new_lists.compliance_checks import make_all_excel_compliance_checks
from dsp_tools.commands.excel2json.new_lists.models.deserialise import ExcelSheet
from dsp_tools.commands.excel2json.new_lists.models.input_error import CollectedSheetProblems
from dsp_tools.commands.excel2json.new_lists.models.input_error import ListCreationProblem
from dsp_tools.commands.excel2json.new_lists.models.input_error import ListNodeProblem
from dsp_tools.commands.excel2json.new_lists.models.input_error import ListSheetProblem
from dsp_tools.commands.excel2json.new_lists.models.input_error import SheetProblem
from dsp_tools.commands.excel2json.new_lists.models.serialise import ListNode
from dsp_tools.commands.excel2json.new_lists.models.serialise import ListRoot
from dsp_tools.commands.excel2json.new_lists.utils import get_all_languages_for_columns
from dsp_tools.commands.excel2json.new_lists.utils import get_columns_of_preferred_lang
from dsp_tools.commands.excel2json.new_lists.utils import get_hierarchy_nums
from dsp_tools.commands.excel2json.new_lists.utils import get_lang_string_from_column_name
from dsp_tools.commands.excel2json.new_lists.utils import get_preferred_language
from dsp_tools.commands.excel2json.utils import read_and_clean_all_sheets
from dsp_tools.models.exceptions import InputError


def new_excel2lists(
    excelfolder: str | Path,
    path_to_output_file: Optional[Path] = None,
) -> tuple[list[dict[str, Any]], bool]:
    """
    Convert lists described in Excel files into a "lists" section that can be inserted into a JSON project file.
    If path_to_output_file is not None, write the result into the output file.

    Args:
        excelfolder: path to the folder containing the Excel file(s)
        path_to_output_file: path to the file where the output JSON file will be saved

    Raises:
        InputError: if there is a problem with the input data

    Returns:
        a tuple consisting of the "lists" section as Python list, and the success status (True if everything went well)
    """
    sheet_list = _parse_files(excelfolder)
    sheet_list = _prepare_dfs(sheet_list)

    finished_lists = _make_serialised_lists(sheet_list)
    validate_lists_section_with_schema(lists_section=finished_lists)

    if path_to_output_file:
        with open(path_to_output_file, "w", encoding="utf-8") as fp:
            json.dump(finished_lists, fp, indent=4, ensure_ascii=False)
            print(f"lists section was created successfully and written to file '{path_to_output_file}'")

    return finished_lists, True


def _parse_files(excelfolder: Path | str) -> list[ExcelSheet]:
    file_names = [file for file in Path(excelfolder).glob("*list*.xlsx", case_sensitive=False) if _non_hidden(file)]
    all_sheets = []
    for file in file_names:
        all_sheets.extend(
            [
                ExcelSheet(excel_name=str(file), sheet_name=name, df=df)
                for name, df in read_and_clean_all_sheets(file).items()
            ]
        )
    return all_sheets


def _non_hidden(path: Path) -> bool:
    return not regex.search(r"^(\.|~\$).+", path.name)


def _prepare_dfs(sheet_list: list[ExcelSheet]) -> list[ExcelSheet]:
    sheet_list = _add_id_optional_column_if_not_exists(sheet_list)
    make_all_excel_compliance_checks(sheet_list)
    return _construct_ids(sheet_list)


def _add_id_optional_column_if_not_exists(sheet_list: list[ExcelSheet]) -> list[ExcelSheet]:
    all_sheets = []
    for sheet in sheet_list:
        if "id (optional)" not in sheet.df.columns:
            df = sheet.df
            df["id (optional)"] = pd.NA
            all_sheets.append(ExcelSheet(excel_name=sheet.excel_name, sheet_name=sheet.sheet_name, df=df))
        else:
            all_sheets.append(sheet)
    return all_sheets


def _construct_ids(sheet_list: list[ExcelSheet]) -> list[ExcelSheet]:
    all_sheets = []
    for sheet in sheet_list:
        df = _complete_id_one_df(sheet.df, get_preferred_language(sheet.df.columns))
        all_sheets.append(ExcelSheet(excel_name=sheet.excel_name, sheet_name=sheet.sheet_name, df=df))
    all_sheets = _resolve_duplicate_ids_all_excels(all_sheets)
    return _fill_parent_id_col_all_excels(all_sheets)


def _fill_parent_id_col_all_excels(sheet_list: list[ExcelSheet]) -> list[ExcelSheet]:
    all_sheets = []
    for sheet in sheet_list:
        df = _fill_parent_id_col_one_df(sheet.df, get_preferred_language(sheet.df.columns))
        all_sheets.append(ExcelSheet(excel_name=sheet.excel_name, sheet_name=sheet.sheet_name, df=df))
    return all_sheets


def _fill_parent_id_col_one_df(df: pd.DataFrame, preferred_language: str) -> pd.DataFrame:
    """Create an extra column with the ID of the parent node."""
    # To start, all rows get the ID of the list. These will be overwritten if the row has another parent.
    df["parent_id"] = df.at[0, "id"]
    columns = get_columns_of_preferred_lang(df.columns, preferred_language, r"\d+")
    for num in range(len(columns)):
        grouped = df.groupby(columns[: num + 1])
        for name, group in grouped:
            if group.shape[0] > 1:
                # The first row already has the correct ID assigned
                rest_index = list(group.index)[1:]
                df.loc[rest_index, "parent_id"] = group.at[group.index[0], "id"]
    return df


def _resolve_duplicate_ids_all_excels(sheet_list: list[ExcelSheet]) -> list[ExcelSheet]:
    ids = []
    for sheet in sheet_list:
        ids.extend(sheet.df["id"].tolist())
    counter = Counter(ids)
    if duplicate_ids := [item for item, count in counter.items() if count > 1]:
        return _remove_duplicate_ids_in_all_excels(duplicate_ids, sheet_list)
    return sheet_list


def _remove_duplicate_ids_in_all_excels(duplicate_ids: list[str], sheet_list: list[ExcelSheet]) -> list[ExcelSheet]:
    all_sheets = []
    for sheet in sheet_list:
        preferred_lang = get_preferred_language(sheet.df.columns)
        df = sheet.df
        for i, row in df.iterrows():
            if row["id"] in duplicate_ids and pd.isna(row["id (optional)"]):
                df.at[i, "id"] = _construct_non_duplicate_id_string(df.iloc[int(str(i))], preferred_lang)
        all_sheets.append(ExcelSheet(sheet.excel_name, sheet.sheet_name, df))
    return sheet_list


def _complete_id_one_df(df: pd.DataFrame, preferred_language: str) -> pd.DataFrame:
    if "id (optional)" not in df.columns:
        df["id (optional)"] = pd.NA
    df = _create_auto_id_one_df(df, preferred_language)
    df["id"] = df["id (optional)"].fillna(df["auto_id"])
    df = _resolve_duplicate_ids_keep_custom_change_auto_id_one_df(df, preferred_language)
    return df


def _resolve_duplicate_ids_keep_custom_change_auto_id_one_df(df: pd.DataFrame, preferred_language: str) -> pd.DataFrame:
    """If there are duplicates in the id column, the auto_id is changed, the custom ID remains the same."""
    if (duplicate_filter := df["id"].duplicated(keep=False)).any():
        for i in duplicate_filter.index[duplicate_filter]:
            if pd.isna(df.at[i, "id (optional)"]):
                df.loc[i, "id"] = _construct_non_duplicate_id_string(df.iloc[i], preferred_language)
    return df


def _create_auto_id_one_df(df: pd.DataFrame, preferred_language: str) -> pd.DataFrame:
    """For every node without manual ID, take the label of the preferred language as ID."""
    df["auto_id"] = pd.NA
    if not df["id (optional)"].isna().any():
        return df
    if pd.isna(df.at[0, "id (optional)"]):
        df.loc[0, "auto_id"] = df.at[0, f"{preferred_language}_list"]
    column_names = sorted(get_columns_of_preferred_lang(df.columns, preferred_language, r"\d+"), reverse=True)
    for i, row in df.iterrows():
        if pd.isna(row["id (optional)"]):
            for col in column_names:
                if pd.notna(row[col]):
                    df.at[i, "auto_id"] = row[col]
                    break
    df = _resolve_duplicate_ids_for_auto_id_one_df(df, preferred_language)
    return df


def _resolve_duplicate_ids_for_auto_id_one_df(df: pd.DataFrame, preferred_language: str) -> pd.DataFrame:
    """In case the auto_id is not unique; both auto_ids get a new ID by joining the node names of all the ancestors."""
    if (duplicate_filter := df["auto_id"].dropna().duplicated(keep=False)).any():
        for i in duplicate_filter.index[duplicate_filter]:
            df.at[i, "auto_id"] = _construct_non_duplicate_id_string(df.iloc[i], preferred_language)
    return df


def _construct_non_duplicate_id_string(row: pd.Series[Any], preferred_language: str) -> str:
    """In case the node name is not unique; an ID is created by joining the node names of all the ancestors."""
    column_names = get_columns_of_preferred_lang(row.index, preferred_language, r"\d+")
    column_names.insert(0, f"{preferred_language}_list")
    id_cols = [row[col] for col in column_names if pd.notna(row[col])]
    return ":".join(id_cols)


def _make_serialised_lists(sheet_list: list[ExcelSheet]) -> list[dict[str, Any]]:
    all_lists = _make_all_lists(sheet_list)
    if isinstance(all_lists, ListCreationProblem):
        msg = all_lists.execute_error_protocol()
        logger.error(msg)
        raise InputError(msg)
    return [list_.to_dict() for list_ in all_lists]


def _make_all_lists(sheet_list: list[ExcelSheet]) -> list[ListRoot] | ListCreationProblem:
    good_lists = []
    problem_lists: list[SheetProblem] = []
    for sheet in sheet_list:
        if isinstance(new_list := _make_one_list(sheet), ListRoot):
            good_lists.append(new_list)
        else:
            problem_lists.append(new_list)
    if problem_lists:
        return ListCreationProblem([CollectedSheetProblems(problem_lists)])
    return good_lists


def _make_one_list(sheet: ExcelSheet) -> ListRoot | ListSheetProblem:
    node_dict, node_problems = _make_list_nodes_from_df(sheet.df)
    nodes_for_root = _add_nodes_to_parent(node_dict, sheet.df.at[0, "id"]) if node_dict else []
    col_titles_of_root_cols = [x for x in sheet.df.columns if regex.search(r"^(en|de|fr|it|rm)_list$", x)]
    root = ListRoot.create(
        id_=sheet.df.at[0, "id"],
        labels=_get_labels(sheet.df.iloc[0], col_titles_of_root_cols),
        excel_name=sheet.excel_name,
        sheet_name=sheet.sheet_name,
        nodes=nodes_for_root,
        comments={},
    )
    match (root, node_problems):
        case (ListRoot(), list(ListNodeProblem())):
            return ListSheetProblem(
                excel_name=sheet.excel_name, sheet_name=sheet.sheet_name, root_problems={}, node_problems=node_problems
            )
        case (ListSheetProblem(), _):
            root.node_problems = node_problems
    return root


def _add_nodes_to_parent(node_dict: dict[str, ListNode], list_id: str) -> list[ListNode]:
    root_list = []
    for _, node in node_dict.items():
        if node.parent_id == list_id:
            root_list.append(node)
        else:
            node_dict[node.parent_id].sub_nodes.append(node)
    return root_list


def _make_list_nodes_from_df(df: pd.DataFrame) -> tuple[dict[str, ListNode], list[ListNodeProblem]]:
    columns_for_nodes = _get_reverse_sorted_columns_list(df)
    problems = []
    node_dict = {}
    for i, row in df[1:].iterrows():
        node = _make_one_node(row, columns_for_nodes, str(i))
        match node:
            case ListNode():
                node_dict[node.id_] = node
            case ListNodeProblem():
                problems.append(node)
    return node_dict, problems


def _make_one_node(row: pd.Series[Any], list_of_columns: list[list[str]], index: str) -> ListNode | ListNodeProblem:
    for col_group in list_of_columns:
        if labels := _get_labels(row, col_group):
            return ListNode.create(id_=row["id"], labels=labels, parent_id=row["parent_id"], sub_nodes=[])
    return ListNodeProblem(node_id=row["id"], problems={"Unknown": f"Unknown problem occurred in row number: {index}"})


def _get_reverse_sorted_columns_list(df: pd.DataFrame) -> list[list[str]]:
    numbers = sorted(get_hierarchy_nums(df.columns), reverse=True)
    languages = get_all_languages_for_columns(df.columns, r"\d+")
    return [[f"{lang}_{num}" for lang in languages] for num in numbers]


def _get_labels(row: pd.Series[Any], columns: list[str]) -> dict[str, str]:
    """
    Provided a df row and a list of column titles,
    create a mapping from language codes to the label of that language.
    (The label comes from the Excel cell at the intersection of the row with the column.)

    Parameters:
        row: A pandas Series representing a row of a DataFrame.
        columns: A list of column names.

    Returns:
        A dictionary with language codes as keys and the corresponding labels as values.
    """
    return {
        lang: row[col] for col in columns if not (pd.isna(row[col])) and (lang := get_lang_string_from_column_name(col))
    }
