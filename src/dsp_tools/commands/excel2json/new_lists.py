from __future__ import annotations

import json
import warnings
from collections import Counter
from collections import defaultdict
from pathlib import Path
from typing import Any
from typing import Optional
from typing import cast

import pandas as pd
import regex
from loguru import logger

from dsp_tools.commands.excel2json.lists import validate_lists_section_with_schema
from dsp_tools.commands.excel2json.models.input_error import PositionInExcel
from dsp_tools.commands.excel2json.models.input_error import Problem
from dsp_tools.commands.excel2json.models.input_error_lists import CollectedSheetProblems
from dsp_tools.commands.excel2json.models.input_error_lists import DuplicateIDProblem
from dsp_tools.commands.excel2json.models.input_error_lists import DuplicatesCustomIDInProblem
from dsp_tools.commands.excel2json.models.input_error_lists import DuplicatesInSheetProblem
from dsp_tools.commands.excel2json.models.input_error_lists import DuplicatesListNameProblem
from dsp_tools.commands.excel2json.models.input_error_lists import ListCreationProblem
from dsp_tools.commands.excel2json.models.input_error_lists import ListInformation
from dsp_tools.commands.excel2json.models.input_error_lists import ListNodeProblem
from dsp_tools.commands.excel2json.models.input_error_lists import ListSheetComplianceProblem
from dsp_tools.commands.excel2json.models.input_error_lists import ListSheetContentProblem
from dsp_tools.commands.excel2json.models.input_error_lists import ListSheetProblem
from dsp_tools.commands.excel2json.models.input_error_lists import MissingNodeTranslationProblem
from dsp_tools.commands.excel2json.models.input_error_lists import MissingTranslationsSheetProblem
from dsp_tools.commands.excel2json.models.input_error_lists import MultipleListPerSheetProblem
from dsp_tools.commands.excel2json.models.input_error_lists import NodesPerRowProblem
from dsp_tools.commands.excel2json.models.input_error_lists import SheetProblem
from dsp_tools.commands.excel2json.models.new_lists_deserialise import ExcelFile
from dsp_tools.commands.excel2json.models.new_lists_deserialise import ExcelSheet
from dsp_tools.commands.excel2json.models.new_lists_serialise import ListNode
from dsp_tools.commands.excel2json.models.new_lists_serialise import ListRoot
from dsp_tools.commands.excel2json.utils import read_and_clean_all_sheets
from dsp_tools.models.custom_warnings import DspToolsUserWarning
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
    list_files = _parse_files(excelfolder)

    finished_lists = _make_serialised_lists(list_files)
    validate_lists_section_with_schema(lists_section=finished_lists)

    if path_to_output_file:
        with open(path_to_output_file, "w", encoding="utf-8") as fp:
            json.dump(finished_lists, fp, indent=4, ensure_ascii=False)
            print(f"lists section was created successfully and written to file '{path_to_output_file}'")

    return finished_lists, True


def _parse_files(excelfolder: Path | str) -> list[ExcelFile]:
    file_names = [file for file in Path(excelfolder).glob("*list*.xlsx", case_sensitive=False) if _non_hidden(file)]
    all_files = []
    for file in file_names:
        sheets = [
            ExcelSheet(excel_name=str(file), sheet_name=name, df=df)
            for name, df in read_and_clean_all_sheets(file).items()
        ]
        all_files.append(ExcelFile(filename=str(file), sheets=sheets))
    return all_files


def _non_hidden(path: Path) -> bool:
    return not regex.search(r"^(\.|~\$).+", path.name)


def _make_serialised_lists(list_files: list[ExcelFile]) -> list[dict[str, Any]]:
    list_files = _prepare_dfs(list_files)
    all_lists = _make_all_lists(list_files)
    if isinstance(all_lists, ListCreationProblem):
        msg = all_lists.execute_error_protocol()
        logger.error(msg)
        raise InputError(msg)
    return [list_.to_dict() for list_ in all_lists]


