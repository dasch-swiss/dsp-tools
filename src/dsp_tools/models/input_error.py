from dataclasses import dataclass, field
from typing import Protocol


class Problem(Protocol):
    """Information about input errors."""

    def execute_error_protocol(self) -> None:
        """This function prints/saves the problems that occurred."""


@dataclass(frozen=True)
class DockerNotStartedProblem:
    """This class contains information if the docker program is not started."""

    user_msg: str


@dataclass(frozen=True)
class DirectoryProblem:
    """This class contains information if a path does not exist."""

    user_msg: str


@dataclass(frozen=True)
class FileNotFoundProblem:
    """This class contains information if a file is not found at the expected location."""

    user_msg: str


@dataclass(frozen=True)
class ExcelStructureProblem:
    """This class contains information if the structure (column names, etc.) is incorrect."""

    user_msg: str
    column: list[str] | None = None

    def execute_error_protocol(self) -> str:
        msg = self._generate_error_msg()
        return msg

    def _generate_error_msg(self) -> str:
        separator = "\n\t"
        list_separator = "\n\t- "
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

    # TODO: if longer than...

    def execute_error_protocol(self) -> str:
        msg = self._generate_error_msg()
        return msg

    def _generate_error_msg(self) -> str:
        separator = "\n\t"
        list_separator = "\n\t- "
        msg = self.user_msg + separator
        if self.column:
            msg += "Column: " + self.column + separator
        if self.rows:
            rws = [str(x) for x in self.rows]
            msg += "Row(s):" + list_separator + list_separator.join(rws) + separator
        if self.values:
            msg += "Value(s):" + list_separator + list_separator.join(self.values)
        return msg


@dataclass(frozen=True)
class JsonValidationProblem:
    """This class contains information about a JSON that fails its validation against the schema."""

    user_msg: str
    properties: list[str] | None = None
    classes: list[str] | None = None
    invalid_values: list[str] | None = None
