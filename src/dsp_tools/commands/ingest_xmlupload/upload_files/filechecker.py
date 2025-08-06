from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from dsp_tools.commands.ingest_xmlupload.upload_files.input_error import FileProblems

SUPPORTED_EXTENSIONS = (
    "zip,tar,gz,z,tgz,gzip,7z,mp3,wav,pdf,doc,docx,xls,xlsx,ppt,pptx,epub,"
    "mp4,jpg,jpeg,jp2,json,png,tif,tiff,odd,rng,txt,xml,htm,html,xsd,xsl,csv"
).split(",")


def check_files(files: Iterable[Path]) -> FileProblems | None:
    """Check if the files exist and have supported extensions."""
    unsupported_files = [file for file in files if file.suffix[1:].casefold() not in SUPPORTED_EXTENSIONS]
    non_existing_files = [file for file in files if not file.exists() and file not in unsupported_files]
    if non_existing_files or unsupported_files:
        return FileProblems(non_existing_files, unsupported_files)
    return None
