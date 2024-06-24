from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from dsp_tools.commands.ingest_xmlupload.upload_files.input_error import FileProblems

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
