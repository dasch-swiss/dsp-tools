from __future__ import annotations

from collections.abc import Collection
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from dsp_tools.error.exceptions import UnreachableCodeError
from dsp_tools.utils.data_formats.uri_util import is_iiif_uri
from dsp_tools.xmllib.internal.checkers import check_and_warn_if_a_string_contains_a_potentially_empty_value
from dsp_tools.xmllib.internal.checkers import check_and_warn_potentially_empty_string
from dsp_tools.xmllib.internal.checkers import is_nonempty_value_internal
from dsp_tools.xmllib.internal.input_converters import check_and_fix_authorship_input
from dsp_tools.xmllib.internal.input_converters import check_and_fix_is_non_empty_string
from dsp_tools.xmllib.internal.xmllib_warnings import MessageInfo
from dsp_tools.xmllib.internal.xmllib_warnings_util import emit_xmllib_input_type_mismatch_warning
from dsp_tools.xmllib.internal.xmllib_warnings_util import emit_xmllib_input_warning
from dsp_tools.xmllib.models.licenses.recommended import License
from dsp_tools.xmllib.models.permissions import Permissions
from dsp_tools.xmllib.models.placeholder import PlaceholderFile


@dataclass
class AuthorshipLookup:
    lookup: dict[tuple[str, ...], str]

    def get_id(self, authors: tuple[str, ...] | None) -> str | None:
        if authors is None:
            return None
        if (found := self.lookup.get(authors)) is None:
            raise UnreachableCodeError(f"The authors {authors} are not defined in the look-up.")
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
        permissions: Permissions | str,
        resource_id: str,
    ) -> Metadata:
        lic_ = license
        if license is not None and not isinstance(license, License):
            emit_xmllib_input_type_mismatch_warning(
                expected_type="xmllib.License",
                value=license,
                res_id=resource_id,
                value_field="license (bistream/iiif-uri)",
            )
            lic_ = None
        if isinstance(permissions, Permissions):
            pass
        elif is_nonempty_value_internal(permissions):
            permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS
        else:
            emit_xmllib_input_type_mismatch_warning(
                expected_type="xmllib.Permissions",
                value=permissions,
                res_id=resource_id,
                value_field="permissions (bistream/iiif-uri)",
            )
            permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS
        if copyright_holder is not None:
            copyright_holder = check_and_fix_is_non_empty_string(
                value=copyright_holder,
                res_id=resource_id,
                value_field="copyright_holder (bistream/iiif-uri)",
            )
        authors = check_and_fix_authorship_input(authorship, resource_id, "authorship (bistream/iiif-uri)")
        return cls(
            license=lic_,
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
    value: str | PlaceholderFile
    metadata: Metadata
    comment: str | None

    @classmethod
    def new(
        cls, value: str | Path | PlaceholderFile, metadata: Metadata, comment: str | None, resource_id: str
    ) -> FileValue:
        match value:
            case Path():
                if str(value) == ".":
                    msg_info = MessageInfo(
                        message=f"Your input '{value}' is empty. Please enter a valid file path.",
                        resource_id=resource_id,
                        field="bitstream",
                    )
                    emit_xmllib_input_warning(msg_info)
                    value = ""
                else:
                    value = str(value)
            case PlaceholderFile():
                pass
            case _:
                check_and_warn_potentially_empty_string(
                    value=value,
                    res_id=resource_id,
                    expected="file path",
                    field="bitstream",
                )
                value = str(value)
        if is_nonempty_value_internal(comment):
            fixed_comment = str(comment)
            check_and_warn_if_a_string_contains_a_potentially_empty_value(
                value=comment,
                res_id=resource_id,
                field="comment on bitstream",
            )
        else:
            fixed_comment = None
        return cls(value=value, metadata=metadata, comment=fixed_comment)


@dataclass
class IIIFUri(AbstractFileValue):
    value: str
    metadata: Metadata
    comment: str | None

    @classmethod
    def new(cls, value: str, metadata: Metadata, comment: str | None, resource_id: str) -> IIIFUri:
        v = str(value)
        if not is_iiif_uri(v):
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
        return cls(value=v, metadata=metadata, comment=fixed_comment)
