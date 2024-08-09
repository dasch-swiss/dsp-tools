from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Protocol

from dsp_tools.commands.excel2json.models.input_error import PositionInExcel
from dsp_tools.commands.excel2json.models.input_error import Problem
from dsp_tools.commands.excel2json.models.input_error import grand_separator
from dsp_tools.commands.excel2json.models.input_error import list_separator
from dsp_tools.commands.excel2json.models.input_error import medium_separator


@dataclass(frozen=True)
class ListCreationProblem:
    excel_problems: list[Problem]

    def execute_error_protocol(self) -> str:
        msg = ["\nThe excel file(s) used to create the list section have the following problem(s):"]
        msg.extend([problem.execute_error_protocol() for problem in self.excel_problems])
        return grand_separator.join(msg)


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
    problems: list[SheetProblem]

    def execute_error_protocol(self) -> str:
        raise NotImplementedError

    def _sort_by_excel(self) -> dict[str, SheetProblem]:
        raise NotImplementedError


@dataclass
class ListSheetProblem(SheetProblem):
    excel_name: str
    sheet_name: str
    root_problems: dict[str, str]
    node_problems: list[ListNodeProblem] = field(default_factory=list)

    def execute_error_protocol(self) -> str:
        msg = [f"The excel sheet '{self.sheet_name}' has the following problem(s):"]
        if self.root_problems:
            msg.extend([f"Field: '{key}', Problem: {value}" for key, value in self.root_problems.items()])
        if self.node_problems:
            msg.extend([problem.execute_error_protocol() for problem in self.node_problems])
        return list_separator.join(msg)


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
            f"The following sheet: '{self.sheet_name}' has more than one list: {', '.join(self.list_names)}"
        )


@dataclass
class ListSheetComplianceProblem(SheetProblem):
    excel_name: str
    sheet_name: str
    problems: dict[str, str]

    def execute_error_protocol(self) -> str:
        msg = [f"The excel sheet '{self.sheet_name}' has the following problem(s):"]
        msg.extend([f"{key}: {value}" for key, value in self.problems.items()])
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
            "The following nodes are missing translations:"
        ]
        nodes_sorted = sorted(self.node_problems, key=lambda x: x.index_num)
        msg.extend([x.execute_error_protocol() for x in nodes_sorted])
        return list_separator.join(msg)


@dataclass(frozen=True)
class MissingNodeSheetProblem:
    sheet: str
    node_problems: list[NodesPerRowProblem]

    def execute_error_protocol(self) -> str:
        msg = "Each list node and each list must have its own row in the excel. " "The following rows are incorrect:"
        nodes_sorted = sorted(self.node_problems, key=lambda x: x.index_num)
        nodes = list_separator.join([x.execute_error_protocol() for x in nodes_sorted])
        return msg + nodes


@dataclass(frozen=True)
class DuplicatesListNameProblem:
    all_duplicate_names: list[ListInformation]

    def execute_error_protocol(self) -> str:
        msg = [
            "The name of the list must be unique across all the excel sheets.\n"
            "The following sheets have lists with the same name:"
        ]
        sorted_list = sorted(self.all_duplicate_names, key=lambda x: x.list_name)
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
    custom_id: str = field(default="")
    excel_locations: list[PositionInExcel] = field(default_factory=list)

    def execute_error_protocol(self) -> str:
        msg = [f"ID: '{self.custom_id}'"]
        msg.extend([str(x) for x in self.excel_locations])
        return list_separator.join(msg)


@dataclass(frozen=True)
class MissingNodeTranslationProblem:
    empty_columns: list[str]
    index_num: int

    def execute_error_protocol(self) -> str:
        return f"Row Number: {self.index_num + 2} Column(s): {', '.join(self.empty_columns)}"


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