def _make_all_lists(list_files: list[ExcelFile]) -> list[ListRoot] | ListCreationProblem:
    good_lists = []
    problem_lists: list[SheetProblem] = []
    for file in list_files:
        for sheet in file.sheets:
            if isinstance(new_list := _make_one_list(sheet), ListRoot):
                good_lists.append(new_list)
            else:
                problem_lists.append(new_list)
    if problem_lists:
        return ListCreationProblem([CollectedSheetProblems(problem_lists)])
    return good_lists


def _prepare_dfs(list_files: list[ExcelFile]) -> list[ExcelFile]:
    list_files = _add_id_optional_column_if_not_exists(list_files)
    _make_all_formal_excel_compliance_checks(list_files)
    return _construct_ids(list_files)


def _add_id_optional_column_if_not_exists(list_files: list[ExcelFile]) -> list[ExcelFile]:
    all_files = []
    for file in list_files:
        all_sheets = []
        for sheet in file.sheets:
            if "id (optional)" not in sheet.df.columns:
                df = sheet.df
                df["id (optional)"] = pd.NA
                all_sheets.append(ExcelSheet(excel_name=file.filename, sheet_name=sheet.sheet_name, df=df))
            else:
                all_sheets.append(sheet)
        all_files.append(ExcelFile(filename=file.filename, sheets=all_sheets))
    return all_files


def _construct_ids(list_files: list[ExcelFile]) -> list[ExcelFile]:
    all_files = []
    for file in list_files:
        all_sheets = []
        for sheet in file.sheets:
            df = _complete_id_one_df(sheet.df, _get_preferred_language(sheet.df.columns))
            all_sheets.append(ExcelSheet(excel_name=file.filename, sheet_name=sheet.sheet_name, df=df))
        all_files.append(ExcelFile(filename=file.filename, sheets=all_sheets))
    all_files = _resolve_duplicate_ids_all_excels(all_files)
    return _fill_parent_id_col_all_excels(all_files)


def _fill_parent_id_col_all_excels(list_files: list[ExcelFile]) -> list[ExcelFile]:
    all_files = []
    for file in list_files:
        all_sheets = []
        for sheet in file.sheets:
            df = _fill_parent_id_col_one_df(sheet.df, _get_preferred_language(sheet.df.columns))
            all_sheets.append(ExcelSheet(excel_name=file.filename, sheet_name=sheet.sheet_name, df=df))
        all_files.append(ExcelFile(filename=file.filename, sheets=all_sheets))
    return all_files


def _fill_parent_id_col_one_df(df: pd.DataFrame, preferred_language: str) -> pd.DataFrame:
    """Create an extra column with the ID of the parent node."""
    # To start, all rows get the ID of the list. These will be overwritten if the row has another parent.
    df["parent_id"] = df.at[0, "id"]
    columns = _get_columns_of_preferred_lang(df.columns, preferred_language, r"\d+")
    for num in range(len(columns)):
        grouped = df.groupby(columns[: num + 1])
        for name, group in grouped:
            if group.shape[0] > 1:
                # The first row already has the correct ID assigned
                rest_index = list(group.index)[1:]
                df.loc[rest_index, "parent_id"] = group.at[group.index[0], "id"]
    return df


def _resolve_duplicate_ids_all_excels(list_files: list[ExcelFile]) -> list[ExcelFile]:
    ids = []
    for file in list_files:
        for sheet in file.sheets:
            ids.extend(sheet.df["id"].tolist())
    counter = Counter(ids)
    if duplicate_ids := [item for item, count in counter.items() if count > 1]:
        return _remove_duplicate_ids_in_all_excels(duplicate_ids, list_files)
    return list_files


