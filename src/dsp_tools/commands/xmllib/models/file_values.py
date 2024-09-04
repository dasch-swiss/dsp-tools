from __future__ import annotations

import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from typing import Protocol

from lxml import etree

from dsp_tools.commands.xmllib.value_checkers import is_string
from dsp_tools.models.custom_warnings import DspToolsUserWarning
from dsp_tools.utils.uri_util import is_iiif_uri

XML_NAMESPACE_MAP = {None: "https://dasch.swiss/schema", "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
DASCH_SCHEMA = "{https://dasch.swiss/schema}"


@dataclass
class AbstractFileValue(Protocol):
    value: str | Path
    permissions: str | None
    comment: str | None = None

    def serialise(self) -> etree._Element:
        raise NotImplementedError


@dataclass
class FileValue(AbstractFileValue):
    value: str | Path
    permissions: str | None = "prop-default"
    comment: str | None = None

    def __post_init__(self) -> None:
        if not is_string(self.value):
            _warn_type_mismatch(expected_type="file name", value=self.value)

    def serialise(self) -> etree._Element:
        attribs = {}
        if self.permissions:
            attribs["permissions"] = self.permissions
        if self.comment:
            attribs["comment"] = self.comment
        ele = etree.Element(f"{DASCH_SCHEMA}bitstream", attrib=attribs, nsmap=XML_NAMESPACE_MAP)
        ele.text = str(self.value)
        return ele


@dataclass
class IIIFUri(AbstractFileValue):
    value: str
    permissions: str | None = "prop-default"
    comment: str | None = None

    def __post_init__(self) -> None:
        if not is_iiif_uri(self.value):
            _warn_type_mismatch(expected_type="IIIF-URI", value=self.value)

    def serialise(self) -> etree._Element:
        attribs = {}
        if self.permissions:
            attribs["permissions"] = self.permissions
        if self.comment:
            attribs["comment"] = self.comment
        ele = etree.Element(f"{DASCH_SCHEMA}iiif-uri", attrib=attribs, nsmap=XML_NAMESPACE_MAP)
        ele.text = str(self.value)
        return ele


def _warn_type_mismatch(expected_type: str, value: Any) -> None:
    """Emits a warning if a values is not in the expected format."""
    msg = f"The following value is not a valid {expected_type}.\n    Value: {value}"
    warnings.warn(DspToolsUserWarning(msg))
