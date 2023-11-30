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
class ExcelStructureProblem:
    """This class contains information if the structure (column names, etc.) is incorrect."""

    user_msg: str
    column: list[str] | None = None

    def execute_error_protocol(self) -> str:
        """
        This function initiates all the steps for successful problem communication with the user.

        Returns:
            message for the error
        """
        msg = self.user_msg + separator
        if self.column:
            msg += "Column(s):" + list_separator.join(self.column)
        return msg


@dataclass(frozen=True)
class ExcelContentProblem:
    """This class contains information if the content of an Excel is not as expected."""

    user_msg: str
    column: str | None = None
    rows: list[int] | None = None
    values: list[str] | None = None

    def execute_error_protocol(self) -> str:
        """
        This function initiates all the steps for successful problem communication with the user.

        Returns:
            message for the error
        """
        msg = [self.user_msg]
        if self.column:
            msg.append("Column: " + self.column)
        if self.rows:
            rws = [str(x) for x in self.rows]
            msg.append("Row(s):" + list_separator + list_separator.join(rws))
        if self.values:
            msg.append("Value(s):" + list_separator + list_separator.join(self.values))
        return separator.join(msg)


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