def _remove_duplicate_ids_in_all_excels(duplicate_ids: list[str], list_files: list[ExcelFile]) -> list[ExcelFile]:
    all_files = []
    for file in list_files:
        all_sheets = []
        for sheet in file.sheets:
            preferred_lang = _get_preferred_language(sheet.df.columns)
            df = sheet.df
            for i, row in df.iterrows():
                if row["id"] in duplicate_ids and pd.isna(row["id (optional)"]):
                    df.at[i, "id"] = _construct_non_duplicate_id_string(df.iloc[int(str(i))], preferred_lang)
            all_sheets.append(ExcelSheet(file.filename, sheet.sheet_name, df))
        all_files.append(ExcelFile(file.filename, all_sheets))
    return list_files


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
    column_names = sorted(_get_columns_of_preferred_lang(df.columns, preferred_language, r"\d+"), reverse=True)
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
    column_names = _get_columns_of_preferred_lang(row.index, preferred_language, r"\d+")
    column_names.insert(0, f"{preferred_language}_list")
    id_cols = [row[col] for col in column_names if pd.notna(row[col])]
    return ":".join(id_cols)


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
    numbers = sorted(_get_hierarchy_nums(df.columns), reverse=True)
    languages = _get_all_languages_for_columns(df.columns, r"\d+")
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
        lang: row[col]
        for col in columns
        if not (pd.isna(row[col])) and (lang := _get_lang_string_from_column_name(col))
    }


def _get_lang_string_from_column_name(col_str: str, ending: str = r"(\d+|list)") -> str | None:
    if res := regex.search(rf"^(en|de|fr|it|rm)_{ending}$", col_str):
        return res.group(1)
    return None


def _get_columns_of_preferred_lang(
    columns: pd.Index[str], preferred_language: str, ending: str = r"(\d+|list)"
) -> list[str]:
    return sorted(col for col in columns if regex.search(rf"^{preferred_language}_{ending}$", col))


def _get_hierarchy_nums(columns: pd.Index[str]) -> list[int]:
    return sorted(
        list(set(int(res.group(2)) for x in columns if (res := regex.search(r"^(en|de|fr|it|rm)_(\d+)$", x))))
    )


def _get_all_languages_for_columns(columns: pd.Index[str], ending: str = r"(\d+|list)") -> set[str]:
    return set(res for x in columns if (res := _get_lang_string_from_column_name(x, ending)))


def _get_preferred_language(columns: pd.Index[str], ending: str = r"(\d+|list)") -> str:
    match = [res.group(1) for x in columns if (res := regex.search(rf"^(en|de|fr|it|rm)_{ending}+$", x))]
    if "en" in match:
        return "en"
    elif "de" in match:
        return "de"
    elif "fr" in match:
        return "fr"
    elif "it" in match:
        return "it"
    elif "rm" in match:
        return "rm"
    msg = (
        f"The columns may only contain the languages: 'en', 'de', 'fr', 'it', 'rm'.\n"
        f"The columns are: {" ".join(columns)}"
    )
    raise InputError(msg)


def _make_all_formal_excel_compliance_checks(list_files: list[ExcelFile]) -> None:
    """Check if the excel files are compliant with the expected format."""
    # These functions must be called in this order,
    # as some of the following checks only work if the previous have passed.
    _check_duplicates_all_excels(list_files)
    _check_for_unique_list_names(list_files)
    _make_shape_compliance_all_excels(list_files)
    _make_all_content_compliance_checks_all_excels(list_files)


def _check_duplicates_all_excels(list_files: list[ExcelFile]) -> None:
    """
    Check if the excel files contain duplicates with regard to the node names,
    and if the custom IDs are unique across all excel files.
    A duplicate in the node names is defined as several rows with the same entries in the columns with the node names.

    Args:
        list_files: class instances representing an excel file with sheets

    Raises:
        InputError: If any complete duplicates are found in the excel files.
    """
    problems: list[Problem] = []
    duplicate_problems: list[SheetProblem] = []
    for file in list_files:
        duplicate_problems.extend(
            [p for sheet in file.sheets if (p := _check_for_duplicate_nodes_one_df(sheet)) is not None]
        )
    if duplicate_problems:
        problems.append(CollectedSheetProblems(duplicate_problems))
    if id_problem := _check_for_duplicate_custom_id_all_excels(list_files):
        problems.append(id_problem)
    if problems:
        msg = ListCreationProblem(problems).execute_error_protocol()
        logger.error(msg)
        raise InputError(msg)


