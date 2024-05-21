from __future__ import annotations

from dataclasses import dataclass

list_separator = "\n    - "
medium_separator = "\n----------------------------\n"


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
    passed_regex: bool
    status_code: int | None = None
    response_text: str | None = None
    thrown_exception: Exception | None = None

    def get_msg(self) -> str:
        """Get a message describing the problem with the IIIF URI."""
        msg = [f"URI: {self.uri}"]
        if self.passed_regex:
            msg.append("Passed the internal regex check.")
        else:
            msg.append("Did not pass the internal regex check.")
        if self.status_code is not None:
            msg.extend(self._bad_status_code_msg())
        else:
            msg.extend(self._exception_msg())
        return list_separator.join(msg)

    def _exception_msg(self) -> list[str]:
        return [
            f"A connection error occurred during the network call: {self.thrown_exception.__class__.__name__}",
            f"Original message: {self.thrown_exception}",
        ]

    def _bad_status_code_msg(self) -> list[str]:
        return [
            "The server did not respond as expected.",
            f"Status code: {self.status_code}",
            f"Response text: {self.response_text}",
        ]
