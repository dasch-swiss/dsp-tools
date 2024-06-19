from __future__ import annotations

from dataclasses import dataclass

list_separator = "\n    - "
medium_separator = "\n----------------------------\n"

HTTP_OK = 200


@dataclass(frozen=True)
class AllIIIFUriProblems:
    """Information about all problems with IIIF URIs."""

    problems: list[IIIFUriProblem]

    def get_msg(self) -> str:
        """Get a message describing all problems with the IIIF URIs."""
        msg = "There were problems with the following IIIF URI(s):"
        all_msg = [problem.get_msg() for problem in self.problems]
        return msg + medium_separator + medium_separator.join(all_msg)


@dataclass(frozen=True)
class IIIFUriProblem:
    """Information about a problem with an IIIF URI."""

    uri: str
    regex_has_passed: bool
    status_code: int | None = None
    raised_exception_name: str | None = None
    original_text: str | None = None

    def get_msg(self) -> str:
        """Get a message describing the problem with the IIIF URI."""
        msg = [f"URI: {self.uri}"]
        if self.regex_has_passed:
            msg.append("Passed the internal regex check.")
        else:
            msg.append("Did not pass the internal regex check.")
        if self.status_code == HTTP_OK:
            msg.extend(self._good_status_code_bad_regex_msg())
        elif self.status_code is not None:
            msg.extend(self._bad_status_code_msg())
        else:
            msg.extend(self._exception_msg())
        return list_separator.join(msg)

    def _exception_msg(self) -> list[str]:
        return [
            f"An error occurred during the network call: {self.raised_exception_name}",
            f"Error message: {self.original_text}",
        ]

    def _bad_status_code_msg(self) -> list[str]:
        return [
            "The server did not respond as expected.",
            f"Status code: {self.status_code}",
            f"Response text: {self.original_text}",
        ]

    def _good_status_code_bad_regex_msg(self) -> list[str]:
        return [
            "The URI is correct and the server responded as expected.",
            "Please contact the dsp-tools development team with this information.",
        ]