def _check_for_unique_list_names(list_files: list[ExcelFile]) -> None:
    """This functon checks that one sheet only has one list and that all lists have unique names."""
    list_names: list[ListInformation] = []
    all_problems: list[Problem] = []
    sheet_problems: list[SheetProblem] = []
    for excel_file in list_files:
        for sheet in excel_file.sheets:
            preferred_language = _get_preferred_language(sheet.df.columns, r"list")
            unique_list_names = list(sheet.df[f"{preferred_language}_list"].unique())
            if len(unique_list_names) != 1:
                sheet_problems.append(
                    MultipleListPerSheetProblem(sheet.excel_name, sheet.sheet_name, unique_list_names)
                )
            list_names.extend(
                [ListInformation(excel_file.filename, sheet.sheet_name, name) for name in unique_list_names]
            )
    if sheet_problems:
        all_problems.append(CollectedSheetProblems(sheet_problems))
    list_info_dict = defaultdict(list)
    for item in list_names:
        list_info_dict[item.list_name].append(item)
    duplicate_list_names = []
    for info in list_info_dict.values():
        if len(info) > 1:
            duplicate_list_names.extend(info)
    if duplicate_list_names:
        all_problems.append(DuplicatesListNameProblem(duplicate_list_names))
    if all_problems:
        msg = ListCreationProblem(all_problems).execute_error_protocol()
        logger.error(msg)
        raise InputError(msg)


def _check_for_duplicate_nodes_one_df(sheet: ExcelSheet) -> DuplicatesInSheetProblem | None:
    """Check if any rows have duplicates when taking into account the columns with the node names."""
    lang_columns = [col for col in sheet.df.columns if regex.search(r"^(en|de|fr|it|rm)_(\d+|list)$", col)]
    if (duplicate_filter := sheet.df.duplicated(lang_columns, keep=False)).any():
        return DuplicatesInSheetProblem(
            sheet.excel_name, sheet.sheet_name, duplicate_filter.index[duplicate_filter].tolist()
        )
    return None


def _check_for_duplicate_custom_id_all_excels(list_files: list[ExcelFile]) -> DuplicatesCustomIDInProblem | None:
    id_list = []
    for file in list_files:
        for sheet in file.sheets:
            for i, row in sheet.df.iterrows():
                if not pd.isna(row["id (optional)"]):
                    id_list.append(
                        {
                            "filename": file.filename,
                            "sheet_name": sheet.sheet_name,
                            "id": row["id (optional)"],
                            "row_number": int(str(i)) + 2,
                        }
                    )
    id_df = pd.DataFrame.from_records(id_list)
    if (duplicate_ids := id_df.duplicated("id", keep=False)).any():
        problems: dict[str, DuplicateIDProblem] = defaultdict(lambda: DuplicateIDProblem())
        for i, row in id_df[duplicate_ids].iterrows():
            problems[row["id"]].custom_id = row["id"]
            problems[row["id"]].excel_locations.append(
                PositionInExcel(sheet=row["sheet_name"], excel_filename=row["filename"], row=row["row_number"])
            )
        final_problems = list(problems.values())
        return DuplicatesCustomIDInProblem(final_problems)
    return None


def _make_shape_compliance_all_excels(list_files: list[ExcelFile]) -> None:
    """Check if the excel files are compliant with the expected format."""
    problems: list[SheetProblem] = []
    for file in list_files:
        problems.extend([p for sheet in file.sheets if (p := _make_shape_compliance_one_sheet(sheet)) is not None])
    if problems:
        msg = ListCreationProblem([CollectedSheetProblems(problems)]).execute_error_protocol()
        logger.error(msg)
        raise InputError(msg)


