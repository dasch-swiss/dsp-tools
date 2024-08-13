from __future__ import annotations

import warnings
from collections import defaultdict
from typing import Any
from typing import cast

import pandas as pd
import regex
from loguru import logger

from dsp_tools.commands.excel2json.models.input_error import PositionInExcel
from dsp_tools.commands.excel2json.models.input_error import Problem
from dsp_tools.commands.excel2json.new_lists.models.deserialise import ExcelSheet
from dsp_tools.commands.excel2json.new_lists.models.input_error import CollectedSheetProblems
from dsp_tools.commands.excel2json.new_lists.models.input_error import DuplicateIDProblem
from dsp_tools.commands.excel2json.new_lists.models.input_error import DuplicatesCustomIDInProblem
from dsp_tools.commands.excel2json.new_lists.models.input_error import DuplicatesInSheetProblem
from dsp_tools.commands.excel2json.new_lists.models.input_error import DuplicatesListNameProblem
from dsp_tools.commands.excel2json.new_lists.models.input_error import ListCreationProblem
from dsp_tools.commands.excel2json.new_lists.models.input_error import ListInformation
from dsp_tools.commands.excel2json.new_lists.models.input_error import ListSheetComplianceProblem
from dsp_tools.commands.excel2json.new_lists.models.input_error import ListSheetContentProblem
from dsp_tools.commands.excel2json.new_lists.models.input_error import MissingNodeTranslationProblem
from dsp_tools.commands.excel2json.new_lists.models.input_error import MissingTranslationsSheetProblem
from dsp_tools.commands.excel2json.new_lists.models.input_error import MultipleListPerSheetProblem
from dsp_tools.commands.excel2json.new_lists.models.input_error import NodesPerRowProblem
from dsp_tools.commands.excel2json.new_lists.models.input_error import SheetProblem
from dsp_tools.commands.excel2json.new_lists.utils import get_all_languages_for_columns
from dsp_tools.commands.excel2json.new_lists.utils import get_columns_of_preferred_lang
from dsp_tools.commands.excel2json.new_lists.utils import get_hierarchy_nums
from dsp_tools.commands.excel2json.new_lists.utils import get_lang_string_from_column_name
from dsp_tools.commands.excel2json.new_lists.utils import get_preferred_language
from dsp_tools.models.custom_warnings import DspToolsUserWarning
from dsp_tools.models.exceptions import InputError


def make_all_formal_excel_compliance_checks(sheet_list: list[ExcelSheet]) -> None:
    """Check if the excel files are compliant with the expected format."""
    # These functions must be called in this order,
    # as some of the following checks only work if the previous have passed.
    _check_duplicates_all_excels(sheet_list)
    _check_for_unique_list_names(sheet_list)
    _make_shape_compliance_all_excels(sheet_list)
    _make_all_content_compliance_checks_all_excels(sheet_list)


def _check_duplicates_all_excels(sheet_list: list[ExcelSheet]) -> None:
    """
    Check if the excel files contain duplicates with regard to the node names,
    and if the custom IDs are unique across all excel files.
    A duplicate in the node names is defined as several rows with the same entries in the columns with the node names.

    Args:
        sheet_list: class instances representing an excel file with sheets

    Raises:
        InputError: If any complete duplicates are found in the excel files.
    """
    problems: list[Problem] = []
    duplicate_problems: list[SheetProblem] = [
        p for sheet in sheet_list if (p := _check_for_duplicate_nodes_one_df(sheet)) is not None
    ]
    if duplicate_problems:
        problems.append(CollectedSheetProblems(duplicate_problems))
    if id_problem := _check_for_duplicate_custom_id_all_excels(sheet_list):
        problems.append(id_problem)
    if problems:
        msg = ListCreationProblem(problems).execute_error_protocol()
        logger.error(msg)
        raise InputError(msg)


def _check_for_unique_list_names(sheet_list: list[ExcelSheet]) -> None:
    """This functon checks that one sheet only has one list and that all lists have unique names."""
    list_names: list[ListInformation] = []
    all_problems: list[Problem] = []
    sheet_problems: list[SheetProblem] = []
    for sheet in sheet_list:
        preferred_language = get_preferred_language(sheet.df.columns, r"list")
        unique_list_names = list(sheet.df[f"{preferred_language}_list"].unique())
        if len(unique_list_names) != 1:
            sheet_problems.append(MultipleListPerSheetProblem(sheet.excel_name, sheet.sheet_name, unique_list_names))
        list_names.extend([ListInformation(sheet.excel_name, sheet.sheet_name, name) for name in unique_list_names])
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


def _check_for_duplicate_custom_id_all_excels(sheet_list: list[ExcelSheet]) -> DuplicatesCustomIDInProblem | None:
    id_list = []
    for sheet in sheet_list:
        for i, row in sheet.df.iterrows():
            if not pd.isna(row["id (optional)"]):
                id_list.append(
                    {
                        "filename": sheet.excel_name,
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


def _make_shape_compliance_all_excels(sheet_list: list[ExcelSheet]) -> None:
    """Check if the excel files are compliant with the expected format."""
    problems: list[SheetProblem] = [
        p for sheet in sheet_list if (p := _make_shape_compliance_one_sheet(sheet)) is not None
    ]
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
    node_langs = [get_lang_string_from_column_name(c, r"\d+") for c in cols]
    if not any(node_langs):
        problem["missing columns for nodes"] = (
            "There is no column with the expected format for the list nodes: '[lang]_[column_number]'"
        )
    list_langs = [get_lang_string_from_column_name(c, r"list") for c in cols]
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
    languages = {r for c in cols if (r := get_lang_string_from_column_name(c)) is not None}
    all_nums = [str(n) for n in get_hierarchy_nums(cols)]
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


def _make_all_content_compliance_checks_all_excels(sheet_list: list[ExcelSheet]) -> None:
    """Check if the content of the excel files is compliant with the expected format."""
    _check_for_missing_translations_all_excels(sheet_list)
    _check_for_erroneous_entries_all_excels(sheet_list)


def _check_for_missing_translations_all_excels(sheet_list: list[ExcelSheet]) -> None:
    problems: list[SheetProblem] = [
        p for sheet in sheet_list if (p := _check_for_missing_translations_one_sheet(sheet)) is not None
    ]
    if problems:
        msg = ListCreationProblem([CollectedSheetProblems(problems)]).execute_error_protocol()
        logger.error(msg)
        raise InputError(msg)


def _check_for_missing_translations_one_sheet(sheet: ExcelSheet) -> MissingTranslationsSheetProblem | None:
    col_endings = [str(num) for num in get_hierarchy_nums(sheet.df.columns)]
    col_endings.append("list")
    languages = get_all_languages_for_columns(sheet.df.columns)
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


def _check_for_erroneous_entries_all_excels(sheet_list: list[ExcelSheet]) -> None:
    problems: list[SheetProblem] = [
        p for sheet in sheet_list if (p := _check_for_erroneous_entries_one_list(sheet)) is not None
    ]
    if problems:
        msg = ListCreationProblem([CollectedSheetProblems(problems)]).execute_error_protocol()
        logger.error(msg)
        raise InputError(msg)


def _check_for_erroneous_entries_one_list(sheet: ExcelSheet) -> ListSheetContentProblem | None:
    preferred_lang = get_preferred_language(sheet.df.columns)
    preferred_cols = get_columns_of_preferred_lang(sheet.df.columns, preferred_lang, r"\d+")
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