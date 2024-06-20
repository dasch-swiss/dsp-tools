from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from pathlib import Path

import pandas as pd

SUPPORTED_EXTENSIONS = (
    "zip,tar,gz,z,tgz,gzip,7z,mp3,wav,pdf,doc,docx,xls,xlsx,ppt,pptx,"
    "mp4,jpg,jpeg,jp2,png,tif,tiff,odd,rng,txt,xml,xsd,xsl,csv"
).split(",")


def check_files(files: set[Path]) -> FileProblems | None:
    """Validate the files referenced in the XML file. Check if they exist and have supported extensions."""
    unsupported_files = [file for file in files if file.suffix[1:] not in SUPPORTED_EXTENSIONS]
    non_existing_files = [file for file in files if not file.exists() and file not in unsupported_files]
    if non_existing_files or unsupported_files:
        return FileProblems(non_existing_files, unsupported_files)
    return None


@dataclass(frozen=True)
class FileProblems:
    """Handle the error communication to the user in case that some files don't exist or are unsupported."""

    non_existing_files: list[Path]
    unsupported_files: list[Path]
    maximum_prints: int = field(init=False, default=50)

    def __post_init__(self) -> None:
        if not self.non_existing_files and not self.unsupported_files:
            raise ValueError("No files with problems")

    def execute_error_protocol(self) -> str:
        """
        Generate the error message to communicate the problems to the user.
        If there are too many problems, save them to a file.

        Returns:
            error message
        """
        msg = "Some files referenced in the <bitstream> tags of your XML cannot be uploaded to the server."
        if len(self.non_existing_files) + len(self.unsupported_files) > self.maximum_prints:
            output_file = Path("file_problems.csv")
            df = pd.DataFrame(
                {
                    "Files that don't exist on your computer": self.non_existing_files,
                    "Files with unsupported extensions": self.unsupported_files,
                }
            )
            df.to_csv(output_file, index=False)
            msg += f" The full list of files with problems has been saved to '{output_file}'."
        else:
            msg += "\n\n"
            msg += "The following files don't exist on your computer:\n"
            msg += "\n - ".join([str(file) for file in self.non_existing_files])
            msg += "\n\n"
            msg += "The following files have unsupported extensions:\n"
            msg += "\n - ".join([str(file) for file in self.unsupported_files])
        return msg