def _make_shape_compliance_one_sheet(sheet: ExcelSheet) -> ListSheetComplianceProblem | None:
    problems = {}
    problems.update(_check_minimum_rows(sheet.df))
    problems.update(_check_if_minimum_number_of_cols_present_one_sheet(sheet.df.columns))
    problems.update(_check_if_all_translations_in_all_column_levels_present_one_sheet(sheet.df.columns))
    _check_warn_unusual_columns_one_sheet(sheet.df.columns)
    if problems:
        return ListSheetComplianceProblem(sheet.excel_name, sheet.sheet_name, problems)
    return None


def _check_minimum_rows(df: pd.DataFrame) -> dict[str, str]:
    if len(df) < 2:
        return {
            "minimum rows": "The Excel sheet must contain at least two rows, "
            "one for the list name and one row for a minimum of one node."
        }
    return {}


def _check_if_minimum_number_of_cols_present_one_sheet(cols: pd.Index[str]) -> dict[str, str]:
    problem = {}
    node_langs = [_get_lang_string_from_column_name(c, r"\d+") for c in cols]
    if not any(node_langs):
        problem["missing columns for nodes"] = (
            "There is no column with the expected format for the list nodes: '[lang]_[column_number]'"
        )
    list_langs = [_get_lang_string_from_column_name(c, r"list") for c in cols]
    if not any(list_langs):
        problem["missing columns for list name"] = (
            "There is no column with the expected format for the list names: '[lang]_list'"
        )
    return problem


def _check_warn_unusual_columns_one_sheet(cols: pd.Index[str]) -> None:
    not_matched = [x for x in cols if not regex.search(r"^(en|de|fr|it|rm)_(\d+|list)|(id \(optional\))$", x)]
    if not_matched:
        msg = (
            f"The following columns do not conform to the expected format "
            f"and will not be included in the output: {', '.join(not_matched)}"
        )
        warnings.warn(DspToolsUserWarning(msg))


def _check_if_all_translations_in_all_column_levels_present_one_sheet(cols: pd.Index[str]) -> dict[str, str]:
    # All levels, eg. 1, 2, 3 must have the same languages
    languages = {r for c in cols if (r := _get_lang_string_from_column_name(c)) is not None}
    all_nums = [str(n) for n in _get_hierarchy_nums(cols)]
    all_nums.append("list")

    def make_col_names(lang: str) -> set[str]:
        return {f"{lang}_{num}" for num in all_nums}

    expected_cols = set()
    for lang in languages:
        expected_cols.update(make_col_names(lang))
    if missing_cols := expected_cols - set(cols):
        return {
            "missing translations": f"All nodes must be translated into the same languages. "
            f"Based on the languages used, the following column(s) are missing: "
            f"{', '.join(missing_cols)}"
        }
    return {}


def _make_all_content_compliance_checks_all_excels(list_files: list[ExcelFile]) -> None:
    """Check if the content of the excel files is compliant with the expected format."""
    _check_for_missing_translations_all_excels(list_files)
    _check_for_erroneous_entries_all_excels(list_files)


def _check_for_missing_translations_all_excels(list_files: list[ExcelFile]) -> None:
    problems: list[SheetProblem] = []
    for file in list_files:
        problems.extend(
            [p for sheet in file.sheets if (p := _check_for_missing_translations_one_sheet(sheet)) is not None]
        )
    if problems:
        msg = ListCreationProblem([CollectedSheetProblems(problems)]).execute_error_protocol()
        logger.error(msg)
        raise InputError(msg)


def _check_for_missing_translations_one_sheet(sheet: ExcelSheet) -> MissingTranslationsSheetProblem | None:
    col_endings = [str(num) for num in _get_hierarchy_nums(sheet.df.columns)]
    col_endings.append("list")
    languages = _get_all_languages_for_columns(sheet.df.columns)
    all_cols = _compose_all_combinatoric_column_titles(col_endings, languages)
    problems = []
    for column_group in all_cols:
        problems.extend(_check_for_missing_translations_one_column_level(column_group, sheet.df))
    if problems:
        return MissingTranslationsSheetProblem(sheet.excel_name, sheet.sheet_name, problems)
    return None


