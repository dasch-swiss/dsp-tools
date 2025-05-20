from __future__ import annotations

from collections.abc import Collection
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from dsp_tools.error.xmllib_warnings import MessageInfo
from dsp_tools.error.xmllib_warnings_util import emit_xmllib_input_type_mismatch_warning
from dsp_tools.error.xmllib_warnings_util import emit_xmllib_input_warning
from dsp_tools.utils.data_formats.uri_util import is_iiif_uri
from dsp_tools.xmllib.internal.checkers import check_and_warn_if_a_string_contains_a_potentially_empty_value
from dsp_tools.xmllib.internal.checkers import check_and_warn_potentially_empty_string
from dsp_tools.xmllib.internal.checkers import is_nonempty_value_internal
from dsp_tools.xmllib.internal.input_converters import check_and_fix_collection_input
from dsp_tools.xmllib.models.config_options import Permissions
from dsp_tools.xmllib.models.licenses.recommended import License


@dataclass
class AuthorshipLookup:
    lookup: dict[tuple[str, ...], str]

    def get_id(self, authors: tuple[str, ...] | None) -> str | None:
        if authors is None:
            return None
        if not (found := self.lookup.get(authors)):
            emit_xmllib_input_warning(MessageInfo(f"The input authors {authors} are not defined in the look-up."))
            return " / ".join([str(x) for x in authors])
        return found


@dataclass
class Metadata:
    license: License | None
    copyright_holder: str | None
    authorship: tuple[str, ...] | None
    permissions: Permissions

    @classmethod
    def new(
        cls,
        license: License | None,
        copyright_holder: str | None,
        authorship: Collection[str] | None,
        permissions: Permissions,
        resource_id: str,
    ) -> Metadata:
        if license is not None and not isinstance(license, License):
            emit_xmllib_input_type_mismatch_warning(
                expected_type="xmllib.License",
                value=license,
                res_id=resource_id,
                value_field="license (bistream/iiif-uri)",
            )
        if not isinstance(permissions, Permissions):
            emit_xmllib_input_type_mismatch_warning(
                expected_type="xmllib.Permissions",
                value=permissions,
                res_id=resource_id,
                value_field="permissions (bistream/iiif-uri)",
            )
        if copyright_holder is not None:
            check_and_warn_potentially_empty_string(
                value=copyright_holder,
                res_id=resource_id,
                expected="string",
                field="copyright_holder (bistream/iiif-uri)",
            )
        if authorship is not None:
            if len(authorship) == 0:
                emit_xmllib_input_type_mismatch_warning(
                    expected_type="list of authorship strings",
                    value="empty input",
                    res_id=resource_id,
                    value_field="authorship (bistream/iiif-uri)",
                )
            fixed_authors = set(
                check_and_fix_collection_input(authorship, "authorship (bistream/iiif-uri)", resource_id)
            )
            for author in fixed_authors:
                check_and_warn_potentially_empty_string(
                    value=author, res_id=resource_id, expected="string", field="authorship (bistream/iiif-uri)"
                )
            fixed_authors_list = [str(x).strip() for x in fixed_authors]
            authors = tuple(sorted(fixed_authors_list))
        else:
            authors = None
        return cls(
            license=license,
            copyright_holder=copyright_holder,
            authorship=authors,
            permissions=permissions,
        )


class AbstractFileValue(Protocol):
    value: str
    metadata: Metadata
    comment: str | None


@dataclass
class FileValue(AbstractFileValue):
    value: str
    metadata: Metadata
    comment: str | None

    @classmethod
    def new(cls, value: str | Path, metadata: Metadata, comment: str | None, resource_id: str) -> FileValue:
        if isinstance(value, Path):
            if str(value) == ".":
                value = ""
            else:
                value = str(value)
        check_and_warn_potentially_empty_string(
            value=value,
            res_id=resource_id,
            expected="file name",
            field="bitstream",
        )
        if is_nonempty_value_internal(comment):
            fixed_comment = str(comment)
            check_and_warn_if_a_string_contains_a_potentially_empty_value(
                value=comment,
                res_id=resource_id,
                field="comment on bitstream",
            )
        else:
            fixed_comment = None
        return cls(value=str(value), metadata=metadata, comment=fixed_comment)


@dataclass
class IIIFUri(AbstractFileValue):
    value: str
    metadata: Metadata
    comment: str | None

    @classmethod
    def new(cls, value: str, metadata: Metadata, comment: str | None, resource_id: str) -> IIIFUri:
        if not is_iiif_uri(value):
            emit_xmllib_input_type_mismatch_warning(
                expected_type="IIIF uri",
                value=value,
                res_id=resource_id,
            )
        if is_nonempty_value_internal(comment):
            fixed_comment = str(comment)
            check_and_warn_if_a_string_contains_a_potentially_empty_value(
                value=comment,
                res_id=resource_id,
                field="comment on iiif-uri",
            )
        else:
            fixed_comment = None
        return cls(value=str(value), metadata=metadata, comment=fixed_comment)
