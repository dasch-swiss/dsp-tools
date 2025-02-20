from __future__ import annotations

import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from typing import Protocol

from dsp_tools.models.custom_warnings import DspToolsUserWarning
from dsp_tools.utils.uri_util import is_iiif_uri
from dsp_tools.xmllib.models.config_options import Permissions
from dsp_tools.xmllib.value_checkers import is_string_like


@dataclass
class AuthorshipLookup:
    lookup: dict[tuple[str, ...], str]

    def get_id(self, authors: tuple[str, ...]) -> str:
        if not (found := self.lookup.get(authors)):
            warnings.warn(DspToolsUserWarning(f"The input authors {authors} are not defined in the look-up."))
            return " / ".join([str(x) for x in authors])
        return found


@dataclass
class Metadata:
    license: str
    copyright_holder: str
    authorship: tuple[str, ...]
    permissions: Permissions
    resource_id: str | None = None

    def __post_init__(self) -> None:
        if not is_string_like(self.license):
            _warn_type_mismatch(expected_type="license", value=self.license, res_id=self.resource_id)
        if not is_string_like(str(self.copyright_holder)):
            _warn_type_mismatch(expected_type="copyright holder", value=self.copyright_holder, res_id=self.resource_id)
        if len(self.authorship) == 0:
            _warn_type_mismatch(
                expected_type="list of authorship strings", value="empty input", res_id=self.resource_id
            )
        for author in self.authorship:
            if not is_string_like(author):
                _warn_type_mismatch(expected_type="author", value=author, res_id=self.resource_id)


class AbstractFileValue(Protocol):
    value: str | Path
    metadata: Metadata
    comment: str | None


@dataclass
class FileValue(AbstractFileValue):
    value: str | Path
    metadata: Metadata
    comment: str | None
    resource_id: str | None = None

    def __post_init__(self) -> None:
        if not is_string_like(str(self.value)):
            _warn_type_mismatch(expected_type="file name", value=self.value, res_id=self.resource_id)


@dataclass
class IIIFUri(AbstractFileValue):
    value: str
    metadata: Metadata
    comment: str | None
    resource_id: str | None = None

    def __post_init__(self) -> None:
        if not is_iiif_uri(self.value):
            _warn_type_mismatch(expected_type="IIIF uri", value=self.value, res_id=self.resource_id)


def _warn_type_mismatch(expected_type: str, value: Any, res_id: str | None) -> None:
    """Emits a warning if a values is not in the expected format."""
    if res_id:
        msg = f"The Resource '{res_id}' has an invalid input: The value '{value}' is not a valid {expected_type}."
    else:
        msg = f"The value '{value}' is not a valid {expected_type}."
    warnings.warn(DspToolsUserWarning(msg))
