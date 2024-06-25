from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import regex
from loguru import logger

separator = "\n\n"
list_separator = "\n - "


@dataclass(frozen=True)
class UploadFailure:
    """Information on why the upload of a file to the ingest server failed."""

    filepath: Path
    reason: str


@dataclass(frozen=True)
class UploadFailures:
    """Aggregated information of all failed uploads."""

    outcomes: list[UploadFailure | None]
    shortcode: str
    dsp_ingest_url: str
    maximum_prints: int = 50

    def execute_error_protocol(self) -> str:
        """
        Generate the error message to communicate the problems to the user.
        If there are too many problems, save them to a file.

        Returns:
            error message
        """
        failures = [x for x in self.outcomes if x]
        if not failures:
            return ""
        ratio = f"{len(self.outcomes) - len(failures)}/{len(self.outcomes)}"
        msg = f"Uploaded {ratio} files onto server {self.dsp_ingest_url}. "
        if len(failures) > self.maximum_prints:
            url = regex.sub(r"https?://", "", self.dsp_ingest_url)
            output_file = Path(f"upload_failures_{self.shortcode}_{url}.csv")
            self._save_to_csv(output_file)
            msg += f"Failed to upload {len(failures)} files. "
            msg += f"The full list of failed files has been saved to '{output_file}'."
        else:
            msg += f"Failed to upload the following {len(failures)} files:"
            msg += list_separator + list_separator.join([f"{failure.filepath}: {failure.reason}" for failure in failures])
        return msg

    def make_final_communication(self) -> bool:
        """Determine the success status of the upload process and communicate it to the user."""
        if msg := self.execute_error_protocol():
            success = False
        else:
            msg = f"Uploaded all {len(self.outcomes)} files onto server {self.dsp_ingest_url}."
            success = True
        logger.info(msg) if success else logger.error(msg)
        print(msg)
        return success

    def _save_to_csv(self, output_file: Path) -> None:
        data = {
            "Filepath": [failure.filepath for failure in self.outcomes if failure],
            "Reason": [failure.reason for failure in self.outcomes if failure],
        }
        df = pd.DataFrame(data)
        df.to_csv(output_file, index=False)
