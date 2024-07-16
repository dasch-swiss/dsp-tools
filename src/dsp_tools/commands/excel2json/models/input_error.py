from __future__ import annotations

from dataclasses import dataclass
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
        return " | ".join(msg)

    def execute_error_protocol(self) -> str:
        """
        This function initiates all the steps for successful problem communication with the user.

        Returns:
            message for the error
        """
        return str(self)


@dataclass(frozen=True)
class ExcelFileProblem:
    """This class contains information about problems with an excel file."""

    filename: str
    problems: list[Problem]

    def execute_error_protocol(self) -> str:
        """
        This function initiates all the steps for successful problem communication with the user.

        Returns:
            message for the error
        """
        msg = f"The Excel file '{self.filename}' contains the following problems:\n\n"
        msg += medium_separator.join([x.execute_error_protocol() for x in self.problems])
        return msg


@dataclass(frozen=True)
class ExcelSheetProblem:
    """This class contains information about problems in one excel sheet."""

    sheet_name: str
    problems: list[Problem]

    def execute_error_protocol(self) -> str:
        """
        This function initiates all the steps for successful problem communication with the user.

        Returns:
            message for the error
        """

        problem_strings = [x.execute_error_protocol() for x in self.problems]
        return (
            f"The sheet: '{self.sheet_name}' has the following problems:\n{list_separator}"
            f"{list_separator.join(problem_strings)}"
        )


@dataclass(frozen=True)
class MissingValuesProblem:
    """This class contains information if a value is missing in a location"""

    locations: list[PositionInExcel]

    def execute_error_protocol(self) -> str:
        """
        This function initiates all the steps for successful problem communication with the user.

        Returns:
            message for the error
        """
        locs = [str(x) for x in self.locations]
        return f"At the following locations, mandatory values are missing:{list_separator}{list_separator.join(locs)}"


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
            f"Located at: {self.excel_position}\n"
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
        msg = "The Excel file 'resources.xlsx' has problems.\n"
        missing_names = self.names_sheets - self.names_classes
        if missing_names:
            msg += (
                f"The following sheet(s) do not have an entry in the 'name' column "
                f"of the sheet 'classes':{list_separator}{list_separator.join(missing_names)}"
            )
        return msg


@dataclass(frozen=True)
class MissingSheetProblem:
    """This class contains information if the Excel is missing mandatory sheets."""

    missing_sheets: list[str]
    existing_sheets: list[str]

    def execute_error_protocol(self) -> str:
        """
        This function initiates all the steps for successful problem communication with the user.

        Returns:
            message for the error
        """
        return (
            f"The following sheet(s) are mandatory, but missing in the Excel:"
            f"{list_separator}{list_separator.join(self.missing_sheets)}\n"
            f"These sheets were found in the Excel:{list_separator}{list_separator.join(self.existing_sheets)}"
        )


@dataclass(frozen=True)
class DuplicateSheetProblem:
    duplicate_sheets: list[str]

    def execute_error_protocol(self) -> str:
        """
        This function initiates all the steps for successful problem communication with the user.

        Returns:
            message for the error
        """
        return (
            f"The sheets names in one Excel must be unique. "
            f"Using capitalisation or spaces to differentiate sheets is not valid.\n"
            f"For example 'sheet1' and 'SHEET1  ' are considered identical.\n"
            f"The following sheets appear several times under this condition:"
            f"{list_separator}{list_separator.join(sorted(self.duplicate_sheets))}"
        )


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
            msg.append(f"Located at: {self.excel_position}")
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
            msg.append(f"Located at: {self.excel_position}")
        if self.original_msg:
            msg.append(f"Original Error Message:{separator}{self.original_msg}")
        if self.message_path:
            msg.append(f"The error occurred at {self.message_path}")
        return separator.join(msg)
