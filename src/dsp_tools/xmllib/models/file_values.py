from __future__ import annotations

import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from dsp_tools.error.xmllib_warnings import XmllibInputWarning
from dsp_tools.error.xmllib_warnings_util import emit_xmllib_input_type_mismatch_warning
from dsp_tools.utils.data_formats.uri_util import is_iiif_uri
from dsp_tools.xmllib.internal_helpers import check_and_warn_potentially_empty_string
from dsp_tools.xmllib.models.config_options import Permissions


@dataclass
class AuthorshipLookup:
    lookup: dict[tuple[str, ...], str]

    def get_id(self, authors: tuple[str, ...]) -> str:
        if not (found := self.lookup.get(authors)):
            warnings.warn(XmllibInputWarning(f"The input authors {authors} are not defined in the look-up."))
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
        check_and_warn_potentially_empty_string(
            value=self.license,
            res_id=self.resource_id,
            expected="xmllib.License",
            field="license (bistream/iiif-uri)",
        )
        check_and_warn_potentially_empty_string(
            value=self.copyright_holder,
            res_id=self.resource_id,
            expected="string",
            field="copyright_holder (bistream/iiif-uri)",
        )
        if len(self.authorship) == 0:
            emit_xmllib_input_type_mismatch_warning(
                expected_type="list of authorship strings",
                value="empty input",
                res_id=self.resource_id,
                value_field="authorship (bistream/iiif-uri)",
            )
        for author in self.authorship:
            check_and_warn_potentially_empty_string(
                value=author, res_id=self.resource_id, expected="string", field="authorship (bistream/iiif-uri)"
            )


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
        check_and_warn_potentially_empty_string(
            value=self.value,
            res_id=self.resource_id,
            expected="file name",
            field="bistream",
        )
        check_and_warn_potentially_empty_string(
            value=self.comment,
            res_id=self.resource_id,
            expected="string",
            field="comment (bistream)",
        )


@dataclass
class IIIFUri(AbstractFileValue):
    value: str
    metadata: Metadata
    comment: str | None
    resource_id: str | None = None

    def __post_init__(self) -> None:
        if not is_iiif_uri(self.value):
            emit_xmllib_input_type_mismatch_warning(
                expected_type="IIIF uri",
                value=self.value,
                res_id=self.resource_id,
            )
        check_and_warn_potentially_empty_string(
            value=self.comment,
            res_id=self.resource_id,
            expected="string",
            field="comment (iiif-uri)",
        )
