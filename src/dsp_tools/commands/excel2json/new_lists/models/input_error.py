from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from dataclasses import field
from typing import Protocol

from dsp_tools.commands.excel2json.models.input_error import ExcelFileProblem
from dsp_tools.commands.excel2json.models.input_error import PositionInExcel
from dsp_tools.commands.excel2json.models.input_error import Problem
from dsp_tools.commands.excel2json.models.input_error import grand_separator
from dsp_tools.commands.excel2json.models.input_error import list_separator
from dsp_tools.commands.excel2json.models.input_error import medium_separator


@dataclass(frozen=True)
class ListCreationProblem:
    excel_problems: list[Problem]

    def execute_error_protocol(self) -> str:
        title = "\nThe excel file(s) used to create the list section have the following problem(s):\n\n"
        msg = [problem.execute_error_protocol() for problem in self.excel_problems]
        return title + grand_separator.join(msg)


@dataclass(frozen=True)
class ListNodeProblem:
    node_id: str
    problems: dict[str, str]

    def execute_error_protocol(self) -> str:
        msg = [f"The node '{self.node_id}' has the following problem(s):"]
        msg.extend([f"Field: '{key}', Problem: {value}" for key, value in self.problems.items()])
        return list_separator.join(msg)


@dataclass
class SheetProblem(Protocol):
    excel_name: str

    def execute_error_protocol(self) -> str:
        raise NotImplementedError


@dataclass
class CollectedSheetProblems:
    sheet_problems: list[SheetProblem]

    def execute_error_protocol(self) -> str:
        file_problems = self._group_and_sort_by_excel_name()
        return grand_separator.join([x.execute_error_protocol() for x in file_problems])

    def _group_and_sort_by_excel_name(self) -> list[ExcelFileProblem]:
        file_dict: dict[str, list[Problem]] = defaultdict(list)
        for problem in self.sheet_problems:
            file_dict[problem.excel_name].append(problem)
        file_list = [ExcelFileProblem(k, v) for k, v in file_dict.items()]
        return sorted(file_list, key=lambda x: x.filename)


@dataclass
class DuplicatesInSheetProblem(SheetProblem):
    excel_name: str
    sheet_name: str
    rows: list[int]

    def execute_error_protocol(self) -> str:
        msg = [
            f"The excel sheet '{self.sheet_name}' contains rows that are completely identical "
            f"(excluding the column 'ID (optional)'). The following rows are duplicates:"
        ]
        msg.extend([f"{x + 2}" for x in self.rows])
        return list_separator.join(msg)


@dataclass
class MultipleListPerSheetProblem(SheetProblem):
    excel_name: str
    sheet_name: str
    list_names: list[str]

    def execute_error_protocol(self) -> str:
        return (
            f"Per Excel sheet only one list is allowed.\n"
            f"The sheet '{self.sheet_name}' has more than one list, namely the following: {', '.join(self.list_names)}"
        )


@dataclass
class ListSheetComplianceProblem(SheetProblem):
    excel_name: str
    sheet_name: str
    problems: list[Problem]

    def execute_error_protocol(self) -> str:
        msg = [f"The excel sheet '{self.sheet_name}' has the following problem(s):"]
        msg.extend([x.execute_error_protocol() for x in self.problems])
        return list_separator.join(msg)


@dataclass
class ListSheetContentProblem(SheetProblem):
    excel_name: str
    sheet_name: str
    problems: list[Problem]

    def execute_error_protocol(self) -> str:
        msg = [f"The Excel sheet '{self.sheet_name}' has the following problem(s):"]
        msg.extend([problem.execute_error_protocol() for problem in self.problems])
        return list_separator.join(msg)


@dataclass
class MissingTranslationsSheetProblem(SheetProblem):
    excel_name: str
    sheet: str
    node_problems: list[MissingNodeTranslationProblem]

    def execute_error_protocol(self) -> str:
        msg = [
            f"The excel sheet '{self.sheet}' has the following problem(s):\n"
            "In one list, all the nodes must be translated into all the languages used. "
            "For the following nodes, the translations are missing:"
        ]
        nodes_sorted = sorted(self.node_problems, key=lambda x: x.index_num)
        msg.extend([x.execute_error_protocol() for x in nodes_sorted])
        return list_separator.join(msg)


@dataclass(frozen=True)
class DuplicatesListNameProblem:
    all_duplicate_names: list[ListInformation]

    def execute_error_protocol(self) -> str:
        msg = [
            "The name of the list must be unique across all the excel sheets.\n"
            "The following sheets have lists with the same name:"
        ]
        sorted_list = sorted(self.all_duplicate_names, key=lambda x: x.excel_name)
        msg.extend([x.execute_error_protocol() for x in sorted_list])
        return list_separator.join(msg)


@dataclass(frozen=True)
class ListInformation:
    excel_name: str
    excel_sheet: str
    list_name: str

    def execute_error_protocol(self) -> str:
        return f"Excel file: '{self.excel_name}', Sheet: '{self.excel_sheet}', List: '{self.list_name}'"


@dataclass(frozen=True)
class DuplicatesCustomIDInProblem:
    duplicate_ids: list[DuplicateIDProblem]

    def execute_error_protocol(self) -> str:
        msg = [
            "No duplicates are allowed in the 'ID (optional)' column. At the following locations, IDs are duplicated:"
        ]
        sorted_ids = sorted(self.duplicate_ids, key=lambda x: x.custom_id)
        msg.extend([x.execute_error_protocol() for x in sorted_ids])
        return medium_separator.join(msg)


@dataclass
class DuplicateIDProblem:
    custom_id: str | int | float = field(default="")
    excel_locations: list[PositionInExcel] = field(default_factory=list)

    def execute_error_protocol(self) -> str:
        msg = [f"ID: '{self.custom_id}'"]
        msg.extend([str(x) for x in sorted(self.excel_locations, key=lambda x: str(x.excel_filename))])
        return list_separator.join(msg)


@dataclass(frozen=True)
class MissingNodeTranslationProblem:
    empty_columns: list[str]
    index_num: int

    def execute_error_protocol(self) -> str:
        return f"Row Number: {self.index_num + 2} | Column(s): {', '.join(sorted(self.empty_columns))}"


@dataclass(frozen=True)
class NodesPerRowProblem:
    column_names: list[str]
    index_num: int
    should_be_empty: bool

    def execute_error_protocol(self) -> str:
        if self.should_be_empty:
            description = "Column(s) that must be empty"
        else:
            description = "Column(s) that must be filled"
        return f"Row Number: {self.index_num + 2}, {description}: {', '.join(self.column_names)}"


@dataclass(frozen=True)
class MinimumRowsProblem:
    def execute_error_protocol(self) -> str:
        return (
            "The Excel sheet must contain at least two rows, "
            "one for the list name and one row for a minimum of one node."
        )


@dataclass(frozen=True)
class MissingNodeColumn:
    def execute_error_protocol(self) -> str:
        return (
            "At least one column for the node names in the format '[lang]_[column_number]' is required. "
            "The allowed language tags are: en, de, fr, it, rm."
        )


@dataclass
class MissingExpectedColumn:
    missing_cols: set[str]

    def execute_error_protocol(self) -> str:
        return (
            f"All nodes and lists must be translated into the same languages. "
            f"Based on the languages used, the following column(s) are missing: {', '.join(self.missing_cols)}"
        )
