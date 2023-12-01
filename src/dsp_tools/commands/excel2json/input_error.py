from dataclasses import dataclass
from typing import Protocol

# pylint: disable=too-few-public-methods


separator = "\n    "
list_separator = "\n    - "


class Problem(Protocol):
    """Information about input errors."""

    def execute_error_protocol(self) -> str:
        """
        This function initiates all the steps for successful problem communication with the user.
        """


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
    column: str
    row: int

    def execute_error_protocol(self) -> str:
        """
        This function initiates all the steps for successful problem communication with the user.

        Returns:
            message for the error
        """
        return (
            f"There is invalid content in the column: '{self.column}', row: {self.row}{separator}"
            f"Expected Content: {self.expected_content}{separator}"
            f"Actual Content: {self.actual_content}"
        )


@dataclass(frozen=True)
class MissingExcelSheetProblem:
    """This class contains information if excel sheet(s) are missing"""

    missing_sheets: list[str]

    def execute_error_protocol(self) -> str:
        msg = "The excel does not contain all the required sheets.\n" "The following sheets are missing"
        return msg + list_separator + list_separator.join(self.missing_sheets)


@dataclass(frozen=True)
class MissingExcelResourceMissingColumns:
    """This class contains information if excel sheet(s) are missing"""

    sheet_names: list[str]
    column_names: list[RequiredColumnMissingProblem]

    def execute_error_protocol(self) -> str:
        msg = "There are problems in the excel: 'resources.xlsx'\n"
        for sheet, columns in zip(self.sheet_names, self.column_names):
            msg += separator + f"Sheet: '{sheet}'" + separator + columns.execute_error_protocol()
        return msg


@dataclass(frozen=True)
class InvalidExcelResourceSheetClassProblem:
    """
    If the first sheet in the resource Excel called 'classes' is invalid,
    this class contains the pertinent information for an error.
    """

    duplicate_values: DuplicatesInColumnProblem | None = None
    missing_values: MissingValuesInRowProblem | None = None
    missing_sheets: MissingExcelSheetProblem | None = None

    def execute_error_protocol(self) -> str:
        msg = ["The excel 'resources.xlsx' contains invalid values in the sheet 'classes'."]
        if self.duplicate_values:
            msg.append(self.duplicate_values.execute_error_protocol())
        if self.missing_values:
            msg.append(self.missing_values.execute_error_protocol())
        if self.missing_sheets:
            msg.append(self.missing_sheets.execute_error_protocol())
        return separator.join(msg)


@dataclass(frozen=True)
class JsonValidationPropertyProblem:
    """This class contains information about a JSON property section that fails its validation against the schema."""

    problematic_property: str | None = None
    original_msg: str | None = None
    message_path: str | None = None
    excel_column: str | None = None
    excel_row: int | None = None

    def execute_error_protocol(self) -> str:
        """
        This function initiates all the steps for successful problem communication with the user.

        Returns:
            message for the error
        """
        msg = [
            f"{separator}Section of the problem 'Properties'",
        ]
        if self.problematic_property:
            msg.append(f"Problematic property '{self.problematic_property}'")
        if self.excel_row:
            msg.append(f"The problem is caused by the value in the Excel row {self.excel_row}")
        if self.excel_column:
            msg.append(f"The problem is caused by the value in the Excel column '{self.excel_column}'")
        if self.original_msg:
            msg.append(f"Original Error Message:{separator}{self.original_msg}")
        if self.message_path:
            msg.append(f"The error occurred at {self.message_path}")
        return separator.join(msg)


@dataclass(frozen=True)
class JsonValidationResourceProblem:
    """This class contains information about a JSON resource section that fails its validation against the schema."""

    problematic_resource: str | None = None
    excel_sheet: str | None = None
    excel_column: str | None = None
    excel_row: int | None = None
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
        if self.excel_sheet:
            msg.append(f"The problem is caused by the value in the Excel sheet '{self.excel_sheet}'")
        if self.excel_row:
            msg.append(f"The problem is caused by the value in the Excel row {self.excel_row}")
        if self.excel_column:
            msg.append(f"The problem is caused by the value in the Excel column '{self.excel_column}'")
        if self.original_msg:
            msg.append(f"Original Error Message:{separator}{self.original_msg}")
        if self.message_path:
            msg.append(f"The error occurred at {self.message_path}")
        return separator.join(msg)
