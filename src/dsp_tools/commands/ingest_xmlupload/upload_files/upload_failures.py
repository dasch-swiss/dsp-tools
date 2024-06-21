from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd
from loguru import logger


@dataclass(frozen=True)
class UploadFailureDetail:
    """Information on why the upload of a file to the ingest server failed."""

    filepath: Path
    reason: str


@dataclass(frozen=True)
class UploadFailureDetails:
    """Aggregated information of all failed uploads."""

    failures: list[UploadFailureDetail]
    num_of_files_to_be_uploaded: int
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
        if len(self.failures) > self.maximum_prints:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            output_file = Path(f"{timestamp}_upload_failures_{self.shortcode}_{self.dsp_ingest_url}.csv")
            self._save_to_csv(output_file)
            msg = f"Failed to upload {len(self.failures)} files. "
            msg += f"The full list of failed files has been saved to '{output_file}'."
            return msg
        msg = f"Failed to upload the following {len(self.failures)} files to {self.dsp_ingest_url}:\n - "
        msg += "\n".join([f" - {failure.filepath}: {failure.reason}" for failure in self.failures])
        return msg

    def make_final_communication(self) -> bool:
        """Determine the success status of the upload process and communicate it to the user."""
        if not self.failures:
            msg = f"Uploaded all {self.num_of_files_to_be_uploaded} files onto server {self.dsp_ingest_url}."
            success = True
        else:
            ratio = f"{self.num_of_files_to_be_uploaded - len(self.failures)}/{self.num_of_files_to_be_uploaded}"
            msg = f"Uploaded {ratio} files onto server {self.dsp_ingest_url}."
            success = False
        print(msg)
        logger.info(msg)
        return success

    def _save_to_csv(self, output_file: Path) -> None:
        data = {
            "Filepath": [failure.filepath for failure in self.failures],
            "Reason": [failure.reason for failure in self.failures],
        }
        df = pd.DataFrame(data)
        df.to_csv(output_file, index=False)
