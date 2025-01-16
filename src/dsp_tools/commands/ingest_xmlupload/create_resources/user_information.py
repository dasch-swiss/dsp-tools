from dataclasses import dataclass
from dataclasses import field
from pathlib import Path

import pandas as pd

separator = "\n    "
list_separator = "\n    - "


@dataclass(frozen=True)
class IngestInformation:
    """
    This class stores the information about the mapping of ids provided by the dsp-ingest service
    and the filepaths used in the XML file.
    """

    unused_mediafiles: list[str]
    mediafiles_no_id: list[tuple[str, str]]
    maximum_prints: int = 20
    csv_directory_path: Path = field(default=Path.cwd())
    unused_mediafiles_csv: str = "UnusedMediaUploaded.csv"
    mediafiles_no_id_csv: str = "FilesNotUploaded.csv"

    def ok_msg(self) -> str | None:
        """
        This function checks if no media was unused or not uploaded.
        If that is the case it returns the message,
        if not, it ends without an effect.

        Returns:
            Message if all went well.
        """
        if not self.unused_mediafiles and not self.mediafiles_no_id:
            return (
                "All multimedia files referenced in the XML file were uploaded through dsp-ingest.\n"
                "All multimedia files uploaded through dsp-ingest were referenced in the XML file."
            )
        return None

    def execute_error_protocol(self) -> str:
        """
        This function generates the user message and saves a file with the information
        if a lot of resources are affected.

        Returns:
            User message
        """
        self._save_csv_if_applicable()
        return self._get_error_msg()

    def _get_error_msg(self) -> str:
        msg_list = [
            "The upload cannot continue as there are problems with the multimedia files referenced in the XML.",
        ]
        if has_msg := self._get_unused_mediafiles_msg():
            msg_list.append(has_msg)
        if has_msg := self._get_mediafiles_no_id_msg():
            msg_list.append(has_msg)
        return separator.join(msg_list)

    def _get_mediafiles_no_id_msg(self) -> str | None:
        if 0 < len(self.mediafiles_no_id) <= self.maximum_prints:
            return (
                "The data XML file contains references to the following multimedia files "
                "which were not previously uploaded through dsp-ingest:"
                + list_separator
                + list_separator.join([f"Resource ID: '{x[0]}' | Filepath: '{x[1]}'" for x in self.mediafiles_no_id])
            )
        elif len(self.mediafiles_no_id) > self.maximum_prints:
            return (
                "The data XML file contains references to multimedia files "
                "which were not previously uploaded through dsp-ingest:\n"
                f"    The file with the resource IDs and problematic filenames was saved at "
                f"'{Path(self.csv_directory_path / self.mediafiles_no_id_csv)}'."
            )
        return None

    def _get_unused_mediafiles_msg(self) -> str | None:
        if 0 < len(self.unused_mediafiles) <= self.maximum_prints:
            return (
                "The data XML file does not reference the following multimedia files which were previously "
                "uploaded through dsp-ingest:" + list_separator + list_separator.join(self.unused_mediafiles)
            )
        elif len(self.unused_mediafiles) > self.maximum_prints:
            return (
                "The data XML file does not reference all the multimedia files which were previously "
                "uploaded through dsp-ingest.\n"
                f"    The file with the unused filenames was saved at "
                f"'{Path(self.csv_directory_path / self.unused_mediafiles_csv)}'."
            )
        return None

    def _save_csv_if_applicable(self) -> None:
        if (unused_mediafiles_df := self._unused_mediafiles_to_df()) is not None:
            _save_as_csv(unused_mediafiles_df, self.csv_directory_path, self.unused_mediafiles_csv)
        if (no_id_df := self._mediafiles_no_id_to_df()) is not None:
            _save_as_csv(no_id_df, self.csv_directory_path, self.mediafiles_no_id_csv)

    def _unused_mediafiles_to_df(self) -> pd.DataFrame | None:
        return (
            pd.DataFrame({"Multimedia Filenames": self.unused_mediafiles})
            if len(self.unused_mediafiles) > self.maximum_prints
            else None
        )

    def _mediafiles_no_id_to_df(self) -> pd.DataFrame | None:
        return (
            pd.DataFrame(
                {
                    "Resource ID": [x[0] for x in self.mediafiles_no_id],
                    "Filepath": [x[1] for x in self.mediafiles_no_id],
                }
            )
            if len(self.mediafiles_no_id) > self.maximum_prints
            else None
        )


def _save_as_csv(df: pd.DataFrame, directory_path: Path, filename: str) -> None:
    df.to_csv(Path(directory_path, filename), index=False)
