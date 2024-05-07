from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Protocol

separator = "\n    "
list_separator = "\n    - "
medium_separator = "\n----------------------------\n"

grand_separator = "\n\n---------------------------------------\n\n"


class Problem(Protocol):
    """Information about input errors."""

    def execute_error_protocol(self) -> str:
        """
        This function initiates all the steps for successful problem communication with the user.
        """


@dataclass(frozen=True)
class PositionInExcel:
    """This class contains the information about the position of a value in the excel."""

    sheet: str | None = None
    column: str | None = None
    row: int | None = None
    excel_filename: str | None = None

    def __str__(self) -> str:
        msg = []
        if self.excel_filename:
            msg.append(f"Excel '{self.excel_filename}'")
        if self.sheet:
            msg.append(f"Sheet '{self.sheet}'")
        if self.column:
            msg.append(f"Column '{self.column}'")
        if self.row:
            msg.append(f"Row {self.row}")
        return "Located at: " + " | ".join(msg)


@dataclass(frozen=True)
class RequiredColumnMissingProblem:
    """This class contains information if a required column is missing."""

    columns: list[str]

    def execute_error_protocol(self) -> str:
        """
        This function initiates all the steps for successful problem communication with the user.

        Returns:
            message for the error
        """
        return f"The following required column(s) are missing:{list_separator}{list_separator.join(self.columns)}"


@dataclass(frozen=True)
class DuplicatesInColumnProblem:
    """This class contains information if a required column is missing."""

    column: str
    duplicate_values: list[str]

    def execute_error_protocol(self) -> str:
        """
        This function initiates all the steps for successful problem communication with the user.

        Returns:
            message for the error
        """
        return (
            f"No duplicates are allowed in the column '{self.column}'\n"
            f"The following values appear several times:{list_separator}"
            f"{list_separator.join(self.duplicate_values)}"
        )


@dataclass(frozen=True)
class MissingValuesInRowProblem:
    """This class contains information if a required column is missing."""

    column: str
    row_numbers: list[int]

    def execute_error_protocol(self) -> str:
        """
        This function initiates all the steps for successful problem communication with the user.

        Returns:
            message for the error
        """
        nums = [str(x) for x in self.row_numbers]
        return f"The column '{self.column}' must have values in the row(s):{list_separator}{list_separator.join(nums)}"


@dataclass(frozen=True)
class InvalidExcelContentProblem:
    """This class contains information if a required column is missing."""

    expected_content: str
    actual_content: str
    excel_position: PositionInExcel

    def execute_error_protocol(self) -> str:
        """
        This function initiates all the steps for successful problem communication with the user.

        Returns:
            message for the error
        """
        return (
            f"There is invalid content in the excel.\n"
            f"{self.excel_position!s}\n"
            f"Expected Content: {self.expected_content}\n"
            f"Actual Content: {self.actual_content}"
        )


@dataclass(frozen=True)
class InvalidSheetNameProblem:
    """This class contains information if the excel sheet names are not strings."""

    excelfile: str
    excel_sheet_names: list[Any]

    def execute_error_protocol(self) -> str:
        """
        This function initiates all the steps for successful problem communication with the user.

        Returns:
            message for the error
        """
        sheet_types = [f"Name: {x} | Type {type(x)}" for x in self.excel_sheet_names if not isinstance(x, str)]
        return (
            f"The names sheets in the excel '{self.excelfile}' are not all valid.\n"
            f"They must be of type string. The following names are problematic:\n"
            f"{list_separator}{list_separator.join(sheet_types)}\n"
            f"Please rename them."
        )


@dataclass(frozen=True)
class ResourcesSheetsNotAsExpected:
    """This class contains information if the excel sheet names are not a subset of the expected ones."""

    names_classes: set[str]
    names_sheets: set[str]

    def execute_error_protocol(self) -> str:
        """
        This function initiates all the steps for successful problem communication with the user.

        Returns:
            message for the error
        """
        msg = (
            "The excel file 'resources.xlsx' has problems.\n"
            "The names of the excel sheets must be 'classes' "
            "plus all the entries in the column 'name' from the sheet 'classes'.\n"
        )
        missing_sheets = self.names_classes - self.names_sheets
        if missing_sheets:
            msg += f"The following sheet(s) are missing:{list_separator}" + list_separator.join(missing_sheets)
        missing_names = self.names_sheets - self.names_classes
        if missing_names:
            msg += (
                f"The following sheet(s) do not have an entry in the 'name' column "
                f"of the sheet 'classes':{list_separator}"
            ) + list_separator.join(missing_names)
        return msg


@dataclass(frozen=True)
class MoreThanOneSheetProblem:
    """This class contains information if the excel containing the property values has more than one sheet."""

    excelname: str
    sheet_names: list[str]

    def execute_error_protocol(self) -> str:
        msg = [
            f"\nIn the '{self.excelname}' file only one sheet is allowed.",
            f"The excel used contains the following sheets:{list_separator}{list_separator.join(self.sheet_names)}",
            "Please delete all but one sheet.",
        ]
        return separator.join(msg)


