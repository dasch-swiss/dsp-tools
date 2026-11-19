from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import regex

separator = "\n\n"
list_separator = "\n- "
list_separator_indented = "\n    - "


@dataclass(frozen=True)
class UploadFailure:
    """Information on why the upload of a file to the ingest server failed."""

    filepath: Path
    reason: str
    status_code: int | None = None
    response_text: str | None = None


@dataclass(frozen=True)
class UploadFailures:
    """Aggregated information of all failed uploads."""

    failures: list[UploadFailure]
    num_of_initial_files: int
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
        ratio = f"{self.num_of_initial_files - len(self.failures)}/{self.num_of_initial_files}"
        msg = f"Uploaded {ratio} files onto server {self.dsp_ingest_url}. "
        if len(self.failures) > self.maximum_prints:
            url = regex.sub(r"https?://", "", self.dsp_ingest_url)
            output_file = Path(f"upload_failures_{self.shortcode}_{url}.csv")
            self._save_to_csv(output_file)
            msg += f"Failed to upload {len(self.failures)} files. "
            msg += f"The full list of failed files has been saved to '{output_file}'."
        else:
            msg += f"Failed to upload the following {len(self.failures)} files:"
            for f in self.failures:
                msg += list_separator + f"{f.filepath}: {f.reason}"
                if f.status_code:
                    msg += list_separator_indented + f"Status code: {f.status_code}"
                if f.response_text:
                    msg += list_separator_indented + f"Response text: {f.response_text}"
        return msg

    def _save_to_csv(self, output_file: Path) -> None:
        data = {
            "Filepath": [failure.filepath for failure in self.failures],
            "Reason": [failure.reason for failure in self.failures],
            "Status code": [failure.status_code for failure in self.failures],
            "Response text": [failure.response_text for failure in self.failures],
        }
        df = pd.DataFrame(data)
        df.to_csv(output_file, index=False)
