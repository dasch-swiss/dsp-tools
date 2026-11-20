from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from dsp_tools.error.problems import Problem

separator = "\n\n"
list_separator = "\n - "


@dataclass(frozen=True)
class FileProblems(Problem):
    """Handle the error communication to the user in case that some files don't exist or are unsupported."""

    non_existing_files: list[Path]
    unsupported_files: list[Path]
    maximum_prints: int = 50

    def __post_init__(self) -> None:
        if not self.non_existing_files and not self.unsupported_files:
            raise ValueError("It's not possible to create a FileProblems object without any problems.")

    def execute_error_protocol(self) -> str:
        """
        Generate the error message to communicate the problems to the user.
        If there are too many problems, save them to a file.

        Returns:
            error message
        """
        msg = "Some files referenced in the <bitstream> tags of your XML file cannot be uploaded to the server."
        if len(self.non_existing_files) + len(self.unsupported_files) > self.maximum_prints:
            output_file = Path("file_problems.csv")
            self._save_to_csv(output_file)
            msg += f" The full list of files with problems has been saved to '{output_file}'."
            return msg
        if self.non_existing_files:
            msg += separator
            msg += "The following files don't exist on your computer:"
            msg += list_separator + list_separator.join([str(file) for file in self.non_existing_files])
        if self.unsupported_files:
            msg += separator
            msg += "The following files have unsupported extensions:"
            msg += list_separator + list_separator.join([str(file) for file in self.unsupported_files])
        return msg

    def _save_to_csv(self, output_file: Path) -> None:
        problems = ["File doesn't exist"] * len(self.non_existing_files) + ["Extension not supported"] * len(
            self.unsupported_files
        )
        data = {
            "File": self.non_existing_files + self.unsupported_files,
            "Problem": problems,
        }
        df = pd.DataFrame(data)
        df.to_csv(output_file, index=False)
