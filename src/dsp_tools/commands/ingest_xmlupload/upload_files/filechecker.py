from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd

SUPPORTED_EXTENSIONS = (
    "zip,tar,gz,z,tgz,gzip,7z,mp3,wav,pdf,doc,docx,xls,xlsx,ppt,pptx,"
    "mp4,jpg,jpeg,jp2,png,tif,tiff,odd,rng,txt,xml,xsd,xsl,csv"
).split(",")


@dataclass(frozen=True)
class FileChecker:
    """A validator for files referenced in the XML file"""

    files: Iterable[Path]

    def validate(self) -> FileProblems | None:
        """Check if the files exist and have supported extensions."""
        unsupported_files = [file for file in self.files if file.suffix[1:] not in SUPPORTED_EXTENSIONS]
        non_existing_files = [file for file in self.files if not file.exists() and file not in unsupported_files]
        if non_existing_files or unsupported_files:
            return FileProblems(non_existing_files, unsupported_files)
        return None


@dataclass(frozen=True)
class FileProblems:
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
            msg += "\n\n"
            msg += "The following files don't exist on your computer:\n - "
            msg += "\n - ".join([str(file) for file in self.non_existing_files])
        if self.unsupported_files:
            msg += "\n\n"
            msg += "The following files have unsupported extensions:\n - "
            msg += "\n - ".join([str(file) for file in self.unsupported_files])
        return msg

    def _save_to_csv(self, output_file: Path) -> None:
        non_existing, unsupported = self._add_padding()
        data = {
            "Files that don't exist on your computer": non_existing,
            "Files with unsupported extensions": unsupported,
        }
        df = pd.DataFrame(data)
        df.to_csv(output_file, index=False)

    def _add_padding(self) -> tuple[list[Path | None], list[Path | None]]:
        max_len = max(len(self.non_existing_files), len(self.unsupported_files))
        non_existing = self.non_existing_files + [None] * (max_len - len(self.non_existing_files))
        unsupported = self.unsupported_files + [None] * (max_len - len(self.unsupported_files))
        return non_existing, unsupported
