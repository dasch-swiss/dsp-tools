from __future__ import annotations

import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from typing import Protocol

from lxml import etree

from dsp_tools.models.custom_warnings import DspToolsUserWarning
from dsp_tools.utils.uri_util import is_iiif_uri
from dsp_tools.xmllib.models.config_options import Permissions
from dsp_tools.xmllib.value_checkers import is_string_like

XML_NAMESPACE_MAP = {None: "https://dasch.swiss/schema", "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
DASCH_SCHEMA = "{https://dasch.swiss/schema}"


@dataclass
class Metadata:
    license: str
    copyright_holder: str
    authorship: set[str]
    resource_id: str

    def __post_init__(self) -> None:
        if not is_string_like(str(self.license)):
            _warn_type_mismatch(expected_type="license", value=self.license, res_id=self.resource_id)
        if not is_string_like(str(self.copyright_holder)):
            _warn_type_mismatch(expected_type="copyright holder", value=self.license, res_id=self.resource_id)
        for author in self.authorship:
            if not is_string_like(author):
                _warn_type_mismatch(expected_type="author", value=author, res_id=self.resource_id)

    def serialise(self) -> dict[str, str]:
        return {
            "license": self.license,
            "copyright-holder": self.copyright_holder,
        }


class AbstractFileValue(Protocol):
    value: str | Path
    metadata: Metadata
    permissions: Permissions
    comment: str | None = None

    def serialise(self) -> etree._Element:
        raise NotImplementedError


@dataclass
class FileValue(AbstractFileValue):
    value: str | Path
    metadata: Metadata
    permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS
    comment: str | None = None
    resource_id: str | None = None

    def __post_init__(self) -> None:
        if not is_string_like(str(self.value)):
            _warn_type_mismatch(expected_type="file name", value=self.value, res_id=self.resource_id)

    def serialise(self) -> etree._Element:
        attribs = self.metadata.serialise()
        if self.permissions != Permissions.PROJECT_SPECIFIC_PERMISSIONS:
            attribs["permissions"] = self.permissions.value
        if is_string_like(self.comment):
            attribs["comment"] = str(self.comment)
        ele = etree.Element(f"{DASCH_SCHEMA}bitstream", attrib=attribs, nsmap=XML_NAMESPACE_MAP)
        ele.text = str(self.value)
        return ele


@dataclass
class IIIFUri(AbstractFileValue):
    value: str
    metadata: Metadata
    permissions: Permissions = Permissions.PROJECT_SPECIFIC_PERMISSIONS
    comment: str | None = None
    resource_id: str | None = None

    def __post_init__(self) -> None:
        if not is_iiif_uri(self.value):
            _warn_type_mismatch(expected_type="IIIF uri", value=self.value, res_id=self.resource_id)

    def serialise(self) -> etree._Element:
        attribs = self.metadata.serialise()
        if self.permissions != Permissions.PROJECT_SPECIFIC_PERMISSIONS:
            attribs["permissions"] = self.permissions.value
        if is_string_like(self.comment):
            attribs["comment"] = str(self.comment)
        ele = etree.Element(f"{DASCH_SCHEMA}iiif-uri", attrib=attribs, nsmap=XML_NAMESPACE_MAP)
        ele.text = str(self.value)
        return ele


def _warn_type_mismatch(expected_type: str, value: Any, res_id: str | None) -> None:
    """Emits a warning if a values is not in the expected format."""
    if res_id:
        msg = f"The Resource '{res_id}' has an invalid input: The value '{value}' is not a valid {expected_type}."
    else:
        msg = f"The value '{value}' is not a valid {expected_type}."
    warnings.warn(DspToolsUserWarning(msg))