@dataclass(frozen=True)
class JsonValidationPropertyProblem:
    """This class contains information about a JSON property section that fails its validation against the schema."""

    problematic_property: str | None = None
    original_msg: str | None = None
    message_path: str | None = None
    excel_position: PositionInExcel | None = None

    def execute_error_protocol(self) -> str:
        """
        This function initiates all the steps for successful problem communication with the user.

        Returns:
            message for the error
        """
        msg = [
            f"{separator}Section of the problem: 'Properties'",
        ]
        if self.problematic_property:
            msg.append(f"Problematic property: '{self.problematic_property}'")
        if self.excel_position:
            msg.append(str(self.excel_position))
        if self.original_msg:
            msg.append(f"Original Error Message:\n{self.original_msg}")
        if self.message_path:
            msg.append(f"The error occurred at {self.message_path}")
        return separator.join(msg)


@dataclass(frozen=True)
class JsonValidationResourceProblem:
    """This class contains information about a JSON resource section that fails its validation against the schema."""

    problematic_resource: str | None = None
    excel_position: PositionInExcel | None = None
    original_msg: str | None = None
    message_path: str | None = None

    def execute_error_protocol(self) -> str:
        """
        This function initiates all the steps for successful problem communication with the user.

        Returns:
            message for the error
        """
        msg = [
            f"{separator}Section of the problem: 'Resources'",
        ]
        if self.problematic_resource:
            msg.append(f"Problematic Resource '{self.problematic_resource}'")
        if self.excel_position:
            msg.append(str(self.excel_position))
        if self.original_msg:
            msg.append(f"Original Error Message:{separator}{self.original_msg}")
        if self.message_path:
            msg.append(f"The error occurred at {self.message_path}")
        return separator.join(msg)


@dataclass(frozen=True)
class ListCreationProblem:
    excel_problems: list[Problem]

    def execute_error_protocol(self) -> str:
        msg = ["\nThe excel file(s) used to create the list section have the following problem(s):"]
        msg.extend([problem.execute_error_protocol() for problem in self.excel_problems])
        return grand_separator.join(msg)


@dataclass(frozen=True)
class ListExcelProblem:
    excel_name: str
    problems: list[Problem]

    def execute_error_protocol(self) -> str:
        msg = [f"The excel '{self.excel_name}' has the following problem(s):"]
        msg.extend([problem.execute_error_protocol() for problem in self.problems])
        return medium_separator.join(msg)


@dataclass(frozen=True)
class ListNodeProblem:
    node_id: str
    problems: dict[str, str]

    def execute_error_protocol(self) -> str:
        msg = [f"The node '{self.node_id}' has the following problem(s):"]
        msg.extend([f"Field: '{key}', Problem: {value}" for key, value in self.problems.items()])
        return list_separator.join(msg)


@dataclass
class ListSheetProblem:
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


@dataclass(frozen=True)
class ListSheetComplianceProblem:
    sheet_name: str
    problems: dict[str, str]

    def execute_error_protocol(self) -> str:
        msg = [f"The excel sheet '{self.sheet_name}' has the following problem(s):"]
        msg.extend([f"{key}: {value}" for key, value in self.problems.items()])
        return list_separator.join(msg)


@dataclass(frozen=True)
class ListSheetContentProblem:
    sheet_name: str
    problems: list[Problem]

    def execute_error_protocol(self) -> str:
        msg = [f"The Excel sheet '{self.sheet_name}' has the following problem(s):"]
        msg.extend([problem.execute_error_protocol() for problem in self.problems])
        return list_separator.join(msg)


@dataclass(frozen=True)
class DuplicatesInSheetProblem:
    sheet_name: str
    rows: list[int]

    def execute_error_protocol(self) -> str:
        msg = [
            f"The excel sheet '{self.sheet_name}' contains rows that are completely identical "
            f"(excluding the column 'ID (optional)'). The following rows are duplicates:"
        ]
        msg.extend([f"{x + 2}" for x in self.rows])
        return list_separator.join(msg)


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
    excel_file: str
    excel_sheet: str
    list_name: str

    def execute_error_protocol(self) -> str:
        return f"Excel file: '{self.excel_file}', Sheet: '{self.excel_sheet}', List: '{self.list_name}'"


@dataclass(frozen=True)
class MultipleListPerSheetProblem:
    sheet_name: str
    list_names: list[str]

    def execute_error_protocol(self) -> str:
        return (
            f"Per Excel sheet only one list is allowed.\n"
            f"The following sheet: '{self.sheet_name}' has more than one list: {', '.join(self.list_names)}"
        )


@dataclass(frozen=True)
class DuplicatesCustomIDInProblem:
    duplicate_ids: list[DuplicateIDProblem]

    def execute_error_protocol(self) -> str:
        msg = ["No duplicates are allowed in the 'ID (optional)' column. The following IDs are duplicated:"]
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
class MissingTranslationsSheetProblem:
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
