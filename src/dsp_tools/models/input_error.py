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

        Returns:
            message for the error
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
class JsonValidationProblem:
    """This class contains information about a JSON that fails its validation against the schema."""

    user_msg: str
    json_section: str
    problematic_value: str | None = None
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
            self.user_msg,
            f"Section of the problem: '{self.json_section}'",
        ]
        if self.problematic_value:
            msg.append(f"Problematic value: '{self.problematic_value}'")
        if self.excel_row:
            msg.append(f"The problem is caused by the value in the Excel row {self.excel_row}")
        if self.excel_column:
            msg.append(f"The problem is caused by the value in the Excel column '{self.excel_column}'")
        if self.original_msg:
            msg.append(f"Original Error Message:\n{self.original_msg}")
        if self.message_path:
            msg.append(f"The error occurred at {self.message_path}")
        return separator.join(msg)