def _check_for_missing_translations_one_column_level(
    columns: list[str], df: pd.DataFrame
) -> list[MissingNodeTranslationProblem]:
    # column level refers to the hierarchical level of the nodes. eg. ["en_1", "de_1", "fr_1", "it_1", "rm_1"]
    problems = []
    for i, row in df.iterrows():
        if problem := _check_for_missing_translations_one_node(row, columns, int(str(i))):
            problems.append(problem)
    return problems


def _compose_all_combinatoric_column_titles(nums: list[str], languages: set[str]) -> list[list[str]]:
    return [[f"{lang}_{num}" for lang in languages] for num in nums]


def _check_for_missing_translations_one_node(
    row: pd.Series[Any], columns: list[str], row_index: int
) -> MissingNodeTranslationProblem | None:
    missing = row[columns].isna()
    if missing.any() and not missing.all():
        missing_cols = [str(index) for index, is_missing in missing.items() if is_missing]
        return MissingNodeTranslationProblem(missing_cols, row_index)
    return None


def _check_for_erroneous_entries_all_excels(list_files: list[ExcelFile]) -> None:
    problems: list[SheetProblem] = []
    for file in list_files:
        problems.extend([p for sheet in file.sheets if (p := _check_for_erroneous_entries_one_list(sheet)) is not None])
    if problems:
        msg = ListCreationProblem([CollectedSheetProblems(problems)]).execute_error_protocol()
        logger.error(msg)
        raise InputError(msg)


def _check_for_erroneous_entries_one_list(sheet: ExcelSheet) -> ListSheetContentProblem | None:
    preferred_lang = _get_preferred_language(sheet.df.columns)
    preferred_cols = _get_columns_of_preferred_lang(sheet.df.columns, preferred_lang, r"\d+")
    preferred_cols = sorted(preferred_cols)
    preferred_cols.insert(0, f"{preferred_lang}_list")
    problems = _check_for_erroneous_node_info_one_df(sheet.df, preferred_cols)
    if problems:
        list_problems = cast(list[Problem], problems)
        return ListSheetContentProblem(sheet.excel_name, sheet.sheet_name, list_problems)
    return None


def _check_for_erroneous_node_info_one_df(df: pd.DataFrame, columns: list[str]) -> list[NodesPerRowProblem]:
    problems = []
    for focus_col_index, col in enumerate(columns):
        problems.extend(_check_for_erroneous_entries_one_column_level(df, columns, focus_col_index))
    return problems


def _check_for_erroneous_entries_one_column_level(
    df: pd.DataFrame, columns: list[str], focus_col_index: int
) -> list[NodesPerRowProblem]:
    # column level refers to the hierarchical level of the nodes. eg. "en_1"
    # we need to group by from the current column all the way back to its ancestors,
    # otherwise identical values in that column may be interpreted as belonging to the same group
    grouped = df.groupby(columns[: focus_col_index + 1])
    problems = []
    for name, group in grouped:
        remaining_to_check_columns = columns[focus_col_index:]
        problems.extend(_check_for_erroneous_entries_one_grouped_df(group, remaining_to_check_columns))
    return problems


def _check_for_erroneous_entries_one_grouped_df(
    group: pd.DataFrame, target_cols: list[str]
) -> list[NodesPerRowProblem]:
    problems = []
    first_col = min(group.index)
    # The first row is the current parent node. The remaining columns in that row must be empty.
    if not group.loc[first_col, target_cols[1:]].isna().all():
        problems.append(NodesPerRowProblem(target_cols[1:], int(first_col), should_be_empty=True))
    if not len(target_cols) > 1:
        return problems
    # The second column of the remaining rows must not be empty, as these are the child nodes of the first row.
    remaining_rows_of_next_column = group.loc[group.index[1:], target_cols[1]]
    if (missing := remaining_rows_of_next_column.isna()).any():
        for i, row in group[1:][missing].iterrows():
            problems.append(NodesPerRowProblem([target_cols[1]], int(str(i)), should_be_empty=False))
    return problems
