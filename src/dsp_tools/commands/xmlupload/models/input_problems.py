from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from enum import auto

list_separator = "\n    - "
medium_separator = "\n----------------------------\n"

HTTP_OK = 200
HTTP_SERVER_ERROR = 500
ACCESS_REFUSED_STATUS_CODES = (401, 403, 429)


class IIIFProblemCategory(StrEnum):
    ACCESS_REFUSED = auto()
    INVALID = auto()
    UNREACHABLE = auto()


@dataclass(frozen=True)
class AllIIIFUriProblems:
    """Information about all problems with IIIF URIs."""

    problems: list[IIIFUriProblem]
    refused_hosts: list[IIIFHostRefused]

    def get_warning_msg(self) -> str | None:
        """Get a message about the IIIF URIs that are invalid."""
        invalid = [x.get_msg() for x in self.problems if x.category == IIIFProblemCategory.INVALID]
        return _join_msg("There were problems with the following IIIF URI(s):", invalid)

    def get_info_msg(self) -> str | None:
        """Get a message about the IIIF URIs that could not be checked."""
        refused = [x.get_msg() for x in self.refused_hosts]
        unreachable = [x.get_msg() for x in self.problems if x.category == IIIFProblemCategory.UNREACHABLE]
        return _join_msg("The following IIIF URI(s) could not be checked:", refused + unreachable)


def _join_msg(header: str, msgs: list[str]) -> str | None:
    if not msgs:
        return None
    return header + medium_separator + medium_separator.join(msgs)


@dataclass
class IIIFHostRefused:
    """A IIIF server that refused access. Its URIs are not checked."""

    host: str
    status_code: int | None
    unverified_uris: list[str]

    def get_msg(self) -> str:
        msg = [
            f"IIIF server: {self.host}",
            f"The server refused access to dsp-tools. Status code: {self.status_code}",
            f"Number of IIIF URI(s) that were not checked: {len(self.unverified_uris)}",
            "Some IIIF servers accept automated requests only from their own network or VPN.",
        ]
        return list_separator.join(msg)


@dataclass(frozen=True)
class IIIFUriProblem:
    """Information about a problem with an IIIF URI."""

    uri: str
    regex_has_passed: bool
    status_code: int | None = None
    raised_exception_name: str | None = None

    @property
    def category(self) -> IIIFProblemCategory:
        if self.status_code in ACCESS_REFUSED_STATUS_CODES:
            return IIIFProblemCategory.ACCESS_REFUSED
        if self.status_code is None or self.status_code >= HTTP_SERVER_ERROR:
            return IIIFProblemCategory.UNREACHABLE
        return IIIFProblemCategory.INVALID

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
            msg.append(self._exception_msg())
        return list_separator.join(msg)

    def _exception_msg(self) -> str:
        return f"An error occurred during the network call: {self.raised_exception_name}"

    def _bad_status_code_msg(self) -> list[str]:
        return ["The server did not respond as expected.", f"Status code: {self.status_code}"]

    def _good_status_code_bad_regex_msg(self) -> list[str]:
        return [
            "Although the IIIF-server responded as expected, this URI did not pass validation.",
            "Please contact the dsp-tools development team (at support@dasch.swiss) with this information.",
        ]


@dataclass
class MultimediaFileNotFoundProblem:
    res_id: str
    filepath: str
