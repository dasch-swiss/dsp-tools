from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

# pylint: disable=too-few-public-methods


separator = "\n    "
list_separator = "\n    - "


@dataclass(frozen=True)
class IngestInformation:
    """
    This class stores the information about the mapping of uuids provided by the dsp-ingest service
    and the filepaths used in the XML file.
    """

    unused_media_paths: list[str]
    media_no_uuid: list[tuple[str, str] | Any]
    maximum_prints: int = field(default=20)
    csv_filepath: Path = field(default=Path.cwd())
    unused_media_filename: str = "UnusedMediaUploadedInSipi.csv"
    no_uuid_filename: str = "NotUploadedFilesToSipi.csv"

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
                "All multimedia files referenced in the XML file were uploaded through dsp-ingest.\n"
                "No multimedia files were uploaded through dsp-ingest that were not referenced in the XML file."
            )
        return None

    def execute_error_protocol(self) -> str:
        """
        This function generates the user message and saves a file with the information
        if a lot of resources are affected.

        Returns:
            User message
        """
        self._check_csv_if_applicable()
        return self._get_error_msg()

    def _get_error_msg(self) -> str:
        msg_list = [
            "The upload cannot continue as there are problems with the multimedia files referenced in the XML.",
        ]
        if has_msg := self._get_unused_path_msg():
            msg_list.append(has_msg)
        if has_msg := self._get_no_uuid_msg():
            msg_list.append(has_msg)
        return separator.join(msg_list)

    def _get_no_uuid_msg(self) -> str | None:
        if 0 < len(self.media_no_uuid) <= self.maximum_prints:
            return (
                "The data XML file contains references to the following multimedia files "
                "which were not previously uploaded through dsp-ingest:"
                + list_separator
                + list_separator.join([f"Resource ID: '{x[0]}' | Filepath: '{x[1]}'" for x in self.media_no_uuid])
            )
        elif len(self.media_no_uuid) > self.maximum_prints:
            return (
                "The data XML file contains references to multimedia files "
                "which were not previously uploaded through dsp-ingest:\n"
                f"    The file with the resource IDs and filenames was saved at "
                f"'{self.csv_filepath}/{self.no_uuid_filename}'."
            )
        return None

    def _get_unused_path_msg(self) -> str | None:
        if 0 < len(self.unused_media_paths) <= self.maximum_prints:
            return (
                "The data XML file does not reference the following multimedia files which were previously "
                "uploaded through dsp-ingest:" + list_separator + list_separator.join(self.unused_media_paths)
            )
        elif len(self.unused_media_paths) > self.maximum_prints:
            return (
                "The data XML file does not reference all the multimedia files which were previously "
                "uploaded through dsp-ingest.\n"
                f"    The file with the resource IDs and filenames was saved at "
                f"'{self.csv_filepath}/{self.no_uuid_filename}'."
            )
        return None

    def _check_csv_if_applicable(self) -> None:
        if unused_media_df := self._unused_media_to_df():
            _save_as_csv(unused_media_df, self.csv_filepath, self.unused_media_filename)
        if no_uuid_df := self._no_uuid_to_df():
            _save_as_csv(no_uuid_df, self.csv_filepath, self.no_uuid_filename)

    def _unused_media_to_df(self) -> pd.DataFrame | None:
        return (
            pd.DataFrame({"Multimedia Filenames": self.unused_media_paths})
            if len(self.unused_media_paths) > self.maximum_prints
            else None
        )

    def _no_uuid_to_df(self) -> pd.DataFrame | None:
        return (
            pd.DataFrame(
                {"Resource ID": [x[0] for x in self.media_no_uuid], "Filepath": [x[1] for x in self.media_no_uuid]}
            )
            if len(self.media_no_uuid) > self.maximum_prints
            else None
        )


def _save_as_csv(df: pd.DataFrame, filepath: Path, filename: str) -> None:
    df.to_csv(Path(filepath, filename), index=False)
