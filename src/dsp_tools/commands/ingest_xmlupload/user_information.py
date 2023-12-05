from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

import pandas as pd

# pylint: disable=too-few-public-methods


separator = "\n    "
list_separator = "\n    - "


class UserInformation(Protocol):
    """
    Information about user messages.
    """

    def __str__(self) -> str:
        """
        This function initiates all the steps for successful problem communication with the user.
        """

    def make(self) -> str:
        """
        This function saves the information as a csv file.
        """


@dataclass(frozen=True)
class IngestInformation:
    """
    This class stores the information about the mapping of uuids provided by the dsp-ingest service
    and the filepaths used in the XML file.
    """

    unused_media_paths: list[str]
    media_no_uuid: list[tuple[str, str] | Any]

    def make(self) -> str:
        """
        This function generates the user message and saves a file with the information
        if a lot of resources affected.

        Returns:
            User message
        """
        save_path = Path.home()
        msg = []
        if unused_media_df := self._unused_media_to_df():
            _save_as_csv(unused_media_df, "UnusedMediaUploadedInSipi.csv", save_path)
            msg.append(
                "Media was uploaded to Sipi which was not referenced in the XML file.\n"
                f"The file 'UnusedMediaUploadedInSipi.csv' was saved in '{save_path}' with the filenames."
            )
        if no_uuid_df := self._no_uuid_to_df():
            _save_as_csv(no_uuid_df, "NotUploadedFilesToSipi.csv", save_path)
            msg.append(
                "Media referenced in the file was not previously uploaded to sipi.\n"
                f"The file 'NotUploadedFilesToSipi.csv' was saved in '{save_path}' with the resource IDs and filenames."
            )
        msg.append(str(self))
        return separator.join(msg)

    def __str__(self) -> str:
        msg_list = []
        if not self.unused_media_paths and not self.media_no_uuid:
            return (
                "All media referenced in the XML file were uploaded to sipi.\n"
                "No media was uploaded to sipi that was not referenced in the XML file."
            )
        if self.unused_media_paths:
            msg_list.append(
                "The following media were uploaded to sipi but not used in the data XML file:"
                + list_separator
                + list_separator.join(self.unused_media_paths)
            )
        if self.media_no_uuid:
            msg_list.append(
                "The following media were not uploaded to sipi but referenced in the data XML file:"
                + list_separator
                + list_separator.join([f"Resource ID: '{x[0]}' | Filepath: '{x[1]}'" for x in self.media_no_uuid])
            )
        return separator.join(msg_list)

    def _unused_media_to_df(self) -> pd.DataFrame | None:
        unused_media = None
        if len(self.unused_media_paths) > 10:
            unused_media = pd.DataFrame({"Media Filenames": self.unused_media_paths})
        return unused_media

    def _no_uuid_to_df(self) -> pd.DataFrame | None:
        no_uuid = None
        if len(self.media_no_uuid) > 10:
            no_uuid = pd.DataFrame(
                {"Resource ID": [x[0] for x in self.media_no_uuid], "Filepath": [x[1] for x in self.media_no_uuid]}
            )
        return no_uuid


def _save_as_csv(df: pd.DataFrame, filename: str, filepath: Path) -> None:
    df.to_csv(Path(filepath, filename), index=False)
