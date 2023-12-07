from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

import pandas as pd

# pylint: disable=too-few-public-methods


separator = "\n    "
list_separator = "\n    - "

maximum_prints = 20


class UserInformation(Protocol):
    """
    Information about user messages.
    """

    def all_good_msg(self) -> str:
        """
        If everything went as it should this function returns a success message for the user.
        Returns:

        """

    def execute_error_protocol(self) -> str:
        """
        This function initiates all the steps to communicate the problems to the user.
        """


@dataclass(frozen=True)
class IngestInformation:
    """
    This class stores the information about the mapping of uuids provided by the dsp-ingest service
    and the filepaths used in the XML file.
    """

    unused_media_paths: list[str]
    media_no_uuid: list[tuple[str, str] | Any]

    def all_good_msg(self) -> str | None:
        """
        This function checks if no media was unused or not uploaded.
        If that is the case it returns the message,
        if not, it ends without an effect.

        Returns:
            Message if all went well.
        """
        if not self.unused_media_paths and not self.media_no_uuid:
            return (
                "All media referenced in the XML file were uploaded to sipi.\n"
                "No media was uploaded to sipi that was not referenced in the XML file."
            )
        return None

    def execute_error_protocol(self, save_path: Path) -> str:
        """
        This function generates the user message and saves a file with the information
        if a lot of resources affected.

        Args:
            save_path: Path where the file should be saved.

        Returns:
            User message
        """
        unused_media_filename = "UnusedMediaUploadedInSipi.csv"
        no_uuid_filename = "NotUploadedFilesToSipi.csv"
        self._check_save_csv(save_path, no_uuid_filename, unused_media_filename)
        return self._get_error_msg(save_path, unused_media_filename, no_uuid_filename)

    def _get_error_msg(self, save_path: Path, unused_media_filename: str, no_uuid_filename: str) -> str:
        msg_list = ["The upload cannot continue as there are problems with the media referenced in the XML."]
        if 0 < len(self.unused_media_paths) <= maximum_prints:
            msg_list.append(
                "The following media were uploaded to sipi but not referenced in the data XML file:"
                + list_separator
                + list_separator.join(self.unused_media_paths)
            )
        elif len(self.unused_media_paths) > maximum_prints:
            msg_list.append(
                "Media was uploaded to Sipi which was not referenced in the XML file.\n"
                f"    The file '{unused_media_filename}' was saved in '{save_path}' with the filenames.\n"
            )
        if 0 < len(self.media_no_uuid) <= maximum_prints:
            msg_list.append(
                "The following media were not uploaded to sipi but referenced in the data XML file:"
                + list_separator
                + list_separator.join([f"Resource ID: '{x[0]}' | Filepath: '{x[1]}'" for x in self.media_no_uuid])
            )
        elif len(self.media_no_uuid) > maximum_prints:
            msg_list.append(
                "Media was referenced in the XML file but not previously uploaded to sipi:\n"
                f"    The file '{no_uuid_filename}' was saved in '{save_path}' with the resource IDs and filenames."
            )
        return separator.join(msg_list)

    def _check_save_csv(self, save_path: Path, no_uuid_filename: str, unused_media_filename: str) -> None:
        if unused_media_df := self._unused_media_to_df():
            _save_as_csv(unused_media_df, unused_media_filename, save_path)
        if no_uuid_df := self._no_uuid_to_df():
            _save_as_csv(no_uuid_df, no_uuid_filename, save_path)

    def _unused_media_to_df(self) -> pd.DataFrame | None:
        return (
            pd.DataFrame({"Media Filenames": self.unused_media_paths})
            if len(self.unused_media_paths) > maximum_prints
            else None
        )

    def _no_uuid_to_df(self) -> pd.DataFrame | None:
        return (
            pd.DataFrame(
                {"Resource ID": [x[0] for x in self.media_no_uuid], "Filepath": [x[1] for x in self.media_no_uuid]}
            )
            if len(self.media_no_uuid) > maximum_prints
            else None
        )


def _save_as_csv(df: pd.DataFrame, filename: str, filepath: Path) -> None:
    df.to_csv(Path(filepath, filename), index=False)
