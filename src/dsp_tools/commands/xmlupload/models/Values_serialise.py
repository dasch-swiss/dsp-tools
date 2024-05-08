from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dsp_tools.models.exceptions import BaseError


@dataclass(frozen=True)
class UploadedFileValue:
    """
    Represents a bitstream object,
    consisting of its file name on the local file system,
    the internal file name assigned by SIPI
    and optionally its permissions.
    """

    local_file: str
    internal_file_name: str
    permissions: str | None = None

    def serialise(self) -> dict[str, Any]:
        local_file = Path(self.local_file)
        file_ending = local_file.suffix[1:]
        match file_ending.lower():
            case "zip" | "tar" | "gz" | "z" | "tgz" | "gzip" | "7z":
                prop = "knora-api:hasArchiveFileValue"
                value_type = "ArchiveFileValue"
            case "mp3" | "wav":
                prop = "knora-api:hasAudioFileValue"
                value_type = "AudioFileValue"
            case "pdf" | "doc" | "docx" | "xls" | "xlsx" | "ppt" | "pptx":
                prop = "knora-api:hasDocumentFileValue"
                value_type = "DocumentFileValue"
            case "mp4":
                prop = "knora-api:hasMovingImageFileValue"
                value_type = "MovingImageFileValue"
            # jpx is the extension of the files returned by dsp-ingest
            case "jpg" | "jpeg" | "jp2" | "png" | "tif" | "tiff" | "jpx":
                prop = "knora-api:hasStillImageFileValue"
                value_type = "StillImageFileValue"
            case "odd" | "rng" | "txt" | "xml" | "xsd" | "xsl" | "xslt" | "csv":
                prop = "knora-api:hasTextFileValue"
                value_type = "TextFileValue"
            case _:
                raise BaseError(f"Unknown file ending '{file_ending}' for file '{local_file}'")
        file_value = {
            "@type": f"knora-api:{value_type}",
            "knora-api:fileValueHasFilename": self.internal_file_name,
        }
        if self.permissions:
            file_value["knora-api:hasPermissions"] = self.permissions
        return {prop: file_value}
